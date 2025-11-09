'use client'

import { useState, useEffect } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Eye, AlertTriangle, Target, Sparkles, TrendingUp, Calendar, RefreshCw, History as HistoryIcon, User } from '@/components/icons'
import { apiClient } from '@/lib/api'
import Link from 'next/link'

interface Profile {
  id: string
  name: string
  date_of_birth: string
}

interface LifeTheme {
  title: string
  description: string
  confidence: number
  planetary_basis: string[]
}

interface LifeRisk {
  title: string
  description: string
  severity: string
  date_range?: string
  mitigation?: string
}

interface LifeOpportunity {
  title: string
  description: string
  window: string
  confidence: number
  planetary_support: string[]
}

interface LifeAction {
  action: string
  priority: string
  reason: string
  when?: string
}

interface SnapshotInsights {
  top_themes: LifeTheme[]
  risks: LifeRisk[]
  opportunities: LifeOpportunity[]
  actions: LifeAction[]
  life_phase: string
  read_time_seconds: number
}

interface Snapshot {
  snapshot_id: string
  profile: { id: string; name: string }
  generated_at: string
  expires_at: string
  insights: SnapshotInsights
}

interface SnapshotListItem {
  id: string
  profile_id: string
  profile_name: string
  generated_at: string
  expires_at: string
  is_expired: boolean
  themes_count: number
}

export default function LifeSnapshotPage() {
  const [profiles, setProfiles] = useState<Profile[]>([])
  const [selectedProfile, setSelectedProfile] = useState<string>('')
  const [snapshot, setSnapshot] = useState<Snapshot | null>(null)
  const [history, setHistory] = useState<SnapshotListItem[]>([])
  const [loading, setLoading] = useState(false)
  const [generating, setGenerating] = useState(false)
  const [loadingHistory, setLoadingHistory] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [activeTab, setActiveTab] = useState<'generate' | 'history'>('generate')
  const [isAuthenticated, setIsAuthenticated] = useState(false)
  const [checkingAuth, setCheckingAuth] = useState(true)

  // Check authentication status first
  useEffect(() => {
    const checkAuth = async () => {
      console.log('🎯 Life Snapshot Page: Starting auth check...')
      try {
        const { getValidSession } = await import('@/lib/supabase')

        // Use getValidSession instead of getSession - this will auto-refresh if needed
        // and load the session into localStorage if it's not there yet
        console.log('🔄 Life Snapshot Page: Getting valid session (will auto-refresh if needed)...')
        const session = await getValidSession()

        console.log('📦 Life Snapshot Page: Session result:', session ? 'exists' : 'null')
        if (session) {
          console.log('📦 Life Snapshot Page: Session details:', {
            hasToken: !!session.access_token,
            hasRefreshToken: !!session.refresh_token,
            expiresAt: session.expires_at,
            user: session.user?.email
          })
        }

        if (!session) {
          console.log('⚠️ Life Snapshot Page: No valid session, proceeding as unauthenticated')
          setIsAuthenticated(false)
          setCheckingAuth(false)
          return
        }

        // Session exists and is valid, treat as authenticated
        console.log('✅ Life Snapshot Page: Valid session found, setting authenticated=true')
        setIsAuthenticated(true)

        // Load token before making API calls
        console.log('🔑 Life Snapshot Page: Loading token into API client...')
        await apiClient.loadToken()
        console.log('✅ Life Snapshot Page: Token loaded')

        // Fetch profiles and history
        console.log('📊 Life Snapshot Page: Fetching profiles...')
        fetchProfiles()
        // TODO: Uncomment when backend endpoint is ready
        // fetchHistory()
        console.log('✅ Life Snapshot Page: Auth check complete')
      } catch (error) {
        console.error('❌ Life Snapshot Page: Auth check failed:', error)
        console.error('Error stack:', error)
        // On error, proceed as unauthenticated rather than blocking the page
        setIsAuthenticated(false)
      } finally {
        setCheckingAuth(false)
      }
    }

    checkAuth()
  }, [])

  const fetchProfiles = async () => {
    try {
      const response = await apiClient.get('/profiles')
      setProfiles(response.data)
      if (response.data.length > 0) {
        setSelectedProfile(response.data[0].id)
      }
    } catch (error) {
      console.error('Error fetching profiles:', error)
      setError('Failed to load profiles')
    }
  }

  const fetchHistory = async () => {
    setLoadingHistory(true)
    try {
      const response = await apiClient.get('/api/v2/life-snapshot/list?limit=10&offset=0')
      setHistory(response.data.snapshots)
    } catch (error) {
      console.error('Error fetching history:', error)
    } finally {
      setLoadingHistory(false)
    }
  }

  const generateSnapshot = async (forceRefresh = false) => {
    if (!selectedProfile) {
      setError('Please select a profile')
      return
    }

    setGenerating(true)
    setError(null)

    try {
      const response = await apiClient.post('/api/v2/life-snapshot/generate', {
        profile_id: selectedProfile,
        force_refresh: forceRefresh
      })
      setSnapshot(response.data)
      setActiveTab('generate')
      fetchHistory() // Refresh history
    } catch (error: any) {
      console.error('Error generating snapshot:', error)
      setError(error.response?.data?.detail || 'Failed to generate snapshot')
    } finally {
      setGenerating(false)
    }
  }

  const loadSnapshot = async (snapshotId: string) => {
    setLoading(true)
    setError(null)

    try {
      const response = await apiClient.get(`/api/v2/life-snapshot/${snapshotId}`)
      setSnapshot(response.data)
      setActiveTab('generate')
    } catch (error: any) {
      console.error('Error loading snapshot:', error)
      setError(error.response?.data?.detail || 'Failed to load snapshot')
    } finally {
      setLoading(false)
    }
  }

  const getSeverityColor = (severity: string) => {
    switch (severity.toLowerCase()) {
      case 'high': return 'bg-red-100 text-red-800 border-red-200'
      case 'medium': return 'bg-orange-100 text-orange-800 border-orange-200'
      case 'low': return 'bg-yellow-100 text-yellow-800 border-yellow-200'
      default: return 'bg-gray-100 text-gray-800 border-gray-200'
    }
  }

  const getPriorityColor = (priority: string) => {
    switch (priority.toLowerCase()) {
      case 'high': return 'bg-purple-100 text-purple-800'
      case 'medium': return 'bg-blue-100 text-blue-800'
      case 'low': return 'bg-gray-100 text-gray-800'
      default: return 'bg-gray-100 text-gray-800'
    }
  }

  // Show loading state while checking auth
  if (checkingAuth) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="text-center py-12">
          <RefreshCw className="w-8 h-8 animate-spin mx-auto mb-4 text-purple-600" />
          <p className="text-gray-600">Loading...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="container mx-auto px-4 py-8">
      {/* Header */}
      <div className="mb-8">
        <div className="flex items-center gap-3 mb-2">
          <div className="p-2 bg-purple-100 rounded-lg">
            <Eye className="w-6 h-6 text-purple-600" />
          </div>
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Life Snapshot</h1>
            <p className="text-gray-600">60-second personalized life insights</p>
          </div>
        </div>
      </div>

      {/* Login Required Message for Unauthenticated Users */}
      {!isAuthenticated && (
        <Card className="border-purple-500 bg-gradient-to-r from-purple-50 to-pink-50 mb-6">
          <CardContent className="py-8">
            <div className="text-center">
              <User className="w-12 h-12 mx-auto mb-4 text-purple-600" />
              <h3 className="text-xl font-bold text-gray-900 mb-2">Account Required</h3>
              <p className="text-gray-700 mb-6">
                Life Snapshot requires a saved birth profile to generate personalized insights. Please login or create an account to continue.
              </p>
              <div className="flex gap-3 justify-center">
                <Link href="/auth/login">
                  <Button size="lg" className="bg-purple-600 hover:bg-purple-700">
                    <User className="w-4 h-4 mr-2" />
                    Login
                  </Button>
                </Link>
                <Link href="/auth/signup">
                  <Button size="lg" variant="outline" className="border-purple-600 text-purple-700 hover:bg-purple-50">
                    Create Account
                  </Button>
                </Link>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Only show tabs and content for authenticated users */}
      {isAuthenticated && (
        <>
          {/* Tabs */}
          <div className="flex gap-4 mb-6 border-b">
            <button
              onClick={() => setActiveTab('generate')}
              className={`px-4 py-2 font-medium transition-colors ${
                activeTab === 'generate'
                  ? 'text-purple-600 border-b-2 border-purple-600'
                  : 'text-gray-600 hover:text-gray-900'
              }`}
            >
              <div className="flex items-center gap-2">
                <Sparkles className="w-4 h-4" />
                Generate Snapshot
              </div>
            </button>
            <button
              onClick={() => setActiveTab('history')}
              className={`px-4 py-2 font-medium transition-colors ${
                activeTab === 'history'
                  ? 'text-purple-600 border-b-2 border-purple-600'
                  : 'text-gray-600 hover:text-gray-900'
              }`}
            >
              <div className="flex items-center gap-2">
                <HistoryIcon className="w-4 h-4" />
                History ({history.length})
              </div>
            </button>
          </div>

          {error && (
            <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg text-red-800">
              {error}
            </div>
          )}

      {/* Generate Tab */}
      {activeTab === 'generate' && (
        <div className="space-y-6">
          {/* Profile Selection */}
          {!snapshot && (
            <Card>
              <CardHeader>
                <CardTitle>Select Profile</CardTitle>
                <CardDescription>Choose a birth profile to analyze</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {profiles.length === 0 ? (
                    <p className="text-gray-600">No profiles found. Create one in My Profiles.</p>
                  ) : (
                    <>
                      <select
                        value={selectedProfile}
                        onChange={(e) => setSelectedProfile(e.target.value)}
                        className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                      >
                        {profiles.map((profile) => (
                          <option key={profile.id} value={profile.id}>
                            {profile.name} ({new Date(profile.date_of_birth).toLocaleDateString()})
                          </option>
                        ))}
                      </select>
                      <Button
                        onClick={() => generateSnapshot(false)}
                        disabled={generating || !selectedProfile}
                        className="w-full"
                      >
                        {generating ? (
                          <>
                            <RefreshCw className="w-4 h-4 mr-2 animate-spin" />
                            Generating Snapshot...
                          </>
                        ) : (
                          <>
                            <Sparkles className="w-4 h-4 mr-2" />
                            Generate Life Snapshot
                          </>
                        )}
                      </Button>
                    </>
                  )}
                </div>
              </CardContent>
            </Card>
          )}

          {/* Snapshot Results */}
          {snapshot && (
            <div className="space-y-6">
              {/* Header with profile info */}
              <Card className="border-purple-200 bg-purple-50">
                <CardContent className="pt-6">
                  <div className="flex items-center justify-between">
                    <div>
                      <div className="flex items-center gap-2 mb-2">
                        <User className="w-5 h-5 text-purple-600" />
                        <h2 className="text-xl font-bold text-purple-900">{snapshot.profile.name}</h2>
                      </div>
                      <p className="text-sm text-purple-700">
                        Generated: {new Date(snapshot.generated_at).toLocaleString()}
                      </p>
                      <p className="text-xs text-purple-600">
                        Expires: {new Date(snapshot.expires_at).toLocaleString()}
                      </p>
                    </div>
                    <Button
                      onClick={() => generateSnapshot(true)}
                      variant="outline"
                      size="sm"
                      disabled={generating}
                    >
                      <RefreshCw className={`w-4 h-4 mr-2 ${generating ? 'animate-spin' : ''}`} />
                      Refresh
                    </Button>
                  </div>
                  {snapshot.insights.life_phase && (
                    <div className="mt-4 p-3 bg-white rounded-lg">
                      <p className="text-sm font-medium text-gray-600">Current Life Phase</p>
                      <p className="text-lg font-semibold text-purple-900">{snapshot.insights.life_phase}</p>
                    </div>
                  )}
                </CardContent>
              </Card>

              {/* Top 3 Life Themes */}
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <TrendingUp className="w-5 h-5 text-blue-600" />
                    Top 3 Life Themes
                  </CardTitle>
                  <CardDescription>Current dominant areas in your life</CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    {snapshot.insights.top_themes.map((theme, index) => (
                      <div key={index} className="p-4 bg-blue-50 border border-blue-200 rounded-lg">
                        <div className="flex items-start justify-between mb-2">
                          <h3 className="font-semibold text-blue-900">{theme.title}</h3>
                          <span className="text-xs bg-blue-200 text-blue-800 px-2 py-1 rounded">
                            {Math.round(theme.confidence * 100)}% confidence
                          </span>
                        </div>
                        <p className="text-sm text-blue-700 mb-2">{theme.description}</p>
                        {theme.planetary_basis.length > 0 && (
                          <div className="flex flex-wrap gap-1">
                            {theme.planetary_basis.map((planet, i) => (
                              <span key={i} className="text-xs bg-blue-100 text-blue-600 px-2 py-0.5 rounded">
                                {planet}
                              </span>
                            ))}
                          </div>
                        )}
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>

              {/* 3 Risks This Month */}
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <AlertTriangle className="w-5 h-5 text-orange-600" />
                    3 Risks This Month
                  </CardTitle>
                  <CardDescription>Potential challenges to watch for</CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    {snapshot.insights.risks.map((risk, index) => (
                      <div key={index} className={`p-4 border rounded-lg ${getSeverityColor(risk.severity)}`}>
                        <div className="flex items-start justify-between mb-2">
                          <h3 className="font-semibold">{risk.title}</h3>
                          <span className="text-xs uppercase px-2 py-1 rounded bg-white">
                            {risk.severity} severity
                          </span>
                        </div>
                        <p className="text-sm mb-2">{risk.description}</p>
                        {risk.date_range && (
                          <p className="text-xs mb-2 flex items-center gap-1">
                            <Calendar className="w-3 h-3" />
                            {risk.date_range}
                          </p>
                        )}
                        {risk.mitigation && (
                          <div className="mt-2 pt-2 border-t border-current border-opacity-20">
                            <p className="text-xs font-medium">Mitigation:</p>
                            <p className="text-sm">{risk.mitigation}</p>
                          </div>
                        )}
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>

              {/* 3 Opportunities */}
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Sparkles className="w-5 h-5 text-green-600" />
                    3 Opportunities
                  </CardTitle>
                  <CardDescription>Windows of favorable timing</CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    {snapshot.insights.opportunities.map((opp, index) => (
                      <div key={index} className="p-4 bg-green-50 border border-green-200 rounded-lg">
                        <div className="flex items-start justify-between mb-2">
                          <h3 className="font-semibold text-green-900">{opp.title}</h3>
                          <span className="text-xs bg-green-200 text-green-800 px-2 py-1 rounded">
                            {Math.round(opp.confidence * 100)}% confidence
                          </span>
                        </div>
                        <p className="text-sm text-green-700 mb-2">{opp.description}</p>
                        <p className="text-xs text-green-600 flex items-center gap-1 mb-2">
                          <Calendar className="w-3 h-3" />
                          {opp.window}
                        </p>
                        {opp.planetary_support.length > 0 && (
                          <div className="flex flex-wrap gap-1">
                            {opp.planetary_support.map((planet, i) => (
                              <span key={i} className="text-xs bg-green-100 text-green-600 px-2 py-0.5 rounded">
                                {planet}
                              </span>
                            ))}
                          </div>
                        )}
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>

              {/* 3 Action Items */}
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Target className="w-5 h-5 text-purple-600" />
                    3 Action Items
                  </CardTitle>
                  <CardDescription>Specific steps you can take</CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    {snapshot.insights.actions.map((action, index) => (
                      <div key={index} className="p-4 bg-purple-50 border border-purple-200 rounded-lg">
                        <div className="flex items-start justify-between mb-2">
                          <h3 className="font-semibold text-purple-900">{action.action}</h3>
                          <span className={`text-xs uppercase px-2 py-1 rounded ${getPriorityColor(action.priority)}`}>
                            {action.priority}
                          </span>
                        </div>
                        <p className="text-sm text-purple-700 mb-2">{action.reason}</p>
                        {action.when && (
                          <p className="text-xs text-purple-600 flex items-center gap-1">
                            <Calendar className="w-3 h-3" />
                            {action.when}
                          </p>
                        )}
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>

              {/* Actions */}
              <div className="flex gap-4">
                <Button onClick={() => setSnapshot(null)} variant="outline" className="flex-1">
                  Generate New Snapshot
                </Button>
              </div>
            </div>
          )}
        </div>
      )}

          {/* History Tab */}
          {activeTab === 'history' && (
            <Card>
              <CardHeader>
                <CardTitle>Snapshot History</CardTitle>
                <CardDescription>Your previous life snapshots</CardDescription>
              </CardHeader>
              <CardContent>
                {loadingHistory ? (
                  <div className="text-center py-8">
                    <RefreshCw className="w-6 h-6 animate-spin mx-auto mb-2 text-purple-600" />
                    <p className="text-gray-600">Loading history...</p>
                  </div>
                ) : history.length === 0 ? (
                  <p className="text-gray-600 text-center py-8">No snapshots yet. Generate your first one!</p>
                ) : (
                  <div className="space-y-3">
                    {history.map((item) => (
                      <div
                        key={item.id}
                        className={`p-4 border rounded-lg cursor-pointer transition-colors hover:bg-gray-50 ${
                          item.is_expired ? 'opacity-60 border-gray-200' : 'border-purple-200'
                        }`}
                        onClick={() => !item.is_expired && loadSnapshot(item.id)}
                      >
                        <div className="flex items-center justify-between">
                          <div>
                            <h3 className="font-semibold text-gray-900">{item.profile_name}</h3>
                            <p className="text-sm text-gray-600">
                              Generated: {new Date(item.generated_at).toLocaleDateString()}
                            </p>
                            <p className="text-xs text-gray-500">
                              {item.themes_count} themes • {item.is_expired ? 'Expired' : 'Active'}
                            </p>
                          </div>
                          {!item.is_expired && (
                            <Button size="sm" variant="outline">
                              View
                            </Button>
                          )}
                          {item.is_expired && (
                            <span className="text-xs text-gray-500">Expired</span>
                          )}
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </CardContent>
            </Card>
          )}
        </>
      )}
    </div>
  )
}
