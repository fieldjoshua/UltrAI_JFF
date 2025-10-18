/**
 * useCocktails Hook - Cocktail Configuration Data
 *
 * Returns static cocktail definitions matching backend configuration.
 * This is client-side data, not fetched from API (cocktails are immutable).
 */

export function useCocktails() {
  const cocktails = [
    {
      id: 'PREMIUM',
      name: 'Premium',
      description: 'High-quality models focused on accuracy and capability',
      models: [
        'anthropic/claude-3.7-sonnet',
        'openai/chatgpt-4o-latest',
        'meta-llama/llama-3.3-70b-instruct',
      ],
    },
    {
      id: 'SPEEDY',
      name: 'Speedy',
      description: 'Fast models optimized for quick responses',
      models: [
        'openai/gpt-4o-mini',
        'anthropic/claude-3.5-haiku',
        'google/gemini-2.0-flash-exp:free',
      ],
    },
    {
      id: 'BUDGET',
      name: 'Budget',
      description: 'Cost-effective models balancing quality and expense',
      models: [
        'openai/gpt-3.5-turbo',
        'google/gemini-2.0-flash-exp:free',
        'qwen/qwen-2.5-72b-instruct',
      ],
    },
    {
      id: 'DEPTH',
      name: 'Depth',
      description: 'Deep reasoning models for complex analytical tasks',
      models: [
        'anthropic/claude-3.7-sonnet',
        'openai/gpt-4o',
        'meta-llama/llama-3.3-70b-instruct',
      ],
    },
    {
      id: 'LUXE',
      name: 'Luxe',
      description: 'Flagship premium models for highest quality results',
      models: [
        'openai/gpt-4o',
        'anthropic/claude-sonnet-4.5',
        'google/gemini-2.0-flash-exp:free',
      ],
    },
  ]

  return { cocktails }
}
