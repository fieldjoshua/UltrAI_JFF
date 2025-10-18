/**
 * OrderReceipt Component Tests
 *
 * Tests the running summary panel that shows user's selections.
 */

import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import { OrderReceipt } from '../OrderReceipt'

describe('OrderReceipt Component', () => {
  it('should render with empty order', () => {
    const order = { query: '', cocktail: '', cocktailDescription: '' }
    render(<OrderReceipt order={order} currentStep={1} />)

    expect(screen.getByText('Your UltrAI Order')).toBeInTheDocument()
    expect(screen.getByText('Not yet entered')).toBeInTheDocument()
  })

  it('should show query when entered', () => {
    const order = {
      query: 'Test query about AI',
      cocktail: '',
      cocktailDescription: '',
    }
    render(<OrderReceipt order={order} currentStep={2} />)

    expect(screen.getByText('Test query about AI')).toBeInTheDocument()
  })

  it('should show cocktail when selected', () => {
    const order = {
      query: 'Test query',
      cocktail: 'SPEEDY',
      cocktailDescription: 'Fast models',
    }
    render(<OrderReceipt order={order} currentStep={3} />)

    expect(screen.getByText('SPEEDY')).toBeInTheDocument()
    expect(screen.getByText('Fast models')).toBeInTheDocument()
  })

  it('should show "Ready to Activate" badge at step 4', () => {
    const order = {
      query: 'Test query',
      cocktail: 'SPEEDY',
      cocktailDescription: 'Fast models',
    }
    render(<OrderReceipt order={order} currentStep={4} />)

    expect(screen.getByText('✓ Ready to Activate')).toBeInTheDocument()
  })

  it('should show "Configuration In Progress" badge before step 3', () => {
    const order = { query: 'Test', cocktail: '', cocktailDescription: '' }
    render(<OrderReceipt order={order} currentStep={1} />)

    expect(
      screen.getByText('⚡ Configuration In Progress')
    ).toBeInTheDocument()
  })

  it('should truncate long queries', () => {
    const longQuery = 'a'.repeat(100)
    const order = {
      query: longQuery,
      cocktail: '',
      cocktailDescription: '',
    }
    render(<OrderReceipt order={order} currentStep={1} />)

    // Should show truncated version (60 chars + ...)
    const displayedText = screen.getByText(/^a+\.\.\./)
    expect(displayedText.textContent.length).toBeLessThan(longQuery.length)
  })
})
