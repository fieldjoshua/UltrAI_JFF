/**
 * UltrAI App - Multi-Step Wizard Interface
 *
 * Flow:
 * 1. Query Input (large text area)
 * 2. Cocktail Selection (visual cards)
 * 3. Confirm & Activate (big button emerges)
 * 4. Status Display (while running)
 * 5. Results Display (when complete)
 *
 * Right Side: OrderReceipt (running summary)
 */

import { useState } from 'react'
import { useUltrAI } from './hooks/useUltrAI'
import { useHealth } from './hooks/useHealth'
import { StepIndicator } from './components/StepIndicator'
import { OrderReceipt } from './components/OrderReceipt'
import { Step1QueryInput } from './components/steps/Step1QueryInput'
import { Step2CocktailSelector } from './components/steps/Step2CocktailSelector'
import { Step3Confirm } from './components/steps/Step3Confirm'
import { StatusDisplay } from './components/StatusDisplay'
import { ResultsDisplay } from './components/ResultsDisplay'

function App() {
  const [currentStep, setCurrentStep] = useState(1)
  const [order, setOrder] = useState({
    query: '',
    cocktail: '',
    cocktailDescription: '',
  })

  const { isHealthy, isLoading: healthLoading } = useHealth()
  const { isLoading, currentRun, submitQuery } = useUltrAI()

  // Step 1: Query entered
  const handleQueryNext = (query) => {
    setOrder({ ...order, query })
    setCurrentStep(2)
  }

  // Step 2: Cocktail selected
  const handleCocktailNext = (cocktail, description) => {
    setOrder({ ...order, cocktail, cocktailDescription: description })
    setCurrentStep(3)
  }

  // Step 3: Activate UltrAI
  const handleActivate = async () => {
    await submitQuery(order.query, order.cocktail)
    setCurrentStep(4) // Move to status display
  }

  // Start new query
  const handleNewQuery = () => {
    setCurrentStep(1)
    setOrder({ query: '', cocktail: '', cocktailDescription: '' })
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-purple-50">
      {/* Header */}
      <header className="bg-gradient-to-r from-blue-600 to-purple-600 text-white shadow-lg">
        <div className="container mx-auto px-6 py-8">
          <h1 className="text-4xl font-bold text-center mb-2">
            🚀 UltrAI Synthesis
          </h1>
          <p className="text-center text-blue-100">
            Multi-LLM Convergent Intelligence Platform
          </p>
        </div>
      </header>

      {/* Health Check */}
      {healthLoading && (
        <div className="bg-yellow-50 border-b border-yellow-200 py-2 text-center text-sm text-yellow-800">
          Checking backend connection...
        </div>
      )}
      {!healthLoading && !isHealthy && (
        <div className="bg-red-50 border-b border-red-200 py-3 text-center">
          <span className="text-red-800 font-semibold">
            ⚠️ Backend not available
          </span>
          <span className="text-red-600 text-sm ml-2">
            - Please start the backend server
          </span>
        </div>
      )}

      {/* Main Content */}
      <main className="container mx-auto px-6 py-8">
        {/* Wizard Steps 1-3 */}
        {currentStep <= 3 && (
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Left: Main Content (2/3 width) */}
            <div className="lg:col-span-2 space-y-6">
              {/* Step Indicator */}
              <StepIndicator currentStep={currentStep} />

              {/* Step Content */}
              {currentStep === 1 && (
                <Step1QueryInput
                  initialValue={order.query}
                  onNext={handleQueryNext}
                />
              )}
              {currentStep === 2 && (
                <Step2CocktailSelector
                  initialValue={order.cocktail}
                  onNext={handleCocktailNext}
                  onBack={() => setCurrentStep(1)}
                />
              )}
              {currentStep === 3 && (
                <Step3Confirm
                  order={order}
                  onActivate={handleActivate}
                  onBack={() => setCurrentStep(2)}
                  isActivating={isLoading}
                />
              )}
            </div>

            {/* Right: Order Receipt (1/3 width) */}
            <div className="lg:col-span-1">
              <div className="sticky top-6">
                <OrderReceipt order={order} currentStep={currentStep} />
              </div>
            </div>
          </div>
        )}

        {/* Step 4: Status Display (while running) */}
        {currentStep === 4 && currentRun && !currentRun.completed && (
          <div className="max-w-4xl mx-auto">
            <StatusDisplay run={currentRun} />
          </div>
        )}

        {/* Step 5: Results Display (when complete) */}
        {currentStep === 4 && currentRun && currentRun.completed && (
          <div className="max-w-5xl mx-auto space-y-6">
            <ResultsDisplay run={currentRun} onNewQuery={handleNewQuery} />
            {/* Show status below results for reference */}
            <details className="mt-6">
              <summary className="cursor-pointer text-sm text-gray-600 hover:text-gray-900 font-medium">
                View Run Details
              </summary>
              <div className="mt-4">
                <StatusDisplay run={currentRun} />
              </div>
            </details>
          </div>
        )}
      </main>

      {/* Footer */}
      <footer className="border-t border-gray-200 mt-16 py-6">
        <div className="container mx-auto px-6 text-center text-sm text-gray-600">
          <p>
            UltrAI Synthesis Platform | R1 → R2 → R3 Convergent Intelligence
          </p>
        </div>
      </footer>
    </div>
  )
}

export default App
