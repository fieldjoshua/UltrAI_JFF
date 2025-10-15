# UltrAI Quick Start Guide 🚀

## What is UltrAI?

UltrAI sends your question to multiple AI models, has them review each other, and gives you a synthesized answer. It's like getting multiple expert opinions and then a consensus report.

## Installation (5 minutes)

### 1. Prerequisites
- **Python 3.10+** - Check: `python3 --version`
- **OpenRouter Account** - Sign up at [openrouter.ai](https://openrouter.ai) (free to start)

### 2. Install UltrAI

```bash
# Clone the repo
git clone https://github.com/fieldjoshua/UltrAI_JFF.git
cd UltrAI_JFF

# Install (creates virtual environment and installs everything)
make install
```

### 3. Add Your API Key

Get your API key from [OpenRouter Settings](https://openrouter.ai/settings/keys), then:

```bash
echo "OPENROUTER_API_KEY=sk-or-v1-your-key-here" > .env
```

**That's it! You're ready to go.**

## Usage

### Run UltrAI

```bash
ultrai
```

That's the whole command! Just type `ultrai` and press enter.

### Follow the Prompts

1. **Enter your question**
   ```
   Query: What are the benefits of meditation?
   ```

2. **Pick a cocktail** (AI model group)
   ```
   1. ✨ PRIME    - Best quality (gpt-4o, claude-3.7, gemini-thinking)
   2. PREMIUM     - High quality
   3. SPEEDY      - Fast responses
   4. BUDGET      - Most economical
   5. DEPTH       - Deep analysis
   
   Select: 1
   ```

3. **Add-ons** (optional - just press Enter to skip)
   ```
   Add-ons: [Enter]
   ```

4. **Wait for magic** ✨
   - System checks readiness
   - Queries multiple models
   - Models review each other
   - Final synthesis generated
   - **Result displayed!**

## What You Get

Your answer appears on screen, plus all data is saved to `runs/<timestamp>/`:
- Original responses from each model
- Revised responses after peer review
- Final synthesis
- Statistics and metadata

## Costs

UltrAI uses your OpenRouter credits:
- **PRIME**: ~$0.10-0.30 per query (best quality)
- **PREMIUM**: ~$0.05-0.15 per query
- **SPEEDY**: ~$0.01-0.05 per query (fast)
- **BUDGET**: ~$0.005-0.02 per query (cheapest)

💡 **Tip**: Start with BUDGET to test, use PRIME for important questions.

## Examples

### Quick Test
```bash
ultrai
# Query: What is 2+2?
# Cocktail: 4 (BUDGET)
# Add-ons: [Enter]
```

### Research Question
```bash
ultrai
# Query: Explain the latest developments in quantum computing
# Cocktail: 1 (PRIME)
# Add-ons: 1,5 (citation tracking + confidence intervals)
```

### Code Question
```bash
ultrai
# Query: Best practices for React hooks?
# Cocktail: 3 (SPEEDY)
# Add-ons: [Enter]
```

## Troubleshooting

**"Command not found: ultrai"**
```bash
# Activate the virtual environment first
. .venv/bin/activate
# Then run
ultrai
```

**"System Readiness Error"**
- Check your `.env` file has the correct API key
- Make sure you have OpenRouter credits
- Test internet connection

**"Insufficient ACTIVE LLMs"**
- Some models may be down
- Try a different cocktail

## Need Help?

- 📖 [Full User Guide](USER_GUIDE.md)
- 🐛 [Report Issues](https://github.com/fieldjoshua/UltrAI_JFF/issues)
- 💬 [View Your Results](runs/)

## Tips

✅ **DO**: Be specific with questions  
✅ **DO**: Use PRIME for important queries  
✅ **DO**: Enable cost monitoring to track spending  

❌ **DON'T**: Share your API key  
❌ **DON'T**: Use PRIME for simple test questions  

---

**Ready?** Type `ultrai` and press Enter! 🚀
