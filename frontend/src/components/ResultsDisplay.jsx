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
  const [modelTimes, setModelTimes] = useState([])  // Persist R1/R2 response times

  // Fetch synthesis when component mounts or run changes
  useEffect(() => {
    if (run && run.completed && run.run_id) {
      fetchSynthesis(run.run_id)
      fetchModelTimes(run.run_id)  // Load model response times
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

  const fetchModelTimes = async (runId) => {
    try {
      // Fetch R1 and R2 artifacts to extract model response times
      const r1 = await apiClient.get(`/runs/${runId}/artifacts/03_initial.json`)
      const r2 = await apiClient.get(`/runs/${runId}/artifacts/04_meta.json`)

      const times = []

      // Extract R1 times
      if (Array.isArray(r1)) {
        r1.forEach(resp => {
          if (resp.model && resp.ms) {
            times.push({ round: 'R1', model: resp.model, ms: resp.ms })
          }
        })
      }

      // Extract R2 times
      if (Array.isArray(r2)) {
        r2.forEach(resp => {
          if (resp.model && resp.ms) {
            times.push({ round: 'R2', model: resp.model, ms: resp.ms })
          }
        })
      }

      setModelTimes(times)
    } catch (err) {
      // Silently fail - times are supplementary info
      console.error('Failed to fetch model times:', err)
    }
  }

  // Format artifact data as readable text with spacing
  const formatArtifactAsText = (artifact, title) => {
    if (!Array.isArray(artifact)) return ''

    let text = `${title}\n`
    text += '='.repeat(60) + '\n\n'

    artifact.forEach((item, index) => {
      text += `MODEL ${index + 1}: ${item.model}\n`
      text += '-'.repeat(60) + '\n'
      text += `${item.text}\n\n`
      if (item.ms) {
        text += `Response Time: ${item.ms}ms\n`
      }
      text += '\n' + '='.repeat(60) + '\n\n'
    })

    return text
  }

  // Download formatted TXT file
  const downloadAsText = async (artifactPath, filename, title) => {
    try {
      const data = await apiClient.get(`/runs/${run.run_id}/artifacts/${artifactPath}`)
      const formattedText = formatArtifactAsText(data, title)

      const blob = new Blob([formattedText], { type: 'text/plain' })
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = filename
      document.body.appendChild(a)
      a.click()
      document.body.removeChild(a)
      window.URL.revokeObjectURL(url)
    } catch (err) {
      console.error('Download failed:', err)
    }
  }

  // Open formatted artifact in new tab
  const openFormattedArtifact = async (artifactPath, title) => {
    try {
      const data = await apiClient.get(`/runs/${run.run_id}/artifacts/${artifactPath}`)
      const formattedText = formatArtifactAsText(data, title)

      const newWindow = window.open()
      newWindow.document.write('<pre style="font-family: monospace; white-space: pre-wrap; padding: 20px;">')
      newWindow.document.write(formattedText)
      newWindow.document.write('</pre>')
    } catch (err) {
      console.error('Failed to open artifact:', err)
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

          {/* Persisted Model Response Times */}
          {modelTimes.length > 0 && (
            <div className="border-t border-green-900 pt-3 mt-3">
              <div className="text-green-500 text-sm font-mono mb-2">MODEL_RESPONSE_TIMES:</div>
              <div className="grid grid-cols-2 gap-2 text-xs font-mono">
                {modelTimes.map((item, idx) => (
                  <div key={idx} className="text-green-600">
                    <span className="text-[#7C3AED]">[{item.round}]</span> {item.model.split('/')[1] || item.model}: {item.ms}ms
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}

      {/* Download Options */}
      <div className="border-t border-green-900 pt-4 space-y-3">
        <div className="text-green-500 text-sm font-mono">DOWNLOAD_OUTPUTS:</div>

        {/* R1 Downloads */}
        <div className="space-y-1">
          <div className="text-[#7C3AED] font-mono text-xs">→ R1 Initial Responses:</div>
          <div className="pl-4 space-y-1">
            <button
              onClick={() => openFormattedArtifact('03_initial.json', 'R1 INITIAL RESPONSES')}
              className="block text-[#6366F1] hover:text-[#7C3AED] font-mono text-xs underline"
            >
              [VIEW FORMATTED] Open in new tab
            </button>
            <button
              onClick={() => downloadAsText('03_initial.json', 'r1_initial_responses.txt', 'R1 INITIAL RESPONSES')}
              className="block text-[#6366F1] hover:text-[#7C3AED] font-mono text-xs underline"
            >
              [DOWNLOAD TXT] Formatted with separators
            </button>
            <a
              href={`${import.meta.env.VITE_API_URL || 'https://ultrai-jff.onrender.com'}/runs/${run.run_id}/artifacts/03_initial.json`}
              download="03_initial.json"
              className="block text-[#6366F1] hover:text-[#7C3AED] font-mono text-xs underline"
            >
              [DOWNLOAD JSON] Raw data
            </a>
          </div>
        </div>

        {/* R2 Downloads */}
        <div className="space-y-1">
          <div className="text-[#FF6B35] font-mono text-xs">→ R2 Meta Revisions:</div>
          <div className="pl-4 space-y-1">
            <button
              onClick={() => openFormattedArtifact('04_meta.json', 'R2 META REVISIONS')}
              className="block text-[#F97316] hover:text-[#FF6B35] font-mono text-xs underline"
            >
              [VIEW FORMATTED] Open in new tab
            </button>
            <button
              onClick={() => downloadAsText('04_meta.json', 'r2_meta_revisions.txt', 'R2 META REVISIONS')}
              className="block text-[#F97316] hover:text-[#FF6B35] font-mono text-xs underline"
            >
              [DOWNLOAD TXT] Formatted with separators
            </button>
            <a
              href={`${import.meta.env.VITE_API_URL || 'https://ultrai-jff.onrender.com'}/runs/${run.run_id}/artifacts/04_meta.json`}
              download="04_meta.json"
              className="block text-[#F97316] hover:text-[#FF6B35] font-mono text-xs underline"
            >
              [DOWNLOAD JSON] Raw data
            </a>
          </div>
        </div>

        {/* All Artifacts */}
        <div className="pt-2">
          <a
            href={`${import.meta.env.VITE_API_URL || ''}/runs/${run.run_id}/artifacts`}
            target="_blank"
            rel="noopener noreferrer"
            className="block text-green-600 hover:text-green-500 font-mono text-xs underline"
          >
            → View all artifacts (JSON directory)
          </a>
        </div>
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
