/**
 * useCocktails Hook Tests
 *
 * Tests static cocktail configuration data.
 * Simple test - no timers, no API calls, just data validation.
 */

import { describe, it, expect } from 'vitest'
import { renderHook } from '@testing-library/react'
import { useCocktails } from '../useCocktails'

describe('useCocktails Hook', () => {
  it('should return all 5 cocktails', () => {
    const { result } = renderHook(() => useCocktails())

    expect(result.current.cocktails).toHaveLength(5)
    expect(result.current.cocktails.map((c) => c.id)).toEqual([
      'PREMIUM',
      'SPEEDY',
      'BUDGET',
      'DEPTH',
      'LUXE',
    ])
  })

  it('should include cocktail metadata', () => {
    const { result } = renderHook(() => useCocktails())

    const premium = result.current.cocktails.find((c) => c.id === 'PREMIUM')
    expect(premium).toMatchObject({
      id: 'PREMIUM',
      name: 'Premium',
      description: expect.any(String),
      models: expect.any(Array),
    })
    expect(premium.models).toHaveLength(3)
  })

  it('should match backend cocktail definitions', () => {
    const { result } = renderHook(() => useCocktails())

    // Test SPEEDY PRIMARY models match backend
    const speedy = result.current.cocktails.find((c) => c.id === 'SPEEDY')
    expect(speedy.models).toContain('openai/gpt-4o-mini')
    expect(speedy.models).toContain('anthropic/claude-3-haiku')
    expect(speedy.models).toContain('x-ai/grok-3-mini')

    // Test PREMIUM PRIMARY models match backend
    const premium = result.current.cocktails.find((c) => c.id === 'PREMIUM')
    expect(premium.models).toContain('anthropic/claude-3.7-sonnet')
    expect(premium.models).toContain('openai/gpt-4o')
    expect(premium.models).toContain('google/gemini-2.5-pro')
  })
})
