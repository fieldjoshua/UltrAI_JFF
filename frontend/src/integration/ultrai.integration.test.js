/**
 * Frontend Integration Tests (NO MOCKS)
 *
 * Requires a running backend API at VITE_API_URL or ULTRAI_API_BASE.
 * Tests call real endpoints and use real timers.
 *
 * To run:
 *   npm run test:integration
 *   ULTRAI_API_BASE=http://localhost:8000 npm run test:integration
 *   ULTRAI_API_BASE=https://ultrai-jff.onrender.com npm run test:integration
 */

import { describe, it, expect, beforeAll } from 'vitest'

const BASE = (typeof window !== 'undefined' && window?.VITE_API_URL)
  || import.meta.env?.VITE_API_URL
  || process.env.ULTRAI_API_BASE
  || 'http://127.0.0.1:8000'

async function getJson(url, init) {
  const r = await fetch(url, init).catch((err) => {
    throw new Error(`Network error: ${err.message}. Is backend running at ${BASE}?`)
  })
  const data = await r.json().catch(() => ({}))
  return { status: r.status, data }
}

describe('UltrAI API integration (no mocks)', () => {
  beforeAll(async () => {
    console.log(`\n🔗 Testing against backend: ${BASE}`)
    // Verify backend is reachable
    try {
      const { status } = await getJson(`${BASE}/health`)
      if (status !== 200) {
        throw new Error(`Backend health check failed with status ${status}`)
      }
      console.log('✅ Backend is healthy\n')
    } catch (err) {
      throw new Error(
        `Backend not reachable at ${BASE}. ` +
        `Start backend with 'make run-api' or set ULTRAI_API_BASE env var. ` +
        `Error: ${err.message}`
      )
    }
  })

  it('health endpoint returns ok', async () => {
    const { status, data } = await getJson(`${BASE}/health`)
    expect(status).toBe(200)
    expect(data?.status).toBe('ok')
  })

  it('start run and poll status to completion (real timers, ~60-180s)', async () => {
    // Start synthesis run
    const start = await getJson(`${BASE}/runs`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ query: 'What is 2+2?', cocktail: 'SPEEDY' })
    })
    expect(start.status).toBe(200)
    const runId = start.data?.run_id
    expect(runId).toBeTruthy()

    console.log(`📦 Run created: ${runId}`)
    console.log(`🔍 Trace artifacts at: runs/${runId}/`)

    // Poll until completed or timeout (~3 minutes)
    const deadline = Date.now() + 180_000
    let last
    let pollCount = 0
    while (Date.now() < deadline) {
      const res = await getJson(`${BASE}/runs/${runId}/status`)
      expect(res.status).toBe(200)
      last = res.data
      pollCount++

      if (last?.completed) {
        console.log(`✅ Run completed after ${pollCount} polls`)
        break
      }

      // Log current phase
      const phase = last?.current_phase || 'unknown'
      if (pollCount % 6 === 0) { // Log every ~30s (6 polls × 5s)
        console.log(`⏳ Still running... (phase: ${phase})`)
      }

      await new Promise(r => setTimeout(r, 5000)) // Real timer, 5s poll interval
    }

    expect(last?.completed).toBe(true)
    console.log(`🎉 Synthesis complete: ${runId}`)

    // Verify required artifacts exist
    const art = await getJson(`${BASE}/runs/${runId}/artifacts`)
    expect(art.status).toBe(200)
    const files = art.data?.files || []
    const names = files.map(f => f.split('/').pop())

    const requiredArtifacts = [
      '00_ready.json',
      '01_inputs.json',
      '02_activate.json',
      '03_initial.json',
      '04_meta.json',
      '05_ultrai.json',
      'delivery.json'
    ]

    requiredArtifacts.forEach(artifact => {
      expect(names, `Missing artifact: ${artifact}`).toContain(artifact)
    })

    console.log(`📄 All ${requiredArtifacts.length} required artifacts present`)
  }, 190_000) // 3 min timeout for full synthesis
})
