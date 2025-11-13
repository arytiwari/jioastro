'use client'

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { apiClient } from '@/lib/api'
import { Button } from '@/components/ui/button'
import { Textarea } from '@/components/ui/textarea'
import { Label } from '@/components/ui/label'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Sparkles, Briefcase, Heart, Activity, TrendingUp, BookOpen, GraduationCap, Calendar } from '@/components/icons'

const DOMAINS = [
  { id: 'career', label: 'Career & Work', icon: Briefcase, color: 'text-blue-600', description: 'Professional life, promotions, business' },
  { id: 'wealth', label: 'Finance & Wealth', icon: TrendingUp, color: 'text-yellow-600', description: 'Money matters, investments, prosperity' },
  { id: 'relationships', label: 'Love & Relationships', icon: Heart, color: 'text-pink-600', description: 'Romance, marriage, partnerships' },
  { id: 'health', label: 'Health & Wellness', icon: Activity, color: 'text-green-600', description: 'Physical and mental well-being' },
  { id: 'education', label: 'Education & Learning', icon: GraduationCap, color: 'text-indigo-600', description: 'Studies, knowledge, skills' },
  { id: 'spirituality', label: 'Spiritual Growth', icon: BookOpen, color: 'text-purple-600', description: 'Inner journey, enlightenment' },
]

interface Profile {
  id: string
  name: string
  is_primary?: boolean
}

export default function ComprehensiveReadingsPage() {
  const router = useRouter()
  const [profiles, setProfiles] = useState<Profile[]>([])
  const [loadingProfiles, setLoadingProfiles] = useState(true)
  const [selectedProfile, setSelectedProfile] = useState('')
  const [selectedDomains, setSelectedDomains] = useState<string[]>([])
  const [query, setQuery] = useState('')
  const [includePredictions, setIncludePredictions] = useState(true)
  const [predictionMonths, setPredictionMonths] = useState(6)
  const [forceRegenerate, setForceRegenerate] = useState(false)
  const [generating, setGenerating] = useState(false)
  const [error, setError] = useState('')
  const [pastReadings, setPastReadings] = useState<any[]>([])
  const [loadingReadings, setLoadingReadings] = useState(true)

  // Load profiles
  useEffect(() => {
    const loadProfiles = async () => {
      try {
        const response = await apiClient.getProfiles()
        setProfiles(response.data)
        // Auto-select primary profile
        const primary = response.data.find((p: any) => p.is_primary)
        if (primary) {
          setSelectedProfile(primary.id)
        }
      } catch (err) {
        console.error('Failed to load profiles:', err)
      } finally {
        setLoadingProfiles(false)
      }
    }
    loadProfiles()
  }, [])

  // Load past readings
  useEffect(() => {
    const loadReadings = async () => {
      try {
        console.log('📚 Loading past readings from API...')
        const response = await apiClient.listReadings(10, 0)
        console.log('📚 Loaded readings:', response.data?.length || 0)
        setPastReadings(response.data || [])
      } catch (err) {
        console.error('Failed to load readings:', err)
      } finally {
        setLoadingReadings(false)
      }
    }
    loadReadings()
  }, [])

  // Refresh readings list when page becomes visible (after navigation back)
  useEffect(() => {
    const handleVisibilityChange = async () => {
      if (document.visibilityState === 'visible' && !loadingReadings) {
        console.log('👁️ Page visible - refreshing readings list...')
        setLoadingReadings(true)
        try {
          const response = await apiClient.listReadings(10, 0)
          console.log('📚 Refreshed readings:', response.data?.length || 0)
          setPastReadings(response.data || [])
        } catch (err) {
          console.error('Failed to refresh readings:', err)
        } finally {
          setLoadingReadings(false)
        }
      }
    }

    document.addEventListener('visibilitychange', handleVisibilityChange)
    return () => {
      document.removeEventListener('visibilitychange', handleVisibilityChange)
    }
  }, [loadingReadings])

  const handleDeleteReading = async (sessionId: string, profileName: string, e: React.MouseEvent) => {
    // Prevent navigation when clicking delete button
    e.stopPropagation()

    if (!confirm(`Delete reading for "${profileName}"? This action cannot be undone.`)) {
      return
    }

    try {
      await apiClient.deleteReading(sessionId)
      // Remove from local state
      setPastReadings((prev) => prev.filter((r) => {
        const rId = r.id || r.session_id
        return rId !== sessionId
      }))
    } catch (err: any) {
      console.error('Failed to delete reading:', err)
      alert(err.message || 'Failed to delete reading. Please try again.')
    }
  }

  const toggleDomain = (domainId: string) => {
    setSelectedDomains((prev) =>
      prev.includes(domainId)
        ? prev.filter((d) => d !== domainId)
        : [...prev, domainId]
    )
  }

  const selectAllDomains = () => {
    setSelectedDomains(DOMAINS.map((d) => d.id))
  }

  const clearDomains = () => {
    setSelectedDomains([])
  }

  const handleGenerate = async () => {
    if (!selectedProfile) {
      setError('Please select a birth profile')
      return
    }

    if (selectedDomains.length === 0) {
      setError('Please select at least one domain for analysis')
      return
    }

    setError('')
    setGenerating(true)

    try {
      const response = await apiClient.generateComprehensiveReading({
        profile_id: selectedProfile,
        query: query.trim() || undefined,
        domains: selectedDomains,
        include_predictions: includePredictions,
        prediction_window_months: predictionMonths,
        force_regenerate: forceRegenerate,
      })

      // Store the full reading data and redirect to details page
      console.log('🎯 Full API Response:', response.data)

      const reading = response.data.reading
      console.log('📖 Extracted reading:', reading)

      const sessionId = reading?.session_id || response.data.session_id
      console.log('🆔 Session ID:', sessionId)

      if (!sessionId) {
        throw new Error('No session ID returned from API')
      }

      // Store reading data in sessionStorage so details page can use it
      if (reading) {
        // Include cache_hit flag from response
        const readingWithCacheStatus = {
          ...reading,
          was_cache_hit: response.data.cache_hit || false
        }
        const readingJson = JSON.stringify(readingWithCacheStatus)
        console.log('💾 Storing reading in sessionStorage:', `reading_${sessionId}`)
        console.log('📦 Data being stored:', {
          interpretation_length: reading.interpretation?.length,
          predictions_count: reading.predictions?.length,
          rules_count: reading.rules_used?.length,
          verification: reading.verification,
          was_cache_hit: response.data.cache_hit
        })
        sessionStorage.setItem(`reading_${sessionId}`, readingJson)

        // Verify it was stored
        const stored = sessionStorage.getItem(`reading_${sessionId}`)
        console.log('✅ Verified storage:', stored !== null)
      } else {
        console.warn('⚠️ No reading data to store!')
      }

      console.log('🚀 Navigating to:', `/dashboard/readings/${sessionId}`)
      router.push(`/dashboard/readings/${sessionId}`)
    } catch (err: any) {
      console.error('Failed to generate reading:', err)
      setError(err.message || 'Failed to generate reading. Please try again.')
    } finally {
      setGenerating(false)
    }
  }

  if (loadingProfiles) {
    return (
      <div className="text-center py-12">
        <div className="w-8 h-8 border-4 border-jio-600 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
        <p className="text-gray-600">Loading...</p>
      </div>
    )
  }

  if (!profiles || profiles.length === 0) {
    return (
      <Card>
        <CardContent className="text-center py-12">
          <Sparkles className="w-12 h-12 text-gray-400 mx-auto mb-4" />
          <h3 className="text-lg font-semibold mb-2">No Profiles Yet</h3>
          <p className="text-gray-600 mb-6">
            You need to create a birth profile before generating readings
          </p>
          <Button onClick={() => router.push('/dashboard/profiles/new')}>
            Create Your First Profile
          </Button>
        </CardContent>
      </Card>
    )
  }

  return (
    <div className="max-w-6xl mx-auto space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Comprehensive AI Readings</h1>
        <p className="text-gray-600 mt-2">
          Get scripture-grounded, multi-domain interpretations with predictions using advanced AI orchestration
        </p>
        <div className="mt-3 flex items-center gap-2 text-sm">
          <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-purple-100 text-purple-800">
            NEW
          </span>
          <span className="text-gray-600">
            Powered by 120 BPHS rules with hybrid RAG retrieval
          </span>
        </div>
      </div>

      {/* Generation Form */}
      <Card className="border-2 border-jio-200">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Sparkles className="w-5 h-5 text-jio-600" />
            Generate New Reading
          </CardTitle>
          <CardDescription>
            Select domains and configure your comprehensive astrological reading
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          {error && (
            <div className="p-3 text-sm text-red-600 bg-red-50 rounded-md border border-red-200">
              {error}
            </div>
          )}

          {/* Profile Selection */}
          <div className="space-y-2">
            <Label htmlFor="profile">Birth Profile</Label>
            <select
              id="profile"
              value={selectedProfile}
              onChange={(e) => setSelectedProfile(e.target.value)}
              className="flex h-10 w-full items-center justify-between rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2"
            >
              <option value="">Select a profile</option>
              {profiles.map((profile) => {
                // Check if name looks like a UUID
                const uuidPattern = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i
                const name = profile.name?.trim() || ''
                const isUUID = uuidPattern.test(name)

                // Use 'Unnamed Profile' if empty or if it's a UUID
                const displayName = (name && !isUUID) ? name : 'Unnamed Profile'

                return (
                  <option key={profile.id} value={profile.id}>
                    {displayName} {profile.is_primary && '(Primary)'}
                  </option>
                )
              })}
            </select>
          </div>

          {/* Domain Selection */}
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <Label>Analysis Domains</Label>
              <div className="flex gap-2">
                <button
                  type="button"
                  onClick={selectAllDomains}
                  className="text-xs text-jio-600 hover:underline"
                >
                  Select All
                </button>
                <span className="text-gray-300">|</span>
                <button
                  type="button"
                  onClick={clearDomains}
                  className="text-xs text-gray-600 hover:underline"
                >
                  Clear
                </button>
              </div>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
              {DOMAINS.map((domain) => {
                const Icon = domain.icon
                const isSelected = selectedDomains.includes(domain.id)
                return (
                  <button
                    key={domain.id}
                    type="button"
                    onClick={() => toggleDomain(domain.id)}
                    className={`p-4 border rounded-lg text-left transition-all ${
                      isSelected
                        ? 'border-jio-500 bg-jio-50 shadow-sm'
                        : 'border-gray-200 hover:border-jio-300 hover:bg-gray-50'
                    }`}
                  >
                    <div className="flex items-start gap-3">
                      <div className={`mt-0.5 ${isSelected ? 'text-jio-600' : 'text-gray-400'}`}>
                        <Icon className="w-5 h-5" />
                      </div>
                      <div className="flex-1">
                        <p className={`text-sm font-semibold ${isSelected ? 'text-jio-900' : 'text-gray-700'}`}>
                          {domain.label}
                        </p>
                        <p className="text-xs text-gray-500 mt-0.5">{domain.description}</p>
                      </div>
                      {isSelected && (
                        <div className="w-4 h-4 bg-jio-600 rounded-full flex items-center justify-center flex-shrink-0">
                          <svg className="w-3 h-3 text-white" fill="currentColor" viewBox="0 0 20 20">
                            <path
                              fillRule="evenodd"
                              d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z"
                              clipRule="evenodd"
                            />
                          </svg>
                        </div>
                      )}
                    </div>
                  </button>
                )
              })}
            </div>
            <p className="text-xs text-gray-500">
              Selected: {selectedDomains.length} of {DOMAINS.length} domains
            </p>
          </div>

          {/* Optional Query */}
          <div className="space-y-2">
            <Label htmlFor="query">Specific Question (Optional)</Label>
            <Textarea
              id="query"
              value={query}
              onChange={(e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => setQuery(e.target.value)}
              placeholder="Example: I'm considering a career change. What does my chart suggest?"
              rows={3}
              disabled={generating}
              maxLength={500}
            />
            <p className="text-xs text-gray-500">
              Leave blank for general analysis, or add a specific question to focus the reading
            </p>
          </div>

          {/* Predictions Toggle */}
          <div className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
            <div className="flex-1">
              <div className="flex items-center gap-2">
                <Calendar className="w-4 h-4 text-gray-600" />
                <Label htmlFor="predictions-toggle" className="cursor-pointer">Include Time-Based Predictions</Label>
              </div>
              <p className="text-xs text-gray-500 mt-1">
                Dasha × Transit analysis for upcoming events
              </p>
            </div>
            <button
              id="predictions-toggle"
              type="button"
              onClick={() => setIncludePredictions(!includePredictions)}
              aria-label="Toggle predictions"
              className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${
                includePredictions ? 'bg-jio-600' : 'bg-gray-300'
              }`}
            >
              <span
                className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                  includePredictions ? 'translate-x-6' : 'translate-x-1'
                }`}
              />
            </button>
          </div>

          {/* Prediction Window */}
          {includePredictions && (
            <div className="space-y-3 p-4 bg-purple-50 border border-purple-200 rounded-lg">
              <Label htmlFor="prediction-months">Prediction Timeframe: {predictionMonths} months</Label>
              <input
                id="prediction-months"
                type="range"
                min="1"
                max="12"
                value={predictionMonths}
                onChange={(e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => setPredictionMonths(parseInt(e.target.value))}
                className="w-full h-2 bg-purple-200 rounded-lg appearance-none cursor-pointer accent-jio-600"
                disabled={generating}
              />
              <div className="flex justify-between text-xs text-gray-600">
                <span>1 month</span>
                <span>6 months</span>
                <span>12 months</span>
              </div>
            </div>
          )}

          {/* Force Regenerate Option */}
          <div className="flex items-start gap-3 p-4 bg-amber-50 border border-amber-200 rounded-lg">
            <input
              id="force-regenerate"
              type="checkbox"
              checked={forceRegenerate}
              onChange={(e) => setForceRegenerate(e.target.checked)}
              className="mt-0.5 h-4 w-4 text-jio-600 border-gray-300 rounded focus:ring-jio-500"
              disabled={generating}
            />
            <div className="flex-1">
              <Label htmlFor="force-regenerate" className="cursor-pointer font-medium text-amber-900">
                Force Regenerate (Bypass Cache)
              </Label>
              <p className="text-xs text-amber-700 mt-1">
                Check this to generate a fresh reading with the latest numerology data, ignoring any cached results.
                Useful when you've updated your numerology profile or want to ensure all new features are included.
              </p>
            </div>
          </div>

          {/* Generate Button */}
          <Button
            type="button"
            onClick={handleGenerate}
            className="w-full"
            disabled={generating || !selectedProfile || selectedDomains.length === 0}
            size="lg"
          >
            {generating ? (
              <>
                <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin mr-2"></div>
                Orchestrating AI Analysis...
              </>
            ) : (
              <>
                <Sparkles className="w-5 h-5 mr-2" />
                Generate Comprehensive Reading
              </>
            )}
          </Button>

          <p className="text-xs text-center text-gray-500">
            Generation typically takes 30-60 seconds • Results are cached for 24 hours
          </p>
        </CardContent>
      </Card>

      {/* Past Readings */}
      <Card>
        <CardHeader>
          <CardTitle>Recent Readings</CardTitle>
          <CardDescription>View your past comprehensive readings (cached for 24 hours)</CardDescription>
        </CardHeader>
        <CardContent>
          {loadingReadings ? (
            <div className="text-center py-8">
              <div className="w-6 h-6 border-4 border-jio-600 border-t-transparent rounded-full animate-spin mx-auto mb-2"></div>
              <p className="text-sm text-gray-600">Loading readings...</p>
            </div>
          ) : pastReadings.length === 0 ? (
            <div className="text-center py-8 text-gray-500">
              <BookOpen className="w-12 h-12 text-gray-300 mx-auto mb-3" />
              <p className="text-sm">No readings yet. Generate your first comprehensive reading above!</p>
            </div>
          ) : (
            <div className="space-y-3">
              {pastReadings.map((reading: any) => {
                const sessionId = reading.id || reading.session_id
                const domainCount = reading.domains?.length || 0
                const predictionCount = reading.predictions?.length || 0

                return (
                  <div
                    key={sessionId}
                    className="w-full p-4 border rounded-lg hover:border-jio-300 hover:bg-jio-50 transition-colors"
                  >
                    <div className="flex items-start justify-between gap-4">
                      <button
                        onClick={() => {
                          console.log('🖱️ Clicking reading:', sessionId)
                          router.push(`/dashboard/readings/${sessionId}`)
                        }}
                        className="flex-1 text-left"
                      >
                        <div className="flex items-center gap-2 mb-1">
                          <p className="font-medium text-gray-900">
                            {reading.profile_name || 'Comprehensive Reading'}
                          </p>
                          {domainCount > 0 && (
                            <span className="text-xs text-gray-500">
                              • {domainCount} domain{domainCount !== 1 ? 's' : ''}
                            </span>
                          )}
                        </div>
                        {reading.query && (
                          <p className="text-sm text-gray-600 line-clamp-2">{reading.query}</p>
                        )}
                        <div className="flex items-center gap-3 mt-2 text-xs text-gray-500">
                          <span>{new Date(reading.created_at).toLocaleDateString()}</span>
                          {predictionCount > 0 && (
                            <span className="inline-flex items-center">
                              <Calendar className="w-3 h-3 mr-1" />
                              {predictionCount} prediction{predictionCount !== 1 ? 's' : ''}
                            </span>
                          )}
                        </div>
                      </button>
                      <div className="flex items-center gap-2">
                        <button
                          onClick={(e) => handleDeleteReading(sessionId, reading.profile_name || 'Reading', e)}
                          className="p-2 text-red-600 hover:bg-red-50 rounded-md transition-colors"
                          title="Delete reading"
                        >
                          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                          </svg>
                        </button>
                        <button
                          onClick={() => {
                            console.log('🖱️ Clicking reading:', sessionId)
                            router.push(`/dashboard/readings/${sessionId}`)
                          }}
                          className="text-jio-600"
                        >
                          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                          </svg>
                        </button>
                      </div>
                    </div>
                  </div>
                )
              })}
            </div>
          )}
        </CardContent>
      </Card>

      {/* Info Box */}
      <div className="p-4 bg-blue-50 border border-blue-200 rounded-lg">
        <h4 className="font-semibold text-blue-900 mb-2">What makes this different?</h4>
        <ul className="text-sm text-blue-800 space-y-1">
          <li>• Multi-role AI orchestration (Coordinator, Retriever, Synthesizer, Verifier, Predictor)</li>
          <li>• Scripture-grounded interpretations from 120 Brihat Parashara Hora Shastra rules</li>
          <li>• Hybrid RAG retrieval for accurate rule citations</li>
          <li>• Time-based predictions using Dasha × Transit analysis</li>
          <li>• Confidence scoring and quality verification</li>
        </ul>
      </div>
    </div>
  )
}
