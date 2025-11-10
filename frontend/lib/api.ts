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

    // If path starts with /api/, use it as absolute path (for v2 endpoints)
    // Otherwise, prepend API_URL (for v1 endpoints)
    const url = path.startsWith('/api/')
      ? `${process.env.NEXT_PUBLIC_API_URL?.replace(/\/api\/v\d+$/, '') || 'http://localhost:8000'}${path}`
      : `${API_URL}${path}`

    let response: Response
    try {
      response = await fetch(url, {
        ...init,
        headers: this.buildHeaders(init.headers),
      })
    } catch (networkError) {
      // Handle network errors (e.g., server down, no internet)
      const error = new Error('Unable to connect to server. Please check your connection and try again.') as Error & { status: number }
      error.status = 0
      throw error
    }

    if (response.status === 401) {
      // Only try to refresh if we had a token (meaning user was logged in)
      const hadToken = !!this.token

      // Try to refresh token once
      if (hadToken && typeof window !== 'undefined') {
        try {
          const { refreshSession } = await import('./supabase')
          const refreshResult = await Promise.resolve(refreshSession())

          if (refreshResult?.data?.session?.access_token) {
            // Retry request with new token
            this.token = refreshResult.data.session.access_token
            const retryResponse = await fetch(url, {
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

      // Only redirect to login if we had a valid token before (session expired)
      // Don't redirect for unauthenticated requests that never had a token
      if (hadToken) {
        this.clearToken()
        if (typeof window !== 'undefined') {
          window.location.href = '/auth/login?reason=session_expired'
        }
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

  // Generic HTTP methods
  async get<T = any>(path: string): Promise<{ data: T }> {
    return this.request<T>(path, {
      method: 'GET',
    })
  }

  async post<T = any>(path: string, data?: any): Promise<{ data: T }> {
    return this.request<T>(path, {
      method: 'POST',
      body: data ? JSON.stringify(data) : undefined,
    })
  }

  async patch<T = any>(path: string, data?: any): Promise<{ data: T }> {
    return this.request<T>(path, {
      method: 'PATCH',
      body: data ? JSON.stringify(data) : undefined,
    })
  }

  async delete<T = any>(path: string): Promise<{ data: T }> {
    return this.request<T>(path, {
      method: 'DELETE',
    })
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

  async updateProfile(id: string, data: any) {
    return this.request(`/profiles/${id}`, {
      method: 'PATCH',
      body: JSON.stringify(data),
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

  async findOrCreateCity(cityData: {
    name: string
    state: string
    latitude: number
    longitude: number
    display_name?: string
  }) {
    return this.request('/cities/find-or-create', {
      method: 'POST',
      body: JSON.stringify(cityData),
    })
  }

  // Admin city endpoints
  async createCity(cityData: {
    name: string
    state: string
    latitude: number
    longitude: number
    display_name?: string
  }) {
    return this.request('/cities', {
      method: 'POST',
      body: JSON.stringify(cityData),
    })
  }

  async updateCity(id: number, cityData: {
    name?: string
    state?: string
    latitude?: number
    longitude?: number
    display_name?: string
  }) {
    return this.request(`/cities/${id}`, {
      method: 'PUT',
      body: JSON.stringify(cityData),
    })
  }

  async deleteCity(id: number) {
    return this.request(`/cities/${id}`, {
      method: 'DELETE',
    })
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

  async deleteChart(profileId: string, chartType: 'D1' | 'D9' | 'Moon') {
    return this.request(`/charts/${profileId}/${chartType}`, {
      method: 'DELETE',
    })
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
    force_regenerate?: boolean
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

  async deleteReading(sessionId: string) {
    return this.request(`/readings/${sessionId}`, {
      method: 'DELETE'
    })
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

  // Phase 5: Compatibility Matching endpoints
  async analyzeCompatibility(data: {
    boy_profile_id: string
    girl_profile_id: string
  }) {
    return this.request(`/compatibility/analyze?boy_profile_id=${data.boy_profile_id}&girl_profile_id=${data.girl_profile_id}`, {
      method: 'POST',
    })
  }

  async getGunaMilan(boyProfileId: string, girlProfileId: string) {
    return this.request(`/compatibility/guna-milan/${boyProfileId}/${girlProfileId}`)
  }

  async getManglikDosha(profileId: string) {
    return this.request(`/compatibility/manglik/${profileId}`)
  }

  async getNakshatra(profileId: string) {
    return this.request(`/compatibility/nakshatra/${profileId}`)
  }

  async quickMatch(profileId: string) {
    return this.request(`/compatibility/quick-match?profile_id=${profileId}`, {
      method: 'POST',
    })
  }

  // Varshaphal (Annual Predictions) endpoints
  async generateVarshaphal(data: {
    profile_id: string
    target_year: number
    force_refresh?: boolean
  }) {
    return this.request('/varshaphal/generate', {
      method: 'POST',
      body: JSON.stringify(data),
    })
  }

  async getVarshaphal(varshaphalId: string) {
    return this.request(`/varshaphal/${varshaphalId}`)
  }

  async listVarshaphals(data: {
    profile_id?: string
    limit?: number
    offset?: number
  }) {
    return this.request('/varshaphal/list', {
      method: 'POST',
      body: JSON.stringify({
        profile_id: data.profile_id,
        limit: data.limit || 10,
        offset: data.offset || 0,
      }),
    })
  }

  async deleteVarshaphal(varshaphalId: string) {
    return this.request(`/varshaphal/${varshaphalId}`, {
      method: 'DELETE',
    })
  }

  // Muhurta (Electional Astrology) endpoints
  async getPanchang(data: {
    datetime: string
    latitude: number
    longitude: number
  }) {
    return this.request('/muhurta/panchang', {
      method: 'POST',
      body: JSON.stringify(data),
    })
  }

  async getHora(data: {
    datetime: string
    latitude: number
    longitude: number
  }) {
    return this.request('/muhurta/hora', {
      method: 'POST',
      body: JSON.stringify(data),
    })
  }

  async getDailyHoraTable(data: {
    date: string
    latitude: number
    longitude: number
  }) {
    return this.request('/muhurta/hora/daily-table', {
      method: 'POST',
      body: JSON.stringify(data),
    })
  }

  async findMuhurta(data: {
    activity_type: string
    start_date: string
    end_date: string
    latitude: number
    longitude: number
    max_results?: number
  }) {
    return this.request('/muhurta/find-muhurta', {
      method: 'POST',
      body: JSON.stringify({
        ...data,
        max_results: data.max_results || 10,
      }),
    })
  }

  async getBestTimeToday(data: {
    activity_type: string
    latitude: number
    longitude: number
  }) {
    return this.request('/muhurta/best-time-today', {
      method: 'POST',
      body: JSON.stringify(data),
    })
  }

  async getDecisionCopilotGuidance(data: {
    activity_type: string
    start_date: string
    end_date: string
    latitude: number
    longitude: number
    max_results?: number
    chart_id?: string | null
  }) {
    return this.request('/muhurta/decision-copilot', {
      method: 'POST',
      body: JSON.stringify({
        ...data,
        max_results: data.max_results || 5,
      }),
    })
  }

  // =============================================================================
  // PRASHNA (Horary Astrology) ENDPOINTS
  // =============================================================================

  async analyzePrashna(data: {
    question: string
    question_type: string
    datetime: string
    latitude: number
    longitude: number
    timezone: string
  }) {
    return this.request('/prashna/analyze', {
      method: 'POST',
      body: JSON.stringify(data),
    })
  }

  async savePrashna(data: {
    question: string
    question_type: string
    query_datetime: string
    latitude: number
    longitude: number
    timezone: string
    prashna_chart: any
    analysis: any
    notes?: string
  }) {
    return this.request('/prashna/save', {
      method: 'POST',
      body: JSON.stringify(data),
    })
  }

  async getPrashnas(limit = 10, offset = 0, question_type?: string) {
    const params = new URLSearchParams({
      limit: String(limit),
      offset: String(offset),
    })
    if (question_type) {
      params.append('question_type', question_type)
    }
    return this.request(`/prashna/list?${params}`)
  }

  async getPrashna(prashnaId: string) {
    return this.request(`/prashna/${prashnaId}`)
  }

  async deletePrashna(prashnaId: string) {
    return this.request(`/prashna/${prashnaId}`, {
      method: 'DELETE',
    })
  }

  // =============================================================================
  // CHART COMPARISON ENDPOINTS
  // =============================================================================

  async compareCharts(data: {
    profile_id_1: string
    profile_id_2: string
    comparison_type?: string
  }) {
    return this.request('/chart-comparison/compare', {
      method: 'POST',
      body: JSON.stringify({
        profile_id_1: data.profile_id_1,
        profile_id_2: data.profile_id_2,
        comparison_type: data.comparison_type || 'general',
      }),
    })
  }

  async analyzeSynastry(data: {
    profile_id_1: string
    profile_id_2: string
    focus?: string
  }) {
    return this.request('/chart-comparison/synastry', {
      method: 'POST',
      body: JSON.stringify({
        profile_id_1: data.profile_id_1,
        profile_id_2: data.profile_id_2,
        focus: data.focus || 'romantic',
      }),
    })
  }

  async generateCompositeChart(data: {
    profile_id_1: string
    profile_id_2: string
  }) {
    return this.request('/chart-comparison/composite', {
      method: 'POST',
      body: JSON.stringify({
        profile_id_1: data.profile_id_1,
        profile_id_2: data.profile_id_2,
      }),
    })
  }

  async calculateProgressedChart(data: {
    profile_id: string
    current_age: number
  }) {
    return this.request('/chart-comparison/progressed', {
      method: 'POST',
      body: JSON.stringify({
        profile_id: data.profile_id,
        current_age: data.current_age,
      }),
    })
  }

  async saveComparison(data: {
    profile_id_1: string
    profile_id_2: string
    comparison_type: string
    comparison_data: any
  }) {
    return this.request('/chart-comparison/save', {
      method: 'POST',
      body: JSON.stringify(data),
    })
  }

  async listComparisons(params?: {
    limit?: number
    offset?: number
    comparison_type?: string
  }) {
    const queryParams = new URLSearchParams()
    if (params?.limit) queryParams.append('limit', params.limit.toString())
    if (params?.offset) queryParams.append('offset', params.offset.toString())
    if (params?.comparison_type) queryParams.append('comparison_type', params.comparison_type)

    const query = queryParams.toString()
    return this.request(`/chart-comparison/list${query ? `?${query}` : ''}`, {
      method: 'GET',
    })
  }

  async deleteComparison(comparisonId: string) {
    return this.request(`/chart-comparison/${comparisonId}`, {
      method: 'DELETE',
    })
  }

  // =============================================================================
  // JAIMINI SYSTEM ENDPOINTS
  // =============================================================================

  async getCharaKarakas(profileId: string) {
    return this.request(`/enhancements/jaimini/chara-karakas/${profileId}`)
  }

  async getKarakamsha(profileId: string) {
    return this.request(`/enhancements/jaimini/karakamsha/${profileId}`)
  }

  async getArudhaPadas(profileId: string) {
    return this.request(`/enhancements/jaimini/arudha-padas/${profileId}`)
  }

  async analyzeJaimini(profileId: string) {
    return this.request(`/enhancements/jaimini/analyze/${profileId}`)
  }

  // =============================================================================
  // LAL KITAB SYSTEM ENDPOINTS
  // =============================================================================

  async getPlanetaryDebts(profileId: string) {
    return this.request(`/enhancements/lal-kitab/debts/${profileId}`)
  }

  async getBlindPlanets(profileId: string) {
    return this.request(`/enhancements/lal-kitab/blind-planets/${profileId}`)
  }

  async analyzeLalKitab(profileId: string) {
    return this.request(`/enhancements/lal-kitab/analyze/${profileId}`)
  }

  // =============================================================================
  // ASHTAKAVARGA SYSTEM ENDPOINTS
  // =============================================================================

  async getBhinnaAshtakavarga(profileId: string) {
    return this.request(`/enhancements/ashtakavarga/bhinna/${profileId}`)
  }

  async getSarvaAshtakavarga(profileId: string) {
    return this.request(`/enhancements/ashtakavarga/sarva/${profileId}`)
  }

  async analyzeTransitStrength(profileId: string, transitDate?: string) {
    const params = transitDate ? `?transit_date=${transitDate}` : ''
    return this.request(`/enhancements/ashtakavarga/transit/${profileId}${params}`)
  }

  async analyzeAshtakavarga(profileId: string) {
    return this.request(`/enhancements/ashtakavarga/analyze/${profileId}`)
  }

  // =============================================================================
  // PALMISTRY ENDPOINTS
  // =============================================================================

  async uploadPalmImage(data: {
    hand_type: 'left' | 'right'
    view_type: 'front' | 'back' | 'zoomed' | 'thumb_edge' | 'side'
    image: string
    capture_method: 'camera' | 'upload'
    profile_id?: string  // Optional birth profile ID for holistic analysis
    device_info?: {
      device_type?: 'mobile' | 'tablet' | 'desktop'
      screen_width?: number
      screen_height?: number
      user_agent?: string
    }
  }) {
    return this.request('/palmistry/upload', {
      method: 'POST',
      body: JSON.stringify(data),
    })
  }

  async analyzePalm(data: {
    photo_ids: string[]
    reanalysis?: boolean
    priority?: 'high' | 'normal' | 'low'
  }) {
    return this.request('/palmistry/analyze', {
      method: 'POST',
      body: JSON.stringify(data),
    })
  }

  async getPalmReadings(params?: {
    limit?: number
    offset?: number
    hand_type?: 'left' | 'right'
  }) {
    const queryParams = new URLSearchParams()
    if (params?.limit) queryParams.append('limit', params.limit.toString())
    if (params?.offset) queryParams.append('offset', params.offset.toString())
    if (params?.hand_type) queryParams.append('hand_type', params.hand_type)

    const query = queryParams.toString()
    return this.request(`/palmistry/readings${query ? `?${query}` : ''}`)
  }

  async getPalmReading(readingId: string) {
    return this.request(`/palmistry/readings/${readingId}`)
  }

  async deletePalmReading(readingId: string) {
    return this.request(`/palmistry/readings/${readingId}`, {
      method: 'DELETE'
    })
  }

  async comparePalmHands(params?: {
    left_reading_id?: string
    right_reading_id?: string
  }) {
    const queryParams = new URLSearchParams()
    if (params?.left_reading_id) queryParams.append('left_reading_id', params.left_reading_id)
    if (params?.right_reading_id) queryParams.append('right_reading_id', params.right_reading_id)

    const query = queryParams.toString()
    return this.request(`/palmistry/compare${query ? `?${query}` : ''}`)
  }

  async submitPalmFeedback(data: {
    interpretation_id: string
    rating: number
    feedback_type: 'accuracy' | 'completeness' | 'clarity' | 'relevance'
    comments?: string
  }) {
    return this.request('/palmistry/feedback', {
      method: 'POST',
      body: JSON.stringify(data),
    })
  }

  async getPalmistryHealth() {
    return this.request('/palmistry/health')
  }

  // =============================================================================
  // TAROT READING METHODS
  // =============================================================================

  async getTarotCards(params?: {
    suit?: string
    arcana_type?: string
  }) {
    const queryParams = new URLSearchParams()
    if (params?.suit) queryParams.append('suit', params.suit)
    if (params?.arcana_type) queryParams.append('arcana_type', params.arcana_type)

    const query = queryParams.toString()
    return this.request(`/tarot/cards${query ? `?${query}` : ''}`)
  }

  async getTarotCard(cardId: string) {
    return this.request(`/tarot/cards/${cardId}`)
  }

  async getTarotSpreads(category?: string) {
    const query = category ? `?category=${category}` : ''
    return this.request(`/tarot/spreads${query}`)
  }

  async getTarotSpread(spreadId: string) {
    return this.request(`/tarot/spreads/${spreadId}`)
  }

  async drawDailyCard() {
    return this.request('/tarot/daily-card', {
      method: 'POST',
    })
  }

  async createTarotReading(data: {
    spread_id?: string
    spread_name: string
    reading_type: string
    question?: string
    profile_id?: string
    num_cards?: number
  }) {
    return this.request('/tarot/readings', {
      method: 'POST',
      body: JSON.stringify(data),
    })
  }

  async getTarotReadings(params?: {
    reading_type?: string
    limit?: number
  }) {
    const queryParams = new URLSearchParams()
    if (params?.reading_type) queryParams.append('reading_type', params.reading_type)
    if (params?.limit) queryParams.append('limit', params.limit.toString())

    const query = queryParams.toString()
    return this.request(`/tarot/readings${query ? `?${query}` : ''}`)
  }

  async getTarotReading(readingId: string) {
    return this.request(`/tarot/readings/${readingId}`)
  }

  async updateTarotReading(readingId: string, data: {
    is_favorite?: boolean
    notes?: string
  }) {
    return this.request(`/tarot/readings/${readingId}`, {
      method: 'PATCH',
      body: JSON.stringify(data),
    })
  }

  async deleteTarotReading(readingId: string) {
    return this.request(`/tarot/readings/${readingId}`, {
      method: 'DELETE'
    })
  }

  async getTarotStats() {
    return this.request('/tarot/stats')
  }

  // =============================================================================
  // FENG SHUI METHODS
  // =============================================================================

  async createFengShuiAnalysis(data: {
    profile_id: string
    space_type?: string
    space_orientation?: string
    space_layout?: any
  }) {
    return this.request('/feng-shui/analyze', {
      method: 'POST',
      body: JSON.stringify(data),
    })
  }

  async getFengShuiAnalyses(limit?: number) {
    const query = limit ? `?limit=${limit}` : ''
    return this.request(`/feng-shui/analyses${query}`)
  }

  async getFengShuiAnalysis(analysisId: string) {
    return this.request(`/feng-shui/analyses/${analysisId}`)
  }

  async updateFengShuiAnalysis(analysisId: string, data: {
    space_type?: string
    space_orientation?: string
    space_layout?: any
  }) {
    return this.request(`/feng-shui/analyses/${analysisId}`, {
      method: 'PATCH',
      body: JSON.stringify(data),
    })
  }

  async getFengShuiRecommendations(analysisId: string, params?: {
    category?: string
    priority?: string
  }) {
    const queryParams = new URLSearchParams()
    if (params?.category) queryParams.append('category', params.category)
    if (params?.priority) queryParams.append('priority', params.priority)

    const query = queryParams.toString()
    return this.request(`/feng-shui/analyses/${analysisId}/recommendations${query ? `?${query}` : ''}`)
  }

  async updateFengShuiRecommendation(recommendationId: string, data: {
    is_implemented?: boolean
    user_notes?: string
    effectiveness_rating?: number
  }) {
    return this.request(`/feng-shui/recommendations/${recommendationId}`, {
      method: 'PATCH',
      body: JSON.stringify(data),
    })
  }

  async calculateKua(profileId: string) {
    return this.request(`/feng-shui/calculate-kua?profile_id=${profileId}`, {
      method: 'POST',
    })
  }

  async getDirectionGuidance(kuaNumber: number) {
    return this.request(`/feng-shui/direction-guidance/${kuaNumber}`)
  }

  async getColorTherapy(kuaNumber: number) {
    return this.request(`/feng-shui/color-therapy/${kuaNumber}`)
  }

  async getElementBalance(kuaNumber: number) {
    return this.request(`/feng-shui/element-balance/${kuaNumber}`)
  }

  async getFengShuiStats() {
    return this.request('/feng-shui/stats')
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
