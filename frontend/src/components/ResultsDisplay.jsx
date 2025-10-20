/**
 * ResultsDisplay Component
 *
 * Shows final synthesis results when run completes:
 * - Final synthesis text from R3
 * - Download artifacts button
 * - Option to start new query
 */

import { useState, useEffect } from 'react'
import { apiClient } from '../services/api'

export function ResultsDisplay({ run, onNewQuery }) {
  const [synthesis, setSynthesis] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [displayedText, setDisplayedText] = useState('')
  const [isTyping, setIsTyping] = useState(false)

  // Fetch synthesis when component mounts or run changes
  useEffect(() => {
    if (run && run.completed && run.run_id) {
      fetchSynthesis(run.run_id)
    }
  }, [run])

  // Terminal typing animation effect
  useEffect(() => {
    if (!synthesis || !synthesis.text) return

    setIsTyping(true)
    setDisplayedText('')

    const text = synthesis.text
    let currentIndex = 0

    const typingInterval = setInterval(() => {
      if (currentIndex < text.length) {
        // Type 3-5 characters at a time for faster animation
        const chunkSize = Math.floor(Math.random() * 3) + 3
        setDisplayedText(text.substring(0, currentIndex + chunkSize))
        currentIndex += chunkSize
      } else {
        setDisplayedText(text)
        setIsTyping(false)
        clearInterval(typingInterval)
      }
    }, 20) // 20ms interval for smooth typing

    return () => clearInterval(typingInterval)
  }, [synthesis])

  const fetchSynthesis = async (runId) => {
    try {
      setLoading(true)
      setError(null)
      const result = await apiClient.get(`/runs/${runId}/artifacts/05_ultrai.json`)
      setSynthesis(result)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  if (!run || !run.completed) return null

  return (
    <div className="space-y-4">
      {/* Completion Header */}
      <div className="text-green-500 border-b border-green-900 pb-2">
        <span className="cursor-blink">█</span>{' '}
        <span className="text-[#FF6B35] terminal-glow">⚡ SYNTHESIS COMPLETE</span>
      </div>

      {/* Loading State */}
      {loading && (
        <div className="text-green-600 text-sm font-mono">
          → Loading synthesis data...
        </div>
      )}

      {/* Error State */}
      {error && (
        <div className="border border-red-500 p-3">
          <div className="text-red-500 font-mono text-sm">
            <span className="cursor-blink">█</span> ERROR: Failed to load synthesis
          </div>
          <div className="text-red-400 text-xs mt-1 font-mono">{error}</div>
          <button
            onClick={() => fetchSynthesis(run.run_id)}
            className="text-red-500 underline text-xs mt-2 font-mono hover:text-red-400"
          >
            [RETRY]
          </button>
        </div>
      )}

      {/* Synthesis Output */}
      {synthesis && (
        <div className="space-y-4">
          {/* Synthesis Text */}
          <div className="border border-[#7C3AED] p-4">
            <div className="text-[#7C3AED] font-mono text-sm mb-3 terminal-glow">
              OUTPUT:
            </div>
            <div className="text-green-400 font-mono text-sm whitespace-pre-wrap leading-relaxed">
              {displayedText}
              {isTyping && <span className="cursor-blink text-[#7C3AED]">█</span>}
            </div>
          </div>

          {/* Metadata */}
          {synthesis.stats && (
            <div className="grid grid-cols-2 gap-4 text-sm font-mono">
              <div>
                <span className="text-green-500">ACTIVE_MODELS:</span>{' '}
                <span className="text-[#7C3AED]">{synthesis.stats.active_count}</span>
              </div>
              <div>
                <span className="text-green-500">META_DRAFTS:</span>{' '}
                <span className="text-[#6366F1]">{synthesis.stats.meta_count}</span>
              </div>
            </div>
          )}

          {/* Response Time */}
          {synthesis.ms && (
            <div className="text-green-600 text-xs font-mono">
              → Generated in {synthesis.ms}ms by {synthesis.model}
            </div>
          )}
        </div>
      )}

      {/* Download Options */}
      <div className="border-t border-green-900 pt-4 space-y-2">
        <div className="text-green-500 text-sm font-mono">DOWNLOAD_OUTPUTS:</div>

        {/* R1 Download */}
        <a
          href={`${import.meta.env.VITE_API_URL || 'https://ultrai-jff.onrender.com'}/runs/${run.run_id}/artifacts/03_initial.json`}
          download="03_initial.json"
          className="block text-[#7C3AED] hover:text-[#6366F1] font-mono text-sm terminal-glow"
        >
          → [R1] Initial Responses
        </a>

        {/* R2 Download */}
        <a
          href={`${import.meta.env.VITE_API_URL || 'https://ultrai-jff.onrender.com'}/runs/${run.run_id}/artifacts/04_meta.json`}
          download="04_meta.json"
          className="block text-[#FF6B35] hover:text-[#F97316] font-mono text-sm terminal-glow"
        >
          → [R2] Meta Revisions
        </a>

        {/* All Artifacts */}
        <a
          href={`${import.meta.env.VITE_API_URL || ''}/runs/${run.run_id}/artifacts`}
          target="_blank"
          rel="noopener noreferrer"
          className="block text-green-600 hover:text-green-500 font-mono text-xs"
        >
          → View all artifacts
        </a>
      </div>

      {/* New Query Button */}
      <div className="pt-4">
        <button
          onClick={onNewQuery}
          className="bg-green-900 hover:bg-green-800 text-green-400 px-6 py-2 font-mono text-sm border border-green-700"
        >
          [NEW QUERY]
        </button>
      </div>
    </div>
  )
}
