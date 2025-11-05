'use client'

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { apiClient } from '@/lib/api'
import { Button } from '@/components/ui/button'
import { Label } from '@/components/ui/label'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import {
  Sparkles, Briefcase, Heart, Activity, TrendingUp, GraduationCap, BookOpen,
  Sun, Moon, Gem, Music, DollarSign, Calendar, Clock, Info, ChevronDown, ChevronUp
} from '@/components/icons'

const DOMAINS = [
  { id: '', label: 'All Domains (General)', icon: Sparkles },
  { id: 'career', label: 'Career & Work', icon: Briefcase },
  { id: 'wealth', label: 'Finance & Wealth', icon: TrendingUp },
  { id: 'relationships', label: 'Love & Relationships', icon: Heart },
  { id: 'health', label: 'Health & Wellness', icon: Activity },
  { id: 'education', label: 'Education & Learning', icon: GraduationCap },
  { id: 'spirituality', label: 'Spiritual Growth', icon: BookOpen },
]

const REMEDY_TYPE_ICONS: Record<string, any> = {
  mantra: Music,
  gemstone: Gem,
  charity: DollarSign,
  fasting: Calendar,
  ritual: Sun,
  lifestyle: Activity,
  color: Gem,
  direction: Info,
}

const PRIORITY_COLORS: Record<string, string> = {
  high: 'bg-red-100 text-red-800 border-red-300',
  medium: 'bg-yellow-100 text-yellow-800 border-yellow-300',
  low: 'bg-blue-100 text-blue-800 border-blue-300',
}

interface Profile {
  id: string
  name: string
  is_primary?: boolean
}

interface Remedy {
  remedy_type: string
  planet: string
  priority: string
  primary: any
  alternatives?: any[]
  timing?: string
  instructions?: string
  description?: string
}

export default function RemediesPage() {
  const router = useRouter()
  const [profiles, setProfiles] = useState<Profile[]>([])
  const [selectedProfile, setSelectedProfile] = useState('')
  const [selectedDomain, setSelectedDomain] = useState('')
  const [maxRemedies, setMaxRemedies] = useState(5)
  const [includePractical, setIncludePractical] = useState(true)
  const [loading, setLoading] = useState(true)
  const [generating, setGenerating] = useState(false)
  const [error, setError] = useState('')
  const [remedies, setRemedies] = useState<Remedy[]>([])
  const [expandedRemedies, setExpandedRemedies] = useState<Set<number>>(new Set())

  useEffect(() => {
    const loadProfiles = async () => {
      try {
        const response = await apiClient.getProfiles()
        setProfiles(response.data)
        const primary = response.data.find((p: any) => p.is_primary)
        if (primary) {
          setSelectedProfile(primary.id)
        }
      } catch (err) {
        console.error('Failed to load profiles:', err)
      } finally {
        setLoading(false)
      }
    }
    loadProfiles()
  }, [])

  const toggleRemedy = (index: number) => {
    const newExpanded = new Set(expandedRemedies)
    if (newExpanded.has(index)) {
      newExpanded.delete(index)
    } else {
      newExpanded.add(index)
    }
    setExpandedRemedies(newExpanded)
  }

  const handleGenerate = async () => {
    if (!selectedProfile) {
      setError('Please select a birth profile')
      return
    }

    setError('')
    setGenerating(true)
    setRemedies([])

    try {
      // First get the chart data
      const chartResponse = await apiClient.getChart(selectedProfile, 'D1')
      const chartData = chartResponse.data

      // Generate remedies
      const response = await apiClient.generateRemedies({
        chart_data: chartData,
        domain: selectedDomain || undefined,
        max_remedies: maxRemedies,
        include_practical: includePractical,
      })

      setRemedies(response.data.remedies || [])
    } catch (err: any) {
      console.error('Failed to generate remedies:', err)
      setError(err.message || 'Failed to generate remedies. Please try again.')
    } finally {
      setGenerating(false)
    }
  }

  if (loading) {
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
            You need to create a birth profile before generating remedies
          </p>
          <Button onClick={() => router.push('/dashboard/profiles/new')}>
            Create Your First Profile
          </Button>
        </CardContent>
      </Card>
    )
  }

  return (
    <div className="max-w-5xl mx-auto space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Vedic Remedies</h1>
        <p className="text-gray-600 mt-2">
          Get personalized traditional remedies based on planetary positions and weaknesses in your chart
        </p>
      </div>

      {/* Configuration */}
      <Card>
        <CardHeader>
          <CardTitle>Generate Remedies</CardTitle>
          <CardDescription>Configure your personalized remedy recommendations</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          {error && (
            <div className="p-3 text-sm text-red-600 bg-red-50 rounded-md border border-red-200">
              {error}
            </div>
          )}

          <div className="space-y-2">
            <Label htmlFor="profile">Birth Profile</Label>
            <Select value={selectedProfile} onValueChange={setSelectedProfile}>
              <SelectTrigger>
                <SelectValue placeholder="Select a profile" />
              </SelectTrigger>
              <SelectContent>
                {profiles.map((profile) => (
                  <SelectItem key={profile.id} value={profile.id}>
                    {profile.name} {profile.is_primary && '(Primary)'}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          <div className="space-y-2">
            <Label htmlFor="domain">Focus Domain (Optional)</Label>
            <Select value={selectedDomain} onValueChange={setSelectedDomain}>
              <SelectTrigger>
                <SelectValue placeholder="Select domain or leave blank for general remedies" />
              </SelectTrigger>
              <SelectContent>
                {DOMAINS.map((domain) => (
                  <SelectItem key={domain.id} value={domain.id}>
                    {domain.label}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          <div className="space-y-2">
            <Label htmlFor="max-remedies">Maximum Remedies: {maxRemedies}</Label>
            <input
              id="max-remedies"
              type="range"
              min="3"
              max="10"
              value={maxRemedies}
              onChange={(e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => setMaxRemedies(parseInt(e.target.value))}
              className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer accent-jio-600"
            />
            <div className="flex justify-between text-xs text-gray-600">
              <span>3 remedies</span>
              <span>10 remedies</span>
            </div>
          </div>

          <div className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
            <div>
              <Label htmlFor="practical" className="cursor-pointer">Include Modern Alternatives</Label>
              <p className="text-xs text-gray-500 mt-1">
                Practical substitutes for traditional remedies
              </p>
            </div>
            <button
              type="button"
              onClick={() => setIncludePractical(!includePractical)}
              className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${
                includePractical ? 'bg-jio-600' : 'bg-gray-300'
              }`}
            >
              <span
                className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                  includePractical ? 'translate-x-6' : 'translate-x-1'
                }`}
              />
            </button>
          </div>

          <Button
            onClick={handleGenerate}
            className="w-full"
            disabled={generating || !selectedProfile}
            size="lg"
          >
            {generating ? (
              <>
                <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin mr-2"></div>
                Analyzing Chart...
              </>
            ) : (
              <>
                <Sparkles className="w-5 h-5 mr-2" />
                Generate Remedies
              </>
            )}
          </Button>
        </CardContent>
      </Card>

      {/* Remedies Display */}
      {remedies.length > 0 && (
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="text-2xl font-bold text-gray-900">Your Personalized Remedies</h2>
            <span className="text-sm text-gray-600">{remedies.length} remedies</span>
          </div>

          {remedies.map((remedy, index) => {
            const Icon = REMEDY_TYPE_ICONS[remedy.remedy_type] || Info
            const isExpanded = expandedRemedies.has(index)

            return (
              <Card key={index} className="border-l-4 border-jio-500">
                <CardHeader>
                  <div className="flex items-start justify-between">
                    <div className="flex items-start gap-3 flex-1">
                      <div className="w-10 h-10 rounded-full bg-jio-100 flex items-center justify-center flex-shrink-0">
                        <Icon className="w-5 h-5 text-jio-600" />
                      </div>
                      <div className="flex-1">
                        <CardTitle className="capitalize text-lg">
                          {remedy.remedy_type.replace('_', ' ')}
                        </CardTitle>
                        <CardDescription className="mt-1">
                          For {remedy.planet}
                          {remedy.description && ` • ${remedy.description}`}
                        </CardDescription>
                      </div>
                    </div>
                    <div className="flex items-center gap-2">
                      <span className={`text-xs font-medium px-2 py-1 rounded border ${PRIORITY_COLORS[remedy.priority]}`}>
                        {remedy.priority} priority
                      </span>
                      <button
                        onClick={() => toggleRemedy(index)}
                        className="p-1 hover:bg-gray-100 rounded"
                      >
                        {isExpanded ? (
                          <ChevronUp className="w-5 h-5 text-gray-600" />
                        ) : (
                          <ChevronDown className="w-5 h-5 text-gray-600" />
                        )}
                      </button>
                    </div>
                  </div>
                </CardHeader>
                <CardContent>
                  {/* Primary Remedy */}
                  <div className="space-y-3">
                    <div>
                      <p className="text-sm font-semibold text-gray-700 mb-1">Primary Recommendation:</p>
                      <div className="pl-4 space-y-1">
                        {typeof remedy.primary === 'string' ? (
                          <p className="text-sm text-gray-700">{remedy.primary}</p>
                        ) : (
                          <>
                            {remedy.primary.text && (
                              <p className="text-sm text-gray-700">{remedy.primary.text}</p>
                            )}
                            {remedy.primary.name && (
                              <p className="text-sm text-gray-700">{remedy.primary.name}</p>
                            )}
                            {remedy.primary.weight && (
                              <p className="text-xs text-gray-600">Weight: {remedy.primary.weight}</p>
                            )}
                            {remedy.primary.finger && (
                              <p className="text-xs text-gray-600">Wear on: {remedy.primary.finger}</p>
                            )}
                            {remedy.primary.metal && (
                              <p className="text-xs text-gray-600">Metal: {remedy.primary.metal}</p>
                            )}
                            {remedy.primary.count && (
                              <p className="text-xs text-gray-600">Repetitions: {remedy.primary.count}</p>
                            )}
                          </>
                        )}
                      </div>
                    </div>

                    {isExpanded && (
                      <>
                        {/* Timing */}
                        {remedy.timing && (
                          <div>
                            <p className="text-sm font-semibold text-gray-700 mb-1 flex items-center gap-1">
                              <Clock className="w-4 h-4" />
                              Timing:
                            </p>
                            <p className="text-sm text-gray-700 pl-4">{remedy.timing}</p>
                          </div>
                        )}

                        {/* Instructions */}
                        {remedy.instructions && (
                          <div>
                            <p className="text-sm font-semibold text-gray-700 mb-1">Instructions:</p>
                            <p className="text-sm text-gray-700 pl-4">{remedy.instructions}</p>
                          </div>
                        )}

                        {/* Alternatives */}
                        {includePractical && remedy.alternatives && remedy.alternatives.length > 0 && (
                          <div>
                            <p className="text-sm font-semibold text-gray-700 mb-2">Modern Alternatives:</p>
                            <div className="space-y-2 pl-4">
                              {remedy.alternatives.map((alt: any, altIndex: number) => (
                                <div key={altIndex} className="p-3 bg-gray-50 rounded border border-gray-200">
                                  {typeof alt === 'string' ? (
                                    <p className="text-sm text-gray-700">{alt}</p>
                                  ) : (
                                    <>
                                      {alt.name && <p className="text-sm font-medium text-gray-900">{alt.name}</p>}
                                      {alt.description && <p className="text-xs text-gray-600 mt-1">{alt.description}</p>}
                                      {alt.text && <p className="text-sm text-gray-700">{alt.text}</p>}
                                    </>
                                  )}
                                </div>
                              ))}
                            </div>
                          </div>
                        )}
                      </>
                    )}
                  </div>
                </CardContent>
              </Card>
            )
          })}
        </div>
      )}

      {/* Info Box */}
      <div className="p-4 bg-yellow-50 border border-yellow-200 rounded-lg">
        <p className="text-sm text-gray-700">
          <strong>Note:</strong> These remedies are based on traditional Vedic astrology principles.
          Remedies should be performed with faith and consistency. For serious concerns, consult with
          a qualified astrologer or spiritual advisor.
        </p>
      </div>
    </div>
  )
}
