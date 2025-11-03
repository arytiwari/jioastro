export interface SupabaseUser {
  id: string
  email?: string
  [key: string]: unknown
}

export interface SupabaseSession {
  access_token: string
  refresh_token?: string
  expires_at?: number
  token_type?: string
  user: SupabaseUser | null
}

interface AuthResponse {
  data: { user: SupabaseUser | null; session: SupabaseSession | null }
  error: Error | null
}

const STORAGE_KEY = 'supabase.session'

function getConfig() {
  const url = process.env.NEXT_PUBLIC_SUPABASE_URL
  const anonKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY

  if (!url || !anonKey) {
    throw new Error('Supabase URL or anon key is not configured')
  }

  return { url: url.replace(/\/$/, ''), anonKey }
}

function storeSession(session: SupabaseSession | null) {
  if (typeof window === 'undefined') return
  if (session) {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(session))
  } else {
    localStorage.removeItem(STORAGE_KEY)
  }
}

export function getSession(): SupabaseSession | null {
  if (typeof window === 'undefined') return null
  const raw = localStorage.getItem(STORAGE_KEY)
  if (!raw) return null

  try {
    return JSON.parse(raw) as SupabaseSession
  } catch (error) {
    console.warn('Failed to parse stored Supabase session', error)
    localStorage.removeItem(STORAGE_KEY)
    return null
  }
}

async function request<T>(
  path: string,
  init: (RequestInit & { accessToken?: string }) | undefined = {}
): Promise<T> {
  const { accessToken, ...fetchInit } = init ?? {}
  const { url, anonKey } = getConfig()
  const headers = new Headers(fetchInit.headers)
  headers.set('apikey', anonKey)
  headers.set('Content-Type', 'application/json')
  if (accessToken) {
    headers.set('Authorization', `Bearer ${accessToken}`)
  } else {
    headers.set('Authorization', `Bearer ${anonKey}`)
  }

  const response = await fetch(`${url}${path}`, {
    ...fetchInit,
    headers,
  })

  const contentType = response.headers.get('content-type')
  const isJson = contentType?.includes('application/json')
  const payload = isJson ? await response.json() : null

  if (!response.ok) {
    const message =
      payload?.error_description || payload?.message || 'Supabase request failed'
    throw new Error(message)
  }

  return payload as T
}

export async function signIn(email: string, password: string): Promise<AuthResponse> {
  try {
    const response = await request<any>(
      '/auth/v1/token?grant_type=password',
      {
        method: 'POST',
        body: JSON.stringify({ email, password }),
      }
    )

    // Supabase returns token data at root level, not nested
    // Structure: { access_token, refresh_token, user, expires_in, expires_at, token_type }
    const session: SupabaseSession = {
      access_token: response.access_token,
      refresh_token: response.refresh_token,
      expires_at: response.expires_at,
      token_type: response.token_type,
      user: response.user,
    }

    storeSession(session)

    return {
      data: {
        user: response.user,
        session
      },
      error: null
    }
  } catch (error: any) {
    console.error('Sign in error:', error)
    return {
      data: { user: null, session: null },
      error: error instanceof Error ? error : new Error('Failed to sign in'),
    }
  }
}

export async function signUp(email: string, password: string): Promise<AuthResponse> {
  try {
    const response = await request<any>(
      '/auth/v1/signup',
      {
        method: 'POST',
        body: JSON.stringify({ email, password }),
      }
    )

    // Supabase returns token data at root level, not nested
    const session: SupabaseSession = {
      access_token: response.access_token,
      refresh_token: response.refresh_token,
      expires_at: response.expires_at,
      token_type: response.token_type,
      user: response.user,
    }

    storeSession(session)

    return {
      data: {
        user: response.user,
        session
      },
      error: null
    }
  } catch (error: any) {
    console.error('Signup error:', error)
    return {
      data: { user: null, session: null },
      error: error instanceof Error ? error : new Error('Failed to sign up'),
    }
  }
}

export async function signOut(): Promise<void> {
  const session = getSession()
  if (!session) return

  try {
    await request('/auth/v1/logout', {
      method: 'POST',
      accessToken: session.access_token,
      body: JSON.stringify({ refresh_token: session.refresh_token }),
    })
  } catch (error) {
    console.warn('Supabase sign-out request failed', error)
  } finally {
    storeSession(null)
  }
}

export async function getCurrentUser(): Promise<SupabaseUser | null> {
  console.log('🔍 getCurrentUser: Starting...')
  const session = getSession()
  console.log('📦 getCurrentUser: Session from storage:', session ? 'exists' : 'null')

  if (!session?.access_token) {
    console.warn('⚠️ getCurrentUser: No access token in session')
    return null
  }

  // If we have a user in the session already, return it
  if (session.user) {
    console.log('✅ getCurrentUser: Returning user from session:', session.user.email)
    return session.user
  }

  try {
    console.log('🌐 getCurrentUser: Fetching user from Supabase API...')
    const data = await request<{ user: SupabaseUser | null }>('/auth/v1/user', {
      method: 'GET',
      accessToken: session.access_token,
    })

    console.log('📦 getCurrentUser: API response:', data)

    if (data.user) {
      storeSession({ ...session, user: data.user })
      console.log('✅ getCurrentUser: User fetched and stored')
    }

    return data.user
  } catch (error) {
    console.error('❌ getCurrentUser: Failed to fetch user', error)
    storeSession(null)
    return null
  }
}

export function setSession(session: SupabaseSession | null) {
  storeSession(session)
}
