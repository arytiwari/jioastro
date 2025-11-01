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
    const response = await fetch(`${API_URL}${path}`, {
      ...init,
      headers: this.buildHeaders(init.headers),
    })

    if (response.status === 401) {
      this.clearToken()
      if (typeof window !== 'undefined') {
        window.location.href = '/auth/login'
      }
    }

    let payload: any = null
    const hasBody = response.status !== 204
    if (hasBody) {
      const contentType = response.headers.get('content-type') ?? ''
      if (contentType.includes('application/json')) {
        payload = await response.json()
      } else {
        payload = await response.text()
      }
    }

    if (!response.ok) {
      const message =
        payload?.detail || payload?.message || (typeof payload === 'string' ? payload : 'Request failed')
      throw new Error(message)
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

    const storedToken = window.localStorage.getItem('auth_token')
    if (storedToken) {
      this.token = storedToken
    }

    try {
      const session = await getSession()
      if (session?.access_token) {
        this.setToken(session.access_token)
      } else if (!storedToken) {
        this.clearToken()
      }
    } catch (error) {
      console.error('Failed to load Supabase session', error)
      if (!storedToken) {
        this.clearToken()
      }
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

  // Chart endpoints
  async calculateChart(profileId: string, chartType: 'D1' | 'D9') {
    return this.request('/charts/calculate', {
      method: 'POST',
      body: JSON.stringify({
        profile_id: profileId,
        chart_type: chartType,
      }),
    })
  }

  async getChart(profileId: string, chartType: 'D1' | 'D9') {
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
    return this.request(`/queries?limit=${limit}&offset=${offset}`)
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

  // VedAstro endpoints
  async getVedAstroStatus() {
    return this.request('/vedastro/status')
  }

  async calculateComprehensiveChart(profileId: string) {
    return this.request('/vedastro/chart/comprehensive', {
      method: 'POST',
      body: JSON.stringify({
        profile_id: profileId,
        chart_type: 'D1',
      }),
    })
  }

  async getVedicKnowledge(topic: string) {
    return this.request(`/vedastro/knowledge/${topic}`)
  }

  async listKnowledgeTopics() {
    return this.request('/vedastro/knowledge')
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
