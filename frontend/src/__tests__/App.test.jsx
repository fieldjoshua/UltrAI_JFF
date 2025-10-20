/**
 * Terminal CLI App Component Tests
 *
 * Tests the terminal-style interface for UltrAI synthesis.
 * Verifies UI rendering, user interactions, and state transitions.
 */

import { describe, it, expect, beforeEach, vi } from 'vitest'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import App from '../App'
import * as useUltrAIModule from '../hooks/useUltrAI'
import * as useHealthModule from '../hooks/useHealth'

// Mock the hooks
vi.mock('../hooks/useUltrAI')
vi.mock('../hooks/useHealth')

describe('Terminal CLI App', () => {
  const mockSubmitQuery = vi.fn()

  beforeEach(() => {
    vi.clearAllMocks()

    // Default mock implementations
    useHealthModule.useHealth.mockReturnValue({
      isHealthy: true,
      isLoading: false,
    })

    useUltrAIModule.useUltrAI.mockReturnValue({
      isLoading: false,
      currentRun: null,
      submitQuery: mockSubmitQuery,
    })
  })

  describe('Initial Render - Input Phase', () => {
    it('should render ASCII logo', () => {
      render(<App />)
      // Check for UltrAI ASCII art text
      expect(screen.getByText(/Multi-LLM Convergent Synthesis/i)).toBeInTheDocument()
    })

    it('should render terminal-style query input', () => {
      render(<App />)
      expect(screen.getByText(/ultrai --query/i)).toBeInTheDocument()
      expect(screen.getByPlaceholderText(/Enter your query.../i)).toBeInTheDocument()
    })

    it('should render cocktail selector with all options', () => {
      render(<App />)
      const textarea = screen.getByPlaceholderText(/Enter your query.../i)

      // Enter query and proceed to Step 2
      fireEvent.change(textarea, { target: { value: 'Test query' } })
      fireEvent.click(screen.getByText('[NEXT]'))

      // Now on Step 2 - cocktail selection
      expect(screen.getByText(/STEP 2: SELECT LLM COCKTAIL/i)).toBeInTheDocument()

      // Verify all cocktail radio buttons are present
      const radios = screen.getAllByRole('radio')
      expect(radios).toHaveLength(5)

      // Verify all cocktail names appear
      expect(screen.getByText('LUXE')).toBeInTheDocument()
      expect(screen.getByText('PREMIUM')).toBeInTheDocument()
      expect(screen.getByText('SPEEDY')).toBeInTheDocument()
      expect(screen.getByText('BUDGET')).toBeInTheDocument()
      expect(screen.getByText('DEPTH')).toBeInTheDocument()
    })

    it('should display cocktail details below selector', () => {
      render(<App />)
      const textarea = screen.getByPlaceholderText(/Enter your query.../i)

      // Enter query and proceed to Step 2
      fireEvent.change(textarea, { target: { value: 'Test query' } })
      fireEvent.click(screen.getByText('[NEXT]'))

      // Default is SPEEDY - check for model names in the details
      expect(screen.getByText(/gpt-4o-mini/i)).toBeInTheDocument()
      expect(screen.getByText(/grok-2-1212/i)).toBeInTheDocument()
      expect(screen.getByText(/claude-3-haiku/i)).toBeInTheDocument()
      expect(screen.getByText(/mistral-small/i)).toBeInTheDocument()
      expect(screen.getByText(/deepseek-chat/i)).toBeInTheDocument()
    })

    it('should default to SPEEDY cocktail', () => {
      render(<App />)
      const textarea = screen.getByPlaceholderText(/Enter your query.../i)

      // Enter query and proceed to Step 2
      fireEvent.change(textarea, { target: { value: 'Test query' } })
      fireEvent.click(screen.getByText('[NEXT]'))

      // Check SPEEDY radio button is selected by default
      const speedyRadio = screen.getByRole('radio', { name: /SPEEDY/i })
      expect(speedyRadio).toBeChecked()
    })

    it('should update cocktail details when selection changes', () => {
      render(<App />)
      const textarea = screen.getByPlaceholderText(/Enter your query.../i)

      // Enter query and proceed to Step 2
      fireEvent.change(textarea, { target: { value: 'Test query' } })
      fireEvent.click(screen.getByText('[NEXT]'))

      // Get all radio buttons
      const radios = screen.getAllByRole('radio')

      // Default is SPEEDY (index 2) - verify it's selected
      const speedyRadio = radios.find(r => r.value === 'SPEEDY')
      expect(speedyRadio).toBeChecked()

      // Change to LUXE (index 0) - verify selection changed
      const luxeRadio = radios.find(r => r.value === 'LUXE')
      fireEvent.click(luxeRadio)
      expect(luxeRadio).toBeChecked()
      expect(speedyRadio).not.toBeChecked()

      // Change to PREMIUM (index 1) - verify selection changed
      const premiumRadio = radios.find(r => r.value === 'PREMIUM')
      fireEvent.click(premiumRadio)
      expect(premiumRadio).toBeChecked()
      expect(luxeRadio).not.toBeChecked()
    })

    it('should disable [NEXT] button when query is empty', () => {
      render(<App />)
      const nextButton = screen.getByText('[NEXT]')
      expect(nextButton).toBeDisabled()
    })

    it('should enable [NEXT] button when query is entered', () => {
      render(<App />)
      const textarea = screen.getByPlaceholderText(/Enter your query.../i)
      const nextButton = screen.getByText('[NEXT]')

      fireEvent.change(textarea, { target: { value: 'Test query' } })
      expect(nextButton).not.toBeDisabled()
    })

    it('should disable [NEXT] button when backend is unhealthy', () => {
      useHealthModule.useHealth.mockReturnValue({
        isHealthy: false,
        isLoading: false,
      })

      render(<App />)
      const textarea = screen.getByPlaceholderText(/Enter your query.../i)
      const nextButton = screen.getByText('[NEXT]')

      fireEvent.change(textarea, { target: { value: 'Test query' } })
      expect(nextButton).toBeDisabled()
    })
  })

  describe('Backend Health Status', () => {
    it('should show error when backend is offline', () => {
      useHealthModule.useHealth.mockReturnValue({
        isHealthy: false,
        isLoading: false,
      })

      render(<App />)
      expect(screen.getByText(/ERROR.*Backend not available/i)).toBeInTheDocument()
    })

    it('should not show error when backend is online', () => {
      useHealthModule.useHealth.mockReturnValue({
        isHealthy: true,
        isLoading: false,
      })

      render(<App />)
      expect(screen.queryByText(/ERROR/i)).not.toBeInTheDocument()
    })

    it('should show ONLINE status in footer when backend is healthy', () => {
      useHealthModule.useHealth.mockReturnValue({
        isHealthy: true,
        isLoading: false,
      })

      render(<App />)
      expect(screen.getByText(/Backend: ● ONLINE/i)).toBeInTheDocument()
    })

    it('should show OFFLINE status in footer when backend is unhealthy', () => {
      useHealthModule.useHealth.mockReturnValue({
        isHealthy: false,
        isLoading: false,
      })

      render(<App />)
      expect(screen.getByText(/Backend: ○ OFFLINE/i)).toBeInTheDocument()
    })
  })

  describe('Confirmation Phase', () => {
    it('should show confirmation screen when [NEXT] is clicked', () => {
      render(<App />)
      const textarea = screen.getByPlaceholderText(/Enter your query.../i)

      // Step 1: Enter query
      fireEvent.change(textarea, { target: { value: 'Test query' } })
      fireEvent.click(screen.getByText('[NEXT]'))

      // Step 2: Select cocktail (SPEEDY is default)
      fireEvent.click(screen.getByText('[NEXT]'))

      // Step 3: Confirmation
      expect(screen.getByText(/CONFIRMATION/i)).toBeInTheDocument()
      expect(screen.getByText(/QUERY:/i)).toBeInTheDocument()
      expect(screen.getByText(/Test query/i)).toBeInTheDocument()
      expect(screen.getByText(/COCKTAIL:/i)).toBeInTheDocument()
      expect(screen.getByText(/SPEEDY/i)).toBeInTheDocument()
      expect(screen.getByText(/R1 → R2 → R3 Synthesis/i)).toBeInTheDocument()
    })

    it('should show [EXECUTE] and [BACK] buttons in confirmation', () => {
      render(<App />)
      const textarea = screen.getByPlaceholderText(/Enter your query.../i)

      // Step 1: Enter query
      fireEvent.change(textarea, { target: { value: 'Test query' } })
      fireEvent.click(screen.getByText('[NEXT]'))

      // Step 2: Select cocktail
      fireEvent.click(screen.getByText('[NEXT]'))

      // Step 3: Should have EXECUTE and BACK buttons
      expect(screen.getByText('[EXECUTE]')).toBeInTheDocument()
      expect(screen.getByText('[BACK]')).toBeInTheDocument()
    })

    it('should return to cocktail selection when [BACK] is clicked', () => {
      render(<App />)
      const textarea = screen.getByPlaceholderText(/Enter your query.../i)

      // Step 1: Enter query
      fireEvent.change(textarea, { target: { value: 'Test query' } })
      fireEvent.click(screen.getByText('[NEXT]'))

      // Step 2: Select cocktail
      fireEvent.click(screen.getByText('[NEXT]'))

      // Step 3: Click BACK from confirmation
      fireEvent.click(screen.getByText('[BACK]'))

      // Should be back at Step 2 (cocktail selection)
      expect(screen.getByText(/STEP 2: SELECT LLM COCKTAIL/i)).toBeInTheDocument()
      expect(screen.getAllByRole('radio')).toHaveLength(5)
    })

    it('should preserve query and cocktail when returning from confirmation', () => {
      render(<App />)
      const textarea = screen.getByPlaceholderText(/Enter your query.../i)

      // Step 1: Enter query
      fireEvent.change(textarea, { target: { value: 'Test query' } })
      fireEvent.click(screen.getByText('[NEXT]'))

      // Step 2: Change to LUXE
      const luxeRadio = screen.getByRole('radio', { name: /LUXE/i })
      fireEvent.click(luxeRadio)
      fireEvent.click(screen.getByText('[NEXT]'))

      // Step 3: Click BACK
      fireEvent.click(screen.getByText('[BACK]'))

      // Should be back at Step 2 with LUXE still selected
      const luxeRadioAfterBack = screen.getByRole('radio', { name: /LUXE/i })
      expect(luxeRadioAfterBack).toBeChecked()
    })
  })

  describe('Running Phase', () => {
    it('should call submitQuery when [EXECUTE] is clicked', async () => {
      render(<App />)
      const textarea = screen.getByPlaceholderText(/Enter your query.../i)

      // Step 1: Enter query
      fireEvent.change(textarea, { target: { value: 'Test query' } })
      fireEvent.click(screen.getByText('[NEXT]'))

      // Step 2: Select cocktail (SPEEDY is default)
      fireEvent.click(screen.getByText('[NEXT]'))

      // Step 3: Execute
      fireEvent.click(screen.getByText('[EXECUTE]'))

      await waitFor(() => {
        expect(mockSubmitQuery).toHaveBeenCalledWith('Test query', 'SPEEDY')
      })
    })

    it('should show terminal status display during run', () => {
      useUltrAIModule.useUltrAI.mockReturnValue({
        isLoading: true,
        currentRun: {
          run_id: 'test_run_123',
          phase: '03_initial.json',
          round: 'R1',
          completed: false,
          artifacts: [],
        },
        submitQuery: mockSubmitQuery,
      })

      render(<App />)
      const textarea = screen.getByPlaceholderText(/Enter your query.../i)

      // Step 1: Enter query
      fireEvent.change(textarea, { target: { value: 'Test query' } })
      fireEvent.click(screen.getByText('[NEXT]'))

      // Step 2: Select cocktail
      fireEvent.click(screen.getByText('[NEXT]'))

      // Step 3: Execute
      fireEvent.click(screen.getByText('[EXECUTE]'))

      expect(screen.getByText(/⚡ PROCESSING/i)).toBeInTheDocument()
      expect(screen.getByText(/RUN_ID:/i)).toBeInTheDocument()
      expect(screen.getByText(/test_run_123/i)).toBeInTheDocument()
      expect(screen.getByText(/PHASE:/i)).toBeInTheDocument()
    })

    it('should display human-readable phase names during processing', () => {
      useUltrAIModule.useUltrAI.mockReturnValue({
        isLoading: true,
        currentRun: {
          run_id: 'api_speedy_20251018_123456',
          phase: '04_meta.json',
          round: 'R2',
          completed: false,
          artifacts: ['03_initial.json'],
        },
        submitQuery: mockSubmitQuery,
      })

      render(<App />)
      const textarea = screen.getByPlaceholderText(/Enter your query.../i)

      // Step 1: Enter query
      fireEvent.change(textarea, { target: { value: 'Test query' } })
      fireEvent.click(screen.getByText('[NEXT]'))

      // Step 2: Select cocktail
      fireEvent.click(screen.getByText('[NEXT]'))

      // Step 3: Execute
      fireEvent.click(screen.getByText('[EXECUTE]'))

      expect(screen.getByText(/Meta Round \(R2\)/i)).toBeInTheDocument()
    })

  })

  describe('Results Phase', () => {
    it('should show terminal completion display when run finishes', () => {
      useUltrAIModule.useUltrAI.mockReturnValue({
        isLoading: false,
        currentRun: {
          run_id: 'test_run_123',
          phase: '05_ultrai.json',
          round: 'R3',
          completed: true,
          artifacts: ['03_initial.json', '04_meta.json', '05_ultrai.json', 'stats.json'],
        },
        submitQuery: mockSubmitQuery,
      })

      render(<App />)
      const textarea = screen.getByPlaceholderText(/Enter your query.../i)

      // Step 1: Enter query
      fireEvent.change(textarea, { target: { value: 'Test query' } })
      fireEvent.click(screen.getByText('[NEXT]'))

      // Step 2: Select cocktail
      fireEvent.click(screen.getByText('[NEXT]'))

      // Step 3: Execute
      fireEvent.click(screen.getByText('[EXECUTE]'))

      expect(screen.getByText(/⚡ SYNTHESIS COMPLETE/i)).toBeInTheDocument()
      expect(screen.getByText(/\[NEW QUERY\]/i)).toBeInTheDocument()
    })

    it('should show download links for R1 and R2 outputs', () => {
      useUltrAIModule.useUltrAI.mockReturnValue({
        isLoading: false,
        currentRun: {
          run_id: 'test_run_123',
          phase: '05_ultrai.json',
          round: 'R3',
          completed: true,
          artifacts: ['03_initial.json', '04_meta.json', '05_ultrai.json'],
        },
        submitQuery: mockSubmitQuery,
      })

      render(<App />)
      const textarea = screen.getByPlaceholderText(/Enter your query.../i)

      // Step 1: Enter query
      fireEvent.change(textarea, { target: { value: 'Test query' } })
      fireEvent.click(screen.getByText('[NEXT]'))

      // Step 2: Select cocktail
      fireEvent.click(screen.getByText('[NEXT]'))

      // Step 3: Execute
      fireEvent.click(screen.getByText('[EXECUTE]'))

      expect(screen.getByText(/\[R1\] Initial Responses/i)).toBeInTheDocument()
      expect(screen.getByText(/\[R2\] Meta Revisions/i)).toBeInTheDocument()
    })

    it('should show NEW QUERY button when complete', () => {
      useUltrAIModule.useUltrAI.mockReturnValue({
        isLoading: false,
        currentRun: {
          run_id: 'test_run_123',
          phase: '05_ultrai.json',
          round: 'R3',
          completed: true,
          artifacts: ['05_ultrai.json'],
        },
        submitQuery: mockSubmitQuery,
      })

      render(<App />)
      const textarea = screen.getByPlaceholderText(/Enter your query.../i)

      // Step 1: Enter query
      fireEvent.change(textarea, { target: { value: 'Test query' } })
      fireEvent.click(screen.getByText('[NEXT]'))

      // Step 2: Select cocktail
      fireEvent.click(screen.getByText('[NEXT]'))

      // Step 3: Execute
      fireEvent.click(screen.getByText('[EXECUTE]'))

      expect(screen.getByText(/\[NEW QUERY\]/i)).toBeInTheDocument()
    })

    it('should reset to input phase when NEW QUERY is clicked', () => {
      useUltrAIModule.useUltrAI.mockReturnValue({
        isLoading: false,
        currentRun: {
          run_id: 'test_run_123',
          phase: '05_ultrai.json',
          round: 'R3',
          completed: true,
          artifacts: ['05_ultrai.json'],
        },
        submitQuery: mockSubmitQuery,
      })

      render(<App />)
      const textarea = screen.getByPlaceholderText(/Enter your query.../i)

      // Step 1: Enter query
      fireEvent.change(textarea, { target: { value: 'Test query' } })
      fireEvent.click(screen.getByText('[NEXT]'))

      // Step 2: Select cocktail
      fireEvent.click(screen.getByText('[NEXT]'))

      // Step 3: Execute
      fireEvent.click(screen.getByText('[EXECUTE]'))

      // Click NEW QUERY
      fireEvent.click(screen.getByText(/\[NEW QUERY\]/i))

      // Should be back at Step 1 (query) with cleared fields
      const newTextarea = screen.getByPlaceholderText(/Enter your query.../i)
      expect(newTextarea.value).toBe('')
      expect(screen.getByText(/STEP 1: ENTER QUERY/i)).toBeInTheDocument()
    })
  })

  describe('Footer', () => {
    it('should display version and tagline', () => {
      render(<App />)
      expect(screen.getByText(/UltrAI v0.1.0/i)).toBeInTheDocument()
      expect(screen.getByText(/R1→R2→R3 Convergent Intelligence/i)).toBeInTheDocument()
    })
  })
})
