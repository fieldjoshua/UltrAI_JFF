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
from pathlib import Path
from typing import Dict, Optional

from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse

from ultrai.system_readiness import check_system_readiness
from ultrai.user_input import collect_user_inputs
from ultrai.active_llms import prepare_active_llms
from ultrai.initial_round import execute_initial_round
from ultrai.meta_round import execute_meta_round
from ultrai.ultrai_synthesis import execute_ultrai_synthesis
from ultrai.addons_processing import apply_addons
from ultrai.statistics import generate_statistics


app = FastAPI(title="UltrAI API", version="0.1.0")


def _build_runs_dir(run_id: str) -> Path:
    return Path("runs") / run_id


async def _orchestrate_pipeline(
    run_id: str,
    query: str,
    cocktail: str,
) -> None:
    """
    Run PR01→PR06 sequentially. Exceptions are logged, not raised to client.
    """
    try:
        await check_system_readiness(run_id=run_id)
        collect_user_inputs(
            query=query,
            analysis="Synthesis",
            cocktail=cocktail,
            addons=[],
            run_id=run_id,
        )
        prepare_active_llms(run_id)
        await execute_initial_round(run_id)
        await execute_meta_round(run_id)
        await execute_ultrai_synthesis(run_id)
        # Apply add-ons (none by default) and produce final.json
        apply_addons(run_id)
        # Generate stats.json
        generate_statistics(run_id)
    except Exception as e:  # Log error artifact
        runs_dir = _build_runs_dir(run_id)
        runs_dir.mkdir(parents=True, exist_ok=True)
        err_path = runs_dir / "error.txt"
        try:
            err_path.write_text(str(e))
        except Exception:
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

    if cocktail not in ["PREMIUM", "SPEEDY", "BUDGET", "DEPTH"]:
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
        raise HTTPException(status_code=400, detail="Missing OPENROUTER_API_KEY")

    asyncio.create_task(_orchestrate_pipeline(run_id, query.strip(), cocktail))
    return JSONResponse({"run_id": run_id})


def _current_phase(run_dir: Path) -> Optional[str]:
    ordered = [
        "00_ready.json",
        "01_inputs.json",
        "02_activate.json",
        "03_initial.json",
        "04_meta.json",
        "05_ultrai.json",
        "06_final.json",
    ]
    present = [name for name in ordered if (run_dir / name).exists()]
    return present[-1] if present else None


@app.get("/runs/{run_id}/status")
async def run_status(run_id: str) -> JSONResponse:
    run_dir = _build_runs_dir(run_id)
    if not run_dir.exists():
        raise HTTPException(status_code=404, detail="run_id not found")

    # Determine phase by highest artifact present
    phase_file = _current_phase(run_dir)
    artifacts = sorted([p.name for p in run_dir.glob("*.json")])
    completed = phase_file == "06_final.json"
    # Attempt to infer round
    round_val = None
    if (run_dir / "03_initial.json").exists() and not (
        run_dir / "04_meta.json"
    ).exists():
        round_val = "R1"
    elif (run_dir / "04_meta.json").exists() and not (
        run_dir / "05_ultrai.json"
    ).exists():
        round_val = "R2"
    elif (run_dir / "05_ultrai.json").exists():
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
    run_dir = _build_runs_dir(run_id)
    if not run_dir.exists():
        raise HTTPException(status_code=404, detail="run_id not found")
    files = sorted([str(p) for p in run_dir.glob("*.*")])
    return JSONResponse({"run_id": run_id, "files": files})


