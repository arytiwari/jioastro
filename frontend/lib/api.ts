/**
 * API client for Vedic Astrology backend
 */

import axios, { AxiosInstance } from 'axios'
import { getSession } from '@/lib/supabase'

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1'

class APIClient {
  private token: string | null = null

  private buildHeaders(headers?: HeadersInit) {
    const merged = new Headers(headers ?? {})
    if (!merged.has('Content-Type')) {
      merged.set('Content-Type', 'application/json')
    }

    if (this.token) {
      merged.set('Authorization', `Bearer ${this.token}`)
    }

    return merged
  }

  private async request<T>(path: string, init: RequestInit = {}): Promise<{ data: T }> {
    // Get valid session before making request (will auto-refresh if needed)
    if (typeof window !== 'undefined') {
      try {
        const { getValidSession } = await import('./supabase')
        const session = await Promise.resolve(getValidSession())
        if (session?.access_token) {
          this.token = session.access_token
        }
      } catch (sessionError) {
        console.warn('Failed to get session:', sessionError)
      }
    }

    const response = await fetch(`${API_URL}${path}`, {
      ...init,
      headers: this.buildHeaders(init.headers),
    })

    if (response.status === 401) {
      // Try to refresh token once
      if (typeof window !== 'undefined') {
        try {
          const { refreshSession } = await import('./supabase')
          const refreshResult = await Promise.resolve(refreshSession())

          if (refreshResult?.data?.session?.access_token) {
            // Retry request with new token
            this.token = refreshResult.data.session.access_token
            const retryResponse = await fetch(`${API_URL}${path}`, {
              ...init,
              headers: this.buildHeaders(init.headers),
            })

            if (retryResponse.ok) {
              // Process successful retry
              let payload: any = null
              const hasBody = retryResponse.status !== 204
              if (hasBody) {
                const contentType = retryResponse.headers.get('content-type') ?? ''
                if (contentType.includes('application/json')) {
                  payload = await retryResponse.json()
                } else {
                  payload = await retryResponse.text()
                }
              }
              return { data: payload as T }
            }
          }
        } catch (refreshError) {
          console.error('Token refresh failed:', refreshError)
        }
      }

      // If refresh failed or retry failed, clear token and redirect
      this.clearToken()
      if (typeof window !== 'undefined') {
        window.location.href = '/auth/login?reason=session_expired'
      }
    }

    let payload: any = null
    const hasBody = response.status !== 204
    if (hasBody) {
      const contentType = response.headers.get('content-type') ?? ''
      if (contentType.includes('application/json')) {
        payload = await response.json()
        // Log raw payload for debugging
        if (path.includes('/queries')) {
          console.log('🔍 API Client request() - Raw HTTP payload for queries:', payload)
          console.log('🔍 API Client request() - First item:', payload?.[0])
        }
      } else {
        payload = await response.text()
      }
    }

    if (!response.ok) {
      const message =
        payload?.detail || payload?.message || (typeof payload === 'string' ? payload : 'Request failed')
      // Create error with status code attached for proper error handling
      const error = new Error(message) as Error & { status: number }
      error.status = response.status
      throw error
    }

    return { data: payload as T }
  }

  setToken(token: string) {
    this.token = token
    if (typeof window !== 'undefined') {
      localStorage.setItem('auth_token', token)
    }
  }

  clearToken() {
    this.token = null
    if (typeof window !== 'undefined') {
      localStorage.removeItem('auth_token')
    }
  }

  async loadToken() {
    if (typeof window === 'undefined') return

    try {
      const session = getSession()
      if (session?.access_token) {
        this.token = session.access_token
        console.log('✅ Loaded Supabase JWT token')
      } else {
        console.log('⚠️ No Supabase session found')
      }
    } catch (error) {
      console.error('Failed to load Supabase token:', error)
    }
  }

  // Profile endpoints
  async createProfile(data: any) {
    return this.request('/profiles', {
      method: 'POST',
      body: JSON.stringify(data),
    })
  }

  async getProfiles() {
    return this.request('/profiles')
  }

  async getProfile(id: string) {
    return this.request(`/profiles/${id}`)
  }

  async updateProfile(id: string, data: any) {
    return this.request(`/profiles/${id}`, {
      method: 'PATCH',
      body: JSON.stringify(data),
    })
  }

  async deleteProfile(id: string) {
    return this.request(`/profiles/${id}`, {
      method: 'DELETE',
    })
  }

  // City endpoints
  async getCities(search?: string, state?: string, limit = 100) {
    const params = new URLSearchParams()
    if (search) params.append('search', search)
    if (state) params.append('state', state)
    params.append('limit', limit.toString())
    return this.request(`/cities?${params.toString()}`)
  }

  async getStates() {
    return this.request('/cities/states')
  }

  async getCity(id: number) {
    return this.request(`/cities/${id}`)
  }

  // Chart endpoints
  async calculateChart(profileId: string, chartType: 'D1' | 'D9' | 'Moon') {
    return this.request('/charts/calculate', {
      method: 'POST',
      body: JSON.stringify({
        profile_id: profileId,
        chart_type: chartType,
      }),
    })
  }

  async getChart(profileId: string, chartType: 'D1' | 'D9' | 'Moon') {
    return this.request(`/charts/${profileId}/${chartType}`)
  }

  // Query endpoints
  async createQuery(data: { profile_id: string; question: string; category?: string }) {
    return this.request('/queries', {
      method: 'POST',
      body: JSON.stringify(data),
    })
  }

  async getQueries(limit = 20, offset = 0) {
    const result = await this.request(`/queries?limit=${limit}&offset=${offset}`)
    console.log('🌐 API Client getQueries - Raw result:', result)
    console.log('🌐 API Client getQueries - result.data:', result.data)
    console.log('🌐 API Client getQueries - First query:', result.data?.[0])
    return result
  }

  async getQuery(id: string) {
    return this.request(`/queries/${id}`)
  }

  // Feedback endpoints
  async createFeedback(data: { response_id: string; rating: number; comment?: string }) {
    return this.request('/feedback', {
      method: 'POST',
      body: JSON.stringify(data),
    })
  }

  async getFeedbackStats() {
    return this.request('/feedback/stats')
  }

  // Phase 3: AI Orchestrator - Comprehensive Readings
  async generateComprehensiveReading(data: {
    profile_id: string
    query?: string
    domains?: string[]
    include_predictions?: boolean
    prediction_window_months?: number
  }) {
    return this.request('/readings/ai', {
      method: 'POST',
      body: JSON.stringify(data),
    })
  }

  async askQuestionWithOrchestrator(data: {
    profile_id: string
    question: string
  }) {
    return this.request('/readings/ask', {
      method: 'POST',
      body: JSON.stringify(data),
    })
  }

  async listReadings(limit = 20, offset = 0) {
    return this.request(`/readings?limit=${limit}&offset=${offset}`)
  }

  async getReading(sessionId: string) {
    return this.request(`/readings/${sessionId}`)
  }

  // Voice Conversation endpoints (OpenAI Whisper + TTS + Translation)
  async askConversationalQuestion(data: {
    profile_id: string
    question: string
    source_language?: string
    is_voice?: boolean
    include_audio_response?: boolean
    voice?: string
    context?: any[]
  }) {
    return this.request('/readings/ask/conversational', {
      method: 'POST',
      body: JSON.stringify({
        profile_id: data.profile_id,
        question: data.question,
        source_language: data.source_language || 'en-US',
        is_voice: data.is_voice || false,
        include_audio_response: data.include_audio_response || false,
        voice: data.voice || 'alloy',
        context: data.context || null,
      }),
    })
  }

  async transcribeAudio(data: {
    audio_data: string
    language?: string
    format?: string
  }) {
    return this.request('/readings/voice/transcribe', {
      method: 'POST',
      body: JSON.stringify({
        audio_data: data.audio_data,
        language: data.language || 'en',
        format: data.format || 'webm',
      }),
    })
  }

  async generateSpeech(data: {
    text: string
    language?: string
    voice?: string
    speed?: number
  }) {
    return this.request('/readings/voice/generate', {
      method: 'POST',
      body: JSON.stringify({
        text: data.text,
        language: data.language || 'en-US',
        voice: data.voice || 'alloy',
        speed: data.speed || 1.0,
      }),
    })
  }

  // Phase 3: Knowledge Base - Rule Retrieval
  async retrieveRules(data: {
    query: string
    chart_context?: any
    domains?: string[]
    top_k?: number
  }) {
    return this.request('/knowledge/retrieve', {
      method: 'POST',
      body: JSON.stringify(data),
    })
  }

  async getRule(ruleId: string) {
    return this.request(`/knowledge/rules/${ruleId}`)
  }

  async getKnowledgeStats() {
    return this.request('/knowledge/stats')
  }

  async getDomains() {
    return this.request('/knowledge/domains')
  }

  async getRulesByDomain(domain: string, limit = 50, minWeight = 0.3) {
    return this.request(`/knowledge/rules/domain/${domain}?limit=${limit}&min_weight=${minWeight}`)
  }

  // Phase 4: Enhancements - Remedies (Profile-based)
  async generateRemediesForProfile(data: {
    profile_id: string
    domain?: 'career' | 'wealth' | 'health' | 'relationships' | 'education' | 'spirituality' | 'general'
    specific_issue?: string
    max_remedies?: number
    include_practical?: boolean
  }) {
    return this.request('/enhancements/remedies/generate', {
      method: 'POST',
      body: JSON.stringify(data),
    })
  }

  // Phase 4: Enhancements - Remedies (From Chart - for testing)
  async generateRemedies(data: {
    chart_data: any
    domain?: string
    max_remedies?: number
    include_practical?: boolean
  }) {
    return this.request('/enhancements/remedies/generate-from-chart', {
      method: 'POST',
      body: JSON.stringify(data),
    })
  }

  // Phase 4: Enhancements - Birth Time Rectification
  async rectifyBirthTime(data: {
    name: string
    birth_date: string
    approximate_time: string
    time_window_minutes: number
    latitude: number
    longitude: number
    timezone_str: string
    city: string
    event_anchors: Array<{
      event_type: string
      event_date: string
      significance: number
      description?: string
    }>
  }) {
    return this.request('/enhancements/rectification/calculate', {
      method: 'POST',
      body: JSON.stringify(data),
    })
  }

  // Phase 4: Enhancements - Transits (Profile-based)
  async getCurrentTransitsForProfile(data: {
    profile_id: string
    transit_date?: string
    include_timeline?: boolean
    focus_planets?: string[]
  }) {
    return this.request('/enhancements/transits/current', {
      method: 'POST',
      body: JSON.stringify(data),
    })
  }

  // Phase 4: Enhancements - Transits (From Chart - for testing)
  async getCurrentTransits(data: {
    chart_data: any
    transit_date?: string
    latitude?: number
    longitude?: number
    timezone_str?: string
  }) {
    return this.request('/enhancements/transits/current-from-chart', {
      method: 'POST',
      body: JSON.stringify(data),
    })
  }

  async getTransitTimeline(data: {
    chart_data: any
    start_date?: string
    end_date?: string
    latitude?: number
    longitude?: number
    timezone_str?: string
  }) {
    return this.request('/enhancements/transits/timeline-from-chart', {
      method: 'POST',
      body: JSON.stringify(data),
    })
  }

  // Phase 4: Enhancements - Shadbala (Profile-based)
  async calculateShadbalaForProfile(data: {
    profile_id: string
    include_breakdown?: boolean
    comparison?: boolean
  }) {
    return this.request('/enhancements/shadbala/calculate', {
      method: 'POST',
      body: JSON.stringify(data),
    })
  }

  // Phase 4: Enhancements - Shadbala (From Chart - for testing)
  async calculateShadbala(data: {
    chart_data: any
    birth_datetime?: string
  }) {
    return this.request('/enhancements/shadbala/calculate-from-chart', {
      method: 'POST',
      body: JSON.stringify(data),
    })
  }

  // Phase 4: Enhancements - Yoga Detection (Profile-based)
  async analyzeYogasForProfile(data: {
    profile_id: string
    include_all?: boolean
  }) {
    return this.request('/enhancements/yogas/analyze', {
      method: 'POST',
      body: JSON.stringify(data),
    })
  }

  // Phase 4: Enhancements - All Combined
  async getAllEnhancements(data: {
    chart_data: any
    birth_datetime?: string
    include_remedies?: boolean
    include_transits?: boolean
    include_shadbala?: boolean
    remedy_domain?: string
  }) {
    return this.request('/enhancements/all-from-chart', {
      method: 'POST',
      body: JSON.stringify(data),
    })
  }

  // Phase 1: Numerology - Calculate and Profile Management
  async calculateNumerology(data: {
    full_name: string
    birth_date: string
    system?: 'western' | 'vedic' | 'chaldean' | 'both'
    common_name?: string
    name_at_birth?: string
    profile_id?: string
  }) {
    return this.request('/numerology/calculate', {
      method: 'POST',
      body: JSON.stringify({
        full_name: data.full_name,
        birth_date: data.birth_date,
        system: data.system || 'both',
        common_name: data.common_name,
        name_at_birth: data.name_at_birth,
        profile_id: data.profile_id,
      }),
    })
  }

  async createNumerologyProfile(data: {
    full_name: string
    birth_date: string
    system?: 'western' | 'vedic' | 'chaldean' | 'both'
    common_name?: string
    name_at_birth?: string
    profile_id?: string
  }) {
    return this.request('/numerology/profiles', {
      method: 'POST',
      body: JSON.stringify(data),
    })
  }

  async getNumerologyProfiles() {
    return this.request('/numerology/profiles')
  }

  async getNumerologyProfile(id: string) {
    return this.request(`/numerology/profiles/${id}`)
  }

  async updateNumerologyProfile(id: string, data: any) {
    return this.request(`/numerology/profiles/${id}`, {
      method: 'PATCH',
      body: JSON.stringify(data),
    })
  }

  async deleteNumerologyProfile(id: string) {
    return this.request(`/numerology/profiles/${id}`, {
      method: 'DELETE',
    })
  }

  async createNameTrial(profileId: string, data: {
    trial_name: string
    system: 'western' | 'vedic' | 'chaldean'
    notes?: string
    is_preferred?: boolean
  }) {
    return this.request(`/numerology/profiles/${profileId}/name-trials`, {
      method: 'POST',
      body: JSON.stringify(data),
    })
  }

  async getNameTrials(profileId: string) {
    return this.request(`/numerology/profiles/${profileId}/name-trials`)
  }

  async compareNames(data: {
    names: string[]
    birth_date: string
    system: 'western' | 'vedic' | 'chaldean'
  }) {
    return this.request('/numerology/compare', {
      method: 'POST',
      body: JSON.stringify(data),
    })
  }
}

export const apiClient = new APIClient()

if (typeof window !== 'undefined') {
  const storedToken = window.localStorage.getItem('auth_token')
  if (storedToken) {
    apiClient.setToken(storedToken)
  }
  void apiClient.loadToken()
}
