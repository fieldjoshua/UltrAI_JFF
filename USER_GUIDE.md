# 🚀 UltrAI - User Guide

## What is UltrAI?

UltrAI is a multi-LLM synthesis system that sends your question to multiple AI models, has them review each other's answers, and produces a final synthesized response with confidence intervals.

## Installation (One-Time Setup)

### Prerequisites
- Python 3.10 or higher
- An [OpenRouter account](https://openrouter.ai/) with API credits

### Setup Steps

1. **Clone or download this repository:**
   ```bash
   git clone https://github.com/fieldjoshua/UltrAI_JFF.git
   cd UltrAI_JFF
   ```

2. **Install UltrAI:**
   ```bash
   make install
   ```
   
   This will:
   - Create a virtual environment
   - Install all dependencies
   - Set up the ultrai command

3. **Get your OpenRouter API key:**
   - Sign up at https://openrouter.ai/
   - Go to your account settings
   - Generate an API key
   - Add credits to your account

4. **Configure your API key:**
   
   Create a file named `.env` in the UltrAI_JFF folder:
   ```bash
   echo "OPENROUTER_API_KEY=your-key-here" > .env
   ```
   
   Replace `your-key-here` with your actual API key.

## How to Use

### Starting UltrAI

In your terminal, from the UltrAI_JFF folder:

```bash
make venv          # Activate environment (first time)
python3 -m ultrai.cli
```

Or if installed globally:
```bash
ultrai
```

### Using the Interface

1. **Enter your question** when prompted
   
2. **Choose a cocktail** (group of AI models):
   - **PREMIUM** - High-quality models
   - **SPEEDY** - Fast responses
   - **BUDGET** - Cost-effective
   - **DEPTH** - Deep reasoning

3. **Select add-ons** (optional):
   - Citation tracking
   - Cost monitoring
   - Extended statistics
   - Visualization
   - Confidence intervals

4. **Wait for synthesis** - UltrAI will:
   - ✅ Check system readiness
   - ✅ Send query to multiple models (R1)
   - ✅ Have models review each other (R2)
   - ✅ Synthesize final answer (R3)
   - ✅ Show you the result!

### Example Session

```
Query: What is quantum computing?

Select cocktail: 1 (PREMIUM)

Add-ons: [press Enter to skip]

⚡ Processing through 3 rounds...
✨ Complete!

[Your synthesized answer appears here]
```

## Output Files

All results are saved in `runs/<timestamp>/`:
- `00_ready.json` - Available models
- `01_inputs.json` - Your question and settings
- `02_activate.json` - Selected models
- `03_initial.json` - Round 1 responses
- `04_meta.json` - Round 2 revised responses
- `05_ultrai.json` - Final synthesis
- `stats.json` - Performance metrics
- `delivery.json` - Complete results

## Costs

- Uses OpenRouter credits
- Costs vary by cocktail choice:
  - **PREMIUM**: High quality, moderate cost
  - **SPEEDY**: Fast, lower cost
  - **BUDGET**: Most economical
  - **DEPTH**: Moderate cost, deep analysis

Enable "cost_monitoring" add-on to track spending.

## Troubleshooting

### "System Readiness Error"
- Check your `.env` file has the correct API key
- Verify you have credits in your OpenRouter account
- Test your internet connection

### "Insufficient ACTIVE LLMs"
- Some models in your chosen cocktail may be unavailable
- Try a different cocktail
- Check OpenRouter status

### "No module named ultrai"
- Run `make install` again
- Activate the virtual environment: `. .venv/bin/activate`

## Tips for Best Results

1. **Be specific** - Clear questions get better answers
2. **Choose appropriate cocktail** - PREMIUM or DEPTH for important queries, BUDGET for quick tests
3. **Use DEPTH** for complex reasoning tasks
4. **Enable confidence intervals** to see how models agree/disagree

## Support

- Report issues: https://github.com/fieldjoshua/UltrAI_JFF/issues
- View all runs: Check the `runs/` folder
- Need help? Read the full docs in the repo

---

🤖 Built with Claude Code
