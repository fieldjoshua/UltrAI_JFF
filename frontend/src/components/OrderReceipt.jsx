/**
 * OrderReceipt Component
 *
 * Running receipt on the right side that shows:
 * - What's been selected so far
 * - What's pending
 * - Total "order" of UltrAI features
 */

export function OrderReceipt({ order, currentStep }) {
  const steps = [
    { id: 1, label: 'Query', key: 'query' },
    { id: 2, label: 'Cocktail', key: 'cocktail' },
    { id: 3, label: 'Confirm', key: 'confirmed' },
  ]

  const getStepStatus = (step) => {
    if (step.id < currentStep) return 'completed'
    if (step.id === currentStep) return 'active'
    return 'pending'
  }

  const getStepIcon = (step) => {
    const status = getStepStatus(step)
    if (status === 'completed') return '✓'
    if (status === 'active') return '⏳'
    return '○'
  }

  return (
    <div className="bg-gradient-to-br from-slate-50 to-slate-100 rounded-xl shadow-lg p-6 border-2 border-slate-200">
      {/* Header */}
      <div className="border-b-2 border-slate-300 pb-3 mb-4">
        <h3 className="text-lg font-bold text-slate-800">Your UltrAI Order</h3>
        <p className="text-xs text-slate-600 mt-1">
          Configure your synthesis request
        </p>
      </div>

      {/* Order Items */}
      <div className="space-y-4">
        {/* Query */}
        <div className="flex items-start space-x-3">
          <span className="text-2xl">{getStepIcon(steps[0])}</span>
          <div className="flex-1">
            <div className="font-semibold text-slate-700">Query</div>
            {order.query ? (
              <div className="text-sm text-slate-600 mt-1 bg-white rounded p-2 border border-slate-200">
                {order.query.length > 60
                  ? order.query.substring(0, 60) + '...'
                  : order.query}
              </div>
            ) : (
              <div className="text-sm text-slate-400 italic mt-1">
                Not yet entered
              </div>
            )}
          </div>
        </div>

        {/* Cocktail */}
        <div className="flex items-start space-x-3">
          <span className="text-2xl">{getStepIcon(steps[1])}</span>
          <div className="flex-1">
            <div className="font-semibold text-slate-700">Cocktail</div>
            {order.cocktail ? (
              <div className="text-sm text-slate-600 mt-1 bg-white rounded p-2 border border-slate-200">
                <span className="font-medium text-blue-700">
                  {order.cocktail}
                </span>
                <div className="text-xs text-slate-500 mt-1">
                  {order.cocktailDescription}
                </div>
              </div>
            ) : (
              <div className="text-sm text-slate-400 italic mt-1">
                Not yet selected
              </div>
            )}
          </div>
        </div>

        {/* Analysis Type */}
        <div className="flex items-start space-x-3">
          <span className="text-2xl">{getStepIcon(steps[2])}</span>
          <div className="flex-1">
            <div className="font-semibold text-slate-700">Analysis</div>
            <div className="text-sm text-slate-600 mt-1 bg-white rounded p-2 border border-slate-200">
              <span className="font-medium">Synthesis</span>
              <div className="text-xs text-slate-500 mt-1">
                R1 → R2 → R3 rounds
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Summary */}
      <div className="mt-6 pt-4 border-t-2 border-slate-300">
        <div className="flex justify-between text-sm">
          <span className="text-slate-600">Total Steps</span>
          <span className="font-semibold text-slate-800">3 Rounds</span>
        </div>
        <div className="flex justify-between text-sm mt-2">
          <span className="text-slate-600">Expected Time</span>
          <span className="font-semibold text-slate-800">~30-60 sec</span>
        </div>
      </div>

      {/* Status Badge */}
      <div className="mt-4">
        {currentStep < 4 ? (
          <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-3 text-center">
            <div className="text-sm font-semibold text-yellow-800">
              ⚡ Configuration In Progress
            </div>
            <div className="text-xs text-yellow-700 mt-1">
              Step {currentStep} of 3
            </div>
          </div>
        ) : (
          <div className="bg-green-50 border border-green-200 rounded-lg p-3 text-center">
            <div className="text-sm font-semibold text-green-800">
              ✓ Ready to Activate
            </div>
            <div className="text-xs text-green-700 mt-1">All steps complete</div>
          </div>
        )}
      </div>
    </div>
  )
}
