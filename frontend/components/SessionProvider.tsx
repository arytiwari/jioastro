'use client'

import { useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { sessionManager } from '@/lib/sessionManager'

export function SessionProvider({ children }: { children: React.ReactNode }) {
  const router = useRouter()

  useEffect(() => {
    // Initialize session manager
    sessionManager.init(() => {
      // Callback when session expires
      console.log('🚪 Session expired, redirecting to login...')
      router.push('/auth/login?reason=session_expired')
    })

    // Cleanup on unmount
    return () => {
      sessionManager.destroy()
    }
  }, [router])

  return <>{children}</>
}
