'use client'

import { useMemo } from 'react'
import { QueryClient, QueryClientProvider } from '@/lib/query'
import { SessionProvider } from '@/components/SessionProvider'

export function Providers({ children }: { children: React.ReactNode }) {
  const queryClient = useMemo(() => new QueryClient(), [])

  return (
    <SessionProvider>
      <QueryClientProvider client={queryClient}>
        {children}
      </QueryClientProvider>
    </SessionProvider>
  )
}
