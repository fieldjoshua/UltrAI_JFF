/**
 * StepIndicator Component
 *
 * Visual progress indicator at the top showing:
 * - Current step
 * - Completed steps
 * - Upcoming steps
 */

export function StepIndicator({ currentStep, totalSteps = 3 }) {
  const steps = [
    { number: 1, label: 'Enter Query' },
    { number: 2, label: 'Choose Cocktail' },
    { number: 3, label: 'Confirm & Activate' },
  ]

  return (
    <div className="w-full">
      {/* Step Progress Bar */}
      <div className="flex items-center justify-between mb-6">
        {steps.map((step, index) => (
          <div key={step.number} className="flex-1 flex items-center">
            {/* Step Circle */}
            <div className="relative flex flex-col items-center">
              <div
                className={`w-12 h-12 rounded-full flex items-center justify-center font-bold text-lg border-4 transition-all ${
                  step.number < currentStep
                    ? 'bg-green-500 border-green-500 text-white'
                    : step.number === currentStep
                      ? 'bg-blue-500 border-blue-500 text-white animate-pulse'
                      : 'bg-gray-200 border-gray-300 text-gray-500'
                }`}
              >
                {step.number < currentStep ? '✓' : step.number}
              </div>
              {/* Step Label */}
              <div
                className={`absolute -bottom-8 text-sm font-medium whitespace-nowrap ${
                  step.number === currentStep
                    ? 'text-blue-700'
                    : step.number < currentStep
                      ? 'text-green-700'
                      : 'text-gray-500'
                }`}
              >
                {step.label}
              </div>
            </div>

            {/* Connector Line */}
            {index < steps.length - 1 && (
              <div
                className={`flex-1 h-1 mx-4 transition-all ${
                  step.number < currentStep
                    ? 'bg-green-500'
                    : 'bg-gray-300'
                }`}
              />
            )}
          </div>
        ))}
      </div>

      {/* Current Step Description */}
      <div className="text-center mt-12 mb-4">
        <h2 className="text-2xl font-bold text-gray-900">
          {steps[currentStep - 1]?.label}
        </h2>
        <p className="text-sm text-gray-600 mt-2">
          {currentStep === 1 && 'What would you like UltrAI to analyze?'}
          {currentStep === 2 && 'Select the model cocktail for your synthesis'}
          {currentStep === 3 && 'Review your configuration and launch UltrAI'}
        </p>
      </div>
    </div>
  )
}
