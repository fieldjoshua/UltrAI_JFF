/**
 * StepIndicator Component Tests
 *
 * Tests the progress bar that shows current step.
 */

import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import { StepIndicator } from '../StepIndicator'

describe('StepIndicator Component', () => {
  it('should render all 3 steps', () => {
    render(<StepIndicator currentStep={1} />)

    expect(screen.getByText('1')).toBeInTheDocument()
    expect(screen.getByText('2')).toBeInTheDocument()
    expect(screen.getByText('3')).toBeInTheDocument()
  })

  it('should highlight current step', () => {
    render(<StepIndicator currentStep={2} />)

    // Check that all step labels are present (appear in step circles AND header)
    expect(screen.getAllByText('Enter Query')).toHaveLength(1)
    expect(screen.getAllByText('Choose Cocktail')).toHaveLength(2) // In circle label + header
    expect(screen.getAllByText('Confirm & Activate')).toHaveLength(1)
  })

  it('should show checkmark for completed steps', () => {
    render(<StepIndicator currentStep={3} />)

    // Steps 1 and 2 should show checkmarks
    const checkmarks = screen.getAllByText('✓')
    expect(checkmarks).toHaveLength(2)
  })

  it('should show step number for incomplete steps', () => {
    render(<StepIndicator currentStep={1} />)

    expect(screen.getByText('2')).toBeInTheDocument()
    expect(screen.getByText('3')).toBeInTheDocument()
  })

  it('should show current step description', () => {
    render(<StepIndicator currentStep={1} />)

    expect(
      screen.getByText('What would you like UltrAI to analyze?')
    ).toBeInTheDocument()
  })
})
