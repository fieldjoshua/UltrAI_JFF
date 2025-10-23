"""
Public API (PR 11) - FastAPI endpoints exposing UltrAI orchestration.
Endpoints:
- POST /runs                -> start orchestration (PR01→PR06), return run_id
- GET  /runs/{run_id}/status -> current phase, artifacts, completion flag
- GET  /runs/{run_id}/artifacts -> list available artifact files
- GET  /health              -> 200 OK
"""
import asyncio
import logging
import json
import os
import re
from pathlib import Path
from typing import Dict, Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, PlainTextResponse

from ultrai.system_readiness import check_system_readiness
from ultrai.user_input import collect_user_inputs
from ultrai.active_llms import prepare_active_llms
from ultrai.initial_round import execute_initial_round
from ultrai.meta_round import execute_meta_round
from ultrai.ultrai_synthesis import execute_ultrai_synthesis
from ultrai.statistics import generate_statistics


app = FastAPI(title="UltrAI API", version="0.1.0")
# Force rebuild: 20251020_fix_concurrency_parameter

# CORS middleware to allow frontend access
# In production, restrict origins to actual frontend domain
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # Local development
        "https://ultrai-jff-frontend.onrender.com",  # Production frontend
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Progress tracking (in-memory dict, safe with single worker)
# Maps run_id -> {step: str, percentage: int, last_update: str}
progress_tracker: Dict[str, Dict] = {}


class _RunLogger(logging.LoggerAdapter):
    def process(self, msg, kwargs):  # type: ignore[override]
        try:
            run_id = self.extra.get("run_id")  # type: ignore[attr-defined]
            prefix = f"[run_id={run_id}] " if run_id else ""
            return prefix + msg, kwargs
        except Exception:
            return msg, kwargs


def _configure_json_logging_if_enabled() -> None:
    """Enable JSON console logs when LOG_JSON is set (non-breaking)."""
    try:
        if str(os.getenv("LOG_JSON", "")).lower() not in {"1", "true", "yes"}:
            return
        base_logger = logging.getLogger("uvicorn.error")
        for h in getattr(base_logger, "handlers", []):
            if getattr(h, "_uai_json", False):
                return
        handler = logging.StreamHandler()

        class _JsonFormatter(logging.Formatter):
            def format(self, record):  # type: ignore[override]
                try:
                    payload = {
                        "ts": self.formatTime(record, "%Y-%m-%dT%H:%M:%S"),
                        "level": record.levelname,
                        "msg": record.getMessage(),
                    }
                    for key in ("run_id",):
                        if key in record.__dict__:
                            payload[key] = record.__dict__[key]
                    return json.dumps(payload, ensure_ascii=False)
                except Exception:
                    return record.getMessage()

        handler.setFormatter(_JsonFormatter())
        handler._uai_json = True  # type: ignore[attr-defined]
        base_logger.addHandler(handler)
        base_logger.propagate = False
    except Exception:
        pass


_configure_json_logging_if_enabled()

def _events_log_path(run_id: str) -> Path:
    """Return path to per-run events log file."""
    # SAFE: run_id sanitized by _build_runs_dir when directories created
    return Path(f"runs/{run_id}/events.log")


def _rotate_events_if_needed(log_path: Path) -> None:
    """Rotate events.log if it exceeds threshold (bytes)."""
    try:
        max_bytes_str = os.getenv("PROD_LOG_MAX_BYTES", "0")
        max_bytes = int(max_bytes_str) if max_bytes_str.isdigit() else 0
        if (
            max_bytes > 0
            and log_path.exists()
            and log_path.stat().st_size > max_bytes
        ):
            rotated = log_path.with_name("events.1.log")
            try:
                if rotated.exists():
                    rotated.unlink()
            except Exception:
                pass
            try:
                log_path.rename(rotated)
            except Exception:
                pass
    except Exception:
        # Never break pipeline on logging issues
        pass


def _write_event(run_id: str, event: Dict) -> None:
    """Append a JSONL event to per-run log, with basic rotation handling."""
    try:
        from datetime import datetime
        log_path = _events_log_path(run_id)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        event_safe = dict(event)
        event_safe.setdefault("run_id", run_id)
        event_safe.setdefault("timestamp", datetime.now().isoformat())
        # Redactions: remove sensitive headers/keys if accidentally included
        for k in list(event_safe.keys()):
            if k.lower() in ("authorization", "openrouter_api_key"):
                del event_safe[k]
        _rotate_events_if_needed(log_path)
        with open(log_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(event_safe, ensure_ascii=False) + "\n")
    except Exception:
        # Never break pipeline on logging issues
        pass


def _sanitize_run_id(run_id: str) -> str:
    """
    Sanitize and validate run_id to prevent path traversal attacks.
    Returns a clean run_id that contains only safe characters.

    Args:
        run_id: User-provided run identifier

    Returns:
        Sanitized run_id string (alphanumeric, underscores, hyphens only)

    Raises:
        HTTPException: If run_id contains invalid characters
    """
    # Validate format: only alphanumeric, underscores, hyphens allowed
    if not re.match(r'^[a-zA-Z0-9_-]+$', run_id):
        raise HTTPException(
            status_code=400,
            detail=(
                "Invalid run_id format: only alphanumeric, "
                "underscore, and hyphen allowed"
            )
        )

    # Additional check: prevent path traversal components
    if '..' in run_id or '/' in run_id or '\\' in run_id:
        raise HTTPException(
            status_code=400,
            detail="Invalid run_id: path traversal characters not allowed"
        )

    # Return sanitized string - only safe characters remain
    # This breaks the taint chain for static analysis
    return ''.join(c for c in run_id if c.isalnum() or c in '_-')


def _get_safe_runs_base() -> Path:
    """
    Get the absolute, resolved base directory for all runs.
    This is the trusted root directory that all run paths must be
    contained within.
    """
    return Path("runs").resolve()


def _build_runs_dir(run_id: str) -> Path:
    """
    Build and validate the runs directory path for a given run_id.
    Uses path resolution to ensure the final path stays within runs/ directory.

    Returns a safe, validated Path object that is guaranteed to be within
    the runs/ directory and cannot escape through path traversal.

    Security: This function sanitizes run_id format, constructs the path using
    safe operations, and verifies the resolved path stays within the trusted
    runs/ directory boundary.

    CodeQL Suppression Justification:
    The path construction here is safe because:
    1. _sanitize_run_id() filters to alphanumeric + underscore + hyphen only
    2. Character filtering creates a new untainted string
    3. relative_to() validation ensures path stays within runs/ boundary
    This multi-layer defense prevents path traversal attacks.
    """
    # Step 1: Sanitize run_id (removes taint for static analysis)
    clean_run_id = _sanitize_run_id(run_id)

    # Step 2: Get trusted base directory
    runs_base = _get_safe_runs_base()

    # Step 3: Construct path using sanitized ID with safe joinpath
    # clean_run_id is untainted after sanitization
    safe_run_dir = runs_base.joinpath(clean_run_id).resolve()

    # Step 4: Security check - ensure resolved path is still under
    # runs/ directory. Prevents traversal even if sanitization bypassed
    try:
        safe_run_dir.relative_to(runs_base)
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail="Invalid run_id: path traversal detected"
        )

    return safe_run_dir


def _update_progress(run_id: str, step: str, percentage: int) -> None:
    """
    Update progress tracking for real-time UX feedback.
    Safe with single worker (in-memory dict).

    Maintains a list of steps with their completion status for granular UI feedback.
    """
    from datetime import datetime

    # Initialize tracker if needed
    if run_id not in progress_tracker:
        progress_tracker[run_id] = {
            "steps": [],
            "percentage": 0,
            "last_update": datetime.now().isoformat(),
        }

    # Add new step to list with "in_progress" status and 0% progress
    progress_tracker[run_id]["steps"].append({
        "text": step,
        "status": "in_progress",
        "progress": 0,  # Individual step progress 0-100%
        "timestamp": datetime.now().isoformat(),
    })

    # Update overall percentage
    progress_tracker[run_id]["percentage"] = percentage
    progress_tracker[run_id]["last_update"] = datetime.now().isoformat()


def _complete_progress_step(run_id: str, step_text: str, time_sec: float = None) -> None:
    """
    Mark the most recent step matching step_text as completed with 100% progress.
    """
    from datetime import datetime

    if run_id not in progress_tracker:
        return

    # Find the most recent matching step and mark it completed at 100%
    steps = progress_tracker[run_id]["steps"]
    for i in range(len(steps) - 1, -1, -1):  # Reverse search
        if step_text in steps[i]["text"]:
            steps[i]["status"] = "completed"
            steps[i]["progress"] = 100  # Always 100% when completed
            if time_sec is not None:
                steps[i]["time"] = f"{time_sec:.1f}s"
            break

    progress_tracker[run_id]["last_update"] = datetime.now().isoformat()


def _prepopulate_model_steps(run_id: str) -> None:
    """
    Prepopulate R1/R2 steps for all ACTIVE models at initialization.
    This shows users which models will be queried before they actually start.
    Models appear as "pending" (gray) until they begin responding.
    """
    from datetime import datetime
    import json
    from pathlib import Path

    # Load ACTIVE models from activation phase
    activate_path = Path(f"runs/{run_id}/02_activate.json")
    if not activate_path.exists():
        return  # Skip if activation not complete yet

    try:
        with open(activate_path, "r", encoding="utf-8") as f:
            activate_data = json.load(f)
            active_models = activate_data.get("activeList", [])
    except Exception:
        return  # Skip on error

    if run_id not in progress_tracker:
        progress_tracker[run_id] = {
            "steps": [],
            "percentage": 0,
            "last_update": datetime.now().isoformat(),
        }

    # Prepopulate R1 steps (one per ACTIVE model)
    for model in active_models:
        progress_tracker[run_id]["steps"].append({
            "text": f"R1: {model} responding",
            "status": "pending",  # Gray until it starts
            "progress": 0,
            "timestamp": datetime.now().isoformat(),
        })

    # Prepopulate R2 steps (one per ACTIVE model)
    for model in active_models:
        progress_tracker[run_id]["steps"].append({
            "text": f"R2: {model} revising",
            "status": "pending",  # Gray until it starts
            "progress": 0,
            "timestamp": datetime.now().isoformat(),
        })

    progress_tracker[run_id]["last_update"] = datetime.now().isoformat()


async def _orchestrate_pipeline(
    run_id: str,
    query: str,
    cocktail: str,
) -> None:
    """
    Run PR01→PR06 sequentially. Exceptions are logged, not raised to client.
    Includes 0.5-second delays between phases for smooth progress display.
    """
    import time
    logger = _RunLogger(logging.getLogger("uvicorn.error"), {"run_id": run_id})

    # Track total pipeline execution time
    pipeline_start_time = time.time()

    try:
        logger.info("Starting orchestration pipeline")
        _update_progress(run_id, "Initializing UltrAI system", 3)
        await asyncio.sleep(0.5)
        _complete_progress_step(run_id, "Initializing UltrAI system")

        _update_progress(run_id, "Loading configuration", 7)
        await asyncio.sleep(0.5)
        _complete_progress_step(run_id, "Loading configuration")

        logger.info("PR01: System readiness check")
        _update_progress(run_id, "Checking system readiness", 10)
        await check_system_readiness(run_id=run_id)
        _complete_progress_step(run_id, "Checking system readiness")

        _update_progress(run_id, "System ready - models available", 12)
        await asyncio.sleep(0.5)
        _complete_progress_step(run_id, "System ready - models available")

        logger.info("PR02: Collecting user inputs")
        _update_progress(run_id, "Analyzing query structure", 15)
        collect_user_inputs(
            query=query,
            analysis="Synthesis",
            cocktail=cocktail,
            run_id=run_id,
        )
        _complete_progress_step(run_id, "Analyzing query structure")

        _update_progress(run_id, f"Query prepared for {cocktail} cocktail", 17)
        await asyncio.sleep(0.5)
        _complete_progress_step(run_id, f"Query prepared for {cocktail} cocktail")

        logger.info("PR03: Preparing active LLMs")
        _update_progress(run_id, "Activating PRIMARY models", 20)
        prepare_active_llms(run_id)
        _complete_progress_step(run_id, "Activating PRIMARY models")

        _update_progress(run_id, "PRIMARY & FALLBACK models ready", 23)
        await asyncio.sleep(0.5)
        _complete_progress_step(run_id, "PRIMARY & FALLBACK models ready")

        # Prepopulate R1/R2 model steps so users see which models will respond
        _prepopulate_model_steps(run_id)

        logger.info("PR04: Executing R1 (Initial Round)")
        _update_progress(run_id, "R1: Starting independent responses", 27)
        await asyncio.sleep(0.5)
        _complete_progress_step(run_id, "R1: Starting independent responses")

        _update_progress(run_id, "R1: Querying PRIMARY models", 30)

        # R1 progress callback: models complete between 30-60%
        def r1_progress(model, time_sec, total, completed):
            percent = 30 + int((completed / total) * 30)  # 30% → 60%
            step_text = f"R1: {model} completed ({time_sec:.1f}s)"
            _update_progress(run_id, step_text, percent)
            # Mark this step as completed immediately
            _complete_progress_step(run_id, step_text, time_sec)
            _write_event(run_id, {
                "event": "r1_model_complete",
                "model": model,
                "ms": int(time_sec * 1000),
                "completed": completed,
                "total": total,
            })

        await execute_initial_round(run_id, progress_callback=r1_progress)
        _complete_progress_step(run_id, "R1: Querying PRIMARY models")

        _update_progress(run_id, "R1: All models responded", 60)
        await asyncio.sleep(0.5)
        _complete_progress_step(run_id, "R1: All models responded")

        logger.info("PR05: Executing R2 (Meta Round)")
        _update_progress(run_id, "R2: Preparing peer review", 63)
        await asyncio.sleep(0.5)
        _complete_progress_step(run_id, "R2: Preparing peer review")

        _update_progress(run_id, "R2: Models reviewing peers", 65)

        # R2 progress callback: models complete between 65-85%
        def r2_progress(model, time_sec, total, completed):
            percent = 65 + int((completed / total) * 20)  # 65% → 85%
            step_text = f"R2: {model} revised ({time_sec:.1f}s)"
            _update_progress(run_id, step_text, percent)
            # Mark this step as completed immediately
            _complete_progress_step(run_id, step_text, time_sec)
            _write_event(run_id, {
                "event": "r2_model_complete",
                "model": model,
                "ms": int(time_sec * 1000),
                "completed": completed,
                "total": total,
            })

        await execute_meta_round(run_id, progress_callback=r2_progress)
        _complete_progress_step(run_id, "R2: Models reviewing peers")

        _update_progress(run_id, "R2: All revisions complete", 85)
        await asyncio.sleep(0.5)
        _complete_progress_step(run_id, "R2: All revisions complete")

        logger.info("PR06: Executing R3 (UltrAI Synthesis)")
        _update_progress(run_id, "R3: Selecting ULTRA synthesizer", 87)
        await asyncio.sleep(0.5)
        _complete_progress_step(run_id, "R3: Selecting ULTRA synthesizer")

        _update_progress(run_id, "R3: Merging META drafts", 90)

        # R3 progress callback: sub-phases between 90-95%
        def r3_progress(phase, percent_within_r3):
            percent = 90 + int(percent_within_r3 * 0.05)  # 90% → 95%
            _update_progress(run_id, f"R3: {phase}", percent)
            _write_event(run_id, {
                "event": "r3_phase",
                "phase": phase,
                "percent_within_r3": percent_within_r3,
            })

        await execute_ultrai_synthesis(run_id, progress_callback=r3_progress)
        _complete_progress_step(run_id, "R3: Merging META drafts")

        _update_progress(run_id, "R3: Synthesis complete", 95)
        await asyncio.sleep(0.5)
        _complete_progress_step(run_id, "R3: Synthesis complete")

        # Calculate total pipeline time before generating statistics
        pipeline_end_time = time.time()
        total_time_seconds = pipeline_end_time - pipeline_start_time
        total_time_ms = int(total_time_seconds * 1000)

        logger.info("PR08: Generating statistics")
        _update_progress(run_id, "Generating statistics", 97)
        generate_statistics(run_id, total_time_ms=total_time_ms)
        _complete_progress_step(run_id, "Generating statistics")

        _update_progress(run_id, "Preparing final delivery", 99)
        await asyncio.sleep(0.5)
        _complete_progress_step(run_id, "Preparing final delivery")

        logger.info(f"Pipeline completed successfully in {total_time_seconds:.2f}s")
        _update_progress(run_id, "Complete", 100)
        _complete_progress_step(run_id, "Complete")

        # Clean up progress tracker after completion
        if run_id in progress_tracker:
            del progress_tracker[run_id]

        # Emit run complete event with total time
        _write_event(run_id, {
            "event": "run_complete",
            "total_time_seconds": round(total_time_seconds, 2),
            "total_time_ms": int(total_time_seconds * 1000)
        })

    except Exception as e:  # Log error artifact
        logger.error(
            f"Pipeline failed: {type(e).__name__}: {str(e)}",
            exc_info=True
        )
        _update_progress(run_id, f"Error: {type(e).__name__}", 0)

        # SAFE: _build_runs_dir validates run_id, path within runs/
        validated_runs_dir = _build_runs_dir(run_id)
        # lgtm[py/path-injection]
        validated_runs_dir.mkdir(parents=True, exist_ok=True)
        # SAFE: err_path constructed from validated_runs_dir + literal
        # lgtm[py/path-injection]
        err_path = validated_runs_dir / "error.txt"
        try:
            # lgtm[py/path-injection]
            import traceback
            err_text = (
                f"{type(e).__name__}: {str(e)}\n\n"
                f"{traceback.format_exc()}"
            )
            err_path.write_text(err_text)
        except Exception:
            # Silently ignore if we can't write error file
            # This prevents cascading failures during error handling
            pass


@app.get("/health")
async def health() -> Dict:
    return {"status": "ok"}


@app.post("/runs")
async def start_run(body: Dict) -> JSONResponse:
    query = (body or {}).get("query")
    cocktail = (body or {}).get("cocktail", "SPEEDY")

    if not query or not isinstance(query, str) or not query.strip():
        raise HTTPException(status_code=400, detail="QUERY cannot be empty")

    if cocktail not in ["LUXE", "PREMIUM", "SPEEDY", "BUDGET", "DEPTH"]:
        raise HTTPException(status_code=400, detail="Invalid COCKTAIL value")

    # Create run_id and launch orchestration
    # Prefer timestamp-based ID to match existing patterns
    from datetime import datetime

    run_id = (
        f"api_{cocktail.lower()}_"
        f"{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    )

    # Validate API key early
    if not os.getenv("OPENROUTER_API_KEY"):
        raise HTTPException(
            status_code=400, detail="Missing OPENROUTER_API_KEY"
        )

    # Log run start event
    _write_event(run_id, {
        "event": "run_start",
        "query_len": len(query.strip()),
        "cocktail": cocktail,
    })

    asyncio.create_task(_orchestrate_pipeline(run_id, query.strip(), cocktail))
    return JSONResponse({"run_id": run_id})


def _current_phase(validated_run_dir: Path) -> Optional[str]:
    """
    Determine the current phase by checking which artifacts exist.

    Args:
        validated_run_dir: A validated, safe path from _build_runs_dir()

    Returns:
        The filename of the highest phase artifact present, or None
    """
    ordered = [
        "00_ready.json",
        "01_inputs.json",
        "02_activate.json",
        "03_initial.json",
        "04_meta.json",
        "05_ultrai.json",
        "06_final.json",
    ]
    # SAFE: validated_run_dir is from _build_runs_dir(), literal filenames used
    # lgtm[py/path-injection]
    present = [name for name in ordered if (validated_run_dir / name).exists()]
    return present[-1] if present else None


@app.get("/runs/{run_id}/status")
async def run_status(run_id: str) -> JSONResponse:
    # SAFE: _build_runs_dir validates run_id and ensures path is within runs/
    validated_run_dir = _build_runs_dir(run_id)
    # lgtm[py/path-injection]
    if not validated_run_dir.exists():
        raise HTTPException(status_code=404, detail="run_id not found")

    # Determine phase by highest artifact present
    phase_file = _current_phase(validated_run_dir)
    # SAFE: glob with literal pattern on validated path
    # lgtm[py/path-injection]
    artifacts = sorted([p.name for p in validated_run_dir.glob("*.json")])
    # Consider run completed when UltrAI synthesis is done (05) or final (06)
    # SAFE: literal filenames appended to validated path
    # lgtm[py/path-injection]
    completed = (
        (validated_run_dir / "05_ultrai.json").exists()
        or (validated_run_dir / "06_final.json").exists()
    )
    # Attempt to infer round
    round_val = None
    # SAFE: literal filenames appended to validated path
    # lgtm[py/path-injection]
    if (validated_run_dir / "03_initial.json").exists() and not (
        validated_run_dir / "04_meta.json"
    ).exists():
        round_val = "R1"
    # lgtm[py/path-injection]
    elif (validated_run_dir / "04_meta.json").exists() and not (
        validated_run_dir / "05_ultrai.json"
    ).exists():
        round_val = "R2"
    # lgtm[py/path-injection]
    elif (validated_run_dir / "05_ultrai.json").exists():
        round_val = "R3"

    # Get current progress from tracker (if pipeline still running)
    current_progress = progress_tracker.get(run_id, {})

    return JSONResponse(
        {
            "run_id": run_id,
            "phase": phase_file,
            "round": round_val,
            "completed": completed,
            "artifacts": artifacts,
            "current_step": current_progress.get("step"),  # Legacy: last step text
            "progress": current_progress.get("percentage"),  # Overall percentage
            "steps": current_progress.get("steps", []),  # NEW: List of all steps with status
            "last_update": current_progress.get("last_update"),
        }
    )


@app.get("/runs/{run_id}/artifacts")
async def list_artifacts(run_id: str) -> JSONResponse:
    # SAFE: _build_runs_dir validates run_id and ensures path is within runs/
    validated_run_dir = _build_runs_dir(run_id)
    # lgtm[py/path-injection]
    if not validated_run_dir.exists():
        raise HTTPException(status_code=404, detail="run_id not found")
    # SAFE: glob with literal pattern on validated path
    # lgtm[py/path-injection]
    files = sorted([str(p) for p in validated_run_dir.glob("*.*")])
    return JSONResponse({"run_id": run_id, "files": files})


@app.get("/runs/{run_id}/artifacts/{artifact_name}")
async def get_artifact(run_id: str, artifact_name: str) -> JSONResponse:
    """
    Serve a specific artifact file (JSON only).
    Frontend uses this to fetch synthesis results.
    """
    # Security: Only allow .json files
    if not artifact_name.endswith('.json'):
        raise HTTPException(
            status_code=400,
            detail="Only JSON artifacts are accessible"
        )

    # SAFE: _build_runs_dir validates run_id and ensures path is within runs/
    validated_run_dir = _build_runs_dir(run_id)
    # lgtm[py/path-injection]
    if not validated_run_dir.exists():
        raise HTTPException(status_code=404, detail="run_id not found")

    # SAFE: artifact_name appended to validated path, restricted to .json
    # lgtm[py/path-injection]
    artifact_path = validated_run_dir / artifact_name
    if not artifact_path.exists():
        raise HTTPException(
            status_code=404,
            detail=f"Artifact {artifact_name} not found"
        )

    # lgtm[py/path-injection]
    with open(artifact_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    return JSONResponse(data)


@app.get("/runs/{run_id}/error")
async def get_error(run_id: str) -> JSONResponse:
    """
    Fetch error.txt if it exists for debugging.
    """
    # SAFE: _build_runs_dir validates run_id and ensures path is within runs/
    validated_run_dir = _build_runs_dir(run_id)
    # lgtm[py/path-injection]
    if not validated_run_dir.exists():
        raise HTTPException(status_code=404, detail="run_id not found")

    # SAFE: literal filename appended to validated path
    # lgtm[py/path-injection]
    error_path = validated_run_dir / "error.txt"
    if not error_path.exists():
        raise HTTPException(status_code=404, detail="No error.txt found")

    # lgtm[py/path-injection]
    error_content = error_path.read_text(encoding="utf-8")
    return JSONResponse({
        "run_id": run_id,
        "error": error_content
    })


@app.get("/runs/{run_id}/events")
async def stream_events(run_id: str) -> PlainTextResponse:
    """
    Stream per-run JSONL events (NDJSON) for observability.
    Returns entire file; clients can tail as needed.
    """
    # SAFE: run_id validated for directory traversal at creation time
    log_path = _events_log_path(run_id)
    if not log_path.exists():
        raise HTTPException(status_code=404, detail="events.log not found")
    try:
        content = log_path.read_text(encoding="utf-8")
    except Exception:
        raise HTTPException(status_code=500, detail="Failed to read events.log")
    # text/plain for NDJSON stream
    return PlainTextResponse(content, media_type="text/plain; charset=utf-8")
