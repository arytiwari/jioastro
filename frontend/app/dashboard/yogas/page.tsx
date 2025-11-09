'use client'

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { apiClient } from '@/lib/api'
import { Button } from '@/components/ui/button'
import { Label } from '@/components/ui/label'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import {
  Sparkles, Award, TrendingUp, BookOpen, Heart, Sun, Star,
  ChevronDown, ChevronUp, Filter, BarChart, Info
} from '@/components/icons'
import { YogaDetailsModal } from '@/components/yoga/YogaDetailsModal'
import { YogaActivationTimeline } from '@/components/yoga/YogaActivationTimeline'

interface Profile {
  id: string
  name: string
  is_primary?: boolean
}

interface Yoga {
  name: string
  description: string
  strength: string
  category: string
}

// Yoga category icons and colors
const CATEGORY_CONFIG: Record<string, { icon: any; color: string; bg: string; border: string }> = {
  'Wealth': { icon: TrendingUp, color: 'text-green-700', bg: 'bg-green-50', border: 'border-green-300' },
  'Wealth & Power': { icon: TrendingUp, color: 'text-emerald-700', bg: 'bg-emerald-50', border: 'border-emerald-300' },
  'Wealth & Wisdom': { icon: TrendingUp, color: 'text-teal-700', bg: 'bg-teal-50', border: 'border-teal-300' },
  'Wealth & Character': { icon: Award, color: 'text-cyan-700', bg: 'bg-cyan-50', border: 'border-cyan-300' },
  'Wealth & Comfort': { icon: TrendingUp, color: 'text-lime-700', bg: 'bg-lime-50', border: 'border-lime-300' },
  'Wealth & Intelligence': { icon: BookOpen, color: 'text-indigo-700', bg: 'bg-indigo-50', border: 'border-indigo-300' },
  'Fame & Wealth': { icon: Star, color: 'text-amber-700', bg: 'bg-amber-50', border: 'border-amber-300' },
  'Fame & Authority': { icon: Award, color: 'text-orange-700', bg: 'bg-orange-50', border: 'border-orange-300' },
  'Fame & Reputation': { icon: Star, color: 'text-yellow-700', bg: 'bg-yellow-50', border: 'border-yellow-300' },
  'Power & Status': { icon: Award, color: 'text-red-700', bg: 'bg-red-50', border: 'border-red-300' },
  'Learning & Wisdom': { icon: BookOpen, color: 'text-purple-700', bg: 'bg-purple-50', border: 'border-purple-300' },
  'Skills & Learning': { icon: BookOpen, color: 'text-violet-700', bg: 'bg-violet-50', border: 'border-violet-300' },
  'Skills & Leadership': { icon: Award, color: 'text-fuchsia-700', bg: 'bg-fuchsia-50', border: 'border-fuchsia-300' },
  'Skills & Authority': { icon: Award, color: 'text-pink-700', bg: 'bg-pink-50', border: 'border-pink-300' },
  'Leadership': { icon: Award, color: 'text-rose-700', bg: 'bg-rose-50', border: 'border-rose-300' },
  'Intelligence': { icon: BookOpen, color: 'text-sky-700', bg: 'bg-sky-50', border: 'border-sky-300' },
  'Health & Fame': { icon: Heart, color: 'text-red-600', bg: 'bg-red-50', border: 'border-red-200' },
  'Pancha Mahapurusha': { icon: Sun, color: 'text-yellow-800', bg: 'bg-yellow-100', border: 'border-yellow-400' },
  'Transformation': { icon: Sparkles, color: 'text-purple-800', bg: 'bg-purple-100', border: 'border-purple-400' },
  'Overcoming Obstacles': { icon: Award, color: 'text-gray-700', bg: 'bg-gray-50', border: 'border-gray-300' },
  'Challenge': { icon: Award, color: 'text-slate-700', bg: 'bg-slate-50', border: 'border-slate-300' },
}

const STRENGTH_CONFIG: Record<string, { color: string; badge: string }> = {
  'Very Strong': { color: 'border-l-4 border-l-red-500', badge: 'bg-red-100 text-red-800' },
  'Strong': { color: 'border-l-4 border-l-orange-500', badge: 'bg-orange-100 text-orange-800' },
  'Medium': { color: 'border-l-4 border-l-blue-500', badge: 'bg-blue-100 text-blue-800' },
  'Weak': { color: 'border-l-4 border-l-gray-400', badge: 'bg-gray-100 text-gray-700' },
}

export default function YogasPage() {
  const router = useRouter()
  const [profiles, setProfiles] = useState<Profile[]>([])
  const [selectedProfile, setSelectedProfile] = useState('')
  const [includeAll, setIncludeAll] = useState(true)
  const [loading, setLoading] = useState(true)
  const [analyzing, setAnalyzing] = useState(false)
  const [error, setError] = useState('')
  const [yogas, setYogas] = useState<Yoga[]>([])
  const [totalYogas, setTotalYogas] = useState(0)
  const [categories, setCategories] = useState<Record<string, number>>({})
  const [strongestYogas, setStrongestYogas] = useState<string[]>([])
  const [summary, setSummary] = useState('')
  const [chartQuality, setChartQuality] = useState('')
  const [filterCategory, setFilterCategory] = useState('all')
  const [filterStrength, setFilterStrength] = useState('all')
  const [expandedYogas, setExpandedYogas] = useState<Set<number>>(new Set())
  const [selectedYoga, setSelectedYoga] = useState<Yoga | null>(null)
  const [modalOpen, setModalOpen] = useState(false)

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

  const handleAnalyze = async () => {
    if (!selectedProfile) {
      setError('Please select a birth profile')
      return
    }

    setError('')
    setAnalyzing(true)
    setYogas([])

    try {
      const response = await apiClient.analyzeYogasForProfile({
        profile_id: selectedProfile,
        include_all: includeAll,
      })

      const data = response.data
      setYogas(data.yogas || [])
      setTotalYogas(data.total_yogas || 0)
      setCategories(data.categories || {})
      setStrongestYogas(data.strongest_yogas || [])
      setSummary(data.summary || '')
      setChartQuality(data.chart_quality || '')
    } catch (err: any) {
      console.error('Failed to analyze yogas:', err)
      setError(err.message || 'Failed to analyze yogas. Please try again.')
    } finally {
      setAnalyzing(false)
    }
  }

  const toggleYoga = (index: number) => {
    const newExpanded = new Set(expandedYogas)
    if (newExpanded.has(index)) {
      newExpanded.delete(index)
    } else {
      newExpanded.add(index)
    }
    setExpandedYogas(newExpanded)
  }

  const handleYogaDetails = (yoga: Yoga) => {
    setSelectedYoga(yoga)
    setModalOpen(true)
  }

  const getFilteredYogas = () => {
    let filtered = yogas

    if (filterCategory !== 'all') {
      filtered = filtered.filter(y => y.category === filterCategory)
    }

    if (filterStrength !== 'all') {
      filtered = filtered.filter(y => y.strength === filterStrength)
    }

    return filtered
  }

  const filteredYogas = getFilteredYogas()

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
            You need to create a birth profile before analyzing yogas
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
        <h1 className="text-3xl font-bold text-gray-900">Yoga Analysis</h1>
        <p className="text-gray-600 mt-2">
          Discover 25+ classical Vedic yogas in your birth chart - special planetary combinations that indicate specific life themes and strengths
        </p>
      </div>

      {/* Configuration */}
      <Card>
        <CardHeader>
          <CardTitle>Analyze Chart for Yogas</CardTitle>
          <CardDescription>Detect classical planetary combinations in your birth chart</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          {error && (
            <div className="p-3 text-sm text-red-600 bg-red-50 rounded-md border border-red-200">
              {error}
            </div>
          )}

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="profile">Birth Profile</Label>
              <Select value={selectedProfile} onValueChange={setSelectedProfile}>
                <SelectTrigger>
                  <SelectValue>
                    {profiles.find(p => p.id === selectedProfile)?.name || 'Select a profile'}
                  </SelectValue>
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

            <div className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
              <div>
                <Label htmlFor="include-all" className="cursor-pointer font-medium">Show All Yogas</Label>
                <p className="text-xs text-gray-500 mt-1">
                  Include weak yogas or only show strong ones
                </p>
              </div>
              <button
                type="button"
                onClick={() => setIncludeAll(!includeAll)}
                className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${
                  includeAll ? 'bg-jio-600' : 'bg-gray-300'
                }`}
              >
                <span
                  className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                    includeAll ? 'translate-x-6' : 'translate-x-1'
                  }`}
                />
              </button>
            </div>
          </div>

          <Button
            onClick={handleAnalyze}
            className="w-full"
            disabled={analyzing || !selectedProfile}
            size="lg"
          >
            {analyzing ? (
              <>
                <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin mr-2"></div>
                Analyzing Chart...
              </>
            ) : (
              <>
                <Sparkles className="w-5 h-5 mr-2" />
                Analyze Yogas
              </>
            )}
          </Button>
        </CardContent>
      </Card>

      {/* Results */}
      {yogas.length > 0 && (
        <>
          {/* Summary Card */}
          <Card className="border-2 border-jio-500 bg-gradient-to-r from-jio-50 to-blue-50">
            <CardHeader>
              <div className="flex items-center justify-between">
                <CardTitle className="text-2xl">Chart Quality: {chartQuality}</CardTitle>
                <div className="flex items-center gap-2">
                  <Award className="w-6 h-6 text-jio-600" />
                  <span className="text-3xl font-bold text-jio-700">{totalYogas}</span>
                  <span className="text-sm text-gray-600">yogas</span>
                </div>
              </div>
            </CardHeader>
            <CardContent>
              <p className="text-gray-700">{summary}</p>

              {strongestYogas.length > 0 && (
                <div className="mt-4 p-3 bg-white rounded-lg border border-jio-300">
                  <p className="text-sm font-semibold text-jio-900 mb-2">⭐ Most Powerful Yogas:</p>
                  <div className="flex flex-wrap gap-2">
                    {strongestYogas.map((yoga, idx) => (
                      <span key={idx} className="px-3 py-1 bg-red-100 text-red-800 text-sm font-medium rounded-full border border-red-300">
                        {yoga}
                      </span>
                    ))}
                  </div>
                </div>
              )}

              {/* Categories */}
              <div className="mt-4 grid grid-cols-2 md:grid-cols-4 gap-2">
                {Object.entries(categories).map(([cat, count]) => (
                  <div key={cat} className="p-2 bg-white rounded border border-gray-200 text-center">
                    <p className="text-xs text-gray-600">{cat}</p>
                    <p className="text-lg font-bold text-gray-900">{count}</p>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>

          {/* Filters */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Filter className="w-5 h-5" />
                Filter Yogas
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label>Category</Label>
                  <Select value={filterCategory} onValueChange={setFilterCategory}>
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="all">All Categories</SelectItem>
                      {Object.keys(categories).map(cat => (
                        <SelectItem key={cat} value={cat}>{cat} ({categories[cat]})</SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>

                <div className="space-y-2">
                  <Label>Strength</Label>
                  <Select value={filterStrength} onValueChange={setFilterStrength}>
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="all">All Strengths</SelectItem>
                      <SelectItem value="Very Strong">Very Strong</SelectItem>
                      <SelectItem value="Strong">Strong</SelectItem>
                      <SelectItem value="Medium">Medium</SelectItem>
                      <SelectItem value="Weak">Weak</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </div>

              <div className="text-sm text-gray-600">
                Showing {filteredYogas.length} of {totalYogas} yogas
              </div>
            </CardContent>
          </Card>

          {/* Yoga List */}
          <div className="space-y-3">
            {filteredYogas.map((yoga, index) => {
              const categoryConfig = CATEGORY_CONFIG[yoga.category] || {
                icon: Star,
                color: 'text-gray-700',
                bg: 'bg-gray-50',
                border: 'border-gray-300'
              }
              const Icon = categoryConfig.icon
              const strengthConfig = STRENGTH_CONFIG[yoga.strength] || STRENGTH_CONFIG['Weak']
              const isExpanded = expandedYogas.has(index)

              return (
                <Card key={index} className={`${strengthConfig.color} hover:shadow-md transition-shadow`}>
                  <CardHeader className="cursor-pointer" onClick={() => toggleYoga(index)}>
                    <div className="flex items-start justify-between">
                      <div className="flex items-start gap-3 flex-1">
                        <div className={`w-10 h-10 rounded-full ${categoryConfig.bg} flex items-center justify-center flex-shrink-0 border-2 ${categoryConfig.border}`}>
                          <Icon className={`w-5 h-5 ${categoryConfig.color}`} />
                        </div>
                        <div className="flex-1">
                          <div className="flex items-center gap-2 flex-wrap">
                            <CardTitle className="text-lg">{yoga.name}</CardTitle>
                            <span className={`px-2 py-0.5 rounded-full text-xs font-medium ${strengthConfig.badge}`}>
                              {yoga.strength}
                            </span>
                            <span className={`px-2 py-0.5 rounded-full text-xs font-medium ${categoryConfig.bg} ${categoryConfig.color} border ${categoryConfig.border}`}>
                              {yoga.category}
                            </span>
                          </div>
                          {!isExpanded && (
                            <p className="text-sm text-gray-600 mt-1 line-clamp-2">{yoga.description}</p>
                          )}
                        </div>
                      </div>
                      <button className="p-1 hover:bg-gray-100 rounded">
                        {isExpanded ? (
                          <ChevronUp className="w-5 h-5 text-gray-600" />
                        ) : (
                          <ChevronDown className="w-5 h-5 text-gray-600" />
                        )}
                      </button>
                    </div>
                  </CardHeader>
                  {isExpanded && (
                    <CardContent>
                      <p className="text-gray-700 leading-relaxed mb-4">{yoga.description}</p>
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={(e) => {
                          e.stopPropagation()
                          handleYogaDetails(yoga)
                        }}
                        className="flex items-center gap-2"
                      >
                        <Info className="w-4 h-4" />
                        View Full Details
                      </Button>
                    </CardContent>
                  )}
                </Card>
              )
            })}
          </div>

          {/* Yoga Details Modal */}
          <YogaDetailsModal
            yoga={selectedYoga}
            open={modalOpen}
            onOpenChange={setModalOpen}
            profileId={selectedProfile}
          />

          {/* Yoga Activation Timeline */}
          <YogaActivationTimeline yogas={yogas} profileId={selectedProfile} />
        </>
      )}

      {/* Info Box */}
      <div className="p-4 bg-blue-50 border border-blue-200 rounded-lg">
        <p className="text-sm text-gray-700">
          <strong>About Yogas:</strong> Yogas are specific planetary combinations in Vedic astrology that indicate
          particular life themes, strengths, and potential outcomes. Strong yogas can significantly enhance the positive
          effects in their corresponding life areas. The presence and strength of yogas should be considered alongside
          the overall chart analysis.
        </p>
      </div>
    </div>
  )
}
