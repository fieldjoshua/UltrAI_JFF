"""
UltrAI Command Line Interface

Allows users to access all UltrAI features and submit queries through an interactive CLI.
"""

import asyncio
import sys
from pathlib import Path
from datetime import datetime
from ultrai.system_readiness import check_system_readiness, SystemReadinessError
from ultrai.user_input import (
    collect_user_inputs,
    UserInputError,
    VALID_COCKTAILS,
    AVAILABLE_ADDONS
)
from ultrai.active_llms import prepare_active_llms, ActiveLLMError
from ultrai.initial_round import execute_initial_round, InitialRoundError


def print_banner():
    """Display UltrAI banner"""
    print("\n" + "="*70)
    print(" " * 20 + "UltrAI Multi-LLM Synthesis")
    print("="*70 + "\n")


def print_ready_status(ready_result):
    """Display system readiness status"""
    print(f"\n✓ System Ready")
    print(f"  Run ID: {ready_result['run_id']}")
    print(f"  Available LLMs: {ready_result['llm_count']}")
    print(f"  Status: {ready_result['status']}")
    print(f"  Artifact: runs/{ready_result['run_id']}/00_ready.json")


def prompt_query():
    """Prompt user for query"""
    print("\n" + "-"*70)
    print("STEP 1: Enter Your Query")
    print("-"*70)
    print("What question or prompt would you like the LLMs to analyze?")
    print("(This will be sent to multiple LLMs for synthesis)")
    print()

    query = input("Query: ").strip()

    if not query:
        raise UserInputError("Query cannot be empty")

    return query


def prompt_cocktail():
    """Prompt user to select a cocktail"""
    print("\n" + "-"*70)
    print("STEP 2: Select LLM Cocktail")
    print("-"*70)
    print("Choose a pre-selected group of LLMs:\n")

    print("1. PREMIUM  - High-quality models (gpt-4o, claude-3.7-sonnet, grok-4)")
    print("2. SPEEDY   - Fast response models (gpt-4o-mini, claude-3.7-sonnet)")
    print("3. BUDGET   - Cost-effective models (gpt-3.5-turbo, mistral-large)")
    print("4. DEPTH    - Deep reasoning models (claude-3.7-sonnet, deepseek-r1)")
    print()

    while True:
        choice = input("Select cocktail (1-4) [default: 1]: ").strip() or "1"

        if choice in ["1", "2", "3", "4"]:
            cocktails = ["PREMIUM", "SPEEDY", "BUDGET", "DEPTH"]
            selected = cocktails[int(choice) - 1]
            print(f"\n✓ Selected: {selected}")
            return selected
        else:
            print("Invalid choice. Please enter 1, 2, 3, or 4.")


def prompt_addons():
    """Prompt user to select add-ons"""
    print("\n" + "-"*70)
    print("STEP 3: Enable Add-ons (Optional)")
    print("-"*70)
    print("Available add-ons:\n")

    for i, addon in enumerate(AVAILABLE_ADDONS, 1):
        descriptions = {
            "citation_tracking": "Track sources and citations in responses",
            "cost_monitoring": "Monitor token usage and API costs",
            "extended_stats": "Generate additional statistical metrics",
            "visualization": "Create visual representations of results",
            "confidence_intervals": "Include confidence scores in synthesis"
        }
        print(f"{i}. {addon:20} - {descriptions[addon]}")

    print("\nEnter add-on numbers separated by commas (e.g., 1,2,5)")
    print("Press Enter to skip add-ons")
    print()

    selection = input("Add-ons: ").strip()

    if not selection:
        print("\n✓ No add-ons selected")
        return []

    selected_addons = []
    try:
        indices = [int(x.strip()) for x in selection.split(",")]
        for idx in indices:
            if 1 <= idx <= len(AVAILABLE_ADDONS):
                selected_addons.append(AVAILABLE_ADDONS[idx - 1])
            else:
                print(f"Warning: Invalid add-on number {idx}, skipping")

        if selected_addons:
            print(f"\n✓ Selected add-ons: {', '.join(selected_addons)}")
        else:
            print("\n✓ No valid add-ons selected")

        return selected_addons

    except ValueError:
        print("Invalid format. Skipping add-ons.")
        return []


def print_submission_summary(inputs_result):
    """Display submission summary"""
    print("\n" + "="*70)
    print("SUBMISSION SUMMARY")
    print("="*70)
    print(f"\nQuery: {inputs_result['QUERY']}")
    print(f"Analysis Type: {inputs_result['ANALYSIS']}")
    print(f"Cocktail: {inputs_result['COCKTAIL']}")
    print(f"Add-ons: {', '.join(inputs_result['ADDONS']) if inputs_result['ADDONS'] else 'None'}")
    print(f"\nRun ID: {inputs_result['metadata']['run_id']}")
    print(f"Artifact: runs/{inputs_result['metadata']['run_id']}/01_inputs.json")
    print("\n" + "="*70)


async def main():
    """Main CLI flow"""
    try:
        print_banner()

        # Step 0: System Readiness Check
        print("Checking system readiness...")
        print("Connecting to OpenRouter API...")

        try:
            ready_result = await check_system_readiness()
            print_ready_status(ready_result)
            run_id = ready_result['run_id']

        except SystemReadinessError as e:
            print(f"\n✗ System Readiness Error: {e}")
            print("\nPlease ensure:")
            print("1. OPENROUTER_API_KEY is set in your .env file")
            print("2. You have an active OpenRouter account with credits")
            print("3. Your network connection is working")
            sys.exit(1)

        # Step 1: Get Query
        try:
            query = prompt_query()
        except UserInputError as e:
            print(f"\n✗ Error: {e}")
            sys.exit(1)

        # Step 2: Select Cocktail
        cocktail = prompt_cocktail()

        # Step 3: Select Add-ons
        addons = prompt_addons()

        # Step 4: Collect Inputs
        print("\n" + "-"*70)
        print("Collecting inputs...")

        try:
            inputs_result = collect_user_inputs(
                query=query,
                analysis="Synthesis",
                cocktail=cocktail,
                addons=addons,
                run_id=run_id
            )

            print_submission_summary(inputs_result)

            # Step 5: Prepare Active LLMs (PR 03)
            print("\n" + "-"*70)
            print("Determining active LLMs (READY ∩ COCKTAIL)...")

            active_result = prepare_active_llms(run_id)

            print(f"\n✓ Active LLMs prepared")
            print(f"  Cocktail: {active_result['cocktail']}")
            print(f"  Active models: {len(active_result['activeList'])}")
            print(f"  Quorum: {active_result['quorum']}")
            print(f"  Artifact: runs/{run_id}/02_activate.json")
            print(f"\n  Models:")
            for model in active_result['activeList']:
                print(f"    - {model}")

            # Step 6: Execute Initial Round (R1) (PR 04)
            print("\n" + "-"*70)
            print("Executing Initial Round (R1)...")
            print(f"Sending query to {len(active_result['activeList'])} models in parallel...")

            r1_result = await execute_initial_round(run_id)

            print(f"\n✓ Initial Round (R1) completed")
            print(f"  Responses: {len(r1_result['responses'])}")
            successful = [r for r in r1_result['responses'] if not r.get('error')]
            errors = [r for r in r1_result['responses'] if r.get('error')]
            print(f"  Successful: {len(successful)}")
            if errors:
                print(f"  Errors: {len(errors)}")
            print(f"  Artifacts:")
            print(f"    - runs/{run_id}/03_initial.json")
            print(f"    - runs/{run_id}/03_initial_status.json")

            # Show timing summary
            if successful:
                timings = [r['ms'] for r in successful]
                avg_ms = sum(timings) // len(timings)
                print(f"\n  Timing:")
                print(f"    Average: {avg_ms}ms")
                print(f"    Fastest: {min(timings)}ms")
                print(f"    Slowest: {max(timings)}ms")

            print("\n✓ Your query has been processed through R1!")
            print("\nNext steps:")
            print("1. PR 05 will execute Meta Round (R2)")
            print("2. PR 06 will synthesize UltrAI response (R3)")
            print("\n(Implementation of PR 05-06 coming in future releases)")

        except UserInputError as e:
            print(f"\n✗ Input Error: {e}")
            sys.exit(1)
        except ActiveLLMError as e:
            print(f"\n✗ Active LLMs Error: {e}")
            sys.exit(1)
        except InitialRoundError as e:
            print(f"\n✗ Initial Round Error: {e}")
            sys.exit(1)

    except KeyboardInterrupt:
        print("\n\nOperation cancelled by user.")
        sys.exit(0)

    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


def run_cli():
    """Entry point for CLI"""
    asyncio.run(main())


if __name__ == "__main__":
    run_cli()
