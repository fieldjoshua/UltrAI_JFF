# PR 21 — API Integration Layer
# AGENT INSTRUCTIONS (General-Purpose Agent)

## Overview

You are the **Builder** for PR 21: API Integration Layer. Your role is to create the frontend service layer that connects the React frontend to the FastAPI backend at `https://ultrai-jff.onrender.com` (production) and `http://localhost:8000` (development).

**Division of Labor**:
- **You (General-Purpose Agent)**: Build all API integration files
- **Native Cursor Editor**: Test API integration with real backend (QA Lead)
- **User**: Approve visual verification and merge PR

## Your Task: Create 7 Files

You will create the following files exactly as specified below. Do NOT modify any existing files unless explicitly instructed.

---

## File 1: `frontend/src/services/api.js`

**Purpose**: Centralized API client with fetch wrapper and error handling

```javascript
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
```

---

## File 2: `frontend/src/hooks/useHealth.js`

**Purpose**: React hook for backend health checks

```javascript
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
```

---

## File 3: `frontend/src/hooks/useUltrAI.js`

**Purpose**: React hook for submitting queries and tracking runs

```javascript
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
```

---

## File 4: `frontend/src/hooks/useCocktails.js`

**Purpose**: React hook for fetching cocktail options

```javascript
import { useState, useEffect } from 'react'

const COCKTAILS = ['PREMIUM', 'SPEEDY', 'BUDGET', 'DEPTH']

export function useCocktails() {
  const [cocktails, setCocktails] = useState(COCKTAILS)
  const [isLoading, setIsLoading] = useState(false)

  useEffect(() => {
    // Currently returns static list
    // Future: could fetch from backend GET /cocktails endpoint
    setCocktails(COCKTAILS)
    setIsLoading(false)
  }, [])

  return { cocktails, isLoading }
}
```

---

## File 5: `frontend/.env.local`

**Purpose**: Local development environment configuration

```bash
VITE_API_URL=http://localhost:8000
```

**CRITICAL**: This file should be git-ignored (already in .gitignore)

---

## File 6: `frontend/.env.production`

**Purpose**: Production environment configuration

```bash
VITE_API_URL=https://ultrai-jff.onrender.com
```

---

## File 7: `frontend/.gitignore` (UPDATE)

**Purpose**: Ensure .env.local is never committed

**Action**: Add this line to `frontend/.gitignore` if not already present:

```
.env.local
```

---

## After Creating All Files

Once all 7 files are created, report back with the following message:

```
✅ PR 21 API Integration Layer - Build Complete

Files Created:
1. frontend/src/services/api.js - API client with fetch wrapper (64 lines)
2. frontend/src/hooks/useHealth.js - Health check hook (27 lines)
3. frontend/src/hooks/useUltrAI.js - Query submission and run tracking hook (62 lines)
4. frontend/src/hooks/useCocktails.js - Cocktail options hook (18 lines)
5. frontend/.env.local - Development environment config (git-ignored)
6. frontend/.env.production - Production environment config
7. frontend/.gitignore - Updated to exclude .env.local

Total Lines: 171 lines of integration code

Key Features:
- Native fetch API (zero external dependencies)
- Custom APIError class with status codes
- Automatic 2-second polling for run status
- Environment-based API URL configuration
- Proper cleanup on unmount (polling intervals cleared)

Ready for Testing Phase.
Handoff to native Cursor editor (QA Lead) for integration testing.
```

---

## Important Notes

1. **No UI changes**: This PR only creates the API layer. No modifications to `App.jsx` or other UI files.

2. **Zero new npm dependencies**: Uses native browser fetch API.

3. **Error handling**: All hooks include proper error states and cleanup.

4. **Polling strategy**: `useUltrAI` polls every 2 seconds until `completed: true`.

5. **Environment variables**: Uses Vite's `import.meta.env` pattern for configuration.

6. **Security**: `.env.local` is git-ignored to prevent committing sensitive dev configs.

7. **Backend compatibility**: Matches exact API contract from `ultrai/api.py`:
   - POST /runs → {run_id}
   - GET /runs/{run_id}/status → {run_id, phase, round, completed, artifacts}
   - GET /health → {status: "ok"}

8. **Cleanup**: `useUltrAI` properly clears polling intervals on unmount to prevent memory leaks.

---

## Testing Preparation

After you finish building, the native Cursor editor will test:
- Health check shows backend status
- Query submission returns run_id
- Polling updates phase/round in real-time
- Completed flag stops polling
- Error handling when backend is down

You do NOT need to test. Focus only on creating the 7 files exactly as specified.
