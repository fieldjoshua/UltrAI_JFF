/**
 * useUltrAI Hook - Main Query Submission and Run Tracking
 *
 * Handles:
 * - Submitting queries to backend (POST /runs)
 * - Polling run status every 2 seconds
 * - Tracking current run state (phase, round, completion)
 * - Automatic cleanup of polling interval
 */

import { useState, useEffect, useRef } from 'react'
import { apiClient } from '../services/api'

export function useUltrAI() {
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState(null)
  const [currentRun, setCurrentRun] = useState(null)
  const pollIntervalRef = useRef(null)

  /**
   * Submit a query to start a new UltrAI run
   * @param {string} query - User query
   * @param {string} cocktail - Cocktail name (PREMIUM, SPEEDY, BUDGET, DEPTH, LUXE)
   * @returns {Promise<void>}
   */
  const submitQuery = async (query, cocktail) => {
    try {
      setIsLoading(true)
      setError(null)

      // Start the run
      const result = await apiClient.post('/runs', {
        query,
        cocktail,
        analysis: 'Synthesis',
      })

      // Immediately fetch the first status instead of using POST result
      // This ensures currentRun has all fields (phase, round, completed, artifacts)
      try {
        const initialStatus = await apiClient.get(`/runs/${result.run_id}/status`)
        setCurrentRun(initialStatus)
      } catch (statusError) {
        // Fallback to POST result if status fetch fails
        console.error('Initial status fetch failed:', statusError)
        setCurrentRun(result)
      }

      // Start polling status every 2 seconds (REAL timers, not fake)
      pollIntervalRef.current = setInterval(async () => {
        try {
          const status = await apiClient.get(`/runs/${result.run_id}/status`)
          setCurrentRun(status)

          if (status.completed) {
            clearInterval(pollIntervalRef.current)
            setIsLoading(false)
          }
        } catch (pollError) {
          console.error('Polling error:', pollError)
          // Continue polling despite errors
        }
      }, 2000)
    } catch (err) {
      setError(err.message)
      setIsLoading(false)
    }
  }

  // Cleanup polling on unmount
  useEffect(() => {
    return () => {
      if (pollIntervalRef.current) {
        clearInterval(pollIntervalRef.current)
      }
    }
  }, [])

  return {
    isLoading,
    error,
    currentRun,
    submitQuery,
  }
}
