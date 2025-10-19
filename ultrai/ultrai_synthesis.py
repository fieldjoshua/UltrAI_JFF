"""
PR 06 — UltrAI Synthesis (R3)

Final synthesis by a neutral ULTRA model that reviews META drafts and
produces a single synthesis with confidence notes and basic stats.

Reads:
- runs/<run_id>/02_activate.json (for activeList)
- runs/<run_id>/04_meta.json (for META drafts)
- runs/<run_id>/04_meta_status.json (optional, for concurrency reflection)

Creates:
- runs/<run_id>/05_ultrai.json (final synthesis object)
- runs/<run_id>/05_ultrai_status.json (metadata and status)
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


class UltraiSynthesisError(Exception):
    """Raised when UltrAI synthesis fails"""
    pass


# Neutral model preference order (selected from READY/ACTIVE by preference)
PREFERRED_ULTRA = [
    "anthropic/claude-3.7-sonnet",
    "openai/gpt-4o",
    "google/gemini-2.0-flash-thinking-exp:free",
    "meta-llama/llama-3.3-70b-instruct",
]


def calculate_synthesis_timeout(
    peer_context: str,
    num_meta_drafts: int
) -> float:
    """
    Calculate dynamic timeout for synthesis based on input complexity.

    Longer META context and more drafts require more time for both:
    - Processing input (reading all META drafts)
    - Generating output (comprehensive synthesis)

    Args:
        peer_context: Concatenated META drafts for synthesis
        num_meta_drafts: Number of META drafts to synthesize

    Returns:
        Timeout in seconds (60-300)
    """
    base_timeout = 60.0

    # Adjust for META context length
    # More context → more processing + longer synthesis output needed
    context_len = len(peer_context)
    if context_len < 1000:
        # Short context: Quick synthesis (~1-2 paragraphs)
        length_factor = 1.0  # 60s
    elif context_len < 3000:
        # Medium context: Moderate synthesis (~3-4 paragraphs)
        length_factor = 1.5  # 90s
    elif context_len < 5000:
        # Long context: Detailed synthesis (~5-6 paragraphs)
        length_factor = 2.0  # 120s
    else:
        # Very long context: Comprehensive synthesis (full page+)
        length_factor = 3.0  # 180s

    # Adjust for number of META drafts
    # More drafts → more perspectives to integrate
    if num_meta_drafts > 3:
        # 4+ drafts require more careful integration
        length_factor *= 1.2

    timeout = base_timeout * length_factor

    # Enforce minimum 60s, maximum 300s (5 minutes)
    return max(60.0, min(300.0, timeout))


async def execute_ultrai_synthesis(run_id: str, progress_callback=None) -> Dict:
    """
    Execute R3 (UltrAI Synthesis) — a neutral model synthesizes META drafts.

    Args:
        run_id: The run ID to process
        progress_callback: Optional callback function(phase_name, percent_within_r3)
                          called at different R3 sub-phases

    Returns:
        Dict containing:
        - result: Final synthesis object
        - status: Execution status
        - metadata: Run metadata

    Raises:
        UltraiSynthesisError: If execution fails
    """
    load_dotenv()
    runs_dir = Path(f"runs/{run_id}")

    # R3 Phase 1: Initializing NEUTRAL LLM (0%)
    if progress_callback:
        progress_callback("Initializing NEUTRAL LLM", 0)
    await asyncio.sleep(3)  # 3s buffer

    # Load ACTIVE list
    activate_path = runs_dir / "02_activate.json"
    if not activate_path.exists():
        raise UltraiSynthesisError(
            (
                f"Missing 02_activate.json for run_id: {run_id}. "
                "Run active LLMs preparation first."
            )
        )
    with open(activate_path, "r", encoding="utf-8") as f:
        activate_data = json.load(f)
        active_list: List[str] = activate_data.get("activeList", [])

    if len(active_list) < 2:
        raise UltraiSynthesisError(
            f"Insufficient ACTIVE models: {len(active_list)}. Need at least 2."
        )

    # Load META drafts
    meta_path = runs_dir / "04_meta.json"
    if not meta_path.exists():
        raise UltraiSynthesisError(
            (
                f"Missing 04_meta.json for run_id: {run_id}. "
                "Execute meta round first."
            )
        )
    with open(meta_path, "r", encoding="utf-8") as f:
        meta_drafts: List[Dict] = json.load(f)

    if not isinstance(meta_drafts, list) or len(meta_drafts) == 0:
        raise UltraiSynthesisError("META drafts are missing or invalid")

    # R3 Phase 2: Receives META Output (20%)
    if progress_callback:
        progress_callback("receives META Output", 20)
    await asyncio.sleep(3)  # 3s buffer

    # Load original QUERY (CRITICAL: ULTRA needs to know what question to answer)
    inputs_path = runs_dir / "01_inputs.json"
    if not inputs_path.exists():
        raise UltraiSynthesisError(
            f"Missing 01_inputs.json for run_id: {run_id}"
        )
    with open(inputs_path, "r", encoding="utf-8") as f:
        inputs_data = json.load(f)
        original_query = inputs_data.get("QUERY", "")

    if not original_query:
        raise UltraiSynthesisError("QUERY not found in 01_inputs.json")

    # Optional: reflect PR05 concurrency in our status
    meta_status_path = runs_dir / "04_meta_status.json"
    concurrency_from_meta = None
    if meta_status_path.exists():
        try:
            with open(meta_status_path, "r", encoding="utf-8") as f:
                meta_status = json.load(f)
                details = meta_status.get("details", {})
                concurrency_from_meta = details.get("concurrency_limit")
        except Exception:
            concurrency_from_meta = None

    # Get API key
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        raise UltraiSynthesisError(
            "Missing OPENROUTER_API_KEY environment variable"
        )

    site_url = os.getenv("YOUR_SITE_URL", "http://localhost:8000")
    site_name = os.getenv("YOUR_SITE_NAME", "UltrAI Project")

    # Choose neutral model by preference among ACTIVE models
    neutral_model = _select_ultra_model(active_list)
    if not neutral_model:
        raise UltraiSynthesisError(
            "Unable to select neutral ULTRA model from ACTIVE list"
        )

    # Build META context for synthesis (dynamic truncation based on timeout needs)
    # Calculate max chars per draft based on timeout tolerance
    timeout_prelim = calculate_synthesis_timeout(
        peer_context="x" * 10000,  # Worst case estimate
        num_meta_drafts=len(meta_drafts)
    )

    # If timeout is high (complex synthesis), allow more context per draft
    # Otherwise, truncate to keep within reasonable limits
    if timeout_prelim >= 180:  # Long timeout = complex query
        max_chars_per_draft = 2000  # Allow substantial context
    elif timeout_prelim >= 120:  # Medium timeout
        max_chars_per_draft = 1200
    elif timeout_prelim >= 90:  # Moderate timeout
        max_chars_per_draft = 800
    else:  # Short timeout = simple query
        max_chars_per_draft = 500

    peer_summaries: List[str] = []
    for draft in meta_drafts:
        model_id = draft.get("model", "unknown")
        text = draft.get("text", "")
        if draft.get("error"):
            summary = f"- {model_id}: ERROR"
        else:
            # Dynamic truncation based on synthesis complexity
            snippet = text[:max_chars_per_draft] if len(text) > max_chars_per_draft else text
            summary = f"- {model_id}: {snippet}"
        peer_summaries.append(summary)
    peer_context = "\n".join(peer_summaries)

    # R3 Phase 3: Reviews (40%)
    if progress_callback:
        progress_callback("Reviews", 40)
    await asyncio.sleep(3)  # 3s buffer

    # Calculate final timeout based on actual context
    timeout = calculate_synthesis_timeout(
        peer_context=peer_context,
        num_meta_drafts=len(meta_drafts)
    )

    # Prompt with original query and explicit constraints
    instruction = (
        f'The user asked: "{original_query}"\n\n'
        "Multiple LLM models provided META responses to this query. "
        "Your job is to synthesize these META drafts into one coherent answer "
        "that best addresses the user's original query.\n\n"
        "CRITICAL CONSTRAINTS:\n"
        "- DO NOT introduce new information beyond what the META models provided\n"
        "- DO NOT use your own knowledge - rely ONLY on the META drafts and the query\n"
        "- DO NOT include data that evokes low confidence (omit claims where models "
        "strongly disagree or express uncertainty)\n"
        "- Your role is to MERGE and SYNTHESIZE, not to contribute new content\n\n"
        "Review all META drafts below. Merge convergent points and resolve "
        "contradictions. Cite which META claims were retained or omitted. "
        "Generate one coherent synthesis with confidence notes and basic stats."
    )

    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "HTTP-Referer": site_url,
        "X-Title": site_name,
        "Content-Type": "application/json",
    }
    payload = {
        "model": neutral_model,
        "messages": [
            {
                "role": "system",
                "content": "You are the ULTRAI neutral synthesis model (R3).",
            },
            {
                "role": "user",
                "content": instruction + "\n\nMETA DRAFTS:\n" + peer_context,
            },
        ],
    }

    # R3 Phase 4: Writing Synthesis (60%)
    if progress_callback:
        progress_callback("Writing Synthesis", 60)
    await asyncio.sleep(3)  # 3s buffer

    max_retries = 3
    start_time = time.time()

    for attempt in range(max_retries):
        try:
            async with httpx.AsyncClient(timeout=timeout) as client:
                resp = await client.post(
                    url,
                    headers=headers,
                    json=payload,
                )

                if resp.status_code == 401:
                    raise UltraiSynthesisError(
                        f"Invalid API key for model {neutral_model}"
                    )
                elif resp.status_code == 402:
                    raise UltraiSynthesisError(
                        f"Insufficient credits for model {neutral_model}"
                    )
                elif resp.status_code == 429:
                    retry_after = int(resp.headers.get("Retry-After", 60))
                    if attempt < max_retries - 1:
                        await asyncio.sleep(retry_after)
                        continue
                    raise UltraiSynthesisError(
                        (
                            f"Rate limited for model {neutral_model}. "
                            f"Retry after {retry_after}s."
                        )
                    )
                elif resp.status_code >= 500:
                    if attempt < max_retries - 1:
                        await asyncio.sleep(2 ** attempt)
                        continue
                    raise UltraiSynthesisError(
                        (
                            "Server error for model "
                            f"{neutral_model}: {resp.status_code}"
                        )
                    )

                resp.raise_for_status()

                data = resp.json()
                if "choices" in data and len(data["choices"]) > 0:
                    finish_reason = data["choices"][0].get("finish_reason")
                    if finish_reason == "error":
                        error_msg = (
                            data["choices"][0]
                            .get("message", {})
                            .get("content", "Unknown error")
                        )
                        raise UltraiSynthesisError(
                            (
                                "Model "
                                f"{neutral_model} returned error: {error_msg}"
                            )
                        )

                    text = data["choices"][0].get(
                        "message", {}
                    ).get("content", "")
                else:
                    raise UltraiSynthesisError(
                        (
                            "Invalid response structure from model "
                            f"{neutral_model}"
                        )
                    )

                # R3 Phase 5: Synthesis ready (80%)
                if progress_callback:
                    progress_callback("Synthesis ready", 80)
                await asyncio.sleep(3)  # 3s buffer

                elapsed_ms = int((time.time() - start_time) * 1000)

                result = {
                    "round": "ULTRAI",
                    "model": neutral_model,
                    "neutralChosen": neutral_model,
                    "text": text,
                    "ms": elapsed_ms,
                    "stats": {
                        "active_count": len(active_list),
                        "meta_count": len(meta_drafts),
                    },
                }

                # Write artifacts
                synthesis_path = runs_dir / "05_ultrai.json"
                with open(synthesis_path, "w", encoding="utf-8") as f:
                    json.dump(
                        result,
                        f,
                        indent=2,
                        ensure_ascii=False,
                    )

                status = {
                    "status": "COMPLETED",
                    "round": "R3",
                    "details": {
                        "model": neutral_model,
                        "neutral": True,
                        "concurrency_from_meta": concurrency_from_meta,
                        "timeout": timeout,
                        "context_length": len(peer_context),
                        "num_meta_drafts": len(meta_drafts),
                        "max_chars_per_draft": max_chars_per_draft,
                    },
                    "metadata": {
                        "run_id": run_id,
                        "timestamp": datetime.now().isoformat(),
                        "phase": "05_ultrai",
                    },
                }

                status_path = runs_dir / "05_ultrai_status.json"
                with open(status_path, "w", encoding="utf-8") as f:
                    json.dump(status, f, indent=2, ensure_ascii=False)

                return {
                    "result": result,
                    "status": status["status"],
                    "metadata": status["metadata"],
                }

        except httpx.TimeoutException:
            if attempt < max_retries - 1:
                await asyncio.sleep(2 ** attempt)
                continue
            raise UltraiSynthesisError(
                "Timeout during UltrAI synthesis after retries"
            )
        except httpx.HTTPStatusError as e:
            if attempt < max_retries - 1 and e.response.status_code >= 500:
                await asyncio.sleep(2 ** attempt)
                continue
            raise UltraiSynthesisError(
                f"HTTP error during UltrAI synthesis: {e.response.status_code}"
            )
        except UltraiSynthesisError:
            raise
        except Exception as e:
            if attempt < max_retries - 1:
                await asyncio.sleep(2 ** attempt)
                continue
            raise UltraiSynthesisError(
                f"UltrAI synthesis failed: {str(e)}"
            )

    raise UltraiSynthesisError(
        "UltrAI synthesis failed after maximum retry attempts"
    )


def _select_ultra_model(active_list: List[str]) -> str:
    """Select preferred neutral model from ACTIVE list."""
    active_set = set(active_list)
    for preferred in PREFERRED_ULTRA:
        if preferred in active_set:
            return preferred
    # Fallback to first ACTIVE model if none match preference
    return active_list[0] if active_list else ""


def main():
    """CLI entry point for UltrAI synthesis (R3)."""
    import sys

    if len(sys.argv) < 2:
        print("Usage: python -m ultrai.ultrai_synthesis <run_id>")
        sys.exit(1)

    run_id = sys.argv[1]

    async def async_main():
        try:
            result = await execute_ultrai_synthesis(run_id)
            print("UltrAI Synthesis (R3) COMPLETED")
            print(f"Run ID: {run_id}")
            print(f"Model: {result['result']['model']}")
            print("Artifacts:")
            print(f"  - runs/{run_id}/05_ultrai.json")
            print(f"  - runs/{run_id}/05_ultrai_status.json")
            return 0
        except UltraiSynthesisError as e:
            print(f"UltrAI Synthesis FAILED: {e}")
            return 1
        except Exception as e:
            print(f"Unexpected error: {e}")
            import traceback
            traceback.print_exc()
            return 1

    sys.exit(asyncio.run(async_main()))


if __name__ == "__main__":
    main()
