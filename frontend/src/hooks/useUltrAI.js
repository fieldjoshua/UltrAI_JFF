import { useState, useCallback, useRef } from 'react'
import { apiClient } from '../services/api'

export function useUltrAI() {
  const [currentRun, setCurrentRun] = useState(null)
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState(null)
  const pollIntervalRef = useRef(null)

  const stopPolling = useCallback(() => {
    if (pollIntervalRef.current) {
      clearInterval(pollIntervalRef.current)
      pollIntervalRef.current = null
    }
  }, [])

  const submitQuery = useCallback(
    async (query, cocktail = 'SPEEDY') => {
      setIsLoading(true)
      setError(null)
      stopPolling()

      try {
        // Start new run
        const result = await apiClient.post('/runs', { query, cocktail })
        setCurrentRun({
          run_id: result.run_id,
          phase: null,
          round: null,
          completed: false,
          artifacts: [],
        })

        // Start polling status
        pollIntervalRef.current = setInterval(async () => {
          try {
            const status = await apiClient.get(`/runs/${result.run_id}/status`)
            setCurrentRun(status)

            if (status.completed) {
              stopPolling()
              setIsLoading(false)
            }
          } catch (pollError) {
            console.error('Polling error:', pollError)
            // Continue polling despite errors (backend might be processing)
          }
        }, 2000)

        return result.run_id
      } catch (err) {
        setError(err.message)
        setIsLoading(false)
        stopPolling()
        throw err
      }
    },
    [stopPolling]
  )

  return { submitQuery, currentRun, isLoading, error, stopPolling }
}