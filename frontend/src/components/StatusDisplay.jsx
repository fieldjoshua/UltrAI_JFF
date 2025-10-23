/**
 * StatusDisplay Component
 *
 * Shows granular real-time run status with hierarchical progress bars:
 * - System initialization
 * - R1 (INITIAL) parent with child steps for each ACTIVE LLM
 * - R2 (META) parent with child steps for each ACTIVE LLM
 * - R3 (ULTRA) parent with synthesis child steps
 * - Final statistics and packaging
 *
 * Features:
 * - Auto-scroll to keep latest steps visible
 * - Hierarchical indentation for grouped steps
 * - Purple progress for R1/R2/R3 parent phases
 * - FALLBACK substitution indicators
 */

import { useRef, useEffect } from 'react'

export function StatusDisplay({ run }) {
  const scrollContainerRef = useRef(null)
  const prevStepCountRef = useRef(0)

  if (!run) return null

  // Get steps from backend (new detailed tracking)
  const steps = run.steps || []

  // Auto-scroll when new steps are added
  useEffect(() => {
    if (steps.length > prevStepCountRef.current && scrollContainerRef.current) {
      scrollContainerRef.current.scrollTop = scrollContainerRef.current.scrollHeight
    }
    prevStepCountRef.current = steps.length
  }, [steps.length])

  // Terminal-style progress bar based on actual percentage (0-100)
  const renderProgressBar = (progress) => {
    const width = 20
    const filled = Math.floor((progress / 100) * width)
    const empty = width - filled
    return '[' + '█'.repeat(filled) + '░'.repeat(empty) + ']'
  }

  // Get status icon and color (with purple for R1/R2/R3 parents)
  const getStatusDisplay = (status, isParent = false) => {
    if (status === 'completed') {
      return { icon: '✓', color: isParent ? 'text-purple-500' : 'text-green-600', glowClass: '' }
    } else if (status === 'in_progress') {
      return { icon: '→', color: isParent ? 'text-purple-500 terminal-glow' : 'text-[#FF6B35]', glowClass: 'terminal-glow' }
    } else {
      return { icon: ' ', color: 'text-gray-600', glowClass: '' }
    }
  }

  // Determine if step is a parent (R1/R2/R3 section headers)
  const isParentStep = (stepText) => {
    return (
      stepText.match(/^R1: (Starting|All models|Querying)/) ||
      stepText.match(/^R2: (Preparing|Models reviewing|All revisions)/) ||
      stepText.match(/^R3: (Selecting|Reviewing|Synthesizing)/)
    )
  }

  // Determine indentation level
  const getIndentClass = (stepText) => {
    // Child steps under R1/R2/R3 get indented (individual model responses)
    if (
      stepText.match(/^R1: .*(completed|responding)/) ||
      stepText.match(/^R2: .*(revised|revising)/) ||
      stepText.match(/^R3: .*synthesis/)
    ) {
      return 'pl-4' // Indent model-specific steps
    }
    return '' // No indent for parent steps
  }

  return (
    <div className="space-y-4">
      {/* Status Header */}
      <div className="text-green-500 border-b border-green-900 pb-2">
        <span className="cursor-blink">█</span>{' '}
        {run.completed ? (
          <span className="text-[#FF6B35] terminal-glow">✓ SYNTHESIS COMPLETE</span>
        ) : (
          <span className="text-[#7C3AED] terminal-glow">⚡ PROCESSING...</span>
        )}
      </div>

      {/* Run ID */}
      <div className="text-green-600 text-xs font-mono">
        <span className="text-green-500">RUN_ID:</span> {run.run_id}
      </div>

      {/* Overall Progress Percentage */}
      {!run.completed && run.progress !== undefined && run.progress !== null && (
        <div className="text-green-600 text-xs font-mono">
          <span className="text-green-500">OVERALL:</span> {run.progress}%
        </div>
      )}

      {/* Detailed Step-by-Step Progress */}
      {steps.length > 0 && (
        <div className="space-y-1.5">
          <div className="text-green-500 text-xs font-mono border-b border-green-900 pb-1">
            PIPELINE_STEPS:
          </div>
          <div
            ref={scrollContainerRef}
            className="space-y-1 max-h-96 overflow-y-auto scroll-smooth"
          >
            {steps.map((step, index) => {
              const isParent = isParentStep(step.text)
              const { icon, color, glowClass } = getStatusDisplay(step.status, isParent)
              const progress = step.progress !== undefined ? step.progress : 0
              const indentClass = getIndentClass(step.text)

              return (
                <div key={index} className={`space-y-0.5 ${indentClass}`}>
                  {/* Step Text with Status Icon and Percentage */}
                  <div className="flex items-center justify-between text-xs font-mono">
                    <span className={`${color} ${glowClass} flex-1`}>
                      {icon} {step.text}
                      {step.fallback && (
                        <span className="text-yellow-500 ml-2 text-xs">
                          (FALLBACK: {step.fallback})
                        </span>
                      )}
                    </span>
                    <span className={color + " ml-2"}>
                      {progress}%
                    </span>
                  </div>

                  {/* Progress Bar with Time */}
                  <div className="flex items-center justify-between font-mono text-xs">
                    <span className={color}>
                      {renderProgressBar(progress)}
                    </span>
                    {step.time && (
                      <span className="text-green-600 ml-2 text-xs">
                        {step.time}
                      </span>
                    )}
                  </div>
                </div>
              )
            })}
          </div>
        </div>
      )}

      {/* Fallback for legacy runs (no detailed steps) */}
      {steps.length === 0 && !run.completed && (
        <div className="text-green-600 text-sm font-mono">
          → Processing... (polling every 100ms)
          {run.current_step && (
            <div className="text-[#6366F1] text-xs mt-1 pl-2">
              {run.current_step}
            </div>
          )}
        </div>
      )}

      {/* Error */}
      {run.error && (
        <div className="border border-red-500 p-3 mt-3">
          <div className="text-red-500 font-mono text-sm">
            <span className="cursor-blink">█</span> ERROR
          </div>
          <div className="text-red-400 text-xs mt-1 font-mono">{run.error}</div>
        </div>
      )}
    </div>
  )
}
