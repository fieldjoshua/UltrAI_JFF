"""
Quick test of new LUXE cocktail to verify speed improvement.
"""
import asyncio
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from ultrai.system_readiness import check_system_readiness
from ultrai.user_input import collect_user_inputs
from ultrai.active_llms import prepare_active_llms
from ultrai.initial_round import execute_initial_round


async def test_luxe():
    """Test LUXE speed with simple query"""
    print("\n" + "="*70)
    print("TESTING NEW LUXE CONFIGURATION")
    print("="*70)

    start_total = time.time()

    # System readiness
    ready_result = await check_system_readiness()
    run_id = ready_result['run_id']
    print(f"✓ System ready - Run ID: {run_id}")

    # Collect inputs
    collect_user_inputs(
        query="What is 2+2?",
        analysis="Synthesis",
        cocktail="LUXE",
        addons=[],
        run_id=run_id
    )

    # Prepare active LLMs
    active_result = prepare_active_llms(run_id)
    model_count = len(active_result['activeList'])
    print(f"✓ Active LLMs prepared: {model_count} models")
    print(f"\nModels:")
    for model in active_result['activeList']:
        short_name = model.split('/')[-1] if '/' in model else model
        print(f"  - {model}")

    # R1 - Initial Round
    print(f"\n🚀 R1 (INITIAL) - Executing with {model_count} models...")
    start_r1 = time.time()

    def progress(model, time_sec, total, completed):
        short_name = model.split('/')[-1] if '/' in model else model
        print(f"  ✓ {short_name}: {time_sec:.2f}s ({completed}/{total})")

    r1_result = await execute_initial_round(run_id, progress_callback=progress)
    r1_time = time.time() - start_r1

    successful = [r for r in r1_result['responses'] if not r.get('error')]
    errors = [r for r in r1_result['responses'] if r.get('error')]

    print(f"\n✓ R1 completed in {r1_time:.2f}s")
    print(f"  Successful: {len(successful)}/{model_count}")
    if errors:
        print(f"  Errors: {len(errors)}")
        for err in errors:
            print(f"    - {err['model']}: {err['text']}")

    total_time = time.time() - start_total

    print(f"\n" + "="*70)
    print(f"TOTAL TIME: {total_time:.2f}s")
    print(f"="*70)

    # Compare to previous benchmarks
    print(f"\nCOMPARISON:")
    print(f"  Old LUXE:  >60s (never completed)")
    print(f"  PREMIUM:   27.40s")
    print(f"  SPEEDY:    15.77s")
    print(f"  BUDGET:     8.92s")
    print(f"  New LUXE:  {total_time:.2f}s ← CURRENT TEST")

    if total_time < 30:
        print(f"\n✨ SUCCESS! New LUXE is {30/total_time:.1f}x faster than target!")
    else:
        print(f"\n⚠️  Still slow - needs more optimization")


if __name__ == "__main__":
    asyncio.run(test_luxe())
