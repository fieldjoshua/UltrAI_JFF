import asyncio
import os
from datetime import datetime

from ultrai.system_readiness import check_system_readiness
import csv
from pathlib import Path
from ultrai.user_input import collect_user_inputs
from ultrai.active_llms import prepare_active_llms
from ultrai.initial_round import execute_initial_round
from ultrai.meta_round import execute_meta_round
from ultrai.ultrai_synthesis import execute_ultrai_synthesis
from ultrai.statistics import generate_statistics


COCKTAILS = ["PREMIUM", "SPEEDY", "BUDGET", "DEPTH"]


async def run_for_cocktail(cocktail: str):
    run_id = f"timing_{cocktail.lower()}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    await check_system_readiness(run_id=run_id)

    collect_user_inputs(
        query="Timing benchmark for cocktails",
        cocktail=cocktail,
        addons=[],
        run_id=run_id,
    )
    prepare_active_llms(run_id)
    await execute_initial_round(run_id)
    await execute_meta_round(run_id)
    await execute_ultrai_synthesis(run_id)

    stats = generate_statistics(run_id)
    initial = stats.get("INITIAL", {})
    meta = stats.get("META", {})
    ultrai = stats.get("ULTRAI", {})

    return {
        "run_id": run_id,
        "cocktail": cocktail,
        "initial_count": initial.get("count", 0),
        "initial_avg_ms": initial.get("avg_ms", 0),
        "meta_count": meta.get("count", 0),
        "meta_avg_ms": meta.get("avg_ms", 0),
        "ultrai_ms": ultrai.get("ms", 0),
    }


async def run_with_retries(cocktail: str, attempts: int = 3):
    for i in range(attempts):
        try:
            return await run_for_cocktail(cocktail)
        except Exception as e:
            if i == attempts - 1:
                raise
            # Exponential backoff before retry
            await asyncio.sleep(2 ** i)


async def main():
    if not os.getenv("OPENROUTER_API_KEY"):
        print("Missing OPENROUTER_API_KEY; cannot run real timing.")
        return 1

    results = []
    for c in COCKTAILS:
        print(f"\n=== Running timing for {c} ===")
        res = await run_with_retries(c)
        results.append(res)
        print(
            f"{c}: INITIAL avg_ms={res['initial_avg_ms']} (n={res['initial_count']}), "
            f"META avg_ms={res['meta_avg_ms']} (n={res['meta_count']}), "
            f"ULTRAI ms={res['ultrai_ms']}"
        )

    # Write CSV
    bench_dir = Path("runs/benchmarks")
    bench_dir.mkdir(parents=True, exist_ok=True)
    csv_path = bench_dir / f"cocktail_timings_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    with open(csv_path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["cocktail", "initial_s", "meta_s", "ultrai_s", "run_id", "initial_count", "meta_count"])
        for r in results:
            init_s = r['initial_avg_ms'] / 1000 if r['initial_avg_ms'] else 0
            meta_s = r['meta_avg_ms'] / 1000 if r['meta_avg_ms'] else 0
            ultrai_s = r['ultrai_ms'] / 1000 if r['ultrai_ms'] else 0
            writer.writerow([
                r['cocktail'], f"{init_s:.2f}", f"{meta_s:.2f}", f"{ultrai_s:.2f}", r['run_id'], r['initial_count'], r['meta_count']
            ])

    print(f"\nCSV written: {csv_path}")
    print("\nSummary:")
    for r in results:
        init_s = r['initial_avg_ms'] / 1000 if r['initial_avg_ms'] else 0
        meta_s = r['meta_avg_ms'] / 1000 if r['meta_avg_ms'] else 0
        ultrai_s = r['ultrai_ms'] / 1000 if r['ultrai_ms'] else 0
        print(
            f"{r['cocktail']}: INITIAL {init_s:.2f}s, "
            f"META {meta_s:.2f}s, ULTRAI {ultrai_s:.2f}s "
            f"(run_id={r['run_id']})"
        )
    return 0


if __name__ == "__main__":
    exit(asyncio.run(main()))


