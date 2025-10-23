/**
 * StatusDisplay Component
 *
 * Shows granular real-time run status with individual progress bars for each step:
 * - System initialization
 * - Each ACTIVE LLM's INITIAL response (R1)
 * - Each ACTIVE LLM's META revision (R2)
 * - ULTRA LLM selection and synthesis (R3)
 * - Final statistics and packaging
 *
 * Each step gets its own terminal-style progress bar that shows completed/in-progress/pending
 */

export function StatusDisplay({ run }) {
  if (!run) return null

  // Get steps from backend (new detailed tracking)
  const steps = run.steps || []

  // Terminal-style progress bar (always 100% for individual steps)
  const renderProgressBar = (status) => {
    const width = 20
    if (status === 'completed') {
      return '[' + '█'.repeat(width) + ']'
    } else if (status === 'in_progress') {
      const filled = Math.floor(width * 0.6)  // Show ~60% for in-progress
      return '[' + '█'.repeat(filled) + '░'.repeat(width - filled) + ']'
    } else {
      // pending
      return '[' + '░'.repeat(width) + ']'
    }
  }

  // Get status icon and color
  const getStatusDisplay = (status) => {
    if (status === 'completed') {
      return { icon: '✓', color: 'text-green-600', glowClass: '' }
    } else if (status === 'in_progress') {
      return { icon: '→', color: 'text-[#FF6B35]', glowClass: 'terminal-glow' }
    } else {
      return { icon: ' ', color: 'text-gray-600', glowClass: '' }
    }
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
          <div className="space-y-1 max-h-96 overflow-y-auto">
            {steps.map((step, index) => {
              const { icon, color, glowClass } = getStatusDisplay(step.status)

              return (
                <div key={index} className="space-y-0.5">
                  {/* Step Text with Status Icon */}
                  <div className="flex items-center justify-between text-xs font-mono">
                    <span className={`${color} ${glowClass} flex-1`}>
                      {icon} {step.text}
                    </span>
                    {step.time && (
                      <span className="text-green-600 ml-2 text-xs">
                        {step.time}
                      </span>
                    )}
                  </div>

                  {/* Progress Bar */}
                  <div className="font-mono text-xs">
                    <span className={color}>
                      {renderProgressBar(step.status)}
                    </span>
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
          → Processing... (polling every 2s)
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
