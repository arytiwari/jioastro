import { createClient } from '@supabase/supabase-js'
import type {
  AuthError,
  AuthResponse,
  AuthTokenResponsePassword,
  Session,
  SupabaseClient,
  User,
} from '@supabase/supabase-js'

type AuthChangeCallback = (event: string, session: Session | null) => void

const STORAGE_KEY = 'supabase.auth.token'

const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL
const supabaseAnonKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY

if (!supabaseUrl || !supabaseAnonKey) {
  throw new Error('Supabase credentials are not configured')
}

let client: SupabaseClient | null = null

function getClient(): SupabaseClient {
  if (!client) {
    const isBrowser = typeof window !== 'undefined'
    client = createClient(supabaseUrl, supabaseAnonKey, {
      auth: {
        persistSession: isBrowser,
        autoRefreshToken: isBrowser,
        storageKey: STORAGE_KEY,
      },
    })
  }

  return client
}

export async function signIn(email: string, password: string): Promise<AuthTokenResponsePassword> {
  const supabase = getClient()
  return supabase.auth.signInWithPassword({ email, password })
}

export async function signUp(email: string, password: string): Promise<AuthResponse> {
  const supabase = getClient()
  return supabase.auth.signUp({ email, password })
}

export async function signOut(): Promise<{ error: AuthError | null }> {
  const supabase = getClient()
  return supabase.auth.signOut()
}

export async function getCurrentUser(): Promise<User | null> {
  const supabase = getClient()
  const { data, error } = await supabase.auth.getUser()
  if (error) {
    console.warn('Failed to fetch Supabase user', error)
    return null
  }
  return data.user
}

export async function getSession(): Promise<Session | null> {
  const supabase = getClient()
  const { data, error } = await supabase.auth.getSession()
  if (error) {
    console.warn('Failed to fetch Supabase session', error)
    return null
  }
  return data.session
}

export function onAuthStateChange(callback: AuthChangeCallback) {
  const supabase = getClient()
  return supabase.auth.onAuthStateChange((event, session) => callback(event, session))
}

export type { Session, User }
