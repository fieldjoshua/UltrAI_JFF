import { useState, useEffect } from 'react'
import { apiClient } from '../services/api'

export function useHealth() {
  const [isHealthy, setIsHealthy] = useState(false)
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    async function checkHealth() {
      try {
        const result = await apiClient.get('/health')
        setIsHealthy(result.status === 'ok')
        setError(null)
      } catch (err) {
        setIsHealthy(false)
        setError(err.message)
      } finally {
        setIsLoading(false)
      }
    }

    checkHealth()
  }, [])

  return { isHealthy, isLoading, error }
}