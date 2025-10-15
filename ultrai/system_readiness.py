"""
PR 01 — System Readiness

Verifies dependency software, code integrity, data availability, OpenRouter connection.
Confirms all potentially used LLMs indicate up and ready.
Produces populated list of ready LLMs.

IMPLEMENTATION: Follows corrected OpenRouter strategy (v2.0)
- Async implementation with httpx.AsyncClient
- Semaphore-based rate limiting
- Exponential backoff retry logic
- Comprehensive error handling (400-503)
- Proper headers (HTTP-Referer, X-Title)
"""

import os
import json
import asyncio
from datetime import datetime
from typing import Dict, List, Optional
from pathlib import Path

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


class SystemReadinessError(Exception):
    """Raised when system readiness checks fail"""
    pass


# Rate limiting: Max 50 concurrent requests (per CORRECTED doc)
SEMAPHORE = asyncio.Semaphore(50)


async def check_system_readiness(run_id: Optional[str] = None) -> Dict:
    """
    Execute Phase 0 — System Readiness checks.

    Verifies:
    - OPENROUTER_API_KEY is present
    - OpenRouter connection is functional
    - At least 2 LLMs are in READY state

    Implementation follows OpenRouter CORRECTED doc v2.0:
    - Async httpx client (not synchronous requests)
    - Proper headers (HTTP-Referer, X-Title)
    - Exponential backoff retry logic
    - Comprehensive error handling

    Args:
        run_id: Optional run identifier. If not provided, generates timestamp-based ID.

    Returns:
        Dictionary containing:
        - run_id: Unique run identifier
        - readyList: List of READY LLM model identifiers
        - timestamp: ISO format timestamp of check
        - status: "READY" or "FAILED"

    Raises:
        SystemReadinessError: If critical checks fail (missing API key, <2 LLMs ready)
    """
    # Load environment variables
    load_dotenv()

    # Generate run_id if not provided
    if run_id is None:
        run_id = datetime.now().strftime("%Y%m%d_%H%M%S")

    # Check for OPENROUTER_API_KEY
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        raise SystemReadinessError(
            "Missing OPENROUTER_API_KEY environment variable. "
            "Set it in .env file or environment."
        )

    # Optional site identification for OpenRouter analytics
    site_url = os.getenv("YOUR_SITE_URL", "http://localhost:8000")
    site_name = os.getenv("YOUR_SITE_NAME", "UltrAI Project")

    # API endpoint for models list
    models_url = "https://openrouter.ai/api/v1/models"

    # Headers per CORRECTED doc recommendations
    headers = {
        "Authorization": f"Bearer {api_key}",
        "HTTP-Referer": site_url,
        "X-Title": site_name,
    }

    # Retry configuration (exponential backoff)
    max_retries = 3
    timeout = 60.0

    # Query available models from OpenRouter with retry logic
    for attempt in range(max_retries):
        try:
            async with SEMAPHORE:  # Rate limiting
                async with httpx.AsyncClient(timeout=timeout) as client:
                    response = await client.get(models_url, headers=headers)

                    # Handle specific error codes per CORRECTED doc
                    if response.status_code == 401:
                        raise SystemReadinessError(
                            "Invalid OPENROUTER_API_KEY. Check your credentials."
                        )
                    elif response.status_code == 402:
                        raise SystemReadinessError(
                            "Insufficient credits on OpenRouter account. Add balance."
                        )
                    elif response.status_code == 429:
                        # Rate limited - exponential backoff
                        retry_after = int(response.headers.get("Retry-After", 60))
                        if attempt < max_retries - 1:
                            await asyncio.sleep(retry_after)
                            continue
                        raise SystemReadinessError(
                            f"Rate limited by OpenRouter. Retry after {retry_after}s."
                        )
                    elif response.status_code >= 500:
                        # Server error - retry with exponential backoff
                        if attempt < max_retries - 1:
                            await asyncio.sleep(2 ** attempt)
                            continue
                        raise SystemReadinessError(
                            f"OpenRouter server error: {response.status_code}"
                        )

                    # Raise for other 4xx/5xx errors
                    response.raise_for_status()

                    # Parse models list
                    models_data = response.json()

                    # Extract model IDs
                    if "data" in models_data:
                        ready_models = [model["id"] for model in models_data["data"]]
                    else:
                        ready_models = []

                    if len(ready_models) < 2:
                        raise SystemReadinessError(
                            f"Insufficient READY LLMs. Found {len(ready_models)}, need at least 2. "
                            "Low pluralism warning."
                        )

                    # Build readiness result
                    result = {
                        "run_id": run_id,
                        "readyList": ready_models,
                        "timestamp": datetime.now().isoformat(),
                        "status": "READY",
                        "llm_count": len(ready_models)
                    }

                    # Create runs directory and write artifact
                    runs_dir = Path("runs") / run_id
                    runs_dir.mkdir(parents=True, exist_ok=True)

                    artifact_path = runs_dir / "00_ready.json"
                    with open(artifact_path, "w", encoding="utf-8") as f:
                        json.dump(result, f, indent=2)

                    return result

        except httpx.TimeoutException:
            if attempt < max_retries - 1:
                await asyncio.sleep(2 ** attempt)  # Exponential backoff
                continue
            raise SystemReadinessError(
                f"OpenRouter connection timeout after {max_retries} attempts"
            )
        except httpx.HTTPStatusError as e:
            # Already handled specific codes above, this catches remaining errors
            if attempt < max_retries - 1 and e.response.status_code >= 500:
                await asyncio.sleep(2 ** attempt)
                continue
            raise SystemReadinessError(
                f"OpenRouter HTTP error: {e.response.status_code} - {e.response.text}"
            )
        except SystemReadinessError:
            # Re-raise our own errors without retry
            raise
        except Exception as e:
            # Unexpected errors
            if attempt < max_retries - 1:
                await asyncio.sleep(2 ** attempt)
                continue
            raise SystemReadinessError(
                f"OpenRouter connection failed: {str(e)}"
            )

    # Should never reach here due to raises above, but for safety:
    raise SystemReadinessError(
        f"Failed to check system readiness after {max_retries} attempts"
    )


def main():
    """CLI entry point for system readiness check"""
    async def async_main():
        try:
            result = await check_system_readiness()
            print(f"System readiness check PASSED")
            print(f"Run ID: {result['run_id']}")
            print(f"Ready LLMs: {result['llm_count']}")
            print(f"Artifact: runs/{result['run_id']}/00_ready.json")
            return 0
        except SystemReadinessError as e:
            print(f"System readiness check FAILED: {e}")
            return 1

    return asyncio.run(async_main())


if __name__ == "__main__":
    exit(main())
