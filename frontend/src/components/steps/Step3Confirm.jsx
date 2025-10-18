/**
 * Step 3: Confirm & Activate
 *
 * Final review and the big "Activate UltrAI" button.
 * Shows summary of selections and initiates synthesis.
 */

export function Step3Confirm({ order, onActivate, onBack, isActivating }) {
  return (
    <div className="bg-white rounded-xl shadow-lg p-8 space-y-6">
      {/* Confirmation Banner */}
      <div className="bg-gradient-to-r from-green-50 to-blue-50 border-2 border-green-200 rounded-xl p-6">
        <div className="flex items-center space-x-3 mb-2">
          <span className="text-3xl">✨</span>
          <h3 className="text-2xl font-bold text-gray-900">
            Ready to Launch UltrAI
          </h3>
        </div>
        <p className="text-gray-700">
          Your synthesis request is configured and ready. Review the details
          below and activate when ready.
        </p>
      </div>

      {/* Order Summary */}
      <div className="space-y-4">
        {/* Query Summary */}
        <div className="bg-gray-50 rounded-lg p-4 border border-gray-200">
          <div className="text-sm font-semibold text-gray-600 uppercase mb-2">
            Query
          </div>
          <div className="text-gray-900 leading-relaxed">{order.query}</div>
        </div>

        {/* Cocktail Summary */}
        <div className="bg-gray-50 rounded-lg p-4 border border-gray-200">
          <div className="text-sm font-semibold text-gray-600 uppercase mb-2">
            Cocktail
          </div>
          <div className="text-xl font-bold text-blue-700 mb-1">
            {order.cocktail}
          </div>
          <div className="text-sm text-gray-600">
            {order.cocktailDescription}
          </div>
        </div>

        {/* Process Summary */}
        <div className="bg-gray-50 rounded-lg p-4 border border-gray-200">
          <div className="text-sm font-semibold text-gray-600 uppercase mb-3">
            Synthesis Process
          </div>
          <div className="space-y-2 text-sm text-gray-700">
            <div className="flex items-center space-x-2">
              <span className="text-blue-500 font-bold">R1</span>
              <span>→ Initial Round: Independent model responses</span>
            </div>
            <div className="flex items-center space-x-2">
              <span className="text-purple-500 font-bold">R2</span>
              <span>→ Meta Round: Peer review and revisions</span>
            </div>
            <div className="flex items-center space-x-2">
              <span className="text-green-500 font-bold">R3</span>
              <span>→ UltrAI Synthesis: Final convergent output</span>
            </div>
          </div>
        </div>

        {/* Expected Time */}
        <div className="bg-amber-50 border border-amber-200 rounded-lg p-4">
          <div className="flex items-center space-x-2">
            <span className="text-xl">⏱️</span>
            <div>
              <div className="text-sm font-semibold text-amber-900">
                Expected Processing Time
              </div>
              <div className="text-sm text-amber-700">
                Approximately 30-60 seconds
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Navigation Buttons */}
      <div className="flex justify-between items-center pt-6">
        <button
          onClick={onBack}
          disabled={isActivating}
          className={`px-6 py-3 rounded-xl font-semibold transition-colors ${
            isActivating
              ? 'bg-gray-200 text-gray-400 cursor-not-allowed'
              : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
          }`}
        >
          ← Back
        </button>

        {/* THE BIG ACTIVATE BUTTON */}
        <button
          onClick={onActivate}
          disabled={isActivating}
          className={`px-12 py-4 rounded-xl font-bold text-xl transition-all ${
            isActivating
              ? 'bg-gray-400 text-gray-200 cursor-not-allowed'
              : 'bg-gradient-to-r from-blue-600 to-purple-600 text-white hover:from-blue-700 hover:to-purple-700 shadow-2xl hover:shadow-3xl transform hover:scale-105'
          }`}
        >
          {isActivating ? (
            <span className="flex items-center space-x-3">
              <div className="animate-spin h-6 w-6 border-4 border-white border-t-transparent rounded-full"></div>
              <span>Activating UltrAI...</span>
            </span>
          ) : (
            <span className="flex items-center space-x-2">
              <span>🚀</span>
              <span>Activate UltrAI</span>
            </span>
          )}
        </button>
      </div>
    </div>
  )
}
