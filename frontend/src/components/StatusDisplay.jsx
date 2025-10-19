/**
 * StatusDisplay Component
 *
 * Shows real-time run status:
 * - Current phase (00_ready.json → 05_ultrai.json)
 * - Current round (R1, R2, R3)
 * - Progress indicator
 * - Artifacts generated
 */

export function StatusDisplay({ run }) {
  if (!run) return null

  const phaseNames = {
    '00_ready.json': 'System Readiness',
    '01_inputs.json': 'User Input',
    '02_activate.json': 'Active LLMs',
    '03_initial.json': 'Initial Round (R1)',
    '04_meta.json': 'Meta Round (R2)',
    '05_ultrai.json': 'UltrAI Synthesis (R3)',
    '06_final.json': 'Final Delivery',
  }

  const roundNames = {
    R1: 'Initial Round - Independent Responses',
    R2: 'Meta Round - Peer Review & Revision',
    R3: 'UltrAI Synthesis - Final Merge',
  }

  // Terminal-style progress bar
  const renderProgressBar = (percent) => {
    const width = 30
    const filled = Math.floor((percent / 100) * width)
    const empty = width - filled
    return '[' + '█'.repeat(filled) + '░'.repeat(empty) + ']'
  }

  return (
    <div className="space-y-3">
      {/* Status Header */}
      <div className="text-green-500 border-b border-green-900 pb-2">
        <span className="cursor-blink">█</span>{' '}
        {run.completed ? (
          <span className="text-[#FF6B35]">✓ COMPLETED</span>
        ) : (
          <span className="text-[#7C3AED] terminal-glow">⚡ PROCESSING...</span>
        )}
      </div>

      {/* Run ID */}
      <div className="text-green-600 text-sm font-mono">
        <span className="text-green-500">RUN_ID:</span> {run.run_id}
      </div>

      {/* Current Phase */}
      <div className="text-sm font-mono">
        <div className="text-green-500">PHASE:</div>
        <div className="text-[#7C3AED] pl-2 terminal-glow">
          → {phaseNames[run.phase] || run.phase}
        </div>
        {run.round && (
          <div className="text-[#6366F1] pl-2 mt-1">
            → {roundNames[run.round] || run.round}
          </div>
        )}
      </div>

      {/* Progress Bar */}
      {!run.completed && run.progress !== undefined && run.progress !== null && (
        <div className="space-y-1">
          <div className="text-green-500 text-sm font-mono">PROGRESS:</div>
          <div className="font-mono text-sm">
            <span className="text-[#7C3AED] terminal-glow">
              {renderProgressBar(run.progress)}
            </span>
            <span className="text-[#FF6B35] ml-2">{run.progress}%</span>
          </div>
          {run.current_step && (
            <div className="text-[#6366F1] text-xs font-mono pl-2">
              → {run.current_step}
            </div>
          )}
        </div>
      )}

      {/* Fallback for older runs */}
      {!run.completed && (!run.progress || run.progress === null) && (
        <div className="text-green-600 text-sm font-mono">
          → Processing... (polling every 2s)
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
