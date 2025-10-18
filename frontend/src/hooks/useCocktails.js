import { useState, useEffect } from 'react'

const COCKTAILS = ['PREMIUM', 'SPEEDY', 'BUDGET', 'DEPTH']

export function useCocktails() {
  const [cocktails, setCocktails] = useState(COCKTAILS)
  const [isLoading, setIsLoading] = useState(false)

  useEffect(() => {
    // Currently returns static list
    // Future: could fetch from backend GET /cocktails endpoint
    setCocktails(COCKTAILS)
    setIsLoading(false)
  }, [])

  return { cocktails, isLoading }
}