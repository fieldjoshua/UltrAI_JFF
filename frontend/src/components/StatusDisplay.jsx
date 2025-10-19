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

  return (
    <div className="bg-white rounded-lg shadow-md p-6 space-y-4">
      {/* Header */}
      <div className="flex items-center justify-between">
        <h2 className="text-xl font-bold text-gray-900">Run Status</h2>
        <span
          className={`px-3 py-1 rounded-full text-sm font-semibold shadow-lg ${
            run.completed
              ? 'bg-gradient-to-r from-[#FF6B35] to-[#F97316] text-white shadow-[0_0_15px_rgba(255,107,53,0.5)]'
              : 'bg-gradient-to-r from-[#7C3AED] to-[#6366F1] text-white shadow-[0_0_15px_rgba(124,58,237,0.5)] animate-pulse'
          }`}
        >
          {run.completed ? '✓ Completed' : '⚡ In Progress'}
        </span>
      </div>

      {/* Run ID */}
      <div className="text-sm text-gray-600">
        <span className="font-medium">Run ID:</span>{' '}
        <code className="bg-gray-100 px-2 py-1 rounded">{run.run_id}</code>
      </div>

      {/* Current Phase */}
      <div>
        <div className="text-sm font-medium text-gray-700 mb-2">
          Current Phase
        </div>
        <div className="bg-gradient-to-br from-[#7C3AED]/10 to-[#6366F1]/10 border-2 border-[#7C3AED] rounded-lg p-3 shadow-[0_0_15px_rgba(124,58,237,0.2)]">
          <div className="font-bold text-[#7C3AED]">
            {phaseNames[run.phase] || run.phase}
          </div>
          {run.round && (
            <div className="text-sm text-[#6366F1] mt-1 font-medium">
              {roundNames[run.round] || run.round}
            </div>
          )}
        </div>
      </div>

      {/* Progress Bar */}
      {!run.completed && run.progress !== undefined && run.progress !== null && (
        <div className="space-y-2">
          {/* Progress Bar */}
          <div className="w-full bg-gray-800 rounded-full h-5 overflow-hidden shadow-lg">
            <div
              className="bg-gradient-to-r from-[#7C3AED] via-[#6366F1] to-[#FF6B35] h-full transition-all duration-500 ease-out flex items-center justify-center text-xs font-bold text-white shadow-[0_0_20px_rgba(124,58,237,0.5)]"
              style={{ width: `${run.progress}%` }}
            >
              {run.progress > 10 && `${run.progress}%`}
            </div>
          </div>
          {/* Current Step */}
          {run.current_step && (
            <div className="flex items-center space-x-2 text-sm font-medium text-gray-700">
              <div className="animate-spin h-4 w-4 border-2 border-[#7C3AED] border-t-transparent rounded-full shadow-[0_0_10px_rgba(124,58,237,0.4)]"></div>
              <span className="text-[#7C3AED]">{run.current_step}</span>
            </div>
          )}
          {/* Last Update */}
          {run.last_update && (
            <div className="text-xs text-gray-500">
              Last updated: {new Date(run.last_update).toLocaleTimeString()}
            </div>
          )}
        </div>
      )}

      {/* Fallback Progress Indicator (for older runs without progress tracking) */}
      {!run.completed && (!run.progress || run.progress === null) && (
        <div className="flex items-center space-x-2">
          <div className="animate-spin h-5 w-5 border-2 border-blue-500 border-t-transparent rounded-full"></div>
          <span className="text-sm text-gray-600">
            Processing... (updates every 2 seconds)
          </span>
        </div>
      )}

      {/* Error */}
      {run.error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-3">
          <div className="font-semibold text-red-900">Error</div>
          <div className="text-sm text-red-700 mt-1">{run.error}</div>
        </div>
      )}
    </div>
  )
}
