/**
 * UltrAI Terminal CLI Interface
 *
 * Simulates a terminal/CLI experience for LLM synthesis.
 * Low-res, fast, developer-focused aesthetic.
 */

import { useState, useEffect } from 'react'
import { useUltrAI } from './hooks/useUltrAI'
import { useHealth } from './hooks/useHealth'
import { StatusDisplay } from './components/StatusDisplay'
import { ResultsDisplay } from './components/ResultsDisplay'

function App() {
  const [query, setQuery] = useState('')
  const [cocktail, setCocktail] = useState('SPEEDY')
  const [step, setStep] = useState('query') // query, cocktail, confirm, running, results
  const [headerColor, setHeaderColor] = useState('blurple')

  const { isHealthy } = useHealth()
  const { isLoading, currentRun, submitQuery } = useUltrAI()

  // Dynamic header color animation
  useEffect(() => {
    const interval = setInterval(() => {
      setHeaderColor(prev => prev === 'blurple' ? 'orange' : 'blurple')
    }, 3000) // Alternate every 3 seconds
    return () => clearInterval(interval)
  }, [])

  const cocktails = {
    LUXE: {
      name: 'Flagship premium models',
      models: ['gpt-4o', 'claude-sonnet-4.5', 'gemini-2.0-flash'],
      count: 3
    },
    PREMIUM: {
      name: 'High-quality balanced',
      models: ['gpt-4o', 'claude-3.7-sonnet', 'gemini-2.5-pro', 'mistral-large'],
      count: 4
    },
    SPEEDY: {
      name: 'Fast response optimized',
      models: ['gpt-4o-mini', 'grok-2-1212', 'claude-3-haiku', 'mistral-small', 'deepseek-chat'],
      count: 5
    },
    BUDGET: {
      name: 'Cost-effective quality',
      models: ['gpt-3.5-turbo', 'gemini-2.0-flash', 'qwen-2.5-72b'],
      count: 3
    },
    DEPTH: {
      name: 'Deep reasoning focus',
      models: ['claude-3.7-sonnet', 'gpt-4o', 'llama-3.3-70b'],
      count: 3
    },
  }

  const handleSubmit = async () => {
    if (!query.trim()) return
    setStep('running')
    await submitQuery(query, cocktail)
  }

  const handleReset = () => {
    setQuery('')
    setCocktail('SPEEDY')
    setStep('query')
  }

  const headerColorClass = headerColor === 'blurple' ? 'text-[#7C3AED]' : 'text-[#FF6B35]'

  return (
    <div className="min-h-screen p-4 terminal-scan">
      <div className="max-w-4xl mx-auto">
        {/* ASCII Logo - Dynamic Color */}
        <pre className={`${headerColorClass} terminal-glow text-xs mb-6 transition-colors duration-1000`}>
{` _   _ _ _         _   _____
| | | | | |_ _ __ / \\ |_   _|
| | | | | __| '__/ _ \\  | |
| |_| | | |_| |_/ ___ \\_| |_
\\________________/   \\______|

Multi-LLM Convergent Synthesis
`}
        </pre>

        {/* Connection Status */}
        {!isHealthy && (
          <div className="mb-4 text-red-500">
            <span className="cursor-blink">█</span> [ERROR] Backend not available - check API server
          </div>
        )}

        {/* Step 1: Query Input */}
        {step === 'query' && (
          <div className="space-y-4">
            <div className="text-green-500 mb-2 border-b border-green-900 pb-2">
              <span className="cursor-blink">█</span> STEP 1: ENTER QUERY
            </div>
            <div>
              <div className="text-green-500 mb-2">
                <span className="text-green-400">$</span> ultrai --query
              </div>
              <textarea
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                className="w-full bg-black border border-green-900 text-green-400 p-3 font-mono text-sm focus:outline-none focus:border-green-500 resize-none"
                rows="5"
                placeholder="Enter your query..."
              />
            </div>

            <button
              onClick={() => setStep('cocktail')}
              disabled={!query.trim() || !isHealthy}
              className="bg-green-900 hover:bg-green-800 disabled:bg-gray-800 disabled:text-gray-600 text-green-400 px-6 py-2 font-mono text-sm border border-green-700 disabled:border-gray-700"
            >
              [NEXT]
            </button>
          </div>
        )}

        {/* Step 2: Cocktail Selection */}
        {step === 'cocktail' && (
          <div className="space-y-4">
            <div className="text-green-500 mb-2 border-b border-green-900 pb-2">
              <span className="cursor-blink">█</span> STEP 2: SELECT LLM COCKTAIL
            </div>

            <div className="space-y-3">
              {Object.keys(cocktails).map((key) => (
                <label
                  key={key}
                  className={`block border p-3 cursor-pointer transition-colors ${
                    cocktail === key
                      ? 'border-[#7C3AED] bg-[#7C3AED]/10'
                      : 'border-green-900 hover:border-green-700'
                  }`}
                >
                  <div className="flex items-start gap-3">
                    <input
                      type="radio"
                      name="cocktail"
                      value={key}
                      checked={cocktail === key}
                      onChange={(e) => setCocktail(e.target.value)}
                      className="mt-1"
                    />
                    <div className="flex-1">
                      <div className="text-green-400 font-mono text-sm font-bold">
                        {key}
                      </div>
                      <div className="text-green-600 text-xs mt-1">
                        {cocktails[key].name}
                      </div>
                      <div className="text-green-700 text-xs mt-2 font-mono">
                        → {cocktails[key].count} models: {cocktails[key].models.join(', ')}
                      </div>
                    </div>
                  </div>
                </label>
              ))}
            </div>

            <div className="flex gap-4">
              <button
                onClick={() => setStep('confirm')}
                disabled={!isHealthy}
                className="bg-green-900 hover:bg-green-800 disabled:bg-gray-800 text-green-400 px-6 py-2 font-mono text-sm border border-green-700"
              >
                [NEXT]
              </button>
              <button
                onClick={() => setStep('query')}
                className="bg-gray-900 hover:bg-gray-800 text-green-400 px-6 py-2 font-mono text-sm border border-gray-700"
              >
                [BACK]
              </button>
            </div>
          </div>
        )}

        {/* Step 3: Confirm Phase */}
        {step === 'confirm' && (
          <div className="space-y-4">
            <div className="text-green-500 mb-2 border-b border-green-900 pb-2">
              <span className="cursor-blink">█</span> STEP 3: CONFIRMATION
            </div>
            <div className="border border-green-900 p-4">
              <div className="space-y-2 text-sm">
                <div>
                  <span className="text-green-600">QUERY:</span>
                  <div className="text-green-400 mt-1 pl-2">{query}</div>
                </div>
                <div className="mt-3">
                  <span className="text-green-600">COCKTAIL:</span>
                  <div className="text-[#7C3AED] mt-1 pl-2 font-bold">{cocktail}</div>
                  <div className="text-green-700 text-xs mt-1 pl-2">
                    → {cocktails[cocktail].count} models: {cocktails[cocktail].models.join(', ')}
                  </div>
                </div>
                <div className="mt-3">
                  <span className="text-green-600">ANALYSIS:</span>
                  <div className="text-green-400 mt-1 pl-2">R1 → R2 → R3 Synthesis</div>
                </div>
              </div>
            </div>

            <div className="flex gap-4">
              <button
                onClick={handleSubmit}
                disabled={!isHealthy}
                className="bg-green-900 hover:bg-green-800 disabled:bg-gray-800 text-green-400 px-6 py-2 font-mono text-sm border border-green-700"
              >
                [EXECUTE]
              </button>
              <button
                onClick={() => setStep('cocktail')}
                className="bg-gray-900 hover:bg-gray-800 text-green-400 px-6 py-2 font-mono text-sm border border-gray-700"
              >
                [BACK]
              </button>
            </div>
          </div>
        )}

        {/* Running Phase - Neon Status Display */}
        {step === 'running' && currentRun && !currentRun.completed && (
          <StatusDisplay run={currentRun} />
        )}

        {/* Results Phase - Neon Results Display */}
        {step === 'running' && currentRun && currentRun.completed && (
          <ResultsDisplay run={currentRun} onNewQuery={handleReset} />
        )}

        {/* Footer */}
        <div className="mt-8 pt-4 border-t border-green-900 text-green-600 text-xs">
          <div>UltrAI v0.1.0 | R1→R2→R3 Convergent Intelligence</div>
          <div className="mt-1">Backend: {isHealthy ? '● ONLINE' : '○ OFFLINE'}</div>
        </div>
      </div>
    </div>
  )
}

export default App
// Force cache bust 1760900478
