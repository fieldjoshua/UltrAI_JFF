/**
 * StatusDisplay Component
 *
 * Shows real-time run status with stacking progress bars for each phase:
 * - System Readiness (00_ready.json)
 * - User Input (01_inputs.json)
 * - Active LLMs (02_activate.json)
 * - Initial Round R1 (03_initial.json)
 * - Meta Round R2 (04_meta.json)
 * - UltrAI Synthesis R3 (05_ultrai.json)
 *
 * Each phase gets its own terminal-style progress bar that levels up to 100%
 */

export function StatusDisplay({ run }) {
  if (!run) return null

  // Define all phases in order
  const phases = [
    { id: '00_ready.json', name: 'System Readiness', color: 'text-green-500' },
    { id: '01_inputs.json', name: 'User Input', color: 'text-green-500' },
    { id: '02_activate.json', name: 'Active LLMs', color: 'text-green-500' },
    { id: '03_initial.json', name: 'R1: Initial Round', color: 'text-[#7C3AED]' },
    { id: '04_meta.json', name: 'R2: Meta Round', color: 'text-[#FF6B35]' },
    { id: '05_ultrai.json', name: 'R3: UltrAI Synthesis', color: 'text-[#6366F1]' },
  ]

  // Calculate progress for each phase
  const getPhaseProgress = (phaseId) => {
    const artifacts = run.artifacts || []

    // If artifact exists, phase is 100% complete
    if (artifacts.includes(phaseId)) {
      return 100
    }

    // If this is the current phase, use the overall progress
    if (run.phase === phaseId && run.progress !== undefined && run.progress !== null) {
      return run.progress
    }

    // If we're past this phase (current phase is later), show 100%
    const currentIndex = phases.findIndex(p => p.id === run.phase)
    const thisIndex = phases.findIndex(p => p.id === phaseId)
    if (currentIndex > thisIndex) {
      return 100
    }

    // Otherwise phase hasn't started yet
    return 0
  }

  // Terminal-style progress bar
  const renderProgressBar = (percent) => {
    const width = 25
    const filled = Math.floor((percent / 100) * width)
    const empty = width - filled
    return '[' + '█'.repeat(filled) + '░'.repeat(empty) + ']'
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

      {/* Stacking Progress Bars */}
      <div className="space-y-2">
        <div className="text-green-500 text-sm font-mono border-b border-green-900 pb-1">
          PIPELINE_PROGRESS:
        </div>
        {phases.map((phase) => {
          const progress = getPhaseProgress(phase.id)
          const isActive = run.phase === phase.id && !run.completed
          const isComplete = progress === 100

          return (
            <div key={phase.id} className="space-y-0.5">
              {/* Phase Name */}
              <div className="flex items-center justify-between text-xs font-mono">
                <span className={isActive ? phase.color + ' terminal-glow' : isComplete ? 'text-green-600' : 'text-gray-600'}>
                  {isActive && '→ '}
                  {isComplete && '✓ '}
                  {!isActive && !isComplete && '  '}
                  {phase.name}
                </span>
                <span className={isActive ? 'text-[#FF6B35]' : isComplete ? 'text-green-500' : 'text-gray-600'}>
                  {progress}%
                </span>
              </div>

              {/* Progress Bar */}
              <div className="font-mono text-xs">
                <span className={isActive ? phase.color + ' terminal-glow' : isComplete ? 'text-green-600' : 'text-gray-700'}>
                  {renderProgressBar(progress)}
                </span>
              </div>
            </div>
          )
        })}
      </div>

      {/* Current Step Detail (optional extra info) */}
      {!run.completed && run.current_step && (
        <div className="border-t border-green-900 pt-3">
          <div className="text-[#6366F1] text-xs font-mono">
            → {run.current_step}
          </div>
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
