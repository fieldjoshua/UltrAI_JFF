"""
PR 05 — Meta Round (R2)

Each ACTIVE model revises its answer after reviewing peers' INITIAL drafts.

Reads:
- runs/<run_id>/02_activate.json (for activeList)
- runs/<run_id>/03_initial.json (for peer drafts)

Creates:
- runs/<run_id>/04_meta.json (revised response array)
- runs/<run_id>/04_meta_status.json (metadata and status)
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
        "python-dotenv package is required. Install with: "
        "pip install python-dotenv"
    )

# Import variable rate limiting from initial_round
from ultrai.initial_round import calculate_concurrency_limit


class MetaRoundError(Exception):
    """Raised when meta round execution fails"""
    pass


async def execute_meta_round(run_id: str, progress_callback=None) -> Dict:
    """
    Execute R2 (Meta Round) - each ACTIVE model revises after reviewing peers.

    Args:
        run_id: The run ID to process
        progress_callback: Optional callback function(model, time_sec, total, completed)
                          called when each model completes

    Returns:
        Dict containing:
        - responses: List of META response objects
        - status: Execution status
        - metadata: Run metadata

    Raises:
        MetaRoundError: If execution fails
    """
    load_dotenv()
    runs_dir = Path(f"runs/{run_id}")

    # Load original user query from inputs
    inputs_path = runs_dir / "01_inputs.json"
    if not inputs_path.exists():
        raise MetaRoundError(
            f"Missing 01_inputs.json for run_id: {run_id}. "
            "Collect user inputs first."
        )

    with open(inputs_path, "r", encoding="utf-8") as f:
        inputs_data = json.load(f)
        original_query = inputs_data.get("QUERY", "")

    if not original_query:
        raise MetaRoundError("Original query not found in 01_inputs.json")

    # Load INITIAL responses to see which models actually succeeded
    # (including backup models that replaced failed primaries)
    initial_path = runs_dir / "03_initial.json"
    if not initial_path.exists():
        raise MetaRoundError(
            (
                f"Missing 03_initial.json for run_id: {run_id}. "
                "Execute initial round first."
            )
        )

    # Get the list of models that succeeded in R1 (including backups)
    with open(initial_path, "r", encoding="utf-8") as f:
        initial_drafts: List[Dict] = json.load(f)

    # Use only models that succeeded in R1 - this includes backup replacements!
    active_list = [
        draft.get("model")
        for draft in initial_drafts
        if not draft.get("error") and draft.get("model")
    ]

    if len(active_list) < 2:
        raise MetaRoundError(
            f"Insufficient successful models from R1: {len(active_list)}. Need at least 2."
        )

    # Validate initial_drafts
    if not isinstance(initial_drafts, list) or len(initial_drafts) == 0:
        raise MetaRoundError("Initial drafts are missing or invalid")

    # Get API key
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        raise MetaRoundError("Missing OPENROUTER_API_KEY environment variable")

    # Optional site identification
    site_url = os.getenv("YOUR_SITE_URL", "http://localhost:8000")
    site_name = os.getenv("YOUR_SITE_NAME", "UltrAI Project")

    # Build peer context (FULL responses, no truncation) for META instruction
    peer_summaries = []
    for draft in initial_drafts:
        model_id = draft.get("model", "unknown")
        text = draft.get("text", "")
        if draft.get("error"):
            summary = f"- {model_id}: ERROR"
        else:
            # Include FULL peer response (no truncation)
            # Models need complete context to properly revise
            summary = f"- {model_id}: {text}"
        peer_summaries.append(summary)

    peer_context = "\n\n".join(peer_summaries)  # Double newline for readability

    # Calculate dynamic concurrency limit based on peer context length
    # META queries are longer due to peer review content
    concurrency_limit = calculate_concurrency_limit(
        query=peer_context,
        has_attachments=False,
        attachment_count=0,
        num_primary_models=len(active_list)
    )

    # Execute META queries for each ACTIVE model in parallel
    responses = await _execute_parallel_meta(
        active_list=active_list,
        original_query=original_query,
        peer_context=peer_context,
        api_key=api_key,
        site_url=site_url,
        site_name=site_name,
        concurrency_limit=concurrency_limit,
        progress_callback=progress_callback,
    )

    # Build result
    result: Dict = {
        "responses": responses,
        "status": "COMPLETED",
        "metadata": {
            "run_id": run_id,
            "timestamp": datetime.now().isoformat(),
            "phase": "04_meta",
            "round": "R2",
        },
    }

    # Persist artifacts
    meta_path = runs_dir / "04_meta.json"
    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(responses, f, indent=2, ensure_ascii=False)

    status = {
        "status": "COMPLETED",
        "round": "R2",
        "details": {
            "count": len(responses),
            "models": [r.get("model") for r in responses],
            "concurrency_limit": concurrency_limit,
        },
        "metadata": {
            "run_id": run_id,
            "timestamp": datetime.now().isoformat(),
        },
    }

    status_path = runs_dir / "04_meta_status.json"
    with open(status_path, "w", encoding="utf-8") as f:
        json.dump(status, f, indent=2, ensure_ascii=False)

    return result


async def _execute_parallel_meta(
    active_list: List[str],
    original_query: str,
    peer_context: str,
    api_key: str,
    site_url: str,
    site_name: str,
    concurrency_limit: int,
    progress_callback=None,
) -> List[Dict]:
    """
    Execute META queries with variable rate limiting.

    Args:
        active_list: List of model identifiers
        original_query: The original user query from R1
        peer_context: Peer drafts for review
        api_key: OpenRouter API key
        site_url: Site URL for headers
        site_name: Site name for headers
        concurrency_limit: Maximum concurrent requests
        progress_callback: Optional callback for progress updates

    Returns:
        List of response objects with fields: round, model, text, ms
    """
    # Create dynamic semaphore based on peer context characteristics
    semaphore = asyncio.Semaphore(concurrency_limit)

    tasks = [
        _query_meta_single(
            model,
            original_query,
            peer_context,
            api_key,
            site_url,
            site_name,
            semaphore,
        )
        for model in active_list
    ]

    # Use as_completed to report progress as each model finishes
    responses = []
    completed_count = 0
    total_count = len(active_list)

    for coro in asyncio.as_completed(tasks):
        try:
            result = await coro
            responses.append(result)
            completed_count += 1

            # Call progress callback if provided
            if progress_callback and not result.get("error"):
                time_sec = result.get("ms", 0) / 1000.0
                progress_callback(result["model"], time_sec, total_count, completed_count)

        except Exception as e:
            # Find which model failed (this is a limitation of as_completed)
            # We'll append error responses at the end
            responses.append({
                "round": "META",
                "model": "unknown",  # Will be corrected below
                "text": f"ERROR: {str(e)}",
                "ms": 0,
                "error": True
            })
            completed_count += 1

    # Ensure we have responses for all models (handle errors)
    if len(responses) < total_count:
        for i in range(len(responses), total_count):
            responses.append({
                "round": "META",
                "model": active_list[i],
                "text": "ERROR: No response received",
                "ms": 0,
                "error": True
            })

    return responses


async def _query_meta_single(
    model: str,
    original_query: str,
    peer_context: str,
    api_key: str,
    site_url: str,
    site_name: str,
    semaphore: asyncio.Semaphore,
) -> Dict:
    """
    Query a single model for META revision and return response object.

    Args:
        model: Model identifier
        original_query: The original user query from R1
        peer_context: Peer drafts for review (full responses, not truncated)
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
        "Content-Type": "application/json",
    }

    instruction = (
        "Do not assume any response is true. "
        "Review your peers' INITIAL drafts below. "
        "Revise your answer accordingly. "
        "List contradictions you resolved and what changed."
    )

    # Build complete R2 prompt with original query AND full peer responses
    user_prompt = (
        f"{instruction}\n\n"
        f"ORIGINAL QUERY:\n{original_query}\n\n"
        f"PEER DRAFTS (INITIAL ROUND):\n{peer_context}"
    )

    payload = {
        "model": model,
        "messages": [
            {
                "role": "system",
                "content": "You are in the META revision round (R2).",
            },
            {
                "role": "user",
                "content": user_prompt,
            },
        ],
    }

    # PRIMARY_ATTEMPTS configuration: 2 attempts before giving up (R2 is revision round)
    max_retries = 2  # PRIMARY_ATTEMPTS (fail fast in R2, models already validated in R1)

    # Timeout configuration: PRIMARY_TIMEOUT per attempt
    timeout_config = httpx.Timeout(
        connect=10.0,  # 10s to establish connection (fail fast if no response)
        read=15.0,     # PRIMARY_TIMEOUT: 15s between bytes (2 attempts = 30s max)
        write=10.0,    # 10s to send request
        pool=5.0       # 5s to get connection from pool
    )

    # Connection pooling optimized for PRIMARY model usage (max 3 concurrent)
    # Same optimization as initial_round for consistency
    limits_config = httpx.Limits(
        max_connections=3,        # Exactly PRIMARY count (no FALLBACK in R2)
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
                    response = await client.post(
                        url,
                        headers=headers,
                        json=payload,
                    )

                    if response.status_code == 401:
                        raise MetaRoundError(
                            f"Invalid API key for model {model}"
                        )
                    elif response.status_code == 402:
                        raise MetaRoundError(
                            f"Insufficient credits for model {model}"
                        )
                    elif response.status_code == 429:
                        # Rate limited in R2 - fail fast, we already have R1 data
                        retry_after = min(int(response.headers.get("Retry-After", 10)), 10)
                        if attempt < max_retries - 1:
                            await asyncio.sleep(retry_after)
                            continue
                        raise MetaRoundError(
                            f"Rate limited for model {model} in R2. Using R1 data."
                        )
                    elif response.status_code >= 500:
                        if attempt < max_retries - 1:
                            await asyncio.sleep(2 ** attempt)
                            continue
                        raise MetaRoundError(
                            (
                                "Server error for model "
                                f"{model}: {response.status_code}"
                            )
                        )

                    response.raise_for_status()

                    data = response.json()

                    # Mid-stream error detection
                    if "choices" in data and len(data["choices"]) > 0:
                        finish_reason = data["choices"][0].get(
                            "finish_reason"
                        )
                        if finish_reason == "error":
                            error_msg = (
                                data["choices"][0]
                                .get("message", {})
                                .get("content", "Unknown error")
                            )
                            raise MetaRoundError(
                                f"Model {model} returned error: {error_msg}"
                            )

                        text = (
                            data["choices"][0]
                            .get("message", {})
                            .get("content", "")
                        )
                    else:
                        raise MetaRoundError(
                            f"Invalid response structure from model {model}"
                        )

                    elapsed_ms = int((time.time() - start_time) * 1000)

                    return {
                        "round": "META",
                        "model": model,
                        "text": text,
                        "ms": elapsed_ms,
                    }

        except httpx.TimeoutException:
            if attempt < max_retries - 1:
                await asyncio.sleep(2 ** attempt)
                continue
            raise MetaRoundError(
                f"Timeout for model {model} after {max_retries} attempts"
            )
        except httpx.HTTPStatusError as e:
            if attempt < max_retries - 1 and e.response.status_code >= 500:
                await asyncio.sleep(2 ** attempt)
                continue
            raise MetaRoundError(
                f"HTTP error for model {model}: {e.response.status_code}"
            )
        except MetaRoundError:
            raise
        except Exception as e:
            if attempt < max_retries - 1:
                await asyncio.sleep(2 ** attempt)
                continue
            raise MetaRoundError(
                f"Failed to query model {model}: {str(e)}"
            )

    raise MetaRoundError(
        f"Failed to query model {model} after {max_retries} attempts"
    )


def main():
    """CLI entry point for meta round execution"""
    import sys

    if len(sys.argv) < 2:
        print("Usage: python -m ultrai.meta_round <run_id>")
        sys.exit(1)

    run_id = sys.argv[1]

    async def async_main():
        try:
            result = await execute_meta_round(run_id)
            print("Meta Round (R2) COMPLETED")
            print(f"Run ID: {run_id}")
            print(f"Responses: {len(result['responses'])}")
            print("Artifacts:")
            print(f"  - runs/{run_id}/04_meta.json")
            print(f"  - runs/{run_id}/04_meta_status.json")
            return 0
        except MetaRoundError as e:
            print(f"Meta Round FAILED: {e}")
            return 1
        except Exception as e:
            print(f"Unexpected error: {e}")
            import traceback
            traceback.print_exc()
            return 1

    sys.exit(asyncio.run(async_main()))


if __name__ == "__main__":
    main()
