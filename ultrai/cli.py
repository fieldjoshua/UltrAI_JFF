"""
UltrAI Command Line Interface

Allows users to access all UltrAI features and submit queries through an interactive CLI.
"""

import asyncio
import sys
from pathlib import Path

# ANSI Color Codes - Vibrant Cyberpunk Terminal Theme
NEON_BLURPLE = '\033[38;5;99m'    # Neon Blue-Purple
NEON_GREEN = '\033[38;5;46m'      # Bright Neon Green
NEON_CYAN = '\033[38;5;51m'       # Neon Cyan
NEON_PINK = '\033[38;5;201m'      # Neon Pink/Magenta
WHITE = '\033[97m'                # Bright white
GRAY = '\033[38;5;245m'           # Gray for subtle elements
BLUE = '\033[38;5;75m'            # Bright blue
YELLOW = '\033[38;5;221m'         # Yellow highlights
BOLD = '\033[1m'
DIM = '\033[2m'
BLINK = '\033[5m'                 # Blinking text
UNDERLINE = '\033[4m'             # Underlined text
RESET = '\033[0m'

# Unicode Box Characters & Symbols
BOX_H = '═'
BOX_V = '║'
BOX_TL = '╔'
BOX_TR = '╗'
BOX_BL = '╚'
BOX_BR = '╝'
ARROW = '▶'
DOT = '●'
STAR = '✦'
LIGHTNING = '⚡'
ROCKET = '🚀'
SPARKLE = '✨'

# Divider Styles
DIV_DOUBLE = '═' * 70
DIV_SINGLE = '─' * 70
DIV_THICK = '━' * 70
DIV_DOTS = '·' * 70
DIV_WAVE = '~' * 70
from ultrai.system_readiness import check_system_readiness, SystemReadinessError
from ultrai.user_input import (
    collect_user_inputs,
    UserInputError,
    AVAILABLE_ADDONS
)
from ultrai.active_llms import prepare_active_llms, ActiveLLMError
from ultrai.initial_round import execute_initial_round, InitialRoundError
from ultrai.meta_round import execute_meta_round, MetaRoundError
from ultrai.ultrai_synthesis import execute_ultrai_synthesis, UltraiSynthesisError
from ultrai.statistics import generate_statistics
from ultrai.final_delivery import deliver_results


class AnimatedBanner:
    """Animated ASCII art banner that cycles between frames"""
    def __init__(self):
        self.frames = []
        self.load_frames()
        self.idx = 0
        self.running = False
        self.thread = None

    def load_frames(self):
        """Load ASCII art frames for animation"""
        frame_files = [
            "ascii-art (19).txt",
            "ascii-art (20).txt"
        ]

        for art_file in frame_files:
            art_path = Path(__file__).parent.parent / "Images1" / art_file
            try:
                with open(art_path, 'r', encoding='utf-8') as f:
                    self.frames.append(f.read())
            except (FileNotFoundError, PermissionError, UnicodeDecodeError):
                continue

        # Fallback to static banner if animation frames not found
        if not self.frames:
            fallback_files = ["ascii-art (17).txt", "ascii-art (14).txt"]
            for art_file in fallback_files:
                art_path = Path(__file__).parent.parent / "Images1" / art_file
                try:
                    with open(art_path, 'r', encoding='utf-8') as f:
                        self.frames.append(f.read())
                        break
                except (FileNotFoundError, PermissionError, UnicodeDecodeError):
                    continue

    def _animate(self):
        """Animate the banner by cycling through frames"""
        import time
        frame_count = len(self.frames)
        if frame_count == 0:
            return

        # Calculate frame height for clearing
        frame_height = self.frames[0].count('\n') + 1

        while self.running:
            # Clear previous frame
            sys.stdout.write(f'\033[{frame_height}A')  # Move cursor up
            sys.stdout.write('\033[J')  # Clear from cursor to end of screen

            # Print current frame with color
            sys.stdout.write(f"{NEON_BLURPLE}{BOLD}{self.frames[self.idx]}{RESET}")
            sys.stdout.flush()

            # Move to next frame
            self.idx = (self.idx + 1) % frame_count
            time.sleep(0.3)  # 300ms per frame

    def start(self):
        """Start the banner animation"""
        import threading
        if len(self.frames) < 2:
            # Static display if only one frame
            if self.frames:
                print(f"{NEON_BLURPLE}{BOLD}{self.frames[0]}{RESET}")
            return

        # Show first frame
        print(f"{NEON_BLURPLE}{BOLD}{self.frames[0]}{RESET}")

        self.running = True
        self.thread = threading.Thread(target=self._animate)
        self.thread.start()

    def stop(self):
        """Stop the animation and clear for final banner"""
        if not self.running:
            return

        self.running = False
        if self.thread:
            self.thread.join()


def print_banner():
    """Display UltrAI banner with animated ASCII art"""
    # Create animated banner
    banner = AnimatedBanner()
    banner.start()

    # Let it animate for a few cycles
    import time
    time.sleep(2.0)  # Animate for 2 seconds

    banner.stop()

    # Clear and show final static banner
    if banner.frames:
        frame_height = banner.frames[0].count('\n') + 1
        sys.stdout.write(f'\033[{frame_height}A')
        sys.stdout.write('\033[J')
        print(f"{NEON_BLURPLE}{BOLD}{banner.frames[0]}{RESET}")

    # Large stylized title with variations
    print(f"\n{NEON_GREEN}{BOLD}{DIV_THICK}{RESET}")
    print(f"{NEON_GREEN}{BOX_V}{RESET}{NEON_CYAN}{BOLD}        U L T R A I   {RESET}{NEON_PINK}{LIGHTNING}{RESET}  {WHITE}{BOLD}M U L T I - L L M   S Y N T H E S I S{RESET}        {NEON_GREEN}{BOX_V}{RESET}")
    print(f"{NEON_GREEN}{BOLD}{DIV_THICK}{RESET}\n")


def print_ready_status(ready_result):
    """Display system readiness status"""
    print(f"\n{NEON_GREEN}{BOLD}{SPARKLE} System Ready {SPARKLE}{RESET}")
    print(f"{NEON_BLURPLE}  {ARROW} {WHITE}Run ID:{RESET} {NEON_CYAN}{BOLD}{ready_result['run_id']}{RESET}")
    print(f"{NEON_BLURPLE}  {ARROW} {WHITE}Available LLMs:{RESET} {NEON_GREEN}{BOLD}{ready_result['llm_count']}{RESET}")
    print(f"{NEON_BLURPLE}  {ARROW} {WHITE}Status:{RESET} {NEON_GREEN}{BOLD}{ready_result['status']}{RESET}")
    print(f"{NEON_BLURPLE}  {ARROW} {WHITE}Artifact:{RESET} {GRAY}{DIM}runs/{ready_result['run_id']}/00_ready.json{RESET}")


def prompt_query():
    """Prompt user for query"""
    print(f"\n{NEON_GREEN}{DIV_DOUBLE}{RESET}")
    print(f"{NEON_PINK}{BOLD}{ROCKET} STEP 1: {RESET}{NEON_CYAN}{BOLD}{UNDERLINE}Enter Your Query{RESET}")
    print(f"{NEON_BLURPLE}{DIV_SINGLE}{RESET}")
    print(f"{WHITE}What question or prompt would you like the LLMs to analyze?{RESET}")
    print(f"{GRAY}(This will be sent to multiple LLMs for synthesis){RESET}")
    print()

    query = input(f"{NEON_GREEN}{BLINK}▶{RESET} {NEON_CYAN}Query:{RESET} ").strip()

    if not query:
        raise UserInputError("Query cannot be empty")

    return query


def prompt_cocktail():
    """Prompt user to select a cocktail"""
    print(f"\n{NEON_GREEN}{DIV_DOUBLE}{RESET}")
    print(f"{NEON_PINK}{BOLD}{LIGHTNING} STEP 2: {RESET}{NEON_CYAN}{BOLD}{UNDERLINE}Select LLM Cocktail{RESET}")
    print(f"{NEON_BLURPLE}{DIV_WAVE}{RESET}")
    print(f"{WHITE}{BOLD}Choose a pre-selected group of LLMs:\n{RESET}")

    print(f"{NEON_BLURPLE}{BOLD}1.{RESET} {NEON_GREEN}PREMIUM{RESET}  {GRAY}- High-quality models (claude-3.7-sonnet, chatgpt-4o-latest, llama-3.3-70b){RESET}")
    print(f"{NEON_BLURPLE}{BOLD}2.{RESET} {YELLOW}SPEEDY{RESET}   {GRAY}- Fast response models (gpt-4o-mini, claude-3.5-haiku, gemini-2.0){RESET}")
    print(f"{NEON_BLURPLE}{BOLD}3.{RESET} {WHITE}BUDGET{RESET}   {GRAY}- Cost-effective models (gpt-3.5-turbo, gemini-2.0, qwen-2.5){RESET}")
    print(f"{NEON_BLURPLE}{BOLD}4.{RESET} {NEON_CYAN}DEPTH{RESET}    {GRAY}- Deep reasoning models (claude-3.7-sonnet, gpt-4o, gemini-thinking){RESET}")
    print()

    while True:
        choice = input(f"{NEON_GREEN}{BLINK}▶{RESET} {NEON_CYAN}Select cocktail (1-4) [default: 1]:{RESET} ").strip() or "1"

        if choice in ["1", "2", "3", "4"]:
            cocktails = ["PREMIUM", "SPEEDY", "BUDGET", "DEPTH"]
            selected = cocktails[int(choice) - 1]
            print(f"\n{NEON_GREEN}{BOLD}{STAR} Selected: {NEON_CYAN}{BOLD}{selected}{RESET}")
            return selected
        else:
            print(f"{NEON_PINK}{BOLD}✗ Invalid choice. Please enter 1-4.{RESET}")


def prompt_addons():
    """Prompt user to select add-ons"""
    print(f"\n{NEON_GREEN}{DIV_DOUBLE}{RESET}")
    print(f"{NEON_PINK}{BOLD}{SPARKLE} STEP 3: {RESET}{NEON_CYAN}{BOLD}{UNDERLINE}Enable Add-ons (Optional){RESET}")
    print(f"{NEON_BLURPLE}{DIV_DOTS}{RESET}")
    print(f"{WHITE}{BOLD}Available add-ons:\n{RESET}")

    for i, addon in enumerate(AVAILABLE_ADDONS, 1):
        descriptions = {
            "citation_tracking": "Track sources and citations in responses",
            "cost_monitoring": "Monitor token usage and API costs",
            "extended_stats": "Generate additional statistical metrics",
            "visualization": "Create visual representations of results",
            "confidence_intervals": "Include confidence scores in synthesis"
        }
        print(f"{NEON_BLURPLE}{BOLD}{i}.{RESET} {NEON_CYAN}{addon:20}{RESET} {GRAY}- {descriptions[addon]}{RESET}")

    print(f"\n{GRAY}Enter add-on numbers separated by commas (e.g., 1,2,5){RESET}")
    print(f"{GRAY}Press Enter to skip add-ons{RESET}")
    print()

    selection = input(f"{NEON_GREEN}{BLINK}▶{RESET} {NEON_CYAN}Add-ons:{RESET} ").strip()

    if not selection:
        print(f"\n{NEON_GREEN}{BOLD}{STAR} No add-ons selected{RESET}")
        return []

    selected_addons = []
    try:
        indices = [int(x.strip()) for x in selection.split(",")]
        for idx in indices:
            if 1 <= idx <= len(AVAILABLE_ADDONS):
                selected_addons.append(AVAILABLE_ADDONS[idx - 1])
            else:
                print(f"{NEON_PINK}{BOLD}⚠ Warning: Invalid add-on number {idx}, skipping{RESET}")

        if selected_addons:
            print(f"\n{NEON_GREEN}{BOLD}{STAR} Selected add-ons: {NEON_CYAN}{BOLD}{', '.join(selected_addons)}{RESET}")
        else:
            print(f"\n{NEON_GREEN}{BOLD}{STAR} No valid add-ons selected{RESET}")

        return selected_addons

    except ValueError:
        print(f"{NEON_PINK}{BOLD}✗ Invalid format. Skipping add-ons.{RESET}")
        return []


def print_submission_summary(inputs_result):
    """Display submission summary"""
    print(f"\n{NEON_GREEN}{BOLD}{BOX_TL}{BOX_H * 68}{BOX_TR}{RESET}")
    print(f"{NEON_GREEN}{BOX_V}{RESET}{NEON_PINK}{BOLD}  {ROCKET} SUBMISSION SUMMARY{' ' * 45}{NEON_GREEN}{BOX_V}{RESET}")
    print(f"{NEON_GREEN}{BOLD}{BOX_BL}{BOX_H * 68}{BOX_BR}{RESET}")
    print(f"\n{NEON_BLURPLE}{BOLD}Query:{RESET} {WHITE}{inputs_result['QUERY']}{RESET}")
    print(f"{NEON_BLURPLE}{BOLD}Analysis Type:{RESET} {NEON_CYAN}{inputs_result['ANALYSIS']}{RESET}")
    print(f"{NEON_BLURPLE}{BOLD}Cocktail:{RESET} {NEON_GREEN}{BOLD}{inputs_result['COCKTAIL']}{RESET}")
    # Add-ons line removed - feature disabled (placeholder implementations only)
    print(f"\n{NEON_BLURPLE}{BOLD}Run ID:{RESET} {YELLOW}{inputs_result['metadata']['run_id']}{RESET}")
    print(f"{NEON_BLURPLE}{BOLD}Artifact:{RESET} {GRAY}{DIM}runs/{inputs_result['metadata']['run_id']}/01_inputs.json{RESET}")
    print(f"\n{NEON_GREEN}{BOLD}{DIV_THICK}{RESET}")


class ProgressSpinner:
    """Animated spinner for showing progress"""
    def __init__(self, message):
        self.message = message
        self.spinner_chars = ['⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏']
        self.idx = 0
        self.running = False
        self.thread = None

    def _spin(self):
        import time
        while self.running:
            sys.stdout.write(f'\r{BLUE}{self.spinner_chars[self.idx]}{RESET} {WHITE}{self.message}...{RESET}')
            sys.stdout.flush()
            self.idx = (self.idx + 1) % len(self.spinner_chars)
            time.sleep(0.1)

    def start(self):
        import threading
        self.running = True
        self.thread = threading.Thread(target=self._spin)
        self.thread.start()

    def stop(self, final_message=None):
        self.running = False
        if self.thread:
            self.thread.join()
        sys.stdout.write('\r' + ' ' * (len(self.message) + 10) + '\r')  # Clear line
        if final_message:
            print(final_message)
        sys.stdout.flush()


async def main():
    """Main CLI flow"""
    try:
        print_banner()

        # Step 0: System Readiness Check
        spinner = ProgressSpinner("Checking system readiness")
        spinner.start()

        try:
            ready_result = await check_system_readiness()
            spinner.stop()
            print_ready_status(ready_result)
            run_id = ready_result['run_id']

        except SystemReadinessError as e:
            spinner.stop()
            print(f"\n{NEON_PINK}{BOLD}✗ System Readiness Error:{RESET} {WHITE}{e}{RESET}")
            print(f"\n{NEON_GREEN}{BOLD}{DIV_SINGLE}{RESET}")
            print(f"{NEON_CYAN}{BOLD}Please ensure:{RESET}")
            print(f"{NEON_BLURPLE}  {ARROW}{RESET} {WHITE}OPENROUTER_API_KEY is set in your .env file{RESET}")
            print(f"{NEON_BLURPLE}  {ARROW}{RESET} {WHITE}You have an active OpenRouter account with credits{RESET}")
            print(f"{NEON_BLURPLE}  {ARROW}{RESET} {WHITE}Your network connection is working{RESET}")
            print(f"{NEON_GREEN}{BOLD}{DIV_SINGLE}{RESET}\n")
            sys.exit(1)

        # Step 1: Get Query
        try:
            query = prompt_query()
        except UserInputError as e:
            print(f"\n{NEON_PINK}{BOLD}✗ Error: {e}{RESET}")
            sys.exit(1)

        # Step 2: Select Cocktail
        cocktail = prompt_cocktail()

        # DISABLED: Add-ons are placeholder implementations only
        # Add-ons create truncated/incomplete outputs and should not be offered to users
        addons = []  # Force empty - add-ons disabled until real implementations exist

        # Step 3: Collect Inputs
        print(f"\n{NEON_GREEN}{BOLD}{DIV_WAVE}{RESET}")
        print(f"{NEON_BLURPLE}{BOLD}{LIGHTNING} {RESET}{NEON_CYAN}{BOLD}Collecting inputs...{RESET}")

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
            print(f"\n{NEON_GREEN}{BOLD}{DIV_DOTS}{RESET}")
            print(f"{NEON_PINK}{BOLD}{SPARKLE} {RESET}{NEON_CYAN}{BOLD}Determining active LLMs {WHITE}(READY ∩ COCKTAIL){RESET}{NEON_CYAN}{BOLD}...{RESET}")

            active_result = prepare_active_llms(run_id)

            print(f"\n{NEON_GREEN}{BOLD}{UNDERLINE}{STAR} Active LLMs Prepared{RESET}")
            print(f"{NEON_BLURPLE}{BOLD}  {ARROW}{RESET} {WHITE}Cocktail:{RESET} {NEON_GREEN}{BOLD}{active_result['cocktail']}{RESET}")
            print(f"{NEON_BLURPLE}{BOLD}  {ARROW}{RESET} {WHITE}Active models:{RESET} {NEON_PINK}{BOLD}{len(active_result['activeList'])}{RESET}")
            print(f"{NEON_BLURPLE}{BOLD}  {ARROW}{RESET} {WHITE}Quorum:{RESET} {NEON_PINK}{BOLD}{active_result['quorum']}{RESET}")
            print(f"{NEON_BLURPLE}{BOLD}  {ARROW}{RESET} {GRAY}Artifact: {DIM}runs/{run_id}/02_activate.json{RESET}")
            print(f"\n{NEON_CYAN}{BOLD}  {LIGHTNING} Models:{RESET}")
            for model in active_result['activeList']:
                print(f"{NEON_BLURPLE}    {DOT} {WHITE}{model}{RESET}")

            # Step 6: Execute Initial Round (R1) (PR 04)
            print(f"\n{NEON_GREEN}{BOLD}{DIV_THICK}{RESET}")
            print(f"{NEON_PINK}{BOLD}{ROCKET} ROUND 1: {RESET}{NEON_CYAN}{BOLD}{UNDERLINE}INITIAL{RESET}")
            print(f"{NEON_BLURPLE}{DIV_SINGLE}{RESET}")
            print(f"{WHITE}Sending query to {NEON_PINK}{BOLD}{len(active_result['activeList'])}{RESET}{WHITE} models in parallel...{RESET}\n")

            # Define progress callback for R1
            def r1_progress(model, time_sec, total, completed):
                # Extract short model name (last part after /)
                short_name = model.split('/')[-1] if '/' in model else model
                print(f"{NEON_GREEN}{BOLD}  ✓{RESET} {WHITE}{short_name}{RESET} {GRAY}completed in{RESET} {NEON_CYAN}{BOLD}{time_sec:.2f}s{RESET} {GRAY}({completed}/{total}){RESET}")

            r1_result = await execute_initial_round(run_id, progress_callback=r1_progress)

            print(f"\n{NEON_GREEN}{BOLD}{SPARKLE} Initial Round (R1) {RESET}{NEON_GREEN}{BOLD}Completed{RESET}")
            print(f"{NEON_BLURPLE}{BOLD}  {ARROW}{RESET} {WHITE}Responses:{RESET} {NEON_PINK}{BOLD}{len(r1_result['responses'])}{RESET}")
            successful = [r for r in r1_result['responses'] if not r.get('error')]
            errors = [r for r in r1_result['responses'] if r.get('error')]
            print(f"{NEON_BLURPLE}{BOLD}  {ARROW}{RESET} {WHITE}Successful:{RESET} {NEON_GREEN}{BOLD}{len(successful)}{RESET}")
            if errors:
                print(f"{NEON_BLURPLE}{BOLD}  {ARROW}{RESET} {WHITE}Errors:{RESET} {NEON_PINK}{BOLD}{len(errors)}{RESET}")
            print(f"{NEON_BLURPLE}{BOLD}  {ARROW}{RESET} {GRAY}Artifacts:{RESET}")
            print(f"{GRAY}{DIM}    - runs/{run_id}/03_initial.json{RESET}")
            print(f"{GRAY}{DIM}    - runs/{run_id}/03_initial_status.json{RESET}")

            # Show timing summary (convert ms to seconds)
            if successful:
                timings = [r['ms'] / 1000.0 for r in successful]  # Convert to seconds
                avg_sec = sum(timings) / len(timings)
                print(f"\n{NEON_CYAN}{BOLD}  {LIGHTNING} Timing:{RESET}")
                print(f"{NEON_BLURPLE}    {DOT} {WHITE}Average: {NEON_CYAN}{avg_sec:.2f}s{RESET}")
                print(f"{NEON_BLURPLE}    {DOT} {WHITE}Fastest: {NEON_GREEN}{min(timings):.2f}s{RESET}")
                print(f"{NEON_BLURPLE}    {DOT} {WHITE}Slowest: {YELLOW}{max(timings):.2f}s{RESET}")

            print(f"\n{NEON_GREEN}{BOLD}{DIV_WAVE}{RESET}")
            print(f"{NEON_GREEN}{BOLD}{STAR} Your query has been processed through R1! {SPARKLE}{RESET}")

            # Step 7: Execute Meta Round (R2) (PR 05)
            print(f"\n{NEON_GREEN}{BOLD}{DIV_THICK}{RESET}")
            print(f"{NEON_PINK}{BOLD}{ROCKET} ROUND 2: {RESET}{NEON_CYAN}{BOLD}{UNDERLINE}META{RESET}")
            print(f"{NEON_BLURPLE}{DIV_SINGLE}{RESET}")
            print(f"{WHITE}Models reviewing peer responses and revising...{RESET}\n")

            # Define progress callback for R2
            def r2_progress(model, time_sec, total, completed):
                # Extract short model name (last part after /)
                short_name = model.split('/')[-1] if '/' in model else model
                print(f"{NEON_GREEN}{BOLD}  ✓{RESET} {WHITE}{short_name}{RESET} {GRAY}revised in{RESET} {NEON_CYAN}{BOLD}{time_sec:.2f}s{RESET} {GRAY}({completed}/{total}){RESET}")

            r2_result = await execute_meta_round(run_id, progress_callback=r2_progress)

            print(f"\n{NEON_GREEN}{BOLD}{SPARKLE} Meta Round (R2) {RESET}{NEON_GREEN}{BOLD}Completed{RESET}")
            print(f"{NEON_BLURPLE}{BOLD}  {ARROW}{RESET} {WHITE}META responses:{RESET} {NEON_PINK}{BOLD}{len(r2_result['responses'])}{RESET}")
            meta_successful = [r for r in r2_result['responses'] if not r.get('error')]
            meta_errors = [r for r in r2_result['responses'] if r.get('error')]
            print(f"{NEON_BLURPLE}{BOLD}  {ARROW}{RESET} {WHITE}Successful:{RESET} {NEON_GREEN}{BOLD}{len(meta_successful)}{RESET}")
            if meta_errors:
                print(f"{NEON_BLURPLE}{BOLD}  {ARROW}{RESET} {WHITE}Errors:{RESET} {NEON_PINK}{BOLD}{len(meta_errors)}{RESET}")
            print(f"{NEON_BLURPLE}{BOLD}  {ARROW}{RESET} {GRAY}Artifacts:{RESET}")
            print(f"{GRAY}{DIM}    - runs/{run_id}/04_meta.json{RESET}")
            print(f"{GRAY}{DIM}    - runs/{run_id}/04_meta_status.json{RESET}")

            # Step 8: Execute UltrAI Synthesis (R3) (PR 06)
            print(f"\n{NEON_GREEN}{BOLD}{DIV_THICK}{RESET}")
            print(f"{NEON_PINK}{BOLD}{ROCKET} ROUND 3: {RESET}{NEON_CYAN}{BOLD}{UNDERLINE}ULTRA SYNTHESIS{RESET}")
            print(f"{NEON_BLURPLE}{DIV_SINGLE}{RESET}")
            print(f"{WHITE}Neutral model synthesizing final response...{RESET}\n")

            r3_spinner = ProgressSpinner("Executing R3 - ULTRA synthesizing consensus")
            r3_spinner.start()
            r3_result = await execute_ultrai_synthesis(run_id)
            r3_spinner.stop()

            print(f"\n{NEON_GREEN}{BOLD}{SPARKLE} UltrAI Synthesis (R3) {RESET}{NEON_GREEN}{BOLD}Completed{RESET}")
            print(f"{NEON_BLURPLE}{BOLD}  {ARROW}{RESET} {WHITE}Neutral model:{RESET} {NEON_CYAN}{r3_result['result']['model']}{RESET}")
            synthesis_time = r3_result['result']['ms'] / 1000.0  # Convert to seconds
            print(f"{NEON_BLURPLE}{BOLD}  {ARROW}{RESET} {WHITE}Response time:{RESET} {NEON_PINK}{BOLD}{synthesis_time:.2f}s{RESET}")
            print(f"{NEON_BLURPLE}{BOLD}  {ARROW}{RESET} {GRAY}Artifacts:{RESET}")
            print(f"{GRAY}{DIM}    - runs/{run_id}/05_ultrai.json{RESET}")
            print(f"{GRAY}{DIM}    - runs/{run_id}/05_ultrai_status.json{RESET}")
            print(f"\n{NEON_GREEN}{BOLD}{DIV_DOTS}{RESET}")

            # Step 9: Generate Statistics (PR 08)
            print(f"\n{NEON_GREEN}{BOLD}{DIV_SINGLE}{RESET}")
            print(f"{NEON_BLURPLE}{BOLD}{LIGHTNING} {RESET}{NEON_CYAN}{BOLD}Generating statistics...{RESET}\n")

            stats_spinner = ProgressSpinner("Analyzing performance metrics")
            stats_spinner.start()
            stats_result = generate_statistics(run_id)
            stats_spinner.stop()

            print(f"\n{NEON_GREEN}{BOLD}{UNDERLINE}{STAR} Statistics Generated{RESET}")
            print(f"{NEON_BLURPLE}{BOLD}  {ARROW}{RESET} {WHITE}R1 responses:{RESET} {NEON_PINK}{BOLD}{stats_result['INITIAL']['count']}{RESET}")
            print(f"{NEON_BLURPLE}{BOLD}  {ARROW}{RESET} {WHITE}R2 responses:{RESET} {NEON_PINK}{BOLD}{stats_result['META']['count']}{RESET}")
            print(f"{NEON_BLURPLE}{BOLD}  {ARROW}{RESET} {WHITE}R3 synthesis:{RESET} {NEON_PINK}{BOLD}{stats_result['ULTRAI']['count']}{RESET}")
            print(f"{NEON_BLURPLE}{BOLD}  {ARROW}{RESET} {GRAY}Artifact: {DIM}runs/{run_id}/stats.json{RESET}")
            print(f"{NEON_GREEN}{BOLD}{DIV_WAVE}{RESET}")

            # Step 11: Final Delivery (PR 09)
            print(f"\n{NEON_GREEN}{BOLD}{DIV_THICK}{RESET}")
            print(f"{NEON_PINK}{BOLD}{ROCKET} {RESET}{NEON_CYAN}{BOLD}Preparing final delivery...{RESET}\n")

            delivery_spinner = ProgressSpinner("Packaging all results")
            delivery_spinner.start()
            delivery_result = deliver_results(run_id)
            delivery_spinner.stop()

            print(f"\n{NEON_GREEN}{BOLD}{SPARKLE} Final Delivery {RESET}{NEON_GREEN}{BOLD}{delivery_result['status']}{RESET}")
            print(f"{NEON_BLURPLE}{BOLD}  {ARROW}{RESET} {WHITE}Total artifacts:{RESET} {NEON_PINK}{BOLD}{delivery_result['metadata']['total_artifacts']}{RESET}")
            print(f"{NEON_BLURPLE}{BOLD}  {ARROW}{RESET} {GRAY}Artifact: {DIM}runs/{run_id}/delivery.json{RESET}")

            # Display synthesis with vibrant borders
            print(f"\n{NEON_GREEN}{BOLD}{BOX_TL}{BOX_H * 68}{BOX_TR}{RESET}")
            print(f"{NEON_GREEN}{BOLD}{BOX_V}{RESET}{NEON_PINK}{BOLD}  {SPARKLE} ULTRAI SYNTHESIS {SPARKLE}{' ' * 42}{NEON_GREEN}{BOLD}{BOX_V}{RESET}")
            print(f"{NEON_GREEN}{BOLD}{BOX_BL}{BOX_H * 68}{BOX_BR}{RESET}")
            print(f"\n{WHITE}{r3_result['result']['text']}{RESET}\n")
            print(f"{NEON_GREEN}{BOLD}{DIV_THICK}{RESET}")
            print(f"\n{NEON_GREEN}{BOLD}{STAR} {SPARKLE} Complete!{RESET} {WHITE}All artifacts saved to:{RESET} {NEON_CYAN}{BOLD}runs/{run_id}/{RESET}")

            # Download instructions
            print(f"\n{NEON_PINK}{BOLD}{ROCKET} DOWNLOADABLE RESULTS:{RESET}")
            print(f"\n{WHITE}All round outputs are saved as JSON files in: {NEON_CYAN}{BOLD}runs/{run_id}/{RESET}")
            print(f"\n{NEON_BLURPLE}{BOLD}  {ARROW}{RESET} {NEON_GREEN}{BOLD}INITIAL (R1):{RESET} {GRAY}runs/{run_id}/03_initial.json{RESET}")
            print(f"{NEON_BLURPLE}{BOLD}  {ARROW}{RESET} {NEON_GREEN}{BOLD}META (R2):{RESET}    {GRAY}runs/{run_id}/04_meta.json{RESET}")
            print(f"{NEON_BLURPLE}{BOLD}  {ARROW}{RESET} {NEON_GREEN}{BOLD}FINAL (R3):{RESET}   {GRAY}runs/{run_id}/05_ultrai.json{RESET}")
            print(f"{NEON_BLURPLE}{BOLD}  {ARROW}{RESET} {NEON_CYAN}{BOLD}STATS:{RESET}        {GRAY}runs/{run_id}/stats.json{RESET}")
            print(f"{NEON_BLURPLE}{BOLD}  {ARROW}{RESET} {NEON_CYAN}{BOLD}DELIVERY:{RESET}     {GRAY}runs/{run_id}/delivery.json{RESET}")

            # Add-on exports section removed - add-ons disabled (placeholder implementations)

            print(f"\n{GRAY}{DIM}Open these files in any text editor or JSON viewer.{RESET}")
            print(f"{NEON_BLURPLE}{BOLD}{DIV_WAVE}{RESET}\n")

        except UserInputError as e:
            print(f"\n{NEON_PINK}{BOLD}✗ Input Error: {e}{RESET}")
            sys.exit(1)
        except ActiveLLMError as e:
            print(f"\n{NEON_PINK}{BOLD}✗ Active LLMs Error: {e}{RESET}")
            sys.exit(1)
        except InitialRoundError as e:
            print(f"\n{NEON_PINK}{BOLD}✗ Initial Round Error: {e}{RESET}")
            sys.exit(1)
        except MetaRoundError as e:
            print(f"\n{NEON_PINK}{BOLD}✗ Meta Round Error: {e}{RESET}")
            sys.exit(1)
        except UltraiSynthesisError as e:
            print(f"\n{NEON_PINK}{BOLD}✗ Synthesis Error: {e}{RESET}")
            sys.exit(1)

    except KeyboardInterrupt:
        print(f"\n\n{NEON_CYAN}Operation cancelled by user.{RESET}")
        sys.exit(0)

    except Exception as e:
        print(f"\n{NEON_PINK}{BOLD}✗ Unexpected error: {e}{RESET}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


def run_cli():
    """Entry point for CLI"""
    asyncio.run(main())


if __name__ == "__main__":
    run_cli()
