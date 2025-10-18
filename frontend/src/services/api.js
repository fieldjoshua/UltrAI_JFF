/**
 * API Client - Native Fetch Implementation
 *
 * Provides HTTP communication with UltrAI backend using native fetch API.
 * No external dependencies (axios, etc.) - keeps bundle small and simple.
 */

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

/**
 * Custom error class for API failures
 * @property {number} status - HTTP status code
 * @property {object} data - Response data (if available)
 */
class APIError extends Error {
  constructor(message, status, data) {
    super(message)
    this.name = 'APIError'
    this.status = status
    this.data = data
  }
}

/**
 * Fetch wrapper with error handling and JSON parsing
 * @param {string} url - Full URL to fetch
 * @param {object} options - Fetch options
 * @returns {Promise<object>} Parsed JSON response
 * @throws {APIError} On HTTP errors or network failures
 */
async function fetchWithErrorHandling(url, options = {}) {
  try {
    const response = await fetch(url, {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
    })

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}))
      throw new APIError(
        errorData.detail || `Request failed with status ${response.status}`,
        response.status,
        errorData
      )
    }

    return await response.json()
  } catch (error) {
    if (error instanceof APIError) throw error
    throw new APIError(
      'Network error: Could not connect to backend',
      0,
      { originalError: error.message }
    )
  }
}

/**
 * API client with GET and POST methods
 */
export const apiClient = {
  /**
   * GET request
   * @param {string} endpoint - API endpoint (e.g., '/health')
   * @returns {Promise<object>} Response data
   */
  get: (endpoint) => fetchWithErrorHandling(`${API_BASE_URL}${endpoint}`),

  /**
   * POST request
   * @param {string} endpoint - API endpoint (e.g., '/runs')
   * @param {object} body - Request body
   * @returns {Promise<object>} Response data
   */
  post: (endpoint, body) =>
    fetchWithErrorHandling(`${API_BASE_URL}${endpoint}`, {
      method: 'POST',
      body: JSON.stringify(body),
    }),
}

export { APIError }
