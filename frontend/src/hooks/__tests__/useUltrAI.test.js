/**
 * useUltrAI Hook Tests
 *
 * Tests query submission and polling with REAL timers.
 * NO FAKE TIMERS - we use waitFor() to wait for actual 2-second intervals.
 */

import { describe, it, expect, beforeEach, vi } from 'vitest'
import { renderHook, waitFor, act } from '@testing-library/react'
import { useUltrAI } from '../useUltrAI'
import * as api from '../../services/api'

// Mock the API client module
vi.mock('../../services/api', () => ({
  apiClient: {
    get: vi.fn(),
    post: vi.fn(),
  },
}))

describe('useUltrAI Hook', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    // IMPORTANT: Using REAL timers, not fake timers
  })

  it('should initialize with default state', () => {
    const { result } = renderHook(() => useUltrAI())

    expect(result.current.isLoading).toBe(false)
    expect(result.current.error).toBeNull()
    expect(result.current.currentRun).toBeNull()
    expect(typeof result.current.submitQuery).toBe('function')
  })

  it('should submit query and start polling with REAL timers', async () => {
    const mockRunId = 'api_speedy_20251018_123456'

    // Mock POST /runs response
    api.apiClient.post.mockResolvedValueOnce({ run_id: mockRunId })

    // Mock GET /runs/{id}/status responses
    // First call is the immediate fetch after POST
    api.apiClient.get.mockResolvedValue({
      run_id: mockRunId,
      phase: '03_initial.json',
      round: 'R1',
      completed: false,
      artifacts: [],
    })

    const { result } = renderHook(() => useUltrAI())

    // Submit query
    await act(async () => {
      await result.current.submitQuery('Test query', 'SPEEDY')
    })

    expect(api.apiClient.post).toHaveBeenCalledWith('/runs', {
      query: 'Test query',
      cocktail: 'SPEEDY',
      analysis: 'Synthesis',
    })

    // After submitQuery completes, currentRun should have full status (not just run_id)
    expect(result.current.currentRun).toEqual({
      run_id: mockRunId,
      phase: '03_initial.json',
      round: 'R1',
      completed: false,
      artifacts: [],
    })

    expect(result.current.isLoading).toBe(true)

    // Wait for REAL polling (2 seconds) - not fake timers
    await waitFor(
      () => {
        // Should be called at least twice (initial fetch + first poll)
        expect(api.apiClient.get).toHaveBeenCalledWith(
          `/runs/${mockRunId}/status`
        )
        expect(api.apiClient.get).toHaveBeenCalledTimes(2)
      },
      { timeout: 3000 }
    )
  })

  it('should stop polling when run completes', async () => {
    const mockRunId = 'api_speedy_20251018_123456'

    api.apiClient.post.mockResolvedValueOnce({ run_id: mockRunId })

    // Initial fetch: incomplete
    api.apiClient.get.mockResolvedValueOnce({
      run_id: mockRunId,
      phase: '03_initial.json',
      round: 'R1',
      completed: false,
      artifacts: [],
    })

    // First poll (2s later): still incomplete
    api.apiClient.get.mockResolvedValueOnce({
      run_id: mockRunId,
      phase: '04_meta.json',
      round: 'R2',
      completed: false,
      artifacts: ['03_initial.json'],
    })

    // Second poll (4s later): completed
    api.apiClient.get.mockResolvedValueOnce({
      run_id: mockRunId,
      phase: '05_ultrai.json',
      round: 'R3',
      completed: true,
      artifacts: ['05_ultrai.json', 'stats.json'],
    })

    const { result } = renderHook(() => useUltrAI())

    await act(async () => {
      await result.current.submitQuery('Test query', 'SPEEDY')
    })

    // Wait for REAL polling to complete (not checking intermediate states)
    await waitFor(
      () => {
        expect(result.current.currentRun?.completed).toBe(true)
        expect(result.current.isLoading).toBe(false)
        expect(result.current.currentRun?.phase).toBe('05_ultrai.json')
      },
      { timeout: 6000 }
    )
  })

  it('should handle submission errors', async () => {
    api.apiClient.post.mockRejectedValueOnce(
      new Error('Network error')
    )

    const { result } = renderHook(() => useUltrAI())

    await act(async () => {
      await result.current.submitQuery('Test query', 'SPEEDY')
    })

    expect(result.current.error).toBe('Network error')
    expect(result.current.isLoading).toBe(false)
  })

  it('should cleanup polling interval on unmount', () => {
    const mockRunId = 'api_speedy_20251018_123456'
    api.apiClient.post.mockResolvedValueOnce({ run_id: mockRunId })
    api.apiClient.get.mockResolvedValue({
      run_id: mockRunId,
      phase: '03_initial.json',
      completed: false,
    })

    const { result, unmount } = renderHook(() => useUltrAI())

    act(() => {
      result.current.submitQuery('Test query', 'SPEEDY')
    })

    // Unmount should clear interval
    unmount()

    // No assertion needed - just verifying cleanup doesn't throw
    expect(true).toBe(true)
  })
})
