'use client'

import { useEffect, useMemo } from 'react'
import { QueryClient, QueryClientProvider } from '@/lib/query'
import { apiClient } from '@/lib/api'
import { onAuthStateChange } from '@/lib/supabase'

export function Providers({ children }: { children: React.ReactNode }) {
  const queryClient = useMemo(() => new QueryClient(), [])

  useEffect(() => {
    let isMounted = true

    void apiClient.loadToken()

    const {
      data: { subscription },
    } = onAuthStateChange((_, session) => {
      if (!isMounted) return

      if (session?.access_token) {
        apiClient.setToken(session.access_token)
      } else {
        apiClient.clearToken()
      }
    })

    return () => {
      isMounted = false
      subscription.unsubscribe()
    }
  }, [])

  return (
    <QueryClientProvider client={queryClient}>
      {children}
    </QueryClientProvider>
  )
}
