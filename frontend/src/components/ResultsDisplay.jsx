/**
 * ResultsDisplay Component
 *
 * Shows final synthesis results when run completes:
 * - Final synthesis text from R3
 * - Download artifacts button
 * - Option to start new query
 */

import { useState } from 'react'
import { apiClient } from '../services/api'

export function ResultsDisplay({ run, onNewQuery }) {
  const [synthesis, setSynthesis] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  // Fetch synthesis when component mounts or run changes
  useState(() => {
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
        <h2 className="text-2xl font-bold text-gray-900">
          UltrAI Synthesis Complete
        </h2>
        <button
          onClick={onNewQuery}
          className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
        >
          New Query
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
          <div className="bg-gradient-to-br from-blue-50 to-indigo-50 rounded-lg p-6 border border-blue-200">
            <div className="text-sm font-semibold text-blue-900 mb-3">
              Final Synthesis
            </div>
            <div className="prose prose-sm max-w-none text-gray-800 whitespace-pre-wrap">
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

      {/* Download Artifacts */}
      <div className="pt-4 border-t">
        <a
          href={`/api/runs/${run.run_id}/artifacts`}
          target="_blank"
          rel="noopener noreferrer"
          className="inline-flex items-center px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition-colors"
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
              d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
            />
          </svg>
          Download All Artifacts
        </a>
      </div>
    </div>
  )
}
