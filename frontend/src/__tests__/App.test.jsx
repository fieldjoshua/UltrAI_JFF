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
      expect(screen.getByText(/ultrai --cocktail/i)).toBeInTheDocument()

      const select = screen.getByRole('combobox')
      expect(select).toBeInTheDocument()

      // Verify all cocktail options are present
      const options = screen.getAllByRole('option')
      const cocktailNames = options.map(opt => opt.value)
      expect(cocktailNames).toContain('LUXE')
      expect(cocktailNames).toContain('PREMIUM')
      expect(cocktailNames).toContain('SPEEDY')
      expect(cocktailNames).toContain('BUDGET')
      expect(cocktailNames).toContain('DEPTH')
    })

    it('should display cocktail details below selector', () => {
      render(<App />)
      // Default is SPEEDY
      expect(screen.getByText(/gpt-4o-mini \+ claude-haiku \+ gemini-flash/i)).toBeInTheDocument()
    })

    it('should default to SPEEDY cocktail', () => {
      render(<App />)
      const select = screen.getByRole('combobox')
      expect(select.value).toBe('SPEEDY')
    })

    it('should update cocktail details when selection changes', () => {
      render(<App />)
      const select = screen.getByRole('combobox')

      // Change to LUXE
      fireEvent.change(select, { target: { value: 'LUXE' } })
      expect(screen.getByText(/gpt-4o \+ claude-sonnet-4.5 \+ gemini-2.0/i)).toBeInTheDocument()

      // Change to PREMIUM
      fireEvent.change(select, { target: { value: 'PREMIUM' } })
      expect(screen.getByText(/claude-3.7 \+ chatgpt-4o \+ llama-3.3/i)).toBeInTheDocument()
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
      const nextButton = screen.getByText('[NEXT]')

      fireEvent.change(textarea, { target: { value: 'Test query' } })
      fireEvent.click(nextButton)

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
      fireEvent.change(textarea, { target: { value: 'Test query' } })
      fireEvent.click(screen.getByText('[NEXT]'))

      expect(screen.getByText('[EXECUTE]')).toBeInTheDocument()
      expect(screen.getByText('[BACK]')).toBeInTheDocument()
    })

    it('should return to input when [BACK] is clicked', () => {
      render(<App />)
      const textarea = screen.getByPlaceholderText(/Enter your query.../i)
      fireEvent.change(textarea, { target: { value: 'Test query' } })
      fireEvent.click(screen.getByText('[NEXT]'))

      fireEvent.click(screen.getByText('[BACK]'))

      // Should be back at input phase
      expect(screen.getByPlaceholderText(/Enter your query.../i)).toBeInTheDocument()
      expect(screen.getByText('[NEXT]')).toBeInTheDocument()
    })

    it('should preserve query and cocktail when returning from confirmation', () => {
      render(<App />)
      const textarea = screen.getByPlaceholderText(/Enter your query.../i)
      const select = screen.getByRole('combobox')

      fireEvent.change(textarea, { target: { value: 'Test query' } })
      fireEvent.change(select, { target: { value: 'LUXE' } })
      fireEvent.click(screen.getByText('[NEXT]'))
      fireEvent.click(screen.getByText('[BACK]'))

      expect(textarea.value).toBe('Test query')
      expect(select.value).toBe('LUXE')
    })
  })

  describe('Running Phase', () => {
    it('should call submitQuery when [EXECUTE] is clicked', async () => {
      render(<App />)
      const textarea = screen.getByPlaceholderText(/Enter your query.../i)
      fireEvent.change(textarea, { target: { value: 'Test query' } })
      fireEvent.click(screen.getByText('[NEXT]'))

      fireEvent.click(screen.getByText('[EXECUTE]'))

      await waitFor(() => {
        expect(mockSubmitQuery).toHaveBeenCalledWith('Test query', 'SPEEDY')
      })
    })

    it('should show PROCESSING status during run', () => {
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
      fireEvent.change(textarea, { target: { value: 'Test query' } })
      fireEvent.click(screen.getByText('[NEXT]'))
      fireEvent.click(screen.getByText('[EXECUTE]'))

      expect(screen.getByText(/PROCESSING.../i)).toBeInTheDocument()
      expect(screen.getByText(/RUN_ID:/i)).toBeInTheDocument()
      expect(screen.getByText(/test_run_123/i)).toBeInTheDocument()
      expect(screen.getByText(/PHASE:/i)).toBeInTheDocument()
      expect(screen.getByText(/ROUND:/i)).toBeInTheDocument()
    })

    it('should display run metadata during processing', () => {
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
      fireEvent.change(textarea, { target: { value: 'Test query' } })
      fireEvent.click(screen.getByText('[NEXT]'))
      fireEvent.click(screen.getByText('[EXECUTE]'))

      expect(screen.getByText(/04_meta.json/i)).toBeInTheDocument()
      expect(screen.getByText(/ROUND:/i)).toBeInTheDocument()
      expect(screen.getAllByText(/R2/i).length).toBeGreaterThan(0)
    })

    it('should show artifacts during processing', () => {
      useUltrAIModule.useUltrAI.mockReturnValue({
        isLoading: true,
        currentRun: {
          run_id: 'test_run_123',
          phase: '04_meta.json',
          round: 'R2',
          completed: false,
          artifacts: ['03_initial.json', '04_meta.json'],
        },
        submitQuery: mockSubmitQuery,
      })

      render(<App />)
      const textarea = screen.getByPlaceholderText(/Enter your query.../i)
      fireEvent.change(textarea, { target: { value: 'Test query' } })
      fireEvent.click(screen.getByText('[NEXT]'))
      fireEvent.click(screen.getByText('[EXECUTE]'))

      expect(screen.getByText(/ARTIFACTS:/i)).toBeInTheDocument()
      expect(screen.getByText(/\[✓\] 03_initial.json/i)).toBeInTheDocument()
      expect(screen.getByText(/\[✓\] 04_meta.json/i)).toBeInTheDocument()
    })

    it('should show polling message', () => {
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
      fireEvent.change(textarea, { target: { value: 'Test query' } })
      fireEvent.click(screen.getByText('[NEXT]'))
      fireEvent.click(screen.getByText('[EXECUTE]'))

      expect(screen.getByText(/Polling every 2 seconds.../i)).toBeInTheDocument()
    })
  })

  describe('Results Phase', () => {
    it('should show completion status when run finishes', () => {
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
      fireEvent.change(textarea, { target: { value: 'Test query' } })
      fireEvent.click(screen.getByText('[NEXT]'))
      fireEvent.click(screen.getByText('[EXECUTE]'))

      expect(screen.getByText(/SYNTHESIS COMPLETE/i)).toBeInTheDocument()
      expect(screen.getByText(/OUTPUT:/i)).toBeInTheDocument()
      expect(screen.getByText(/UltrAI synthesis ready/i)).toBeInTheDocument()
    })

    it('should show artifact count in results', () => {
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
      fireEvent.change(textarea, { target: { value: 'Test query' } })
      fireEvent.click(screen.getByText('[NEXT]'))
      fireEvent.click(screen.getByText('[EXECUTE]'))

      expect(screen.getByText(/ARTIFACTS:/i)).toBeInTheDocument()
      expect(screen.getByText(/4 generated/i)).toBeInTheDocument()
    })

    it('should list all artifacts in results', () => {
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
      fireEvent.change(textarea, { target: { value: 'Test query' } })
      fireEvent.click(screen.getByText('[NEXT]'))
      fireEvent.click(screen.getByText('[EXECUTE]'))

      expect(screen.getByText(/→ 03_initial.json/i)).toBeInTheDocument()
      expect(screen.getByText(/→ 04_meta.json/i)).toBeInTheDocument()
      expect(screen.getByText(/→ 05_ultrai.json/i)).toBeInTheDocument()
    })

    it('should show [NEW QUERY] button when complete', () => {
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
      fireEvent.change(textarea, { target: { value: 'Test query' } })
      fireEvent.click(screen.getByText('[NEXT]'))
      fireEvent.click(screen.getByText('[EXECUTE]'))

      expect(screen.getByText('[NEW QUERY]')).toBeInTheDocument()
    })

    it('should reset to input phase when [NEW QUERY] is clicked', () => {
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
      fireEvent.change(textarea, { target: { value: 'Test query' } })
      fireEvent.click(screen.getByText('[NEXT]'))
      fireEvent.click(screen.getByText('[EXECUTE]'))

      fireEvent.click(screen.getByText('[NEW QUERY]'))

      // Should be back at input with cleared fields
      const newTextarea = screen.getByPlaceholderText(/Enter your query.../i)
      const select = screen.getByRole('combobox')
      expect(newTextarea.value).toBe('')
      expect(select.value).toBe('SPEEDY') // Default
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
