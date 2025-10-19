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

  // Fetch synthesis when component mounts or run changes
  useEffect(() => {
    if (run && run.completed && run.run_id) {
      fetchSynthesis(run.run_id)
    }
  }, [run])

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
    <div className="bg-white rounded-lg shadow-md p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold bg-gradient-to-r from-[#7C3AED] to-[#FF6B35] bg-clip-text text-transparent">
          ⚡ UltrAI Synthesis Complete
        </h2>
        <button
          onClick={onNewQuery}
          className="px-4 py-2 bg-gradient-to-r from-[#FF6B35] to-[#F97316] text-white rounded-lg hover:shadow-[0_0_20px_rgba(255,107,53,0.5)] transition-all font-semibold"
        >
          New Query →
        </button>
      </div>

      {/* Loading State */}
      {loading && (
        <div className="flex items-center justify-center py-8">
          <div className="animate-spin h-8 w-8 border-4 border-blue-500 border-t-transparent rounded-full"></div>
          <span className="ml-3 text-gray-600">Loading synthesis...</span>
        </div>
      )}

      {/* Error State */}
      {error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <div className="font-semibold text-red-900">
            Failed to Load Synthesis
          </div>
          <div className="text-sm text-red-700 mt-1">{error}</div>
          <button
            onClick={() => fetchSynthesis(run.run_id)}
            className="mt-3 text-sm text-red-700 underline hover:text-red-900"
          >
            Try Again
          </button>
        </div>
      )}

      {/* Synthesis Output */}
      {synthesis && (
        <div className="space-y-4">
          {/* Synthesis Text */}
          <div className="bg-gradient-to-br from-[#7C3AED]/5 via-[#6366F1]/5 to-[#FF6B35]/5 rounded-lg p-6 border-2 border-[#7C3AED] shadow-[0_0_25px_rgba(124,58,237,0.15)]">
            <div className="text-sm font-bold text-[#7C3AED] mb-3 uppercase tracking-wide">
              🎯 Final Synthesis
            </div>
            <div className="prose prose-sm max-w-none text-gray-900 whitespace-pre-wrap leading-relaxed">
              {synthesis.text}
            </div>
          </div>

          {/* Metadata */}
          {synthesis.stats && (
            <div className="grid grid-cols-2 gap-4">
              <div className="bg-gray-50 rounded-lg p-4">
                <div className="text-xs text-gray-600">Active Models</div>
                <div className="text-2xl font-bold text-gray-900 mt-1">
                  {synthesis.stats.active_count}
                </div>
              </div>
              <div className="bg-gray-50 rounded-lg p-4">
                <div className="text-xs text-gray-600">Meta Drafts</div>
                <div className="text-2xl font-bold text-gray-900 mt-1">
                  {synthesis.stats.meta_count}
                </div>
              </div>
            </div>
          )}

          {/* Response Time */}
          {synthesis.ms && (
            <div className="text-xs text-gray-500">
              Synthesis generated in {synthesis.ms}ms by{' '}
              <code className="bg-gray-100 px-1 py-0.5 rounded">
                {synthesis.model}
              </code>
            </div>
          )}
        </div>
      )}

      {/* Download Round Outputs */}
      <div className="pt-4 border-t space-y-3">
        <div className="text-sm font-medium text-gray-700 mb-2">
          Download Round Outputs
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
          {/* R1 INITIAL Download */}
          <a
            href={`${import.meta.env.VITE_API_URL || ''}/runs/${
              run.run_id
            }/artifacts`}
            download="initial_round.json"
            className="inline-flex items-center justify-center px-4 py-3 bg-gradient-to-r from-[#7C3AED] to-[#6366F1] text-white rounded-lg hover:shadow-[0_0_20px_rgba(124,58,237,0.5)] transition-all font-semibold"
          >
            <svg
              className="w-5 h-5 mr-2"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M9 19l3 3m0 0l3-3m-3 3V10"
              />
            </svg>
            R1 - Initial Responses
          </a>

          {/* R2 META Download */}
          <a
            href={`${import.meta.env.VITE_API_URL || ''}/runs/${
              run.run_id
            }/artifacts`}
            download="meta_round.json"
            className="inline-flex items-center justify-center px-4 py-3 bg-gradient-to-r from-[#FF6B35] to-[#F97316] text-white rounded-lg hover:shadow-[0_0_20px_rgba(255,107,53,0.5)] transition-all font-semibold"
          >
            <svg
              className="w-5 h-5 mr-2"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M9 19l3 3m0 0l3-3m-3 3V10"
              />
            </svg>
            R2 - Meta Revisions
          </a>
        </div>

        {/* All Artifacts Link */}
        <div className="text-center pt-2">
          <a
            href={`${import.meta.env.VITE_API_URL || ''}/runs/${
              run.run_id
            }/artifacts`}
            target="_blank"
            rel="noopener noreferrer"
            className="text-sm text-gray-600 hover:text-gray-900 underline"
          >
            View all artifacts →
          </a>
        </div>
      </div>
    </div>
  )
}
