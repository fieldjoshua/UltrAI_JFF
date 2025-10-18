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
          className={`px-3 py-1 rounded-full text-sm font-semibold ${
            run.completed
              ? 'bg-green-100 text-green-800'
              : 'bg-blue-100 text-blue-800'
          }`}
        >
          {run.completed ? 'Completed' : 'In Progress'}
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
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-3">
          <div className="font-semibold text-blue-900">
            {phaseNames[run.phase] || run.phase}
          </div>
          {run.round && (
            <div className="text-sm text-blue-700 mt-1">
              {roundNames[run.round] || run.round}
            </div>
          )}
        </div>
      </div>

      {/* Progress Indicator */}
      {!run.completed && (
        <div className="flex items-center space-x-2">
          <div className="animate-spin h-5 w-5 border-2 border-blue-500 border-t-transparent rounded-full"></div>
          <span className="text-sm text-gray-600">
            Processing... (updates every 2 seconds)
          </span>
        </div>
      )}

      {/* Artifacts */}
      {run.artifacts && run.artifacts.length > 0 && (
        <div>
          <div className="text-sm font-medium text-gray-700 mb-2">
            Artifacts Generated ({run.artifacts.length})
          </div>
          <div className="bg-gray-50 rounded-lg p-3">
            <ul className="space-y-1 text-sm text-gray-700">
              {run.artifacts.map((artifact, idx) => (
                <li key={idx} className="flex items-center space-x-2">
                  <span className="text-green-500">✓</span>
                  <code className="text-xs">{artifact}</code>
                </li>
              ))}
            </ul>
          </div>
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
