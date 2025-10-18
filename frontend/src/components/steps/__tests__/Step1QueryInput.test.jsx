/**
 * Step1QueryInput Component Tests
 *
 * Tests the query input step.
 */

import { describe, it, expect, vi } from 'vitest'
import { render, screen, fireEvent } from '@testing-library/react'
import { Step1QueryInput } from '../Step1QueryInput'

describe('Step1QueryInput Component', () => {
  it('should render with empty query', () => {
    const onNext = vi.fn()
    render(<Step1QueryInput initialValue="" onNext={onNext} />)

    expect(screen.getByLabelText('Your Query')).toBeInTheDocument()
    expect(screen.getByText('Next: Choose Cocktail →')).toBeInTheDocument()
  })

  it('should render with initial value', () => {
    const onNext = vi.fn()
    render(<Step1QueryInput initialValue="Test query" onNext={onNext} />)

    const textarea = screen.getByLabelText('Your Query')
    expect(textarea.value).toBe('Test query')
  })

  it('should disable Next button when query is empty', () => {
    const onNext = vi.fn()
    render(<Step1QueryInput initialValue="" onNext={onNext} />)

    const nextButton = screen.getByText('Next: Choose Cocktail →')
    expect(nextButton).toBeDisabled()
  })

  it('should enable Next button when query is entered', () => {
    const onNext = vi.fn()
    render(<Step1QueryInput initialValue="" onNext={onNext} />)

    const textarea = screen.getByLabelText('Your Query')
    fireEvent.change(textarea, { target: { value: 'My test query' } })

    const nextButton = screen.getByText('Next: Choose Cocktail →')
    expect(nextButton).not.toBeDisabled()
  })

  it('should call onNext with query when Next clicked', () => {
    const onNext = vi.fn()
    render(<Step1QueryInput initialValue="" onNext={onNext} />)

    const textarea = screen.getByLabelText('Your Query')
    fireEvent.change(textarea, { target: { value: 'My test query' } })

    const nextButton = screen.getByText('Next: Choose Cocktail →')
    fireEvent.click(nextButton)

    expect(onNext).toHaveBeenCalledWith('My test query')
  })

  it('should show character count', () => {
    const onNext = vi.fn()
    render(<Step1QueryInput initialValue="Test" onNext={onNext} />)

    expect(screen.getByText('4 characters')).toBeInTheDocument()
  })

  it('should show warning for short queries', () => {
    const onNext = vi.fn()
    render(<Step1QueryInput initialValue="Short" onNext={onNext} />)

    expect(
      screen.getByText(/Query seems short - add more detail/)
    ).toBeInTheDocument()
  })

  it('should allow clicking example queries', () => {
    const onNext = vi.fn()
    render(<Step1QueryInput initialValue="" onNext={onNext} />)

    const exampleButton = screen.getByText(/key differences between React/)
    fireEvent.click(exampleButton)

    const textarea = screen.getByLabelText('Your Query')
    expect(textarea.value).toContain('React')
  })
})
