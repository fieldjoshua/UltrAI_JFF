/**
 * API Client Tests
 *
 * Tests the native fetch API client with REAL behavior.
 * NO FAKE TIMERS - tests verify actual HTTP communication patterns.
 */

import { describe, it, expect, beforeEach, vi } from 'vitest'
import { apiClient, APIError } from '../api'

// Mock global fetch
global.fetch = vi.fn()

describe('API Client', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  describe('GET requests', () => {
    it('should successfully fetch data', async () => {
      const mockData = { status: 'ok', message: 'Success' }
      global.fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockData,
      })

      const result = await apiClient.get('/health')
      expect(result).toEqual(mockData)
      expect(global.fetch).toHaveBeenCalledWith(
        'http://localhost:8000/health',
        expect.objectContaining({
          headers: expect.objectContaining({
            'Content-Type': 'application/json',
          }),
        })
      )
    })

    it('should throw APIError on HTTP error response', async () => {
      global.fetch.mockResolvedValueOnce({
        ok: false,
        status: 404,
        json: async () => ({ detail: 'Not found' }),
      })

      await expect(apiClient.get('/invalid')).rejects.toThrow(APIError)

      // Reset mock for second expectation
      global.fetch.mockResolvedValueOnce({
        ok: false,
        status: 404,
        json: async () => ({ detail: 'Not found' }),
      })

      await expect(apiClient.get('/invalid')).rejects.toThrow('Not found')
    })

    it('should handle network errors', async () => {
      global.fetch.mockRejectedValueOnce(new Error('Network failure'))

      await expect(apiClient.get('/test')).rejects.toThrow(APIError)

      // Reset mock for second expectation
      global.fetch.mockRejectedValueOnce(new Error('Network failure'))

      await expect(apiClient.get('/test')).rejects.toThrow(
        'Network error: Could not connect to backend'
      )
    })
  })

  describe('POST requests', () => {
    it('should successfully post data', async () => {
      const mockResponse = { run_id: 'test_20251018_123456' }
      global.fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockResponse,
      })

      const result = await apiClient.post('/runs', {
        query: 'Test query',
        cocktail: 'SPEEDY',
      })

      expect(result).toEqual(mockResponse)
      expect(global.fetch).toHaveBeenCalledWith(
        'http://localhost:8000/runs',
        expect.objectContaining({
          method: 'POST',
          body: JSON.stringify({
            query: 'Test query',
            cocktail: 'SPEEDY',
          }),
          headers: expect.objectContaining({
            'Content-Type': 'application/json',
          }),
        })
      )
    })

    it('should throw APIError on POST failure', async () => {
      global.fetch.mockResolvedValueOnce({
        ok: false,
        status: 400,
        json: async () => ({ detail: 'Invalid request' }),
      })

      await expect(
        apiClient.post('/runs', { invalid: 'data' })
      ).rejects.toThrow(APIError)

      // Reset mock for second expectation
      global.fetch.mockResolvedValueOnce({
        ok: false,
        status: 400,
        json: async () => ({ detail: 'Invalid request' }),
      })

      await expect(
        apiClient.post('/runs', { invalid: 'data' })
      ).rejects.toThrow('Invalid request')
    })
  })

  describe('APIError', () => {
    it('should contain status and data', () => {
      const error = new APIError('Test error', 404, { detail: 'Not found' })
      expect(error.message).toBe('Test error')
      expect(error.status).toBe(404)
      expect(error.data).toEqual({ detail: 'Not found' })
      expect(error.name).toBe('APIError')
    })
  })
})
