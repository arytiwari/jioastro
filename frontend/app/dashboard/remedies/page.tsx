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
      console.log(`🔽 Collapsing remedy ${index}`)
    } else {
      newExpanded.add(index)
      console.log(`🔼 Expanding remedy ${index}`)
      console.log(`📋 Full remedy data:`, remedies[index])
      console.log(`📋 Available fields:`, Object.keys(remedies[index]))
    }
    setExpandedRemedies(newExpanded)
    console.log(`📊 Expanded remedies set:`, Array.from(newExpanded))
  }

  const handleGenerate = async () => {
    console.log('🎯 Remedies: handleGenerate called')
    console.log('🎯 Selected profile:', selectedProfile)

    if (!selectedProfile) {
      setError('Please select a birth profile')
      return
    }

    setError('')
    setGenerating(true)
    setRemedies([])

    console.log('🎯 Remedies: Fetching chart data...')
    try {
      // First get the chart data
      const chartResponse = await apiClient.getChart(selectedProfile, 'D1')
      const chartData = chartResponse.data
      console.log('🎯 Remedies: Chart data received:', chartData)
      console.log('🎯 Remedies: Sending chart_data:', chartData.chart_data)

      // Generate remedies
      const response = await apiClient.generateRemedies({
        chart_data: chartData.chart_data,
        domain: selectedDomain || undefined,
        max_remedies: maxRemedies,
        include_practical: includePractical,
      })
      console.log('🎯 Remedies: Response received:', response)

      // Backend returns {success, remedies: {remedies: [], weak_planets: [], ...}}
      const remediesData = response.data.remedies?.remedies || response.data.remedies || []
      console.log('🎯 Remedies: remediesData type:', Array.isArray(remediesData), 'length:', remediesData.length)
      console.log('🎯 Remedies: First remedy:', remediesData[0])
      setRemedies(remediesData)
      console.log('🎯 Remedies: Set remedies:', remediesData)
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
            const Icon = REMEDY_TYPE_ICONS[remedy.type] || Info
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
                          {remedy.title || (remedy.type ? remedy.type.replace('_', ' ') : 'Remedy')}
                        </CardTitle>
                        <CardDescription className="mt-1">
                          {remedy.planet && `For ${remedy.planet}`}
                        </CardDescription>
                      </div>
                    </div>
                    <div className="flex items-center gap-2">
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
                  <div className="space-y-3">
                    {/* Description */}
                    {remedy.description && (
                      <div>
                        <p className="text-sm text-gray-700">{remedy.description}</p>
                      </div>
                    )}

                    {/* Day (for fasting, rituals, etc.) */}
                    {remedy.day && (
                      <div className="flex items-center gap-2 text-sm">
                        <Calendar className="w-4 h-4 text-jio-600" />
                        <span className="font-semibold text-gray-700">Day:</span>
                        <span className="text-gray-700">{remedy.day}</span>
                      </div>
                    )}

                    {isExpanded && (
                      <>
                        {/* Purpose */}
                        {remedy.purpose && (
                          <div className="p-3 bg-jio-50 rounded border border-jio-200">
                            <p className="text-sm font-semibold text-jio-900 mb-1">Purpose:</p>
                            <p className="text-sm text-jio-800">{remedy.purpose}</p>
                          </div>
                        )}

                        {/* Difficulty & Cost */}
                        <div className="flex gap-3">
                          {remedy.difficulty && (
                            <div className="flex-1 p-2 bg-gray-50 rounded border border-gray-200">
                              <p className="text-xs font-semibold text-gray-700">Difficulty</p>
                              <p className="text-sm text-gray-900 capitalize">{remedy.difficulty}</p>
                            </div>
                          )}
                          {remedy.cost && (
                            <div className="flex-1 p-2 bg-gray-50 rounded border border-gray-200">
                              <p className="text-xs font-semibold text-gray-700">Cost</p>
                              <p className="text-sm text-gray-900 capitalize">{remedy.cost}</p>
                            </div>
                          )}
                        </div>

                        {/* Recommended Foods */}
                        {remedy.recommended_foods && remedy.recommended_foods.length > 0 && (
                          <div>
                            <p className="text-sm font-semibold text-green-900 mb-2">✓ Recommended Foods:</p>
                            <div className="flex flex-wrap gap-2 pl-4">
                              {remedy.recommended_foods.map((food: string, idx: number) => (
                                <span key={idx} className="px-3 py-1 bg-green-50 text-green-800 text-sm rounded-full border border-green-200">
                                  {food}
                                </span>
                              ))}
                            </div>
                          </div>
                        )}

                        {/* Foods to Avoid */}
                        {remedy.foods_to_avoid && remedy.foods_to_avoid.length > 0 && (
                          <div>
                            <p className="text-sm font-semibold text-red-900 mb-2">✗ Foods to Avoid:</p>
                            <div className="flex flex-wrap gap-2 pl-4">
                              {remedy.foods_to_avoid.map((food: string, idx: number) => (
                                <span key={idx} className="px-3 py-1 bg-red-50 text-red-800 text-sm rounded-full border border-red-200">
                                  {food}
                                </span>
                              ))}
                            </div>
                          </div>
                        )}

                        {/* Practical Alternative */}
                        {includePractical && remedy.practical_alternative && (
                          <div className="mt-3 p-4 bg-blue-50 rounded-lg border border-blue-200">
                            <p className="text-sm font-semibold text-blue-900 mb-2">💡 Modern Alternative</p>
                            <div className="space-y-2">
                              {remedy.practical_alternative.title && (
                                <p className="text-sm font-medium text-blue-900">{remedy.practical_alternative.title}</p>
                              )}
                              {remedy.practical_alternative.description && (
                                <p className="text-sm text-blue-800">{remedy.practical_alternative.description}</p>
                              )}
                              {remedy.practical_alternative.action && (
                                <p className="text-xs text-blue-700 italic">→ {remedy.practical_alternative.action}</p>
                              )}
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
