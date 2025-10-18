/**
 * useHealth Hook Tests
 *
 * Tests backend health checking on mount.
 * NO FAKE TIMERS - tests verify actual component lifecycle behavior.
 */

import { describe, it, expect, beforeEach, vi } from 'vitest'
import { renderHook, waitFor } from '@testing-library/react'
import { useHealth } from '../useHealth'
import * as api from '../../services/api'

vi.mock('../../services/api', () => ({
  apiClient: {
    get: vi.fn(),
  },
}))

describe('useHealth Hook', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('should check health on mount', async () => {
    api.apiClient.get.mockResolvedValueOnce({ status: 'ok' })

    const { result } = renderHook(() => useHealth())

    expect(result.current.isLoading).toBe(true)

    await waitFor(() => {
      expect(result.current.isLoading).toBe(false)
      expect(result.current.isHealthy).toBe(true)
      expect(result.current.error).toBeNull()
    })

    expect(api.apiClient.get).toHaveBeenCalledWith('/health')
  })

  it('should handle health check failure', async () => {
    api.apiClient.get.mockRejectedValueOnce(new Error('Connection failed'))

    const { result } = renderHook(() => useHealth())

    await waitFor(() => {
      expect(result.current.isLoading).toBe(false)
      expect(result.current.isHealthy).toBe(false)
      expect(result.current.error).toBe('Connection failed')
    })
  })

  it('should handle non-ok status', async () => {
    api.apiClient.get.mockResolvedValueOnce({ status: 'degraded' })

    const { result } = renderHook(() => useHealth())

    await waitFor(() => {
      expect(result.current.isHealthy).toBe(false)
      expect(result.current.error).toBeNull()
    })
  })
})
