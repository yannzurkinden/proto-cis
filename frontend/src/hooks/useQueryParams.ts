import { useCallback } from 'react'
import { useSearchParams } from 'react-router-dom'

/**
 * Hook for reading and writing URL query parameters.
 * Wraps react-router-dom's useSearchParams with convenience methods.
 */
export function useQueryParams() {
  const [searchParams, setSearchParams] = useSearchParams()

  const setParam = useCallback(
    (key: string, value: string) => {
      setSearchParams((prev) => {
        const next = new URLSearchParams(prev)
        next.set(key, value)
        return next
      })
    },
    [setSearchParams]
  )

  const removeParam = useCallback(
    (key: string) => {
      setSearchParams((prev) => {
        const next = new URLSearchParams(prev)
        next.delete(key)
        return next
      })
    },
    [setSearchParams]
  )

  const getParam = useCallback(
    (key: string): string | null => {
      return searchParams.get(key)
    },
    [searchParams]
  )

  return {
    params: searchParams,
    setParam,
    removeParam,
    getParam,
  }
}
