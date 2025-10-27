/**
 * Authentication hook for protecting routes
 */

import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import { getCurrentUser } from '@/lib/supabase'
import { apiClient } from '@/lib/api'

export function useAuth(requireAuth: boolean = true) {
  const router = useRouter()
  const [loading, setLoading] = useState(true)
  const [user, setUser] = useState<any>(null)

  useEffect(() => {
    const checkAuth = async () => {
      const currentUser = await getCurrentUser()

      if (!currentUser && requireAuth) {
        router.push('/auth/login')
        return
      }

      if (currentUser) {
        setUser(currentUser)
        apiClient.loadToken()
      }

      setLoading(false)
    }

    checkAuth()
  }, [requireAuth, router])

  return { user, loading }
}
