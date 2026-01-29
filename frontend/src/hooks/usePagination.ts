import { useState, useCallback } from 'react'

interface PaginationState {
  page: number
  size: number
  total: number
  pages: number
}

export function usePagination(initialPage = 1, initialSize = 20) {
  const [pagination, setPagination] = useState<PaginationState>({
    page: initialPage,
    size: initialSize,
    total: 0,
    pages: 0,
  })

  const setPage = useCallback((page: number) => {
    setPagination((prev) => ({ ...prev, page }))
  }, [])

  const setSize = useCallback((size: number) => {
    setPagination((prev) => ({ ...prev, size, page: 1 }))
  }, [])

  const setTotal = useCallback((total: number, pages: number) => {
    setPagination((prev) => ({ ...prev, total, pages }))
  }, [])

  const nextPage = useCallback(() => {
    setPagination((prev) => {
      if (prev.page < prev.pages) {
        return { ...prev, page: prev.page + 1 }
      }
      return prev
    })
  }, [])

  const prevPage = useCallback(() => {
    setPagination((prev) => {
      if (prev.page > 1) {
        return { ...prev, page: prev.page - 1 }
      }
      return prev
    })
  }, [])

  return {
    pagination,
    setPage,
    setSize,
    setTotal,
    nextPage,
    prevPage,
  }
}
