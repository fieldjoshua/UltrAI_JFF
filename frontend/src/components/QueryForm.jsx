/**
 * QueryForm Component
 *
 * Allows users to:
 * - Enter their query
 * - Select a cocktail (PREMIUM, SPEEDY, BUDGET, DEPTH, LUXE)
 * - Submit to start UltrAI synthesis
 */

import { useState } from 'react'
import { useCocktails } from '../hooks/useCocktails'

export function QueryForm({ onSubmit, isLoading }) {
  const [query, setQuery] = useState('')
  const [selectedCocktail, setSelectedCocktail] = useState('SPEEDY')
  const { cocktails } = useCocktails()

  const handleSubmit = (e) => {
    e.preventDefault()
    if (query.trim() && selectedCocktail) {
      onSubmit(query, selectedCocktail)
    }
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      {/* Query Input */}
      <div>
        <label
          htmlFor="query"
          className="block text-sm font-medium text-gray-700 mb-2"
        >
          Your Query
        </label>
        <textarea
          id="query"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="What would you like UltrAI to analyze?"
          className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none"
          rows={4}
          disabled={isLoading}
          required
        />
      </div>

      {/* Cocktail Selection */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-3">
          Select Cocktail
        </label>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
          {cocktails.map((cocktail) => (
            <button
              key={cocktail.id}
              type="button"
              onClick={() => setSelectedCocktail(cocktail.id)}
              disabled={isLoading}
              className={`p-4 rounded-lg border-2 text-left transition-all ${
                selectedCocktail === cocktail.id
                  ? 'border-blue-500 bg-blue-50'
                  : 'border-gray-200 hover:border-gray-300 bg-white'
              } ${isLoading ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'}`}
            >
              <div className="font-semibold text-gray-900">{cocktail.name}</div>
              <div className="text-xs text-gray-600 mt-1">
                {cocktail.description}
              </div>
              <div className="text-xs text-gray-500 mt-2">
                {cocktail.models.length} models
              </div>
            </button>
          ))}
        </div>
      </div>

      {/* Submit Button */}
      <button
        type="submit"
        disabled={isLoading || !query.trim()}
        className={`w-full py-3 px-6 rounded-lg font-semibold transition-all ${
          isLoading || !query.trim()
            ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
            : 'bg-blue-600 text-white hover:bg-blue-700'
        }`}
      >
        {isLoading ? 'Running Synthesis...' : 'Start UltrAI Synthesis'}
      </button>
    </form>
  )
}
