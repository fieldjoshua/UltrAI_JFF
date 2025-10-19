/**
 * UltrAI Terminal CLI Interface
 *
 * Simulates a terminal/CLI experience for LLM synthesis.
 * Low-res, fast, developer-focused aesthetic.
 */

import { useState } from 'react'
import { useUltrAI } from './hooks/useUltrAI'
import { useHealth } from './hooks/useHealth'
import { StatusDisplay } from './components/StatusDisplay'
import { ResultsDisplay } from './components/ResultsDisplay'

function App() {
  const [query, setQuery] = useState('')
  const [cocktail, setCocktail] = useState('SPEEDY')
  const [step, setStep] = useState('input') // input, confirm, running, results

  const { isHealthy } = useHealth()
  const { isLoading, currentRun, submitQuery } = useUltrAI()

  const cocktails = {
    LUXE: 'Flagship premium models',
    PREMIUM: 'High-quality balanced',
    SPEEDY: 'Fast response optimized',
    BUDGET: 'Cost-effective quality',
    DEPTH: 'Deep reasoning focus',
  }

  const cocktailDetails = {
    LUXE: 'gpt-4o + claude-sonnet-4.5 + gemini-2.0',
    PREMIUM: 'claude-3.7 + chatgpt-4o + llama-3.3',
    SPEEDY: 'gpt-4o-mini + claude-haiku + gemini-flash',
    BUDGET: 'gpt-3.5 + gemini-flash + qwen-72b',
    DEPTH: 'claude-3.7 + gpt-4o + llama-3.3',
  }

  const handleSubmit = async () => {
    if (!query.trim()) return
    setStep('running')
    await submitQuery(query, cocktail)
  }

  const handleReset = () => {
    setQuery('')
    setCocktail('SPEEDY')
    setStep('input')
  }

  return (
    <div className="min-h-screen p-4 terminal-scan">
      <div className="max-w-4xl mx-auto">
        {/* ASCII Logo */}
        <pre className="text-green-500 terminal-glow text-xs mb-6">
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

        {/* Input Phase */}
        {step === 'input' && (
          <div className="space-y-4">
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

            <div>
              <div className="text-green-500 mb-2">
                <span className="text-green-400">$</span> ultrai --cocktail
              </div>
              <select
                value={cocktail}
                onChange={(e) => setCocktail(e.target.value)}
                className="w-full bg-black border border-green-900 text-green-400 p-3 font-mono text-sm focus:outline-none focus:border-green-500"
              >
                {Object.keys(cocktails).map((key) => (
                  <option key={key} value={key}>
                    {key} - {cocktails[key]}
                  </option>
                ))}
              </select>
              <div className="mt-2 text-green-600 text-xs pl-2">
                → {cocktailDetails[cocktail]}
              </div>
            </div>

            <button
              onClick={() => setStep('confirm')}
              disabled={!query.trim() || !isHealthy}
              className="bg-green-900 hover:bg-green-800 disabled:bg-gray-800 disabled:text-gray-600 text-green-400 px-6 py-2 font-mono text-sm border border-green-700 disabled:border-gray-700"
            >
              [NEXT]
            </button>
          </div>
        )}

        {/* Confirm Phase */}
        {step === 'confirm' && (
          <div className="space-y-4">
            <div className="border border-green-900 p-4">
              <div className="text-green-500 mb-2">
                <span className="cursor-blink">█</span> CONFIRMATION
              </div>
              <div className="space-y-2 text-sm">
                <div>
                  <span className="text-green-600">QUERY:</span> {query}
                </div>
                <div>
                  <span className="text-green-600">COCKTAIL:</span> {cocktail}
                </div>
                <div>
                  <span className="text-green-600">ANALYSIS:</span> R1 → R2 → R3 Synthesis
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
                onClick={() => setStep('input')}
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
