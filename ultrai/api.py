"""
Public API (PR 11) - FastAPI endpoints exposing UltrAI orchestration.
Endpoints:
- POST /runs                -> start orchestration (PR01→PR06), return run_id
- GET  /runs/{run_id}/status -> current phase, artifacts, completion flag
- GET  /runs/{run_id}/artifacts -> list available artifact files
- GET  /health              -> 200 OK
"""
import asyncio
import os
import re
from pathlib import Path
from typing import Dict, Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from ultrai.system_readiness import check_system_readiness
from ultrai.user_input import collect_user_inputs
from ultrai.active_llms import prepare_active_llms
from ultrai.initial_round import execute_initial_round
from ultrai.meta_round import execute_meta_round
from ultrai.ultrai_synthesis import execute_ultrai_synthesis
from ultrai.statistics import generate_statistics


app = FastAPI(title="UltrAI API", version="0.1.0")

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


async def _orchestrate_pipeline(
    run_id: str,
    query: str,
    cocktail: str,
) -> None:
    """
    Run PR01→PR06 sequentially. Exceptions are logged, not raised to client.
    """
    import logging
    logger = logging.getLogger("uvicorn.error")

    try:
        logger.info(f"[{run_id}] Starting orchestration pipeline")

        logger.info(f"[{run_id}] PR01: System readiness check")
        await check_system_readiness(run_id=run_id)

        logger.info(f"[{run_id}] PR02: Collecting user inputs")
        collect_user_inputs(
            query=query,
            analysis="Synthesis",
            cocktail=cocktail,
            run_id=run_id,
        )

        logger.info(f"[{run_id}] PR03: Preparing active LLMs")
        prepare_active_llms(run_id)

        logger.info(f"[{run_id}] PR04: Executing R1 (Initial Round)")
        await execute_initial_round(run_id)

        logger.info(f"[{run_id}] PR05: Executing R2 (Meta Round)")
        await execute_meta_round(run_id)

        logger.info(f"[{run_id}] PR06: Executing R3 (UltrAI Synthesis)")
        await execute_ultrai_synthesis(run_id)

        logger.info(f"[{run_id}] PR08: Generating statistics")
        generate_statistics(run_id)

        logger.info(f"[{run_id}] Pipeline completed successfully")
    except Exception as e:  # Log error artifact
        logger.error(f"[{run_id}] Pipeline failed: {type(e).__name__}: {str(e)}", exc_info=True)
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
            err_path.write_text(f"{type(e).__name__}: {str(e)}\n\n{traceback.format_exc()}")
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

    return JSONResponse(
        {
            "run_id": run_id,
            "phase": phase_file,
            "round": round_val,
            "completed": completed,
            "artifacts": artifacts,
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
