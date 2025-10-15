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
    Calculate dynamic concurrency limit based on query characteristics.

    Adjusts rate limiting to optimize performance and cost:
    - Short simple queries: High concurrency (fast, cheap)
    - Long complex queries: Low concurrency (slow, expensive)
    - Queries with attachments: Very low concurrency (images costly)

    Args:
        query: User query text
        has_attachments: Whether query includes attachments (images/files)
        attachment_count: Number of attachments

    Returns:
        Concurrency limit (1-50)
    """
    base_limit = 50

    # Adjust for query length
    query_len = len(query)
    if query_len < 200:
        # Short query: "What is 2+2?" - Full concurrency
        length_factor = 1.0
    elif query_len < 1000:
        # Medium query: Paragraph - Moderate concurrency
        length_factor = 0.6
    elif query_len < 5000:
        # Long query: Multiple paragraphs - Low concurrency
        length_factor = 0.3
    else:
        # Very long query: Essay/document - Very low concurrency
        length_factor = 0.1

    # Adjust for attachments (images are expensive on OpenRouter)
    attachment_factor = 1.0
    if has_attachments:
        # Single attachment: Reduce by 50%
        attachment_factor = 0.5
        if attachment_count > 1:
            # Multiple attachments: Reduce by 75%
            attachment_factor = 0.25
        if attachment_count > 3:
            # Many attachments: Reduce by 90%
            attachment_factor = 0.1

    # Calculate final limit
    limit = int(base_limit * length_factor * attachment_factor)

    # Ensure minimum of 1, maximum of 50
    return max(1, min(50, limit))


async def execute_initial_round(run_id: str) -> Dict:
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
    responses = await _execute_parallel_queries(
        active_list, query, api_key, site_url, site_name, concurrency_limit
    )

    # Build result
    result = {
        "responses": responses,
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
    query: str,
    api_key: str,
    site_url: str,
    site_name: str,
    concurrency_limit: int
) -> List[Dict]:
    """
    Execute queries to multiple models in parallel with rate limiting.

    Args:
        models: List of model identifiers
        query: User query
        api_key: OpenRouter API key
        site_url: Site URL for headers
        site_name: Site name for headers
        concurrency_limit: Maximum concurrent requests

    Returns:
        List of response objects with fields: round, model, text, ms
    """
    # Create dynamic semaphore based on query characteristics
    semaphore = asyncio.Semaphore(concurrency_limit)

    tasks = [
        _query_single_model(
            model, query, api_key, site_url, site_name, semaphore
        )
        for model in models
    ]

    results = await asyncio.gather(*tasks, return_exceptions=True)

    # Filter out exceptions and build response objects
    responses = []
    for i, result in enumerate(results):
        if isinstance(result, Exception):
            # Log error but continue with other models
            responses.append({
                "round": "INITIAL",
                "model": models[i],
                "text": f"ERROR: {str(result)}",
                "ms": 0,
                "error": True
            })
        else:
            responses.append(result)

    return responses


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

    # Retry configuration
    max_retries = 3
    timeout = 60.0

    start_time = time.time()

    for attempt in range(max_retries):
        try:
            async with semaphore:  # Dynamic rate limiting
                async with httpx.AsyncClient(timeout=timeout) as client:
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
                        # Rate limited - exponential backoff
                        retry_after = int(response.headers.get("Retry-After", 60))
                        if attempt < max_retries - 1:
                            await asyncio.sleep(retry_after)
                            continue
                        raise InitialRoundError(
                            f"Rate limited for model {model}. Retry after {retry_after}s."
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
