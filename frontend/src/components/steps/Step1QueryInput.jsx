/**
 * Step 1: Query Input
 *
 * Large text area for user to enter their query.
 * Validates before allowing next step.
 */

import { useState } from 'react'

export function Step1QueryInput({ initialValue, onNext }) {
  const [query, setQuery] = useState(initialValue || '')

  const handleNext = () => {
    if (query.trim()) {
      onNext(query)
    }
  }

  return (
    <div className="bg-white rounded-xl shadow-lg p-8 space-y-6">
      {/* Instructions */}
      <div className="bg-blue-50 border-l-4 border-blue-500 p-4 rounded">
        <p className="text-sm text-blue-900">
          <span className="font-semibold">💡 Tip:</span> Be specific about what
          you want to learn. UltrAI will synthesize responses from multiple
          models to give you the most comprehensive answer.
        </p>
      </div>

      {/* Large Text Area */}
      <div>
        <label
          htmlFor="query"
          className="block text-lg font-semibold text-gray-900 mb-3"
        >
          Your Query
        </label>
        <textarea
          id="query"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Example: Explain quantum computing in simple terms and its practical applications in 2025..."
          className="w-full px-6 py-4 text-lg border-2 border-gray-300 rounded-xl focus:ring-4 focus:ring-blue-200 focus:border-blue-500 resize-none transition-all"
          rows={8}
          autoFocus
        />
        <div className="flex justify-between items-center mt-2">
          <span className="text-sm text-gray-500">
            {query.length} characters
          </span>
          {query.length > 0 && query.length < 20 && (
            <span className="text-sm text-amber-600">
              ⚠️ Query seems short - add more detail for better results
            </span>
          )}
        </div>
      </div>

      {/* Example Queries */}
      <div>
        <div className="text-sm font-medium text-gray-700 mb-2">
          Example queries:
        </div>
        <div className="space-y-2">
          {[
            'What are the key differences between React and Vue.js for building modern web applications?',
            'Explain the implications of quantum computing on cybersecurity',
            'How can I optimize database queries for a high-traffic application?',
          ].map((example, idx) => (
            <button
              key={idx}
              onClick={() => setQuery(example)}
              className="w-full text-left text-sm text-gray-600 bg-gray-50 hover:bg-gray-100 rounded-lg p-3 transition-colors border border-gray-200"
            >
              {example}
            </button>
          ))}
        </div>
      </div>

      {/* Next Button */}
      <div className="flex justify-end pt-4">
        <button
          onClick={handleNext}
          disabled={!query.trim()}
          className={`px-8 py-3 rounded-xl font-semibold text-lg transition-all ${
            query.trim()
              ? 'bg-blue-600 text-white hover:bg-blue-700 shadow-lg hover:shadow-xl'
              : 'bg-gray-300 text-gray-500 cursor-not-allowed'
          }`}
        >
          Next: Choose Cocktail →
        </button>
      </div>
    </div>
  )
}
