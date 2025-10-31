'use client'

import { useMemo } from 'react'
import { QueryClient, QueryClientProvider } from '@/lib/query'

export function Providers({ children }: { children: React.ReactNode }) {
  const queryClient = useMemo(() => new QueryClient(), [])

  return (
    <QueryClientProvider client={queryClient}>
      {children}
    </QueryClientProvider>
  )
}
