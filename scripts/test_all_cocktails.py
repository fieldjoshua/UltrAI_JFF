"""
Test all cocktails with real API calls to measure timing performance.

This is a REAL integration test - no mocks.
"""
import asyncio
import sys
import time
from pathlib import Path
from datetime import datetime

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from ultrai.system_readiness import check_system_readiness
from ultrai.user_input import collect_user_inputs
from ultrai.active_llms import prepare_active_llms
from ultrai.initial_round import execute_initial_round
from ultrai.meta_round import execute_meta_round


async def test_cocktail(cocktail_name: str, test_query: str):
    """Test a single cocktail and return timing results"""
    print(f"\n{'='*70}")
    print(f"Testing: {cocktail_name}")
    print(f"{'='*70}")

    start_total = time.time()

    # System readiness
    ready_result = await check_system_readiness()
    run_id = ready_result['run_id']
    print(f"✓ System ready - Run ID: {run_id}")

    # Collect inputs
    collect_user_inputs(
        query=test_query,
        analysis="Synthesis",
        cocktail=cocktail_name,
        add_ons=[],
        run_id=run_id
    )
    print(f"✓ Inputs collected")

    # Prepare active LLMs
    active_result = prepare_active_llms(run_id)
    model_count = len(active_result['activeList'])
    print(f"✓ Active LLMs prepared: {model_count} models")
    print(f"  Models: {', '.join([m.split('/')[-1] for m in active_result['activeList']])}")

    # R1 - Initial Round
    print(f"\n🚀 R1 (INITIAL) - {model_count} models...")
    start_r1 = time.time()

    def r1_progress(model, time_sec, total, completed):
        short_name = model.split('/')[-1] if '/' in model else model
        print(f"  ✓ {short_name}: {time_sec:.2f}s ({completed}/{total})")

    r1_result = await execute_initial_round(run_id, progress_callback=r1_progress)
    r1_time = time.time() - start_r1
    r1_successful = [r for r in r1_result['responses'] if not r.get('error')]
    print(f"✓ R1 completed in {r1_time:.2f}s ({len(r1_successful)}/{model_count} successful)")

    # R2 - Meta Round
    print(f"\n🚀 R2 (META) - {model_count} models...")
    start_r2 = time.time()

    def r2_progress(model, time_sec, total, completed):
        short_name = model.split('/')[-1] if '/' in model else model
        print(f"  ✓ {short_name}: {time_sec:.2f}s ({completed}/{total})")

    r2_result = await execute_meta_round(run_id, progress_callback=r2_progress)
    r2_time = time.time() - start_r2
    r2_successful = [r for r in r2_result['responses'] if not r.get('error')]
    print(f"✓ R2 completed in {r2_time:.2f}s ({len(r2_successful)}/{model_count} successful)")

    total_time = time.time() - start_total

    return {
        'cocktail': cocktail_name,
        'models': model_count,
        'r1_time': r1_time,
        'r2_time': r2_time,
        'total_time': total_time,
        'r1_successful': len(r1_successful),
        'r2_successful': len(r2_successful),
        'run_id': run_id
    }


async def main():
    """Test all cocktails and compare results"""
    # Simple test query to keep costs down
    test_query = "What is 2+2?"

    cocktails = ["SPEEDY", "BUDGET", "PREMIUM", "DEPTH", "LUXE"]
    results = []

    print(f"\n{'#'*70}")
    print(f"# COCKTAIL TIMING COMPARISON TEST")
    print(f"# Query: {test_query}")
    print(f"# Date: {datetime.now().isoformat()}")
    print(f"{'#'*70}")

    for cocktail in cocktails:
        try:
            result = await test_cocktail(cocktail, test_query)
            results.append(result)
        except Exception as e:
            print(f"\n✗ {cocktail} FAILED: {e}")
            import traceback
            traceback.print_exc()

    # Print comparison table
    print(f"\n{'='*70}")
    print(f"RESULTS SUMMARY")
    print(f"{'='*70}")
    print(f"{'Cocktail':<12} {'Models':<8} {'R1 Time':<12} {'R2 Time':<12} {'Total':<12}")
    print(f"{'-'*70}")

    for r in results:
        print(f"{r['cocktail']:<12} {r['models']:<8} {r['r1_time']:>8.2f}s    {r['r2_time']:>8.2f}s    {r['total_time']:>8.2f}s")

    # Find fastest and slowest
    if results:
        fastest = min(results, key=lambda x: x['total_time'])
        slowest = max(results, key=lambda x: x['total_time'])

        print(f"\n🏆 Fastest: {fastest['cocktail']} ({fastest['total_time']:.2f}s)")
        print(f"🐌 Slowest: {slowest['cocktail']} ({slowest['total_time']:.2f}s)")
        print(f"⚡ Speed difference: {slowest['total_time'] - fastest['total_time']:.2f}s")


if __name__ == "__main__":
    asyncio.run(main())
