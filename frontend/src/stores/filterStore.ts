import { create } from 'zustand'
import { persist } from 'zustand/middleware'

interface FilterState {
  filters: Record<string, Record<string, string>>
  setFilter: (page: string, key: string, value: string) => void
  getFilters: (page: string) => Record<string, string>
  clearFilters: (page: string) => void
}

export const useFilterStore = create<FilterState>()(
  persist(
    (set, get) => ({
      filters: {},
      setFilter: (page, key, value) =>
        set((state) => ({
          filters: {
            ...state.filters,
            [page]: {
              ...(state.filters[page] || {}),
              [key]: value,
            },
          },
        })),
      getFilters: (page) => {
        return get().filters[page] || {}
      },
      clearFilters: (page) =>
        set((state) => {
          const { [page]: _, ...rest } = state.filters
          return { filters: rest }
        }),
    }),
    {
      name: 'cis-filters',
    }
  )
)
