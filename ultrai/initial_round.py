"""
PR 04 — Initial Round (R1)

Executes the first round of LLM queries where each ACTIVE model receives
the user's query independently and produces a response.

Round name: R1
Term for outputs: INITIAL

Creates artifacts:
- runs/<RunID>/03_initial.json - Array of response objects
- runs/<RunID>/03_initial_status.json - Metadata and status
"""

import os
import json
import asyncio
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List

try:
    import httpx
except ImportError:
    raise ImportError(
        "httpx package is required. Install with: pip install httpx"
    )

try:
    from dotenv import load_dotenv
except ImportError:
    raise ImportError(
        "python-dotenv package is required. Install with: pip install python-dotenv"
    )


class InitialRoundError(Exception):
    """Raised when initial round execution fails"""
    pass


def calculate_concurrency_limit(
    query: str,
    has_attachments: bool = False,
    attachment_count: int = 0
) -> int:
    """
    Calculate concurrency limit optimized for PRIMARY model execution.

    UltrAI cocktails use exactly 3 PRIMARY models per cocktail.
    FALLBACK models are sequential (only called after PRIMARY fails/times out).

    Optimization rationale:
    - All cocktails have 3 PRIMARY models (LUXE, PREMIUM, SPEEDY, BUDGET, DEPTH)
    - FALLBACK models are SEQUENTIAL (activated after PRIMARY timeout)
    - Max concurrent: 3 (all PRIMARY models at once)
    - Removes query length calculations (negligible impact with 3 calls)

    Args:
        query: User query text (unused, kept for API compatibility)
        has_attachments: Whether query includes attachments
        attachment_count: Number of attachments

    Returns:
        Concurrency limit (1-3)
    """
    # Hard cap: 3 PRIMARY models (FALLBACK models are sequential)
    base_limit = 3

    # Only reduce for attachments (images are expensive on OpenRouter)
    if has_attachments:
        if attachment_count > 3:
            # Many attachments: Serialize to avoid overwhelming API
            return 1
        elif attachment_count > 1:
            # Multiple attachments: Reduce concurrency
            return 2
        else:
            # Single attachment: Moderate reduction (2 concurrent)
            return 2

    # No attachments: Full concurrency for all PRIMARY models
    return base_limit


async def execute_initial_round(run_id: str, progress_callback=None) -> Dict:
    """
    Execute R1 (Initial Round) - each ACTIVE model responds independently.

    Reads:
    - runs/<run_id>/02_activate.json (for activeList)
    - runs/<run_id>/01_inputs.json (for QUERY)

    Creates:
    - runs/<run_id>/03_initial.json (response array)
    - runs/<run_id>/03_initial_status.json (metadata)

    Args:
        run_id: The run ID to process
        progress_callback: Optional callback function(model, time_sec, total, completed)
                          called when each model completes

    Returns:
        Dictionary containing:
        - responses: List of response objects
        - status: Execution status
        - metadata: Run metadata

    Raises:
        InitialRoundError: If execution fails
    """
    load_dotenv()
    runs_dir = Path(f"runs/{run_id}")

    # Load activeList from 02_activate.json
    activate_path = runs_dir / "02_activate.json"
    if not activate_path.exists():
        raise InitialRoundError(
            f"Missing 02_activate.json for run_id: {run_id}. "
            "Run active LLMs preparation first."
        )

    with open(activate_path, "r", encoding="utf-8") as f:
        activate_data = json.load(f)
        active_list = activate_data.get("activeList", [])
        backup_list = activate_data.get("backupList", [])  # Load backup models

    if len(active_list) < 2:
        raise InitialRoundError(
            f"Insufficient ACTIVE models: {len(active_list)}. Need at least 2."
        )

    # Load QUERY from 01_inputs.json
    inputs_path = runs_dir / "01_inputs.json"
    if not inputs_path.exists():
        raise InitialRoundError(
            f"Missing 01_inputs.json for run_id: {run_id}. "
            "Collect user inputs first."
        )

    with open(inputs_path, "r", encoding="utf-8") as f:
        inputs_data = json.load(f)
        query = inputs_data.get("QUERY")

    if not query:
        raise InitialRoundError("QUERY not found in 01_inputs.json")

    # Get API key
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        raise InitialRoundError(
            "Missing OPENROUTER_API_KEY environment variable"
        )

    # Optional site identification
    site_url = os.getenv("YOUR_SITE_URL", "http://localhost:8000")
    site_name = os.getenv("YOUR_SITE_NAME", "UltrAI Project")

    # Calculate dynamic concurrency limit based on query characteristics
    # TODO: Add attachment detection when attachment support is implemented
    concurrency_limit = calculate_concurrency_limit(
        query=query,
        has_attachments=False,  # Not yet supported
        attachment_count=0
    )

    # Execute R1 for each ACTIVE model in parallel with dynamic rate limiting
    # Backup models will be used if primary models fail
    responses, failed_models = await _execute_parallel_queries(
        active_list, backup_list, query, api_key, site_url, site_name,
        concurrency_limit, progress_callback
    )

    # Build result
    result = {
        "responses": responses,
        "failed_models": failed_models,  # Models that failed (don't retry in R2)
        "status": "COMPLETED",
        "metadata": {
            "run_id": run_id,
            "timestamp": datetime.now().isoformat(),
            "phase": "03_initial",
            "round": "R1"
        }
    }

    # Create 03_initial.json
    initial_path = runs_dir / "03_initial.json"
    with open(initial_path, "w", encoding="utf-8") as f:
        json.dump(responses, f, indent=2, ensure_ascii=False)

    # Create 03_initial_status.json
    status_data = {
        "status": "COMPLETED",
        "round": "R1",
        "details": {
            "count": len(responses),
            "models": [r["model"] for r in responses],
            "failed_models": failed_models,  # Track failures for R2
            "concurrency_limit": concurrency_limit
        },
        "metadata": {
            "run_id": run_id,
            "timestamp": datetime.now().isoformat()
        }
    }

    status_path = runs_dir / "03_initial_status.json"
    with open(status_path, "w", encoding="utf-8") as f:
        json.dump(status_data, f, indent=2, ensure_ascii=False)

    return result


async def _execute_parallel_queries(
    models: List[str],
    backups: List[str],
    query: str,
    api_key: str,
    site_url: str,
    site_name: str,
    concurrency_limit: int,
    progress_callback=None
) -> tuple[List[Dict], List[str]]:
    """
    Execute queries to multiple models with fast-fail backup swapping.

    Args:
        models: List of primary model identifiers
        backups: List of backup models (same indices as models)
        query: User query
        api_key: OpenRouter API key
        site_url: Site URL for headers
        site_name: Site name for headers
        concurrency_limit: Maximum concurrent requests
        progress_callback: Optional callback for progress updates

    Returns:
        Tuple of (responses, failed_models):
        - responses: List of response objects with fields: round, model, text, ms
        - failed_models: List of model names that failed (don't retry in R2)
    """
    # Create dynamic semaphore based on query characteristics
    semaphore = asyncio.Semaphore(concurrency_limit)

    # Track responses and failures
    responses = []
    failed_models = []
    completed_count = 0
    total_count = len(models)

    # Try all primary models first
    for i, model in enumerate(models):
        try:
            result = await _query_single_model(
                model, query, api_key, site_url, site_name, semaphore
            )
            responses.append(result)
            completed_count += 1

            # Call progress callback if provided
            if progress_callback:
                time_sec = result.get("ms", 0) / 1000.0
                progress_callback(result["model"], time_sec, total_count, completed_count)

        except Exception as e:
            # Primary model failed - try backup if available
            failed_models.append(model)
            backup_model = backups[i] if i < len(backups) else None

            if backup_model:
                try:
                    # Immediately try backup model
                    backup_result = await _query_single_model(
                        backup_model, query, api_key, site_url, site_name, semaphore
                    )
                    responses.append(backup_result)
                    completed_count += 1

                    # Call progress callback for backup success
                    if progress_callback:
                        time_sec = backup_result.get("ms", 0) / 1000.0
                        progress_callback(
                            f"{backup_model} (backup)", time_sec, total_count, completed_count
                        )

                except Exception as backup_error:
                    # Both primary and backup failed
                    responses.append({
                        "round": "INITIAL",
                        "model": model,
                        "text": f"ERROR: Primary failed ({str(e)}), Backup failed ({str(backup_error)})",
                        "ms": 0,
                        "error": True
                    })
                    completed_count += 1
            else:
                # No backup available
                responses.append({
                    "round": "INITIAL",
                    "model": model,
                    "text": f"ERROR: {str(e)}",
                    "ms": 0,
                    "error": True
                })
                completed_count += 1

    return responses, failed_models


async def _query_single_model(
    model: str,
    query: str,
    api_key: str,
    site_url: str,
    site_name: str,
    semaphore: asyncio.Semaphore
) -> Dict:
    """
    Query a single model and return response object.

    Args:
        model: Model identifier
        query: User query
        api_key: OpenRouter API key
        site_url: Site URL for headers
        site_name: Site name for headers
        semaphore: Concurrency semaphore for rate limiting

    Returns:
        Dict with fields: round, model, text, ms
    """
    url = "https://openrouter.ai/api/v1/chat/completions"

    headers = {
        "Authorization": f"Bearer {api_key}",
        "HTTP-Referer": site_url,
        "X-Title": site_name,
        "Content-Type": "application/json"
    }

    payload = {
        "model": model,
        "messages": [
            {"role": "user", "content": query}
        ]
    }

    # Fast-fail configuration: Fail quickly and rely on backup models
    max_retries = 1  # Reduced from 3 - fail fast

    # Timeout configuration: Fast connect, but allow model to finish once engaged
    timeout_config = httpx.Timeout(
        connect=10.0,  # 10s to establish connection (fail fast if no response)
        read=45.0,     # 45s between bytes (allow model to think/stream)
        write=10.0,    # 10s to send request
        pool=5.0       # 5s to get connection from pool
    )

    # Connection pooling optimized for PRIMARY model usage (max 3 concurrent)
    # Limits configure exactly what we need, avoiding resource waste
    limits_config = httpx.Limits(
        max_connections=3,        # Exactly PRIMARY count (FALLBACK models are sequential)
        max_keepalive_connections=3,  # Keep all connections warm for reuse
        keepalive_expiry=30.0     # 30s keepalive (OpenRouter recommends)
    )

    start_time = time.time()

    for attempt in range(max_retries):
        try:
            async with semaphore:  # Concurrency limit (1-5)
                async with httpx.AsyncClient(
                    timeout=timeout_config,
                    limits=limits_config  # Optimized connection pooling
                ) as client:
                    response = await client.post(url, headers=headers, json=payload)

                    # Handle specific error codes
                    if response.status_code == 401:
                        raise InitialRoundError(
                            f"Invalid API key for model {model}"
                        )
                    elif response.status_code == 402:
                        raise InitialRoundError(
                            f"Insufficient credits for model {model}"
                        )
                    elif response.status_code == 429:
                        # Rate limited - fail fast, backup model will be used
                        retry_after = min(int(response.headers.get("Retry-After", 10)), 10)
                        if attempt < max_retries - 1:
                            await asyncio.sleep(retry_after)
                            continue
                        raise InitialRoundError(
                            f"Rate limited for model {model}. Will try backup."
                        )
                    elif response.status_code >= 500:
                        # Server error - retry with exponential backoff
                        if attempt < max_retries - 1:
                            await asyncio.sleep(2 ** attempt)
                            continue
                        raise InitialRoundError(
                            f"Server error for model {model}: {response.status_code}"
                        )

                    response.raise_for_status()

                    # Parse response
                    data = response.json()

                    # CRITICAL: Check for mid-stream errors (per dependencies.md)
                    if "choices" in data and len(data["choices"]) > 0:
                        finish_reason = data["choices"][0].get("finish_reason")
                        if finish_reason == "error":
                            error_msg = data["choices"][0].get("message", {}).get("content", "Unknown error")
                            raise InitialRoundError(
                                f"Model {model} returned error: {error_msg}"
                            )

                        # Extract text
                        text = data["choices"][0].get("message", {}).get("content", "")
                    else:
                        raise InitialRoundError(
                            f"Invalid response structure from model {model}"
                        )

                    # Calculate elapsed time in milliseconds
                    elapsed_ms = int((time.time() - start_time) * 1000)

                    return {
                        "round": "INITIAL",
                        "model": model,
                        "text": text,
                        "ms": elapsed_ms
                    }

        except httpx.TimeoutException:
            if attempt < max_retries - 1:
                await asyncio.sleep(2 ** attempt)
                continue
            raise InitialRoundError(
                f"Timeout for model {model} after {max_retries} attempts"
            )
        except httpx.HTTPStatusError as e:
            if attempt < max_retries - 1 and e.response.status_code >= 500:
                await asyncio.sleep(2 ** attempt)
                continue
            raise InitialRoundError(
                f"HTTP error for model {model}: {e.response.status_code}"
            )
        except InitialRoundError:
            raise
        except Exception as e:
            if attempt < max_retries - 1:
                await asyncio.sleep(2 ** attempt)
                continue
            raise InitialRoundError(
                f"Failed to query model {model}: {str(e)}"
            )

    raise InitialRoundError(
        f"Failed to query model {model} after {max_retries} attempts"
    )


def main():
    """CLI entry point for initial round execution"""
    import sys

    if len(sys.argv) < 2:
        print("Usage: python -m ultrai.initial_round <run_id>")
        sys.exit(1)

    run_id = sys.argv[1]

    async def async_main():
        try:
            result = await execute_initial_round(run_id)
            print(f"Initial Round (R1) COMPLETED")
            print(f"Run ID: {run_id}")
            print(f"Responses: {len(result['responses'])}")
            print(f"Artifacts:")
            print(f"  - runs/{run_id}/03_initial.json")
            print(f"  - runs/{run_id}/03_initial_status.json")
            return 0
        except InitialRoundError as e:
            print(f"Initial Round FAILED: {e}")
            return 1
        except Exception as e:
            print(f"Unexpected error: {e}")
            import traceback
            traceback.print_exc()
            return 1

    sys.exit(asyncio.run(async_main()))


if __name__ == "__main__":
    main()
