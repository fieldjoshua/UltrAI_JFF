const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

class APIError extends Error {
  constructor(message, status, data) {
    super(message)
    this.name = 'APIError'
    this.status = status
    this.data = data
  }
}

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
    if (error instanceof APIError) {
      throw error
    }
    throw new APIError(
      'Network error: Could not connect to backend',
      0,
      { originalError: error.message }
    )
  }
}

export const apiClient = {
  get: (endpoint) => fetchWithErrorHandling(`${API_BASE_URL}${endpoint}`),

  post: (endpoint, body) =>
    fetchWithErrorHandling(`${API_BASE_URL}${endpoint}`, {
      method: 'POST',
      body: JSON.stringify(body),
    }),
}

export { APIError }