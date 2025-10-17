"""
UltrAI Command Line Interface

Allows users to access all UltrAI features and submit queries
through an interactive CLI.
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
# Module imports placed after color constants for code organization
from ultrai.system_readiness import (  # noqa: E402
    check_system_readiness,
    SystemReadinessError
)
from ultrai.user_input import (  # noqa: E402
    collect_user_inputs,
    UserInputError
)
from ultrai.active_llms import (  # noqa: E402
    prepare_active_llms,
    ActiveLLMError
)
from ultrai.initial_round import (  # noqa: E402
    execute_initial_round,
    InitialRoundError
)
from ultrai.meta_round import (  # noqa: E402
    execute_meta_round,
    MetaRoundError
)
from ultrai.ultrai_synthesis import (  # noqa: E402
    execute_ultrai_synthesis,
    UltraiSynthesisError
)
from ultrai.statistics import generate_statistics  # noqa: E402
from ultrai.final_delivery import deliver_results  # noqa: E402


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
                except (
                    FileNotFoundError,
                    PermissionError,
                    UnicodeDecodeError
                ):
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
            frame_text = (
                f"{NEON_BLURPLE}{BOLD}"
                f"{self.frames[self.idx]}{RESET}"
            )
            sys.stdout.write(frame_text)
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
    title_line = (
        f"{NEON_GREEN}{BOX_V}{RESET}{NEON_CYAN}{BOLD}"
        f"        U L T R A I   {RESET}{NEON_PINK}{LIGHTNING}{RESET}  "
        f"{WHITE}{BOLD}M U L T I - L L M   S Y N T H E S I S{RESET}"
        f"        {NEON_GREEN}{BOX_V}{RESET}"
    )
    print(title_line)
    print(f"{NEON_GREEN}{BOLD}{DIV_THICK}{RESET}\n")


def print_ready_status(ready_result):
    """Display system readiness status"""
    print(f"\n{NEON_GREEN}{BOLD}{SPARKLE} System Ready {SPARKLE}{RESET}")
    run_id_line = (
        f"{NEON_BLURPLE}  {ARROW} {WHITE}Run ID:{RESET} "
        f"{NEON_CYAN}{BOLD}{ready_result['run_id']}{RESET}"
    )
    print(run_id_line)
    llm_count_line = (
        f"{NEON_BLURPLE}  {ARROW} {WHITE}Available LLMs:{RESET} "
        f"{NEON_GREEN}{BOLD}{ready_result['llm_count']}{RESET}"
    )
    print(llm_count_line)
    status_line = (
        f"{NEON_BLURPLE}  {ARROW} {WHITE}Status:{RESET} "
        f"{NEON_GREEN}{BOLD}{ready_result['status']}{RESET}"
    )
    print(status_line)
    artifact_line = (
        f"{NEON_BLURPLE}  {ARROW} {WHITE}Artifact:{RESET} "
        f"{GRAY}{DIM}runs/{ready_result['run_id']}/00_ready.json{RESET}"
    )
    print(artifact_line)


def prompt_query():
    """Prompt user for query"""
    print(f"\n{NEON_GREEN}{DIV_DOUBLE}{RESET}")
    step1_title = (
        f"{NEON_PINK}{BOLD}{ROCKET} STEP 1: {RESET}"
        f"{NEON_CYAN}{BOLD}{UNDERLINE}Enter Your Query{RESET}"
    )
    print(step1_title)
    print(f"{NEON_BLURPLE}{DIV_SINGLE}{RESET}")
    question_line = (
        f"{WHITE}What question or prompt would you like "
        f"the LLMs to analyze?{RESET}"
    )
    print(question_line)
    print(f"{GRAY}(This will be sent to multiple LLMs for synthesis){RESET}")
    print()

    query_prompt = (
        f"{NEON_GREEN}{BLINK}▶{RESET} {NEON_CYAN}Query:{RESET} "
    )
    query = input(query_prompt).strip()

    if not query:
        raise UserInputError("Query cannot be empty")

    return query


def prompt_cocktail():
    """Prompt user to select a cocktail"""
    print(f"\n{NEON_GREEN}{DIV_DOUBLE}{RESET}")
    step2_title = (
        f"{NEON_PINK}{BOLD}{LIGHTNING} STEP 2: {RESET}"
        f"{NEON_CYAN}{BOLD}{UNDERLINE}Select LLM Cocktail{RESET}"
    )
    print(step2_title)
    print(f"{NEON_BLURPLE}{DIV_WAVE}{RESET}")
    print(f"{WHITE}{BOLD}Choose a pre-selected group of LLMs:\n{RESET}")

    premium_line = (
        f"{NEON_BLURPLE}{BOLD}1.{RESET} {NEON_GREEN}PREMIUM{RESET}  "
        f"{GRAY}- High-quality models "
        f"(claude-3.7-sonnet, chatgpt-4o-latest, llama-3.3-70b){RESET}"
    )
    print(premium_line)
    speedy_line = (
        f"{NEON_BLURPLE}{BOLD}2.{RESET} {YELLOW}SPEEDY{RESET}   "
        f"{GRAY}- Fast response models "
        f"(gpt-4o-mini, claude-3.5-haiku, gemini-2.0){RESET}"
    )
    print(speedy_line)
    budget_line = (
        f"{NEON_BLURPLE}{BOLD}3.{RESET} {WHITE}BUDGET{RESET}   "
        f"{GRAY}- Cost-effective models "
        f"(gpt-3.5-turbo, gemini-2.0, qwen-2.5){RESET}"
    )
    print(budget_line)
    depth_line = (
        f"{NEON_BLURPLE}{BOLD}4.{RESET} {NEON_CYAN}DEPTH{RESET}    "
        f"{GRAY}- Deep reasoning models "
        f"(claude-3.7-sonnet, gpt-4o, gemini-thinking){RESET}"
    )
    print(depth_line)
    print()

    while True:
        cocktail_prompt = (
            f"{NEON_GREEN}{BLINK}▶{RESET} {NEON_CYAN}"
            f"Select cocktail (1-4) [default: 1]:{RESET} "
        )
        choice = input(cocktail_prompt).strip() or "1"

        if choice in ["1", "2", "3", "4"]:
            cocktails = ["PREMIUM", "SPEEDY", "BUDGET", "DEPTH"]
            selected = cocktails[int(choice) - 1]
            selected_line = (
                f"\n{NEON_GREEN}{BOLD}{STAR} Selected: "
                f"{NEON_CYAN}{BOLD}{selected}{RESET}"
            )
            print(selected_line)
            return selected
        else:
            error_line = (
                f"{NEON_PINK}{BOLD}✗ Invalid choice. "
                f"Please enter 1-4.{RESET}"
            )
            print(error_line)


def print_submission_summary(inputs_result):
    """Display submission summary"""
    print(f"\n{NEON_GREEN}{BOLD}{BOX_TL}{BOX_H * 68}{BOX_TR}{RESET}")
    summary_header = (
        f"{NEON_GREEN}{BOX_V}{RESET}{NEON_PINK}{BOLD}  "
        f"{ROCKET} SUBMISSION SUMMARY{' ' * 45}"
        f"{NEON_GREEN}{BOX_V}{RESET}"
    )
    print(summary_header)
    print(f"{NEON_GREEN}{BOLD}{BOX_BL}{BOX_H * 68}{BOX_BR}{RESET}")
    query_line = (
        f"\n{NEON_BLURPLE}{BOLD}Query:{RESET} "
        f"{WHITE}{inputs_result['QUERY']}{RESET}"
    )
    print(query_line)
    analysis_line = (
        f"{NEON_BLURPLE}{BOLD}Analysis Type:{RESET} "
        f"{NEON_CYAN}{inputs_result['ANALYSIS']}{RESET}"
    )
    print(analysis_line)
    cocktail_line = (
        f"{NEON_BLURPLE}{BOLD}Cocktail:{RESET} "
        f"{NEON_GREEN}{BOLD}{inputs_result['COCKTAIL']}{RESET}"
    )
    print(cocktail_line)
    # Add-ons line removed - feature disabled (placeholder implementations)
    run_id_line = (
        f"\n{NEON_BLURPLE}{BOLD}Run ID:{RESET} "
        f"{YELLOW}{inputs_result['metadata']['run_id']}{RESET}"
    )
    print(run_id_line)
    artifact_path = (
        f"{NEON_BLURPLE}{BOLD}Artifact:{RESET} {GRAY}{DIM}runs/"
        f"{inputs_result['metadata']['run_id']}/01_inputs.json{RESET}"
    )
    print(artifact_path)
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
            spinner_text = (
                f'\r{BLUE}{self.spinner_chars[self.idx]}{RESET} '
                f'{WHITE}{self.message}...{RESET}'
            )
            sys.stdout.write(spinner_text)
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
        # Clear line
        clear_line = '\r' + ' ' * (len(self.message) + 10) + '\r'
        sys.stdout.write(clear_line)
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
            error_header = (
                f"\n{NEON_PINK}{BOLD}✗ System Readiness Error:{RESET} "
                f"{WHITE}{e}{RESET}"
            )
            print(error_header)
            print(f"\n{NEON_GREEN}{BOLD}{DIV_SINGLE}{RESET}")
            print(f"{NEON_CYAN}{BOLD}Please ensure:{RESET}")
            # lgtm[py/clear-text-logging-sensitive-data]
            # Note: This prints the env variable NAME, not the actual key value
            api_key_line = (
                f"{NEON_BLURPLE}  {ARROW}{RESET} {WHITE}"
                f"OPENROUTER_API_KEY is set in your .env file{RESET}"
            )
            print(api_key_line)
            account_line = (
                f"{NEON_BLURPLE}  {ARROW}{RESET} {WHITE}"
                f"You have an active OpenRouter account with credits{RESET}"
            )
            print(account_line)
            network_line = (
                f"{NEON_BLURPLE}  {ARROW}{RESET} {WHITE}"
                f"Your network connection is working{RESET}"
            )
            print(network_line)
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
        # Add-ons create truncated/incomplete outputs
        # and should not be offered to users
        # All add-ons functionality has been removed from collect_user_inputs

        # Step 3: Collect Inputs
        print(f"\n{NEON_GREEN}{BOLD}{DIV_WAVE}{RESET}")
        collecting_line = (
            f"{NEON_BLURPLE}{BOLD}{LIGHTNING} {RESET}"
            f"{NEON_CYAN}{BOLD}Collecting inputs...{RESET}"
        )
        print(collecting_line)

        try:
            inputs_result = collect_user_inputs(
                query=query,
                analysis="Synthesis",
                cocktail=cocktail,
                run_id=run_id
            )

            print_submission_summary(inputs_result)

            # Step 5: Prepare Active LLMs (PR 03)
            print(f"\n{NEON_GREEN}{BOLD}{DIV_DOTS}{RESET}")
            determining_line = (
                f"{NEON_PINK}{BOLD}{SPARKLE} {RESET}"
                f"{NEON_CYAN}{BOLD}Determining active LLMs "
                f"{WHITE}(READY ∩ COCKTAIL){RESET}"
                f"{NEON_CYAN}{BOLD}...{RESET}"
            )
            print(determining_line)

            active_result = prepare_active_llms(run_id)

            prepared_header = (
                f"\n{NEON_GREEN}{BOLD}{UNDERLINE}{STAR} "
                f"Active LLMs Prepared{RESET}"
            )
            print(prepared_header)
            cocktail_info = (
                f"{NEON_BLURPLE}{BOLD}  {ARROW}{RESET} "
                f"{WHITE}Cocktail:{RESET} "
                f"{NEON_GREEN}{BOLD}{active_result['cocktail']}{RESET}"
            )
            print(cocktail_info)
            active_count = (
                f"{NEON_BLURPLE}{BOLD}  {ARROW}{RESET} "
                f"{WHITE}Active models:{RESET} "
                f"{NEON_PINK}{BOLD}{len(active_result['activeList'])}{RESET}"
            )
            print(active_count)
            quorum_info = (
                f"{NEON_BLURPLE}{BOLD}  {ARROW}{RESET} "
                f"{WHITE}Quorum:{RESET} "
                f"{NEON_PINK}{BOLD}{active_result['quorum']}{RESET}"
            )
            print(quorum_info)
            artifact_info = (
                f"{NEON_BLURPLE}{BOLD}  {ARROW}{RESET} "
                f"{GRAY}Artifact: {DIM}runs/{run_id}/02_activate.json{RESET}"
            )
            print(artifact_info)
            print(f"\n{NEON_CYAN}{BOLD}  {LIGHTNING} Models:{RESET}")
            for model in active_result['activeList']:
                model_line = (
                    f"{NEON_BLURPLE}    {DOT} {WHITE}{model}{RESET}"
                )
                print(model_line)

            # Step 6: Execute Initial Round (R1) (PR 04)
            print(f"\n{NEON_GREEN}{BOLD}{DIV_THICK}{RESET}")
            r1_header = (
                f"{NEON_PINK}{BOLD}{ROCKET} ROUND 1: {RESET}"
                f"{NEON_CYAN}{BOLD}{UNDERLINE}INITIAL{RESET}"
            )
            print(r1_header)
            print(f"{NEON_BLURPLE}{DIV_SINGLE}{RESET}")
            r1_status = (
                f"{WHITE}Sending query to {NEON_PINK}{BOLD}"
                f"{len(active_result['activeList'])}{RESET}{WHITE} "
                f"models in parallel...{RESET}\n"
            )
            print(r1_status)

            # Define progress callback for R1
            def r1_progress(model, time_sec, total, completed):
                # Extract short model name (last part after /)
                short_name = model.split('/')[-1] if '/' in model else model
                progress_line = (
                    f"{NEON_GREEN}{BOLD}  ✓{RESET} "
                    f"{WHITE}{short_name}{RESET} "
                    f"{GRAY}completed in{RESET} "
                    f"{NEON_CYAN}{BOLD}{time_sec:.2f}s{RESET} "
                    f"{GRAY}({completed}/{total}){RESET}"
                )
                print(progress_line)

            r1_result = await execute_initial_round(
                run_id, progress_callback=r1_progress
            )

            r1_complete = (
                f"\n{NEON_GREEN}{BOLD}{SPARKLE} Initial Round (R1) {RESET}"
                f"{NEON_GREEN}{BOLD}Completed{RESET}"
            )
            print(r1_complete)
            responses_count = (
                f"{NEON_BLURPLE}{BOLD}  {ARROW}{RESET} "
                f"{WHITE}Responses:{RESET} "
                f"{NEON_PINK}{BOLD}{len(r1_result['responses'])}{RESET}"
            )
            print(responses_count)
            successful = [
                r for r in r1_result['responses'] if not r.get('error')
            ]
            errors = [r for r in r1_result['responses'] if r.get('error')]
            successful_line = (
                f"{NEON_BLURPLE}{BOLD}  {ARROW}{RESET} "
                f"{WHITE}Successful:{RESET} "
                f"{NEON_GREEN}{BOLD}{len(successful)}{RESET}"
            )
            print(successful_line)
            if errors:
                errors_line = (
                    f"{NEON_BLURPLE}{BOLD}  {ARROW}{RESET} "
                    f"{WHITE}Errors:{RESET} "
                    f"{NEON_PINK}{BOLD}{len(errors)}{RESET}"
                )
                print(errors_line)
            print(
                f"{NEON_BLURPLE}{BOLD}  {ARROW}{RESET} {GRAY}Artifacts:{RESET}"
            )
            print(
                f"{GRAY}{DIM}    - runs/{run_id}/03_initial.json{RESET}"
            )
            print(
                f"{GRAY}{DIM}    - runs/{run_id}/03_initial_status.json{RESET}"
            )

            # Show timing summary (convert ms to seconds)
            if successful:
                # Convert to seconds
                timings = [r['ms'] / 1000.0 for r in successful]
                avg_sec = sum(timings) / len(timings)
                print(f"\n{NEON_CYAN}{BOLD}  {LIGHTNING} Timing:{RESET}")
                avg_line = (
                    f"{NEON_BLURPLE}    {DOT} {WHITE}Average: "
                    f"{NEON_CYAN}{avg_sec:.2f}s{RESET}"
                )
                print(avg_line)
                fastest_line = (
                    f"{NEON_BLURPLE}    {DOT} {WHITE}Fastest: "
                    f"{NEON_GREEN}{min(timings):.2f}s{RESET}"
                )
                print(fastest_line)
                slowest_line = (
                    f"{NEON_BLURPLE}    {DOT} {WHITE}Slowest: "
                    f"{YELLOW}{max(timings):.2f}s{RESET}"
                )
                print(slowest_line)

            print(f"\n{NEON_GREEN}{BOLD}{DIV_WAVE}{RESET}")
            r1_done = (
                f"{NEON_GREEN}{BOLD}{STAR} Your query has been "
                f"processed through R1! {SPARKLE}{RESET}"
            )
            print(r1_done)

            # Step 7: Execute Meta Round (R2) (PR 05)
            print(f"\n{NEON_GREEN}{BOLD}{DIV_THICK}{RESET}")
            r2_header = (
                f"{NEON_PINK}{BOLD}{ROCKET} ROUND 2: {RESET}"
                f"{NEON_CYAN}{BOLD}{UNDERLINE}META{RESET}"
            )
            print(r2_header)
            print(f"{NEON_BLURPLE}{DIV_SINGLE}{RESET}")
            r2_status = (
                f"{WHITE}Models reviewing peer responses "
                f"and revising...{RESET}\n"
            )
            print(r2_status)

            # Define progress callback for R2
            def r2_progress(model, time_sec, total, completed):
                # Extract short model name (last part after /)
                short_name = model.split('/')[-1] if '/' in model else model
                progress_line = (
                    f"{NEON_GREEN}{BOLD}  ✓{RESET} "
                    f"{WHITE}{short_name}{RESET} "
                    f"{GRAY}revised in{RESET} "
                    f"{NEON_CYAN}{BOLD}{time_sec:.2f}s{RESET} "
                    f"{GRAY}({completed}/{total}){RESET}"
                )
                print(progress_line)

            r2_result = await execute_meta_round(
                run_id, progress_callback=r2_progress
            )

            r2_complete = (
                f"\n{NEON_GREEN}{BOLD}{SPARKLE} Meta Round (R2) {RESET}"
                f"{NEON_GREEN}{BOLD}Completed{RESET}"
            )
            print(r2_complete)
            meta_count = (
                f"{NEON_BLURPLE}{BOLD}  {ARROW}{RESET} "
                f"{WHITE}META responses:{RESET} "
                f"{NEON_PINK}{BOLD}{len(r2_result['responses'])}{RESET}"
            )
            print(meta_count)
            meta_successful = [
                r for r in r2_result['responses'] if not r.get('error')
            ]
            meta_errors = [
                r for r in r2_result['responses'] if r.get('error')
            ]
            meta_success_line = (
                f"{NEON_BLURPLE}{BOLD}  {ARROW}{RESET} "
                f"{WHITE}Successful:{RESET} "
                f"{NEON_GREEN}{BOLD}{len(meta_successful)}{RESET}"
            )
            print(meta_success_line)
            if meta_errors:
                meta_errors_line = (
                    f"{NEON_BLURPLE}{BOLD}  {ARROW}{RESET} "
                    f"{WHITE}Errors:{RESET} "
                    f"{NEON_PINK}{BOLD}{len(meta_errors)}{RESET}"
                )
                print(meta_errors_line)
            print(
                f"{NEON_BLURPLE}{BOLD}  {ARROW}{RESET} {GRAY}Artifacts:{RESET}"
            )
            print(f"{GRAY}{DIM}    - runs/{run_id}/04_meta.json{RESET}")
            print(f"{GRAY}{DIM}    - runs/{run_id}/04_meta_status.json{RESET}")

            # Step 8: Execute UltrAI Synthesis (R3) (PR 06)
            print(f"\n{NEON_GREEN}{BOLD}{DIV_THICK}{RESET}")
            r3_header = (
                f"{NEON_PINK}{BOLD}{ROCKET} ROUND 3: {RESET}"
                f"{NEON_CYAN}{BOLD}{UNDERLINE}ULTRA SYNTHESIS{RESET}"
            )
            print(r3_header)
            print(f"{NEON_BLURPLE}{DIV_SINGLE}{RESET}")
            r3_status = (
                f"{WHITE}Neutral model synthesizing "
                f"final response...{RESET}\n"
            )
            print(r3_status)

            r3_spinner = ProgressSpinner(
                "Executing R3 - ULTRA synthesizing consensus"
            )
            r3_spinner.start()
            r3_result = await execute_ultrai_synthesis(run_id)
            r3_spinner.stop()

            r3_complete = (
                f"\n{NEON_GREEN}{BOLD}{SPARKLE} UltrAI Synthesis (R3) "
                f"{RESET}{NEON_GREEN}{BOLD}Completed{RESET}"
            )
            print(r3_complete)
            neutral_model = (
                f"{NEON_BLURPLE}{BOLD}  {ARROW}{RESET} "
                f"{WHITE}Neutral model:{RESET} "
                f"{NEON_CYAN}{r3_result['result']['model']}{RESET}"
            )
            print(neutral_model)
            # Convert to seconds
            synthesis_time = r3_result['result']['ms'] / 1000.0
            response_time = (
                f"{NEON_BLURPLE}{BOLD}  {ARROW}{RESET} "
                f"{WHITE}Response time:{RESET} "
                f"{NEON_PINK}{BOLD}{synthesis_time:.2f}s{RESET}"
            )
            print(response_time)
            print(
                f"{NEON_BLURPLE}{BOLD}  {ARROW}{RESET} {GRAY}Artifacts:{RESET}"
            )
            print(
                f"{GRAY}{DIM}    - runs/{run_id}/05_ultrai.json{RESET}"
            )
            print(
                f"{GRAY}{DIM}    - runs/{run_id}/05_ultrai_status.json{RESET}"
            )
            print(f"\n{NEON_GREEN}{BOLD}{DIV_DOTS}{RESET}")

            # Step 9: Generate Statistics (PR 08)
            print(f"\n{NEON_GREEN}{BOLD}{DIV_SINGLE}{RESET}")
            stats_header = (
                f"{NEON_BLURPLE}{BOLD}{LIGHTNING} {RESET}"
                f"{NEON_CYAN}{BOLD}Generating statistics...{RESET}\n"
            )
            print(stats_header)

            stats_spinner = ProgressSpinner("Analyzing performance metrics")
            stats_spinner.start()
            stats_result = generate_statistics(run_id)
            stats_spinner.stop()

            stats_complete = (
                f"\n{NEON_GREEN}{BOLD}{UNDERLINE}{STAR} "
                f"Statistics Generated{RESET}"
            )
            print(stats_complete)
            r1_count = (
                f"{NEON_BLURPLE}{BOLD}  {ARROW}{RESET} "
                f"{WHITE}R1 responses:{RESET} "
                f"{NEON_PINK}{BOLD}{stats_result['INITIAL']['count']}{RESET}"
            )
            print(r1_count)
            r2_count = (
                f"{NEON_BLURPLE}{BOLD}  {ARROW}{RESET} "
                f"{WHITE}R2 responses:{RESET} "
                f"{NEON_PINK}{BOLD}{stats_result['META']['count']}{RESET}"
            )
            print(r2_count)
            r3_count = (
                f"{NEON_BLURPLE}{BOLD}  {ARROW}{RESET} "
                f"{WHITE}R3 synthesis:{RESET} "
                f"{NEON_PINK}{BOLD}{stats_result['ULTRAI']['count']}{RESET}"
            )
            print(r3_count)
            stats_artifact = (
                f"{NEON_BLURPLE}{BOLD}  {ARROW}{RESET} "
                f"{GRAY}Artifact: {DIM}runs/{run_id}/stats.json{RESET}"
            )
            print(stats_artifact)
            print(f"{NEON_GREEN}{BOLD}{DIV_WAVE}{RESET}")

            # Step 11: Final Delivery (PR 09)
            print(f"\n{NEON_GREEN}{BOLD}{DIV_THICK}{RESET}")
            delivery_header = (
                f"{NEON_PINK}{BOLD}{ROCKET} {RESET}"
                f"{NEON_CYAN}{BOLD}Preparing final delivery...{RESET}\n"
            )
            print(delivery_header)

            delivery_spinner = ProgressSpinner("Packaging all results")
            delivery_spinner.start()
            delivery_result = deliver_results(run_id)
            delivery_spinner.stop()

            delivery_complete = (
                f"\n{NEON_GREEN}{BOLD}{SPARKLE} Final Delivery {RESET}"
                f"{NEON_GREEN}{BOLD}{delivery_result['status']}{RESET}"
            )
            print(delivery_complete)
            total_artifacts = (
                f"{NEON_BLURPLE}{BOLD}  {ARROW}{RESET} "
                f"{WHITE}Total artifacts:{RESET} "
                f"{NEON_PINK}{BOLD}"
                f"{delivery_result['metadata']['total_artifacts']}{RESET}"
            )
            print(total_artifacts)
            delivery_artifact = (
                f"{NEON_BLURPLE}{BOLD}  {ARROW}{RESET} "
                f"{GRAY}Artifact: {DIM}runs/{run_id}/delivery.json{RESET}"
            )
            print(delivery_artifact)

            # Display synthesis with vibrant borders
            print(f"\n{NEON_GREEN}{BOLD}{BOX_TL}{BOX_H * 68}{BOX_TR}{RESET}")
            synthesis_header = (
                f"{NEON_GREEN}{BOLD}{BOX_V}{RESET}{NEON_PINK}{BOLD}  "
                f"{SPARKLE} ULTRAI SYNTHESIS {SPARKLE}{' ' * 42}"
                f"{NEON_GREEN}{BOLD}{BOX_V}{RESET}"
            )
            print(synthesis_header)
            print(f"{NEON_GREEN}{BOLD}{BOX_BL}{BOX_H * 68}{BOX_BR}{RESET}")
            print(f"\n{WHITE}{r3_result['result']['text']}{RESET}\n")
            print(f"{NEON_GREEN}{BOLD}{DIV_THICK}{RESET}")
            complete_msg = (
                f"\n{NEON_GREEN}{BOLD}{STAR} {SPARKLE} Complete!{RESET} "
                f"{WHITE}All artifacts saved to:{RESET} "
                f"{NEON_CYAN}{BOLD}runs/{run_id}/{RESET}"
            )
            print(complete_msg)

            # Download instructions
            print(f"\n{NEON_PINK}{BOLD}{ROCKET} DOWNLOADABLE RESULTS:{RESET}")
            outputs_saved = (
                f"\n{WHITE}All round outputs are saved as JSON files in: "
                f"{NEON_CYAN}{BOLD}runs/{run_id}/{RESET}"
            )
            print(outputs_saved)
            initial_path = (
                f"\n{NEON_BLURPLE}{BOLD}  {ARROW}{RESET} "
                f"{NEON_GREEN}{BOLD}INITIAL (R1):{RESET} "
                f"{GRAY}runs/{run_id}/03_initial.json{RESET}"
            )
            print(initial_path)
            meta_path = (
                f"{NEON_BLURPLE}{BOLD}  {ARROW}{RESET} "
                f"{NEON_GREEN}{BOLD}META (R2):{RESET}    "
                f"{GRAY}runs/{run_id}/04_meta.json{RESET}"
            )
            print(meta_path)
            final_path = (
                f"{NEON_BLURPLE}{BOLD}  {ARROW}{RESET} "
                f"{NEON_GREEN}{BOLD}FINAL (R3):{RESET}   "
                f"{GRAY}runs/{run_id}/05_ultrai.json{RESET}"
            )
            print(final_path)
            stats_path = (
                f"{NEON_BLURPLE}{BOLD}  {ARROW}{RESET} "
                f"{NEON_CYAN}{BOLD}STATS:{RESET}        "
                f"{GRAY}runs/{run_id}/stats.json{RESET}"
            )
            print(stats_path)
            delivery_path = (
                f"{NEON_BLURPLE}{BOLD}  {ARROW}{RESET} "
                f"{NEON_CYAN}{BOLD}DELIVERY:{RESET}     "
                f"{GRAY}runs/{run_id}/delivery.json{RESET}"
            )
            print(delivery_path)

            # Add-on exports section removed
            # - add-ons disabled (placeholder implementations)

            open_files_msg = (
                f"\n{GRAY}{DIM}Open these files in any text editor "
                f"or JSON viewer.{RESET}"
            )
            print(open_files_msg)
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
