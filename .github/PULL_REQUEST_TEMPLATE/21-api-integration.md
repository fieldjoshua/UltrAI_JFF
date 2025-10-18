# PR 21 — API Integration Layer

## 🎯 **Artifacts Created**
- `frontend/src/services/api.js` - API client with fetch wrapper and error handling
- `frontend/src/hooks/useUltrAI.js` - React hook for submitting UltrAI queries
- `frontend/src/hooks/useHealth.js` - React hook for backend health checks
- `frontend/src/hooks/useCocktails.js` - React hook for fetching cocktail options
- `frontend/.env.local` - Local development environment configuration
- `frontend/.env.production` - Production environment configuration
- `frontend/src/config/api.config.js` - API configuration and endpoint definitions

## 🏗️ **Terminology** (trackers/names.md)
- **API_CLIENT**: Frontend service layer for backend communication
- **API_BASE_URL**: Environment-specific backend URL (localhost dev, Render prod)
- **FETCH_WRAPPER**: Centralized fetch function with error handling and interceptors
- **USE_ULTRAI_HOOK**: React hook for query submission and run tracking
- **RUN_POLLING**: Periodic status checks for active runs (every 2 seconds)

## 📦 **Dependencies** (trackers/dependencies.md)
- No new npm dependencies (uses native fetch API)

## 🔌 **API Endpoints Integrated**

### Backend endpoints (from `ultrai/api.py`):
1. **GET /health** - Health check (200 OK)
2. **POST /runs** - Start new UltrAI run
   - Body: `{query: string, cocktail: string}`
   - Returns: `{run_id: string}`
3. **GET /runs/{run_id}/status** - Poll run status
   - Returns: `{run_id, phase, round, completed, artifacts}`
4. **GET /runs/{run_id}/artifacts** - List run artifacts
   - Returns: `{run_id, files: string[]}`

## ✅ **Testing Endpoints**

### 1. Health Check Test
```bash
# Backend must be running
curl http://localhost:8000/health
# Expected: {"status":"ok"}
```

### 2. API Client Test
```javascript
// In browser console at localhost:3000
import { apiClient } from './services/api.js'
const health = await apiClient.get('/health')
console.log(health) // {status: "ok"}
```

### 3. useHealth Hook Test
```javascript
// Add to App.jsx temporarily:
import { useHealth } from './hooks/useHealth'
const { isHealthy, isLoading } = useHealth()
console.log({ isHealthy, isLoading })
```

### 4. Full Run Submission Test
```javascript
// In browser console
import { apiClient } from './services/api.js'
const result = await apiClient.post('/runs', {
  query: 'What is 2+2?',
  cocktail: 'SPEEDY'
})
console.log(result.run_id) // api_speedy_20251018_123456
```

### 5. Run Polling Test
```javascript
// Using useUltrAI hook
const { submitQuery, currentRun, isLoading } = useUltrAI()
await submitQuery('Test query', 'SPEEDY')
// Should see currentRun.phase updating: 00_ready.json → 01_inputs.json → ...
```

## 🤖 **Agent Work**: general-purpose agent

### Create API Service Layer (`frontend/src/services/api.js`):
```javascript
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

class APIError extends Error {
  constructor(message, status, data) {
    super(message)
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
        errorData.detail || 'Request failed',
        response.status,
        errorData
      )
    }

    return await response.json()
  } catch (error) {
    if (error instanceof APIError) throw error
    throw new APIError('Network error', 0, { originalError: error })
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
```

### Create React Hooks:

**`frontend/src/hooks/useHealth.js`**:
```javascript
import { useState, useEffect } from 'react'
import { apiClient } from '../services/api'

export function useHealth() {
  const [isHealthy, setIsHealthy] = useState(false)
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    async function checkHealth() {
      try {
        const result = await apiClient.get('/health')
        setIsHealthy(result.status === 'ok')
      } catch {
        setIsHealthy(false)
      } finally {
        setIsLoading(false)
      }
    }
    checkHealth()
  }, [])

  return { isHealthy, isLoading }
}
```

**`frontend/src/hooks/useUltrAI.js`**:
```javascript
import { useState, useCallback } from 'react'
import { apiClient } from '../services/api'

export function useUltrAI() {
  const [currentRun, setCurrentRun] = useState(null)
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState(null)

  const submitQuery = useCallback(async (query, cocktail) => {
    setIsLoading(true)
    setError(null)
    try {
      const result = await apiClient.post('/runs', { query, cocktail })
      setCurrentRun({ run_id: result.run_id, phase: null, completed: false })

      // Start polling status
      const pollInterval = setInterval(async () => {
        const status = await apiClient.get(`/runs/${result.run_id}/status`)
        setCurrentRun(status)
        if (status.completed) {
          clearInterval(pollInterval)
          setIsLoading(false)
        }
      }, 2000)

      return result.run_id
    } catch (err) {
      setError(err.message)
      setIsLoading(false)
      throw err
    }
  }, [])

  return { submitQuery, currentRun, isLoading, error }
}
```

**`frontend/src/hooks/useCocktails.js`**:
```javascript
import { useState, useEffect } from 'react'

const COCKTAILS = ['PREMIUM', 'SPEEDY', 'BUDGET', 'DEPTH']

export function useCocktails() {
  const [cocktails, setCocktails] = useState(COCKTAILS)
  const [isLoading, setIsLoading] = useState(false)

  return { cocktails, isLoading }
}
```

### Create Environment Files:

**`frontend/.env.local`**:
```bash
VITE_API_URL=http://localhost:8000
```

**`frontend/.env.production`**:
```bash
VITE_API_URL=https://ultrai-jff.onrender.com
```

**`frontend/.gitignore`** (add):
```
.env.local
```

## 🧪 **Testing Instructions** (for native Cursor editor)

### Test 1: Backend Health Check
1. Start backend: `uvicorn ultrai.api:app --reload`
2. Verify: `curl http://localhost:8000/health`
3. ✅ Should return `{"status":"ok"}`

### Test 2: API Client Import
1. Start frontend: `npm run dev`
2. Open browser console at http://localhost:3000
3. Test import: `const { apiClient } = await import('/src/services/api.js')`
4. ✅ No import errors

### Test 3: Health Hook in UI
1. Add to `App.jsx`:
```javascript
import { useHealth } from './hooks/useHealth'

function App() {
  const { isHealthy, isLoading } = useHealth()

  return (
    <div>
      <p>Backend: {isLoading ? 'Checking...' : isHealthy ? '✅ Healthy' : '❌ Down'}</p>
    </div>
  )
}
```
2. ✅ Should show "✅ Healthy" when backend running

### Test 4: Submit Test Query
1. Add to `App.jsx`:
```javascript
import { useUltrAI } from './hooks/useUltrAI'

function App() {
  const { submitQuery, currentRun, isLoading } = useUltrAI()

  const handleTest = () => {
    submitQuery('What is the capital of France?', 'SPEEDY')
  }

  return (
    <div>
      <button onClick={handleTest}>Test Query</button>
      {currentRun && <pre>{JSON.stringify(currentRun, null, 2)}</pre>}
    </div>
  )
}
```
2. Click "Test Query"
3. ✅ Should show run_id and phase updates in real-time

### Test 5: Error Handling
1. Stop backend server
2. Try submitting query
3. ✅ Should show error message, not crash

### Test 6: Environment Variables
1. Check `console.log(import.meta.env.VITE_API_URL)`
2. ✅ Dev: `http://localhost:8000`
3. ✅ Prod build: `https://ultrai-jff.onrender.com`

### Test 7: Production Build
1. `npm run build`
2. `npm run preview`
3. ✅ Build succeeds, preview works

### Test 8: Real End-to-End Run
1. Backend running with valid `OPENROUTER_API_KEY`
2. Submit query via frontend
3. Watch status updates: R1 → R2 → R3
4. ✅ Verify `completed: true` when synthesis finishes

## 🎨 **Visual Changes**
- No UI changes in this PR (foundation only)
- Health indicator can be added temporarily for testing
- Real UI components come in PR 22

## 🔄 **Next Steps**
- PR 22: Core UI Components (QueryForm, StatusDisplay, ResultsPanel)
- PR 23: Animation Layer (Framer Motion)
- PR 24: 3D Interactive Background (Three.js)
- PR 25: Render Static Site Deployment

## 📝 **Notes**
- Uses native fetch API (no axios dependency)
- Environment variables via Vite's `import.meta.env`
- Polling interval set to 2 seconds (balances UX vs server load)
- Error handling preserves error details for debugging
- API client is intentionally simple (can be extended in future PRs)

## 🔐 **Security Considerations**
- No API keys in frontend code
- CORS handled by FastAPI backend (already configured)
- All user input sanitized by backend (path traversal protection in `api.py`)
- Environment variables never committed to git
