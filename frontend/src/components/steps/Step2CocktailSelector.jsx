/**
 * Step 2: Cocktail Selector
 *
 * Visual cards for selecting model cocktail.
 * Shows model details and characteristics.
 */

import { useState } from 'react'
import { useCocktails } from '../../hooks/useCocktails'

export function Step2CocktailSelector({ initialValue, onNext, onBack }) {
  const [selected, setSelected] = useState(initialValue || 'SPEEDY')
  const { cocktails } = useCocktails()

  const handleNext = () => {
    const cocktail = cocktails.find((c) => c.id === selected)
    onNext(selected, cocktail.description)
  }

  return (
    <div className="bg-white rounded-xl shadow-lg p-8 space-y-6">
      {/* Instructions */}
      <div className="bg-purple-50 border-l-4 border-purple-500 p-4 rounded">
        <p className="text-sm text-purple-900">
          <span className="font-semibold">🍸 Cocktails:</span> Pre-configured
          sets of LLM models optimized for different use cases. Each cocktail
          uses 3 primary models for fast, high-quality synthesis.
        </p>
      </div>

      {/* Cocktail Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {cocktails.map((cocktail) => {
          const isSelected = selected === cocktail.id

          // Icon and color per cocktail
          const styles = {
            LUXE: { icon: '👑', color: 'purple', desc: 'Flagship models' },
            PREMIUM: { icon: '⭐', color: 'blue', desc: 'High quality' },
            SPEEDY: { icon: '⚡', color: 'green', desc: 'Fast responses' },
            BUDGET: { icon: '💰', color: 'amber', desc: 'Cost-effective' },
            DEPTH: { icon: '🧠', color: 'indigo', desc: 'Deep reasoning' },
          }[cocktail.id] || { icon: '🍸', color: 'gray', desc: 'Custom' }

          return (
            <button
              key={cocktail.id}
              onClick={() => setSelected(cocktail.id)}
              className={`text-left p-6 rounded-xl border-4 transition-all ${
                isSelected
                  ? `border-${styles.color}-500 bg-${styles.color}-50 shadow-lg scale-105`
                  : 'border-gray-200 bg-white hover:border-gray-300 hover:shadow-md'
              }`}
            >
              {/* Header */}
              <div className="flex items-center justify-between mb-3">
                <div className="flex items-center space-x-3">
                  <span className="text-3xl">{styles.icon}</span>
                  <div>
                    <h3 className="text-xl font-bold text-gray-900">
                      {cocktail.name}
                    </h3>
                    <p className="text-xs text-gray-600">{styles.desc}</p>
                  </div>
                </div>
                {isSelected && (
                  <div className="w-8 h-8 bg-blue-500 rounded-full flex items-center justify-center">
                    <span className="text-white font-bold">✓</span>
                  </div>
                )}
              </div>

              {/* Description */}
              <p className="text-sm text-gray-700 mb-4">
                {cocktail.description}
              </p>

              {/* Models */}
              <div className="space-y-1">
                <div className="text-xs font-semibold text-gray-600 uppercase">
                  Models (3)
                </div>
                {cocktail.models.slice(0, 3).map((model, idx) => (
                  <div
                    key={idx}
                    className="text-xs text-gray-600 bg-gray-100 rounded px-2 py-1"
                  >
                    {model}
                  </div>
                ))}
              </div>
            </button>
          )
        })}
      </div>

      {/* Navigation Buttons */}
      <div className="flex justify-between items-center pt-4">
        <button
          onClick={onBack}
          className="px-6 py-3 rounded-xl font-semibold text-gray-700 bg-gray-100 hover:bg-gray-200 transition-colors"
        >
          ← Back
        </button>
        <button
          onClick={handleNext}
          className="px-8 py-3 rounded-xl font-semibold text-lg bg-orange-500 text-white hover:bg-orange-600 shadow-lg hover:shadow-xl transition-all"
        >
          Next: Confirm →
        </button>
      </div>
    </div>
  )
}
