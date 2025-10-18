# PR 21 — API Integration Layer
# TESTER INSTRUCTIONS (Native Cursor Editor - QA Lead)

## Overview

You are the **QA Lead** for PR 21: API Integration Layer. The general-purpose agent has built the API integration files. Your role is to **test** that the API layer correctly connects the frontend to the backend.

**Your Responsibilities**:
1. Run the backend server
2. Run the frontend dev server
3. Test all API integration features
4. Verify error handling
5. Report pass/fail for each checkpoint

---

## Prerequisites

Before testing, ensure:
- ✅ Backend running at `http://localhost:8000`
- ✅ Frontend dev server running at `http://localhost:3000` or `http://localhost:5173`
- ✅ `OPENROUTER_API_KEY` set in backend `.env` file

---

## Testing Checklist

### ✅ Checkpoint 1: Backend Health Check

**Goal**: Verify backend is running and accessible

**Steps**:
1. Start backend server:
   ```bash
   uvicorn ultrai.api:app --reload
   ```

2. In a new terminal, test health endpoint:
   ```bash
   curl http://localhost:8000/health
   ```

**Expected Result**:
```json
{"status":"ok"}
```

**Pass/Fail**: ________

---

### ✅ Checkpoint 2: Frontend Dev Server

**Goal**: Verify frontend can start with new API integration files

**Steps**:
1. Start frontend dev server:
   ```bash
   cd frontend
   npm run dev
   ```

2. Check console output for errors

**Expected Result**:
- Server starts successfully
- No import errors
- Shows "Local: http://localhost:3000/" (or 5173)

**Pass/Fail**: ________

---

### ✅ Checkpoint 3: API Client Import

**Goal**: Verify API client can be imported and used

**Steps**:
1. Open browser at `http://localhost:3000` (or 5173)
2. Open browser console (F12)
3. Test API client import:
   ```javascript
   const { apiClient } = await import('/src/services/api.js')
   const health = await apiClient.get('/health')
   console.log(health)
   ```

**Expected Result**:
```javascript
{ status: "ok" }
```

**Pass/Fail**: ________

---

### ✅ Checkpoint 4: useHealth Hook Integration

**Goal**: Verify health hook works in React component

**Steps**:
1. Temporarily modify `frontend/src/App.jsx` to add health check:
   ```javascript
   import { useHealth } from './hooks/useHealth'

   function App() {
     const { isHealthy, isLoading, error } = useHealth()

     return (
       <div className="min-h-screen bg-gradient-to-br from-purple-900 via-blue-900 to-black text-white">
         <div className="container mx-auto px-4 py-16">
           <h1 className="text-5xl font-bold text-center mb-8">
             UltrAI Frontend
           </h1>

           {/* Health Check Display */}
           <div className="mt-8 text-center">
             <p className="text-xl">
               Backend Status:{' '}
               {isLoading ? (
                 <span className="text-yellow-400">Checking...</span>
               ) : isHealthy ? (
                 <span className="text-green-400">✅ Healthy</span>
               ) : (
                 <span className="text-red-400">❌ Down ({error})</span>
               )}
             </p>
           </div>

           <p className="text-center text-xl text-gray-300 mt-4">
             Multi-LLM synthesis system foundation
           </p>
           <div className="mt-12 text-center">
             <p className="text-sm text-gray-400">
               React + Vite + Tailwind CSS scaffold
             </p>
           </div>
         </div>
       </div>
     )
   }

   export default App
   ```

2. Save file and check browser

**Expected Result**:
- Shows "Backend Status: ✅ Healthy"
- No console errors

**Pass/Fail**: ________

---

### ✅ Checkpoint 5: Query Submission Test

**Goal**: Verify query submission and run creation

**Steps**:
1. Update `App.jsx` to add query submission button:
   ```javascript
   import { useHealth } from './hooks/useHealth'
   import { useUltrAI } from './hooks/useUltrAI'

   function App() {
     const { isHealthy, isLoading: healthLoading } = useHealth()
     const { submitQuery, currentRun, isLoading, error } = useUltrAI()

     const handleTestQuery = async () => {
       try {
         const runId = await submitQuery('What is 2+2?', 'SPEEDY')
         console.log('Run started:', runId)
       } catch (err) {
         console.error('Query failed:', err)
       }
     }

     return (
       <div className="min-h-screen bg-gradient-to-br from-purple-900 via-blue-900 to-black text-white">
         <div className="container mx-auto px-4 py-16">
           <h1 className="text-5xl font-bold text-center mb-8">
             UltrAI Frontend
           </h1>

           {/* Health Check */}
           <div className="mt-8 text-center">
             <p className="text-xl">
               Backend:{' '}
               {healthLoading ? (
                 <span className="text-yellow-400">Checking...</span>
               ) : isHealthy ? (
                 <span className="text-green-400">✅ Healthy</span>
               ) : (
                 <span className="text-red-400">❌ Down</span>
               )}
             </p>
           </div>

           {/* Test Query Button */}
           <div className="mt-8 text-center">
             <button
               onClick={handleTestQuery}
               disabled={isLoading || !isHealthy}
               className="bg-blue-600 hover:bg-blue-700 disabled:bg-gray-600 text-white font-bold py-3 px-6 rounded-lg transition"
             >
               {isLoading ? 'Processing...' : 'Test Query (What is 2+2?)'}
             </button>
           </div>

           {/* Run Status Display */}
           {currentRun && (
             <div className="mt-8 max-w-2xl mx-auto bg-gray-800 p-6 rounded-lg">
               <h2 className="text-2xl font-bold mb-4">Run Status</h2>
               <pre className="text-sm text-gray-300 overflow-auto">
                 {JSON.stringify(currentRun, null, 2)}
               </pre>
             </div>
           )}

           {/* Error Display */}
           {error && (
             <div className="mt-8 max-w-2xl mx-auto bg-red-900 p-4 rounded-lg">
               <p className="text-red-200">Error: {error}</p>
             </div>
           )}
         </div>
       </div>
     )
   }

   export default App
   ```

2. Click "Test Query" button
3. Watch run status display

**Expected Result**:
- Button click triggers query submission
- `currentRun` object appears with `run_id`
- Status updates every 2 seconds
- Console shows: `Run started: api_speedy_20251018_HHMMSS`

**Pass/Fail**: ________

---

### ✅ Checkpoint 6: Run Polling Verification

**Goal**: Verify status polling updates phase/round in real-time

**Steps**:
1. With backend and frontend running, submit test query
2. Watch `currentRun` object in UI update every 2 seconds
3. Observe phase progression:
   - `null` → `00_ready.json` → `01_inputs.json` → `02_activate.json` → `03_initial.json` → `04_meta.json` → `05_ultrai.json`
4. Observe round field:
   - `null` → `"R1"` → `"R2"` → `"R3"`

**Expected Result**:
- Phase updates automatically
- Round updates automatically
- `completed: false` changes to `completed: true` when synthesis finishes
- Polling stops after `completed: true`

**Pass/Fail**: ________

---

### ✅ Checkpoint 7: Error Handling (Backend Down)

**Goal**: Verify graceful error handling when backend unavailable

**Steps**:
1. Stop backend server (`Ctrl+C` in terminal running uvicorn)
2. Refresh frontend page
3. Observe health check display

**Expected Result**:
- Shows "Backend Status: ❌ Down (Network error: Could not connect to backend)"
- Test Query button is disabled
- No console errors (graceful degradation)

**Pass/Fail**: ________

---

### ✅ Checkpoint 8: Environment Variables

**Goal**: Verify environment configuration is correct

**Steps**:
1. In browser console, check environment variable:
   ```javascript
   console.log(import.meta.env.VITE_API_URL)
   ```

2. Check `.env.local` file exists in `frontend/` directory

3. Verify `.env.local` is in `.gitignore`

**Expected Result**:
- Console shows: `http://localhost:8000`
- `.env.local` file exists with correct content
- `.env.local` is git-ignored (not staged for commit)

**Pass/Fail**: ________

---

### ✅ Checkpoint 9: Production Build

**Goal**: Verify production build works with API integration

**Steps**:
1. Build for production:
   ```bash
   cd frontend
   npm run build
   ```

2. Preview production build:
   ```bash
   npm run preview
   ```

3. Open preview URL (usually `http://localhost:4173`)

**Expected Result**:
- Build completes successfully
- Preview server starts
- Page loads without errors
- Health check works in production build

**Pass/Fail**: ________

---

### ✅ Checkpoint 10: Full End-to-End Run

**Goal**: Verify complete query → synthesis flow

**Steps**:
1. Ensure backend has valid `OPENROUTER_API_KEY` in `.env`
2. Start backend: `uvicorn ultrai.api:app --reload`
3. Start frontend: `npm run dev`
4. Click "Test Query" button
5. Wait for synthesis to complete (60-180 seconds)

**Expected Result**:
- Run progresses through all phases
- Phase updates: `00_ready.json` → ... → `05_ultrai.json`
- Round updates: `R1` → `R2` → `R3`
- `completed: true` when synthesis finishes
- No errors in console
- Polling stops automatically

**Pass/Fail**: ________

---

## Final Report

After completing all 10 checkpoints, report results:

```
PR 21 API Integration Layer - Test Results

✅ Checkpoint 1: Backend Health Check - PASS/FAIL
✅ Checkpoint 2: Frontend Dev Server - PASS/FAIL
✅ Checkpoint 3: API Client Import - PASS/FAIL
✅ Checkpoint 4: useHealth Hook - PASS/FAIL
✅ Checkpoint 5: Query Submission - PASS/FAIL
✅ Checkpoint 6: Run Polling - PASS/FAIL
✅ Checkpoint 7: Error Handling - PASS/FAIL
✅ Checkpoint 8: Environment Variables - PASS/FAIL
✅ Checkpoint 9: Production Build - PASS/FAIL
✅ Checkpoint 10: End-to-End Run - PASS/FAIL

Total: X/10 PASSED

Issues Found:
- (List any failures or unexpected behavior)

Ready for User Approval: YES/NO
```

---

## After Testing

1. **Revert `App.jsx`**: Remove all test code added during checkpoints 4-6
2. **Keep original scaffold**: Restore `App.jsx` to its PR 20 state (basic purple gradient)
3. **Report results**: Provide pass/fail summary to user
4. **Wait for approval**: User will approve and merge PR 21

---

## Notes

- **Test duration**: Checkpoint 10 takes 60-180 seconds (real API calls)
- **OPENROUTER_API_KEY required**: Checkpoint 10 will fail without valid API key
- **Polling cleanup**: `useUltrAI` hook automatically clears intervals on unmount
- **Error states**: All hooks properly handle network errors and backend downtime
- **No new dependencies**: All code uses native fetch API and React hooks

---

## Troubleshooting

### Backend won't start
- Check `OPENROUTER_API_KEY` is set in backend `.env`
- Verify virtual environment activated: `. .venv/bin/activate`
- Check port 8000 not in use: `lsof -i :8000`

### Frontend import errors
- Verify all 7 files created by agent
- Check file paths match exactly
- Restart dev server: `npm run dev`

### Health check fails
- Verify backend running: `curl http://localhost:8000/health`
- Check CORS enabled in FastAPI (already configured in `ultrai/api.py`)
- Check `.env.local` has correct `VITE_API_URL`

### Polling doesn't stop
- Check `completed: true` is returned by backend
- Verify `useUltrAI` hook cleanup logic
- Check browser console for errors

---

**Testing begins when general-purpose agent reports build complete.**
