/**
 * API client for Vedic Astrology backend
 */

import axios, { AxiosInstance } from 'axios'

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1'

class APIClient {
  private client: AxiosInstance
  private token: string | null = null

  constructor() {
    this.client = axios.create({
      baseURL: API_URL,
      headers: {
        'Content-Type': 'application/json',
      },
    })

    // Request interceptor to add auth token
    this.client.interceptors.request.use((config) => {
      if (this.token) {
        config.headers.Authorization = `Bearer ${this.token}`
      }
      return config
    })

    // Response interceptor for error handling
    this.client.interceptors.response.use(
      (response) => response,
      (error) => {
        if (error.response?.status === 401) {
          // Token expired or invalid
          this.clearToken()
          if (typeof window !== 'undefined') {
            window.location.href = '/auth/login'
          }
        }
        return Promise.reject(error)
      }
    )
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
    if (typeof window !== 'undefined') {
      // Load token from Supabase session instead of custom storage
      try {
        const { createClient } = await import('@supabase/supabase-js')
        const supabase = createClient(
          process.env.NEXT_PUBLIC_SUPABASE_URL!,
          process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!
        )
        const { data: { session } } = await supabase.auth.getSession()
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
  }

  // Profile endpoints
  async createProfile(data: any) {
    return this.client.post('/profiles', data)
  }

  async getProfiles() {
    return this.client.get('/profiles')
  }

  async getProfile(id: string) {
    return this.client.get(`/profiles/${id}`)
  }

  async updateProfile(id: string, data: any) {
    return this.client.patch(`/profiles/${id}`, data)
  }

  async deleteProfile(id: string) {
    return this.client.delete(`/profiles/${id}`)
  }

  // Chart endpoints
  async calculateChart(profileId: string, chartType: 'D1' | 'D9') {
    return this.client.post('/charts/calculate', {
      profile_id: profileId,
      chart_type: chartType,
    })
  }

  async getChart(profileId: string, chartType: 'D1' | 'D9') {
    return this.client.get(`/charts/${profileId}/${chartType}`)
  }

  // Query endpoints
  async createQuery(data: { profile_id: string; question: string; category?: string }) {
    return this.client.post('/queries', data)
  }

  async getQueries(limit = 20, offset = 0) {
    return this.client.get(`/queries?limit=${limit}&offset=${offset}`)
  }

  async getQuery(id: string) {
    return this.client.get(`/queries/${id}`)
  }

  // Feedback endpoints
  async createFeedback(data: { response_id: string; rating: number; comment?: string }) {
    return this.client.post('/feedback', data)
  }

  async getFeedbackStats() {
    return this.client.get('/feedback/stats')
  }

  // VedAstro endpoints
  async getVedAstroStatus() {
    return this.client.get('/vedastro/status')
  }

  async calculateComprehensiveChart(profileId: string) {
    return this.client.post('/vedastro/chart/comprehensive', {
      profile_id: profileId,
      chart_type: 'D1'
    })
  }

  async getVedicKnowledge(topic: string) {
    return this.client.get(`/vedastro/knowledge/${topic}`)
  }

  async listKnowledgeTopics() {
    return this.client.get('/vedastro/knowledge')
  }
}

export const apiClient = new APIClient()

// Load token on initialization (async)
if (typeof window !== 'undefined') {
  apiClient.loadToken().catch(console.error)
}
