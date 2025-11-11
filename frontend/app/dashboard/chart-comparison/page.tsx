'use client'

import { useState } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Label } from '@/components/ui/label'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Input } from '@/components/ui/input'
import { apiClient } from '@/lib/api'
import { useMutation, useQuery } from '@/lib/query'
import {
  Loader2,
  Users,
  User,
  Heart,
  TrendingUp,
  AlertCircle,
  CheckCircle,
  ArrowRight,
  Grid3x3,
  Sparkles,
  Clock,
  Briefcase,
  Star,
  Target,
  Zap,
} from 'lucide-react'

export default function ChartComparisonPage() {
  const [profile1Id, setProfile1Id] = useState('')
  const [profile2Id, setProfile2Id] = useState('')
  const [profile3Id, setProfile3Id] = useState('') // For 3-way business comparison
  const [comparisonType, setComparisonType] = useState('romantic')
  const [currentAge, setCurrentAge] = useState(30)

  // Results for each tab
  const [generalComparison, setGeneralComparison] = useState<any>(null)
  const [synastryResult, setSynastryResult] = useState<any>(null)
  const [compositeResult, setCompositeResult] = useState<any>(null)
  const [progressedResult, setProgressedResult] = useState<any>(null)
  const [business3WayResult, setBusiness3WayResult] = useState<any>(null)

  const [error, setError] = useState<string | null>(null)
  const [activeTab, setActiveTab] = useState('general')

  // Get user profiles
  const profiles = useQuery({
    queryKey: ['profiles'],
    queryFn: async () => {
      const response = await apiClient.getProfiles()
      return response.data
    },
  })

  // General Comparison mutation
  const compareMutation = useMutation({
    mutationFn: async () => {
      setError(null)
      const response = await apiClient.compareCharts({
        profile_id_1: profile1Id,
        profile_id_2: profile2Id,
        comparison_type: comparisonType,
      })
      return response.data
    },
    onSuccess: (data) => {
      setGeneralComparison(data)
      setError(null)
    },
    onError: (error: any) => {
      console.error('Comparison error:', error)
      setError(error?.message || 'Failed to compare charts')
    },
  })

  // Synastry Analysis mutation
  const synastryMutation = useMutation({
    mutationFn: async () => {
      setError(null)
      const response = await apiClient.analyzeSynastry({
        profile_id_1: profile1Id,
        profile_id_2: profile2Id,
        focus: comparisonType,
      })
      return response.data
    },
    onSuccess: (data) => {
      setSynastryResult(data)
      setError(null)
    },
    onError: (error: any) => {
      console.error('Synastry error:', error)
      setError(error?.message || 'Failed to analyze synastry')
    },
  })

  // Composite Chart mutation
  const compositeMutation = useMutation({
    mutationFn: async () => {
      setError(null)
      const response = await apiClient.generateCompositeChart({
        profile_id_1: profile1Id,
        profile_id_2: profile2Id,
      })
      return response.data
    },
    onSuccess: (data) => {
      setCompositeResult(data)
      setError(null)
    },
    onError: (error: any) => {
      console.error('Composite error:', error)
      setError(error?.message || 'Failed to generate composite chart')
    },
  })

  // Progressed Chart mutation
  const progressedMutation = useMutation({
    mutationFn: async () => {
      setError(null)
      const response = await apiClient.calculateProgressedChart({
        profile_id: profile1Id,
        current_age: currentAge,
      })
      return response.data
    },
    onSuccess: (data) => {
      setProgressedResult(data)
      setError(null)
    },
    onError: (error: any) => {
      console.error('Progressed error:', error)
      setError(error?.message || 'Failed to calculate progressed chart')
    },
  })

  // 3-Way Business Comparison (Special WOW Factor)
  const business3WayMutation = useMutation({
    mutationFn: async () => {
      setError(null)
      // Get all three comparisons
      const [comp12, comp13, comp23] = await Promise.all([
        apiClient.compareCharts({
          profile_id_1: profile1Id,
          profile_id_2: profile2Id,
          comparison_type: 'business',
        }),
        apiClient.compareCharts({
          profile_id_1: profile1Id,
          profile_id_2: profile3Id,
          comparison_type: 'business',
        }),
        apiClient.compareCharts({
          profile_id_1: profile2Id,
          profile_id_2: profile3Id,
          comparison_type: 'business',
        }),
      ])

      return {
        pair12: comp12.data,
        pair13: comp13.data,
        pair23: comp23.data,
        profiles: {
          p1: profiles.data?.find((p: any) => p.id === profile1Id),
          p2: profiles.data?.find((p: any) => p.id === profile2Id),
          p3: profiles.data?.find((p: any) => p.id === profile3Id),
        },
      }
    },
    onSuccess: (data) => {
      setBusiness3WayResult(data)
      setError(null)
    },
    onError: (error: any) => {
      console.error('3-way comparison error:', error)
      setError(error?.message || 'Failed to perform 3-way comparison')
    },
  })

  const handleCompare = () => {
    if (!profile1Id || !profile2Id) {
      setError('Please select both profiles')
      return
    }
    if (profile1Id === profile2Id) {
      setError('Please select two different profiles')
      return
    }
    compareMutation.mutate()
  }

  const handleSynastry = () => {
    if (!profile1Id || !profile2Id) {
      setError('Please select both profiles')
      return
    }
    synastryMutation.mutate()
  }

  const handleComposite = () => {
    if (!profile1Id || !profile2Id) {
      setError('Please select both profiles')
      return
    }
    compositeMutation.mutate()
  }

  const handleProgressed = () => {
    if (!profile1Id) {
      setError('Please select a profile')
      return
    }
    progressedMutation.mutate()
  }

  const handle3WayBusiness = () => {
    if (!profile1Id || !profile2Id || !profile3Id) {
      setError('Please select all three profiles for 3-way comparison')
      return
    }
    if (profile1Id === profile2Id || profile1Id === profile3Id || profile2Id === profile3Id) {
      setError('Please select three different profiles')
      return
    }
    business3WayMutation.mutate()
  }

  const getCompatibilityColor = (level: string) => {
    const colors = {
      excellent: 'bg-green-50 border-green-200 dark:bg-green-900/20',
      'very good': 'bg-emerald-50 border-emerald-200 dark:bg-emerald-900/20',
      good: 'bg-blue-50 border-blue-200 dark:bg-blue-900/20',
      moderate: 'bg-yellow-50 border-yellow-200 dark:bg-yellow-900/20',
      challenging: 'bg-orange-50 border-orange-200 dark:bg-orange-900/20',
      difficult: 'bg-red-50 border-red-200 dark:bg-red-900/20',
    }
    return colors[level as keyof typeof colors] || colors.moderate
  }

  const getScoreColor = (score: number) => {
    if (score >= 80) return 'text-green-600 dark:text-green-400'
    if (score >= 70) return 'text-emerald-600 dark:text-emerald-400'
    if (score >= 60) return 'text-blue-600 dark:text-blue-400'
    if (score >= 50) return 'text-yellow-600 dark:text-yellow-400'
    if (score >= 40) return 'text-orange-600 dark:text-orange-400'
    return 'text-red-600 dark:text-red-400'
  }

  const getRatingColor = (rating: string) => {
    const ratings: Record<string, string> = {
      exceptional: 'text-purple-600 dark:text-purple-400',
      excellent: 'text-green-600 dark:text-green-400',
      'very good': 'text-emerald-600 dark:text-emerald-400',
      good: 'text-blue-600 dark:text-blue-400',
      moderate: 'text-yellow-600 dark:text-yellow-400',
      challenging: 'text-orange-600 dark:text-orange-400',
    }
    return ratings[rating.toLowerCase()] || 'text-gray-600'
  }

  return (
    <div className="container mx-auto p-6 max-w-7xl">
      <div className="mb-8">
        <h1 className="text-3xl font-bold flex items-center gap-3">
          <Users className="w-8 h-8 text-blue-600" />
          Chart Comparison & Synastry
        </h1>
        <p className="text-muted-foreground mt-2">
          Advanced chart comparison with synastry, composite charts, progressions, and 3-way business analysis
        </p>
      </div>

      {/* Selection Form */}
      <Card className="mb-6">
        <CardHeader>
          <CardTitle>Select Profiles to Compare</CardTitle>
          <CardDescription>
            Choose profiles for compatibility analysis
            {comparisonType === 'business' && ' • Select 3 profiles for advanced business partnership analysis'}
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div>
              <Label htmlFor="profile1">Person 1</Label>
              <Select value={profile1Id} onValueChange={setProfile1Id}>
                <SelectTrigger id="profile1" className="mt-1">
                  <SelectValue placeholder="Select profile" />
                </SelectTrigger>
                <SelectContent>
                  {profiles.data?.map((profile: any) => (
                    <SelectItem key={profile.id} value={profile.id}>
                      {profile.name}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            <div>
              <Label htmlFor="profile2">Person 2</Label>
              <Select value={profile2Id} onValueChange={setProfile2Id}>
                <SelectTrigger id="profile2" className="mt-1">
                  <SelectValue placeholder="Select profile" />
                </SelectTrigger>
                <SelectContent>
                  {profiles.data?.map((profile: any) => (
                    <SelectItem key={profile.id} value={profile.id}>
                      {profile.name}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            {comparisonType === 'business' && (
              <div>
                <Label htmlFor="profile3" className="flex items-center gap-1">
                  Person 3 <Star className="w-3 h-3 text-yellow-500" />
                </Label>
                <Select value={profile3Id} onValueChange={setProfile3Id}>
                  <SelectTrigger id="profile3" className="mt-1">
                    <SelectValue placeholder="Select profile" />
                  </SelectTrigger>
                  <SelectContent>
                    {profiles.data?.map((profile: any) => (
                      <SelectItem key={profile.id} value={profile.id}>
                        {profile.name}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
            )}

            <div>
              <Label htmlFor="comparisonType">Comparison Type</Label>
              <Select value={comparisonType} onValueChange={setComparisonType}>
                <SelectTrigger id="comparisonType" className="mt-1">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="romantic">
                    <div className="flex items-center gap-2">
                      <Heart className="w-4 h-4" />
                      Romantic
                    </div>
                  </SelectItem>
                  <SelectItem value="business">
                    <div className="flex items-center gap-2">
                      <Briefcase className="w-4 h-4" />
                      Business (3-way available!)
                    </div>
                  </SelectItem>
                  <SelectItem value="family">Family</SelectItem>
                  <SelectItem value="friendship">Friendship</SelectItem>
                  <SelectItem value="general">General</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>

          {error && (
            <div className="p-4 rounded-lg border border-red-300 bg-red-50 dark:bg-red-900/20">
              <p className="text-sm text-red-600 dark:text-red-400">{error}</p>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Tabbed Interface */}
      <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-6">
        <TabsList className="grid w-full grid-cols-5 lg:w-auto">
          <TabsTrigger value="general" className="flex items-center gap-2">
            <TrendingUp className="w-4 h-4" />
            <span className="hidden sm:inline">General</span>
          </TabsTrigger>
          <TabsTrigger value="synastry" className="flex items-center gap-2">
            <Grid3x3 className="w-4 h-4" />
            <span className="hidden sm:inline">Synastry</span>
          </TabsTrigger>
          <TabsTrigger value="composite" className="flex items-center gap-2">
            <Sparkles className="w-4 h-4" />
            <span className="hidden sm:inline">Composite</span>
          </TabsTrigger>
          <TabsTrigger value="progressed" className="flex items-center gap-2">
            <Clock className="w-4 h-4" />
            <span className="hidden sm:inline">Progressed</span>
          </TabsTrigger>
          {comparisonType === 'business' && (
            <TabsTrigger value="3way" className="flex items-center gap-2">
              <Zap className="w-4 h-4 text-yellow-500" />
              <span className="hidden sm:inline">3-Way</span>
            </TabsTrigger>
          )}
        </TabsList>

        {/* GENERAL COMPARISON TAB */}
        <TabsContent value="general" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>General Compatibility Analysis</CardTitle>
              <CardDescription>
                Overall compatibility assessment with detailed factor breakdown
              </CardDescription>
            </CardHeader>
            <CardContent>
              <Button
                onClick={handleCompare}
                disabled={compareMutation.isPending}
                className="w-full"
                size="lg"
              >
                {compareMutation.isPending ? (
                  <>
                    <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                    Analyzing...
                  </>
                ) : (
                  <>
                    <TrendingUp className="w-4 h-4 mr-2" />
                    Compare Charts
                  </>
                )}
              </Button>
            </CardContent>
          </Card>

          {generalComparison && (
            <div className="space-y-6">
              {/* Overall Score */}
              <Card className={getCompatibilityColor(generalComparison.summary?.compatibility_level)}>
                <CardHeader>
                  <CardTitle className="flex items-center justify-between">
                    <span>Compatibility Analysis</span>
                    <div className="flex items-center gap-4">
                      <span className={`text-4xl font-bold ${getScoreColor(generalComparison.summary?.overall_score)}`}>
                        {generalComparison.summary?.overall_score}%
                      </span>
                      <span className="text-lg font-medium capitalize">
                        {generalComparison.summary?.compatibility_level}
                      </span>
                    </div>
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                      <p className="font-semibold text-sm text-muted-foreground mb-1">Person 1</p>
                      <p className="font-medium">{generalComparison.profile_1?.name}</p>
                      <p className="text-sm text-muted-foreground">
                        {generalComparison.profile_1?.ascendant} Asc • {generalComparison.profile_1?.moon_sign} Moon
                      </p>
                    </div>
                    <div>
                      <p className="font-semibold text-sm text-muted-foreground mb-1">Person 2</p>
                      <p className="font-medium">{generalComparison.profile_2?.name}</p>
                      <p className="text-sm text-muted-foreground">
                        {generalComparison.profile_2?.ascendant} Asc • {generalComparison.profile_2?.moon_sign} Moon
                      </p>
                    </div>
                  </div>
                </CardContent>
              </Card>

              {/* Compatibility Factors */}
              <Card>
                <CardHeader>
                  <CardTitle>Compatibility Factors</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    {generalComparison.compatibility_factors?.map((factor: any, idx: number) => (
                      <div key={idx} className="p-4 rounded-lg border bg-card">
                        <div className="flex items-start justify-between mb-2">
                          <div className="flex items-center gap-2">
                            {factor.is_positive ? (
                              <CheckCircle className="w-5 h-5 text-green-600" />
                            ) : (
                              <AlertCircle className="w-5 h-5 text-yellow-600" />
                            )}
                            <h4 className="font-semibold">{factor.factor_name}</h4>
                          </div>
                          <span className={`text-xl font-bold ${getScoreColor(factor.score)}`}>
                            {factor.score}%
                          </span>
                        </div>
                        <p className="text-sm text-muted-foreground">{factor.description}</p>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>

              {/* Strengths & Challenges */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <Card>
                  <CardHeader>
                    <CardTitle className="text-green-700 dark:text-green-400 flex items-center gap-2">
                      <CheckCircle className="w-5 h-5" />
                      Strengths
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <ul className="space-y-2">
                      {generalComparison.summary?.strengths?.map((strength: string, idx: number) => (
                        <li key={idx} className="flex items-start gap-2 text-sm">
                          <ArrowRight className="w-4 h-4 mt-0.5 text-green-600 flex-shrink-0" />
                          <span>{strength}</span>
                        </li>
                      ))}
                    </ul>
                  </CardContent>
                </Card>

                <Card>
                  <CardHeader>
                    <CardTitle className="text-orange-700 dark:text-orange-400 flex items-center gap-2">
                      <AlertCircle className="w-5 h-5" />
                      Challenges
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <ul className="space-y-2">
                      {generalComparison.summary?.challenges?.map((challenge: string, idx: number) => (
                        <li key={idx} className="flex items-start gap-2 text-sm">
                          <ArrowRight className="w-4 h-4 mt-0.5 text-orange-600 flex-shrink-0" />
                          <span>{challenge}</span>
                        </li>
                      ))}
                    </ul>
                  </CardContent>
                </Card>
              </div>

              {/* Key Aspects */}
              <Card>
                <CardHeader>
                  <CardTitle>Key Aspects</CardTitle>
                  <CardDescription>
                    {generalComparison.harmonious_aspects_count} harmonious • {generalComparison.challenging_aspects_count} challenging
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="space-y-2">
                    {generalComparison.inter_chart_aspects?.slice(0, 10).map((aspect: any, idx: number) => (
                      <div
                        key={idx}
                        className={`p-3 rounded-lg border ${aspect.is_harmonious ? 'bg-green-50 border-green-200 dark:bg-green-900/20' : 'bg-orange-50 border-orange-200 dark:bg-orange-900/20'}`}
                      >
                        <div className="flex items-center justify-between">
                          <span className="text-sm font-medium">
                            {aspect.planet_1} {aspect.aspect_type} {aspect.planet_2}
                          </span>
                          <span className="text-xs px-2 py-1 rounded-full bg-background">
                            {aspect.strength}
                          </span>
                        </div>
                        <p className="text-xs text-muted-foreground mt-1">{aspect.interpretation}</p>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            </div>
          )}
        </TabsContent>

        {/* SYNASTRY ANALYSIS TAB */}
        <TabsContent value="synastry" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Synastry Analysis</CardTitle>
              <CardDescription>
                Detailed aspect-by-aspect analysis with aspect grid and double whammies
              </CardDescription>
            </CardHeader>
            <CardContent>
              <Button
                onClick={handleSynastry}
                disabled={synastryMutation.isPending}
                className="w-full"
                size="lg"
              >
                {synastryMutation.isPending ? (
                  <>
                    <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                    Analyzing Synastry...
                  </>
                ) : (
                  <>
                    <Grid3x3 className="w-4 h-4 mr-2" />
                    Analyze Synastry
                  </>
                )}
              </Button>
            </CardContent>
          </Card>

          {synastryResult && (
            <div className="space-y-6">
              {/* Synastry Score */}
              <Card className="border-2 border-purple-200 dark:border-purple-800">
                <CardHeader>
                  <CardTitle className="flex items-center justify-between">
                    <span>Synastry Compatibility</span>
                    <div className="flex items-center gap-4">
                      <span className={`text-4xl font-bold ${getScoreColor(synastryResult.synastry_score?.overall_score)}`}>
                        {synastryResult.synastry_score?.overall_score}%
                      </span>
                      <span className={`text-lg font-medium ${getRatingColor(synastryResult.synastry_score?.rating)}`}>
                        {synastryResult.synastry_score?.rating}
                      </span>
                    </div>
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="grid grid-cols-2 gap-4 text-sm">
                    <div>
                      <p className="text-muted-foreground">Aspects Analyzed</p>
                      <p className="text-xl font-bold">{synastryResult.synastry_score?.aspects_analyzed}</p>
                    </div>
                    <div>
                      <p className="text-muted-foreground">Double Whammies</p>
                      <p className="text-xl font-bold text-purple-600">{synastryResult.synastry_score?.double_whammies_found}</p>
                    </div>
                  </div>
                </CardContent>
              </Card>

              {/* Aspect Grid */}
              <Card>
                <CardHeader>
                  <CardTitle>Aspect Grid</CardTitle>
                  <CardDescription>
                    Visual matrix of all planetary aspects between charts
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="overflow-x-auto">
                    <table className="w-full text-sm">
                      <thead>
                        <tr>
                          <th className="p-2 border"></th>
                          {synastryResult.aspect_grid?.[0]?.slice(1).map((planet: string, idx: number) => (
                            <th key={idx} className="p-2 border font-medium">{planet}</th>
                          ))}
                        </tr>
                      </thead>
                      <tbody>
                        {synastryResult.aspect_grid?.slice(1).map((row: string[], rowIdx: number) => (
                          <tr key={rowIdx}>
                            <th className="p-2 border font-medium">{row[0]}</th>
                            {row.slice(1).map((cell: string, cellIdx: number) => (
                              <td key={cellIdx} className="p-2 border text-center">
                                {cell !== '-' ? <span className="text-2xl">{cell}</span> : <span className="text-gray-300">-</span>}
                              </td>
                            ))}
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                  <div className="mt-4 text-xs text-muted-foreground flex gap-4 flex-wrap">
                    <span>☌ Conjunction</span>
                    <span>⚹ Sextile</span>
                    <span>□ Square</span>
                    <span>△ Trine</span>
                    <span>☍ Opposition</span>
                  </div>
                </CardContent>
              </Card>

              {/* Double Whammies */}
              {synastryResult.double_whammies?.length > 0 && (
                <Card className="bg-purple-50 dark:bg-purple-900/20 border-purple-200 dark:border-purple-800">
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2 text-purple-700 dark:text-purple-300">
                      <Star className="w-5 h-5" />
                      Double Whammies (Extra Powerful!)
                    </CardTitle>
                    <CardDescription>
                      Mutual aspects between same planets - especially significant connections
                    </CardDescription>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-3">
                      {synastryResult.double_whammies.map((dw: any, idx: number) => (
                        <div key={idx} className="p-4 rounded-lg border border-purple-300 dark:border-purple-700 bg-white dark:bg-gray-900">
                          <h4 className="font-semibold text-purple-700 dark:text-purple-300 mb-2">{dw.planet_pair}</h4>
                          <p className="text-sm">{dw.interpretation}</p>
                          <p className="text-xs text-muted-foreground mt-1">{dw.significance}</p>
                        </div>
                      ))}
                    </div>
                  </CardContent>
                </Card>
              )}

              {/* Focus Analysis */}
              <Card>
                <CardHeader>
                  <CardTitle>Focus: {synastryResult.focus_analysis?.focus_type.toUpperCase()}</CardTitle>
                  <CardDescription>
                    Analysis specific to {synastryResult.focus_analysis?.focus_type} compatibility
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="grid grid-cols-3 gap-4 mb-4">
                    <div className="text-center p-3 rounded-lg border">
                      <p className="text-2xl font-bold text-green-600">{synastryResult.focus_analysis?.harmonious_count}</p>
                      <p className="text-xs text-muted-foreground">Harmonious</p>
                    </div>
                    <div className="text-center p-3 rounded-lg border">
                      <p className="text-2xl font-bold text-orange-600">{synastryResult.focus_analysis?.challenging_count}</p>
                      <p className="text-xs text-muted-foreground">Challenging</p>
                    </div>
                    <div className="text-center p-3 rounded-lg border">
                      <p className={`text-2xl font-bold ${getScoreColor(synastryResult.focus_analysis?.focus_score)}`}>
                        {synastryResult.focus_analysis?.focus_score.toFixed(1)}%
                      </p>
                      <p className="text-xs text-muted-foreground">Focus Score</p>
                    </div>
                  </div>
                </CardContent>
              </Card>

              {/* Detailed Interpretations */}
              <Card>
                <CardHeader>
                  <CardTitle>Detailed Aspect Interpretations</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    {synastryResult.detailed_interpretations?.map((interp: any, idx: number) => (
                      <div key={idx} className={`p-4 rounded-lg border ${interp.harmonious ? 'bg-green-50 dark:bg-green-900/20' : 'bg-orange-50 dark:bg-orange-900/20'}`}>
                        <div className="flex items-center justify-between mb-2">
                          <h4 className="font-semibold">{interp.aspect}</h4>
                          <span className="text-xs px-2 py-1 rounded-full bg-background">
                            {interp.strength}
                          </span>
                        </div>
                        <p className="text-sm mb-2">{interp.detailed_interpretation}</p>
                        <div className="flex items-start gap-2 mt-2 pt-2 border-t">
                          <Target className="w-4 h-4 mt-0.5 text-blue-600 flex-shrink-0" />
                          <p className="text-xs text-muted-foreground italic">{interp.advice}</p>
                        </div>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            </div>
          )}
        </TabsContent>

        {/* COMPOSITE CHART TAB */}
        <TabsContent value="composite" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Composite Chart</CardTitle>
              <CardDescription>
                Midpoint chart representing the relationship itself as a unique entity
              </CardDescription>
            </CardHeader>
            <CardContent>
              <Button
                onClick={handleComposite}
                disabled={compositeMutation.isPending}
                className="w-full"
                size="lg"
              >
                {compositeMutation.isPending ? (
                  <>
                    <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                    Generating Composite Chart...
                  </>
                ) : (
                  <>
                    <Sparkles className="w-4 h-4 mr-2" />
                    Generate Composite Chart
                  </>
                )}
              </Button>
            </CardContent>
          </Card>

          {compositeResult && (
            <div className="space-y-6">
              {/* Overall Tone */}
              <Card className="bg-gradient-to-r from-purple-50 to-pink-50 dark:from-purple-900/20 dark:to-pink-900/20 border-purple-200 dark:border-purple-800">
                <CardHeader>
                  <CardTitle className="flex items-center justify-between">
                    <span>Relationship Energy</span>
                    <span className="text-lg font-medium capitalize px-4 py-2 rounded-full bg-white dark:bg-gray-900">
                      {compositeResult.analysis?.overall_tone?.replace('_', ' ')}
                    </span>
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                      <h4 className="font-semibold mb-2 text-green-700 dark:text-green-400">Relationship Strengths</h4>
                      <ul className="space-y-1">
                        {compositeResult.strengths?.map((strength: string, idx: number) => (
                          <li key={idx} className="flex items-start gap-2 text-sm">
                            <CheckCircle className="w-4 h-4 mt-0.5 text-green-600 flex-shrink-0" />
                            <span>{strength}</span>
                          </li>
                        ))}
                      </ul>
                    </div>
                    <div>
                      <h4 className="font-semibold mb-2 text-orange-700 dark:text-orange-400">Relationship Challenges</h4>
                      <ul className="space-y-1">
                        {compositeResult.challenges?.map((challenge: string, idx: number) => (
                          <li key={idx} className="flex items-start gap-2 text-sm">
                            <AlertCircle className="w-4 h-4 mt-0.5 text-orange-600 flex-shrink-0" />
                            <span>{challenge}</span>
                          </li>
                        ))}
                      </ul>
                    </div>
                  </div>
                </CardContent>
              </Card>

              {/* Relationship Themes */}
              <Card>
                <CardHeader>
                  <CardTitle>Relationship Themes</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="flex flex-wrap gap-2">
                    {compositeResult.relationship_themes?.map((theme: string, idx: number) => (
                      <span key={idx} className="px-3 py-1 rounded-full bg-purple-100 dark:bg-purple-900/30 text-purple-700 dark:text-purple-300 text-sm">
                        {theme}
                      </span>
                    ))}
                  </div>
                </CardContent>
              </Card>

              {/* Composite Planets */}
              <Card>
                <CardHeader>
                  <CardTitle>Composite Planet Positions</CardTitle>
                  <CardDescription>
                    Midpoint positions representing the relationship's planetary energies
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                    {Object.entries(compositeResult.relationship_chart?.planets || {}).map(([planet, data]: [string, any]) => (
                      <div key={planet} className="p-3 rounded-lg border bg-card">
                        <div className="flex items-center justify-between mb-1">
                          <h4 className="font-semibold">{planet}</h4>
                          <span className="text-sm px-2 py-1 rounded-full bg-purple-100 dark:bg-purple-900/30">
                            {data.sign}
                          </span>
                        </div>
                        <p className="text-xs text-muted-foreground">{data.description}</p>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>

              {/* Interpretation */}
              <Card>
                <CardHeader>
                  <CardTitle>Composite Chart Interpretation</CardTitle>
                </CardHeader>
                <CardContent>
                  <pre className="text-sm whitespace-pre-wrap text-muted-foreground font-sans">
                    {compositeResult.interpretation}
                  </pre>
                </CardContent>
              </Card>
            </div>
          )}
        </TabsContent>

        {/* PROGRESSED CHART TAB */}
        <TabsContent value="progressed" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Progressed Chart (Secondary Progressions)</CardTitle>
              <CardDescription>
                1 day after birth = 1 year of life. See your current evolutionary stage.
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <Label htmlFor="age">Current Age</Label>
                <Input
                  id="age"
                  type="number"
                  min="0"
                  max="120"
                  value={currentAge}
                  onChange={(e) => setCurrentAge(parseInt(e.target.value) || 0)}
                  className="mt-1"
                />
              </div>
              <Button
                onClick={handleProgressed}
                disabled={progressedMutation.isPending}
                className="w-full"
                size="lg"
              >
                {progressedMutation.isPending ? (
                  <>
                    <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                    Calculating Progressions...
                  </>
                ) : (
                  <>
                    <Clock className="w-4 h-4 mr-2" />
                    Calculate Progressed Chart
                  </>
                )}
              </Button>
            </CardContent>
          </Card>

          {progressedResult && (
            <div className="space-y-6">
              {/* Age Info */}
              <Card className="bg-gradient-to-r from-blue-50 to-cyan-50 dark:from-blue-900/20 dark:to-cyan-900/20">
                <CardHeader>
                  <CardTitle>Progressed Chart for Age {progressedResult.current_age}</CardTitle>
                  <CardDescription>
                    Progressed date: {new Date(progressedResult.progressed_date).toLocaleDateString()}
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="grid grid-cols-2 gap-4 text-sm">
                    <div className="p-3 rounded-lg border bg-white dark:bg-gray-900">
                      <p className="text-muted-foreground mb-1">Progressed Ascendant</p>
                      <p className="text-xl font-bold">{progressedResult.progressed_ascendant?.sign}</p>
                      <p className="text-xs text-muted-foreground">{progressedResult.progressed_ascendant?.degree.toFixed(2)}°</p>
                    </div>
                    <div className="p-3 rounded-lg border bg-white dark:bg-gray-900">
                      <p className="text-muted-foreground mb-1">Progression Speed</p>
                      <p className="text-xs">Sun: ~1°/year</p>
                      <p className="text-xs">Moon: ~13°/year</p>
                    </div>
                  </div>
                </CardContent>
              </Card>

              {/* Major Changes */}
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Star className="w-5 h-5 text-yellow-500" />
                    Major Life Developments
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <ul className="space-y-2">
                    {progressedResult.major_changes?.map((change: string, idx: number) => (
                      <li key={idx} className="flex items-start gap-2 text-sm p-3 rounded-lg bg-yellow-50 dark:bg-yellow-900/20">
                        <ArrowRight className="w-4 h-4 mt-0.5 text-yellow-600 flex-shrink-0" />
                        <span>{change}</span>
                      </li>
                    ))}
                  </ul>
                </CardContent>
              </Card>

              {/* Current Themes */}
              <Card>
                <CardHeader>
                  <CardTitle>Current Life Themes</CardTitle>
                </CardHeader>
                <CardContent>
                  <ul className="space-y-2">
                    {progressedResult.current_themes?.map((theme: string, idx: number) => (
                      <li key={idx} className="flex items-start gap-2 text-sm">
                        <Target className="w-4 h-4 mt-0.5 text-blue-600 flex-shrink-0" />
                        <span>{theme}</span>
                      </li>
                    ))}
                  </ul>
                </CardContent>
              </Card>

              {/* Progressed Planets */}
              <Card>
                <CardHeader>
                  <CardTitle>Progressed Planet Positions</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                    {Object.entries(progressedResult.progressed_planets || {}).map(([planet, data]: [string, any]) => (
                      <div key={planet} className="p-3 rounded-lg border bg-card">
                        <div className="flex items-center justify-between mb-2">
                          <h4 className="font-semibold">{planet}</h4>
                          <span className="text-sm px-2 py-1 rounded-full bg-blue-100 dark:bg-blue-900/30">
                            {data.sign}
                          </span>
                        </div>
                        <div className="text-xs space-y-1">
                          <p className="text-muted-foreground">
                            Degree: {data.degree?.toFixed(2)}°
                          </p>
                          {data.change_from_natal?.sign_change && (
                            <p className="text-green-600 dark:text-green-400 font-medium">
                              ✨ Changed to {data.change_from_natal.new_sign}
                            </p>
                          )}
                          <p className="text-muted-foreground">
                            Moved: {data.change_from_natal?.degrees_moved?.toFixed(2)}° from natal
                          </p>
                        </div>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>

              {/* Interpretation */}
              <Card>
                <CardHeader>
                  <CardTitle>Progressed Chart Interpretation</CardTitle>
                </CardHeader>
                <CardContent>
                  <pre className="text-sm whitespace-pre-wrap text-muted-foreground font-sans">
                    {progressedResult.interpretation}
                  </pre>
                </CardContent>
              </Card>
            </div>
          )}
        </TabsContent>

        {/* 3-WAY BUSINESS COMPARISON TAB (WOW FACTOR!) */}
        {comparisonType === 'business' && (
          <TabsContent value="3way" className="space-y-6">
            <Card className="bg-gradient-to-r from-yellow-50 via-orange-50 to-red-50 dark:from-yellow-900/20 dark:via-orange-900/20 dark:to-red-900/20 border-yellow-300 dark:border-yellow-700">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Zap className="w-6 h-6 text-yellow-500" />
                  3-Way Business Partnership Analysis
                </CardTitle>
                <CardDescription>
                  Analyze three-way business compatibility - find the perfect team dynamic!
                </CardDescription>
              </CardHeader>
              <CardContent>
                <Button
                  onClick={handle3WayBusiness}
                  disabled={business3WayMutation.isPending || !profile1Id || !profile2Id || !profile3Id}
                  className="w-full bg-gradient-to-r from-yellow-500 to-orange-500 hover:from-yellow-600 hover:to-orange-600"
                  size="lg"
                >
                  {business3WayMutation.isPending ? (
                    <>
                      <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                      Analyzing 3-Way Partnership...
                    </>
                  ) : (
                    <>
                      <Briefcase className="w-4 h-4 mr-2" />
                      Analyze 3-Way Business Compatibility
                    </>
                  )}
                </Button>
              </CardContent>
            </Card>

            {business3WayResult && (
              <div className="space-y-6">
                {/* Overall 3-Way Score */}
                <Card className="border-2 border-yellow-300 dark:border-yellow-700">
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      <Star className="w-5 h-5 text-yellow-500" />
                      Team Compatibility Matrix
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="grid grid-cols-3 gap-4">
                      <div className="text-center">
                        <p className="text-sm text-muted-foreground mb-2">{business3WayResult.profiles?.p1?.name}</p>
                        <div className="aspect-square rounded-full bg-blue-100 dark:bg-blue-900/30 flex items-center justify-center">
                          <span className="text-2xl font-bold text-blue-600">P1</span>
                        </div>
                      </div>
                      <div className="text-center">
                        <p className="text-sm text-muted-foreground mb-2">{business3WayResult.profiles?.p2?.name}</p>
                        <div className="aspect-square rounded-full bg-green-100 dark:bg-green-900/30 flex items-center justify-center">
                          <span className="text-2xl font-bold text-green-600">P2</span>
                        </div>
                      </div>
                      <div className="text-center">
                        <p className="text-sm text-muted-foreground mb-2">{business3WayResult.profiles?.p3?.name}</p>
                        <div className="aspect-square rounded-full bg-purple-100 dark:bg-purple-900/30 flex items-center justify-center">
                          <span className="text-2xl font-bold text-purple-600">P3</span>
                        </div>
                      </div>
                    </div>
                  </CardContent>
                </Card>

                {/* Pairwise Comparisons */}
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                  {/* Pair 1-2 */}
                  <Card className="border-2 border-blue-200 dark:border-blue-800">
                    <CardHeader>
                      <CardTitle className="text-sm">
                        {business3WayResult.profiles?.p1?.name} ⟷ {business3WayResult.profiles?.p2?.name}
                      </CardTitle>
                    </CardHeader>
                    <CardContent>
                      <div className="text-center mb-3">
                        <span className={`text-3xl font-bold ${getScoreColor(business3WayResult.pair12?.summary?.overall_score)}`}>
                          {business3WayResult.pair12?.summary?.overall_score}%
                        </span>
                        <p className="text-xs text-muted-foreground mt-1 capitalize">
                          {business3WayResult.pair12?.summary?.compatibility_level}
                        </p>
                      </div>
                      <div className="space-y-1 text-xs">
                        <p className="font-semibold text-green-600">Top Strength:</p>
                        <p className="text-muted-foreground">{business3WayResult.pair12?.summary?.strengths?.[0]}</p>
                      </div>
                    </CardContent>
                  </Card>

                  {/* Pair 1-3 */}
                  <Card className="border-2 border-green-200 dark:border-green-800">
                    <CardHeader>
                      <CardTitle className="text-sm">
                        {business3WayResult.profiles?.p1?.name} ⟷ {business3WayResult.profiles?.p3?.name}
                      </CardTitle>
                    </CardHeader>
                    <CardContent>
                      <div className="text-center mb-3">
                        <span className={`text-3xl font-bold ${getScoreColor(business3WayResult.pair13?.summary?.overall_score)}`}>
                          {business3WayResult.pair13?.summary?.overall_score}%
                        </span>
                        <p className="text-xs text-muted-foreground mt-1 capitalize">
                          {business3WayResult.pair13?.summary?.compatibility_level}
                        </p>
                      </div>
                      <div className="space-y-1 text-xs">
                        <p className="font-semibold text-green-600">Top Strength:</p>
                        <p className="text-muted-foreground">{business3WayResult.pair13?.summary?.strengths?.[0]}</p>
                      </div>
                    </CardContent>
                  </Card>

                  {/* Pair 2-3 */}
                  <Card className="border-2 border-purple-200 dark:border-purple-800">
                    <CardHeader>
                      <CardTitle className="text-sm">
                        {business3WayResult.profiles?.p2?.name} ⟷ {business3WayResult.profiles?.p3?.name}
                      </CardTitle>
                    </CardHeader>
                    <CardContent>
                      <div className="text-center mb-3">
                        <span className={`text-3xl font-bold ${getScoreColor(business3WayResult.pair23?.summary?.overall_score)}`}>
                          {business3WayResult.pair23?.summary?.overall_score}%
                        </span>
                        <p className="text-xs text-muted-foreground mt-1 capitalize">
                          {business3WayResult.pair23?.summary?.compatibility_level}
                        </p>
                      </div>
                      <div className="space-y-1 text-xs">
                        <p className="font-semibold text-green-600">Top Strength:</p>
                        <p className="text-muted-foreground">{business3WayResult.pair23?.summary?.strengths?.[0]}</p>
                      </div>
                    </CardContent>
                  </Card>
                </div>

                {/* Individual Person Analysis - Person 1 */}
                <Card className="border-2 border-blue-300 dark:border-blue-700">
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      <User className="w-5 h-5 text-blue-600" />
                      {business3WayResult.profiles?.p1?.name} - Individual Analysis
                    </CardTitle>
                    <CardDescription>
                      Complete compatibility analysis for Person 1 with both partners
                    </CardDescription>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    {/* P1 Compatibility Overview */}
                    <div className="grid grid-cols-2 gap-4">
                      <div className="p-4 rounded-lg border bg-blue-50 dark:bg-blue-900/20">
                        <p className="text-xs text-muted-foreground mb-1">With {business3WayResult.profiles?.p2?.name}</p>
                        <p className={`text-2xl font-bold ${getScoreColor(business3WayResult.pair12?.summary?.overall_score)}`}>
                          {business3WayResult.pair12?.summary?.overall_score}%
                        </p>
                        <p className="text-xs capitalize mt-1">{business3WayResult.pair12?.summary?.compatibility_level}</p>
                      </div>
                      <div className="p-4 rounded-lg border bg-blue-50 dark:bg-blue-900/20">
                        <p className="text-xs text-muted-foreground mb-1">With {business3WayResult.profiles?.p3?.name}</p>
                        <p className={`text-2xl font-bold ${getScoreColor(business3WayResult.pair13?.summary?.overall_score)}`}>
                          {business3WayResult.pair13?.summary?.overall_score}%
                        </p>
                        <p className="text-xs capitalize mt-1">{business3WayResult.pair13?.summary?.compatibility_level}</p>
                      </div>
                    </div>

                    {/* P1 Strengths */}
                    <div>
                      <h4 className="font-semibold mb-2 flex items-center gap-2 text-green-700 dark:text-green-400">
                        <CheckCircle className="w-4 h-4" />
                        Key Strengths in Team
                      </h4>
                      <ul className="space-y-2 text-sm">
                        {[
                          ...new Set([
                            ...(business3WayResult.pair12?.summary?.strengths || []),
                            ...(business3WayResult.pair13?.summary?.strengths || []),
                          ]),
                        ]
                          .slice(0, 4)
                          .map((strength: any, idx: number) => (
                            <li key={idx} className="flex items-start gap-2 p-2 rounded bg-green-50 dark:bg-green-900/20">
                              <ArrowRight className="w-4 h-4 mt-0.5 text-green-600 flex-shrink-0" />
                              <span>{strength}</span>
                            </li>
                          ))}
                      </ul>
                    </div>

                    {/* P1 Challenges */}
                    <div>
                      <h4 className="font-semibold mb-2 flex items-center gap-2 text-orange-700 dark:text-orange-400">
                        <AlertCircle className="w-4 h-4" />
                        Areas to Navigate
                      </h4>
                      <ul className="space-y-2 text-sm">
                        {[
                          ...new Set([
                            ...(business3WayResult.pair12?.summary?.challenges || []),
                            ...(business3WayResult.pair13?.summary?.challenges || []),
                          ]),
                        ]
                          .slice(0, 4)
                          .map((challenge: any, idx: number) => (
                            <li key={idx} className="flex items-start gap-2 p-2 rounded bg-orange-50 dark:bg-orange-900/20">
                              <ArrowRight className="w-4 h-4 mt-0.5 text-orange-600 flex-shrink-0" />
                              <span>{challenge}</span>
                            </li>
                          ))}
                      </ul>
                    </div>

                    {/* P1 Compatibility Factors */}
                    {business3WayResult.pair12?.compatibility_factors && (
                      <div>
                        <h4 className="font-semibold mb-2">Compatibility Factors Breakdown</h4>
                        <div className="grid grid-cols-2 gap-3 text-xs">
                          {Object.entries(business3WayResult.pair12.compatibility_factors).map(([factor, data]: [string, any]) => (
                            <div key={factor} className="p-3 rounded-lg border bg-card">
                              <p className="font-medium capitalize mb-1">{factor.replace('_', ' ')}</p>
                              <div className="flex items-center gap-2">
                                <div className={`text-lg font-bold ${getScoreColor(data.score)}`}>
                                  {data.score}%
                                </div>
                                <span className="text-muted-foreground">{data.interpretation}</span>
                              </div>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}
                  </CardContent>
                </Card>

                {/* Individual Person Analysis - Person 2 */}
                <Card className="border-2 border-green-300 dark:border-green-700">
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      <User className="w-5 h-5 text-green-600" />
                      {business3WayResult.profiles?.p2?.name} - Individual Analysis
                    </CardTitle>
                    <CardDescription>
                      Complete compatibility analysis for Person 2 with both partners
                    </CardDescription>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    {/* P2 Compatibility Overview */}
                    <div className="grid grid-cols-2 gap-4">
                      <div className="p-4 rounded-lg border bg-green-50 dark:bg-green-900/20">
                        <p className="text-xs text-muted-foreground mb-1">With {business3WayResult.profiles?.p1?.name}</p>
                        <p className={`text-2xl font-bold ${getScoreColor(business3WayResult.pair12?.summary?.overall_score)}`}>
                          {business3WayResult.pair12?.summary?.overall_score}%
                        </p>
                        <p className="text-xs capitalize mt-1">{business3WayResult.pair12?.summary?.compatibility_level}</p>
                      </div>
                      <div className="p-4 rounded-lg border bg-green-50 dark:bg-green-900/20">
                        <p className="text-xs text-muted-foreground mb-1">With {business3WayResult.profiles?.p3?.name}</p>
                        <p className={`text-2xl font-bold ${getScoreColor(business3WayResult.pair23?.summary?.overall_score)}`}>
                          {business3WayResult.pair23?.summary?.overall_score}%
                        </p>
                        <p className="text-xs capitalize mt-1">{business3WayResult.pair23?.summary?.compatibility_level}</p>
                      </div>
                    </div>

                    {/* P2 Strengths */}
                    <div>
                      <h4 className="font-semibold mb-2 flex items-center gap-2 text-green-700 dark:text-green-400">
                        <CheckCircle className="w-4 h-4" />
                        Key Strengths in Team
                      </h4>
                      <ul className="space-y-2 text-sm">
                        {[
                          ...new Set([
                            ...(business3WayResult.pair12?.summary?.strengths || []),
                            ...(business3WayResult.pair23?.summary?.strengths || []),
                          ]),
                        ]
                          .slice(0, 4)
                          .map((strength: any, idx: number) => (
                            <li key={idx} className="flex items-start gap-2 p-2 rounded bg-green-50 dark:bg-green-900/20">
                              <ArrowRight className="w-4 h-4 mt-0.5 text-green-600 flex-shrink-0" />
                              <span>{strength}</span>
                            </li>
                          ))}
                      </ul>
                    </div>

                    {/* P2 Challenges */}
                    <div>
                      <h4 className="font-semibold mb-2 flex items-center gap-2 text-orange-700 dark:text-orange-400">
                        <AlertCircle className="w-4 h-4" />
                        Areas to Navigate
                      </h4>
                      <ul className="space-y-2 text-sm">
                        {[
                          ...new Set([
                            ...(business3WayResult.pair12?.summary?.challenges || []),
                            ...(business3WayResult.pair23?.summary?.challenges || []),
                          ]),
                        ]
                          .slice(0, 4)
                          .map((challenge: any, idx: number) => (
                            <li key={idx} className="flex items-start gap-2 p-2 rounded bg-orange-50 dark:bg-orange-900/20">
                              <ArrowRight className="w-4 h-4 mt-0.5 text-orange-600 flex-shrink-0" />
                              <span>{challenge}</span>
                            </li>
                          ))}
                      </ul>
                    </div>

                    {/* P2 Compatibility Factors */}
                    {business3WayResult.pair12?.compatibility_factors && (
                      <div>
                        <h4 className="font-semibold mb-2">Compatibility Factors Breakdown</h4>
                        <div className="grid grid-cols-2 gap-3 text-xs">
                          {Object.entries(business3WayResult.pair12.compatibility_factors).map(([factor, data]: [string, any]) => (
                            <div key={factor} className="p-3 rounded-lg border bg-card">
                              <p className="font-medium capitalize mb-1">{factor.replace('_', ' ')}</p>
                              <div className="flex items-center gap-2">
                                <div className={`text-lg font-bold ${getScoreColor(data.score)}`}>
                                  {data.score}%
                                </div>
                                <span className="text-muted-foreground">{data.interpretation}</span>
                              </div>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}
                  </CardContent>
                </Card>

                {/* Individual Person Analysis - Person 3 */}
                <Card className="border-2 border-purple-300 dark:border-purple-700">
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      <User className="w-5 h-5 text-purple-600" />
                      {business3WayResult.profiles?.p3?.name} - Individual Analysis
                    </CardTitle>
                    <CardDescription>
                      Complete compatibility analysis for Person 3 with both partners
                    </CardDescription>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    {/* P3 Compatibility Overview */}
                    <div className="grid grid-cols-2 gap-4">
                      <div className="p-4 rounded-lg border bg-purple-50 dark:bg-purple-900/20">
                        <p className="text-xs text-muted-foreground mb-1">With {business3WayResult.profiles?.p1?.name}</p>
                        <p className={`text-2xl font-bold ${getScoreColor(business3WayResult.pair13?.summary?.overall_score)}`}>
                          {business3WayResult.pair13?.summary?.overall_score}%
                        </p>
                        <p className="text-xs capitalize mt-1">{business3WayResult.pair13?.summary?.compatibility_level}</p>
                      </div>
                      <div className="p-4 rounded-lg border bg-purple-50 dark:bg-purple-900/20">
                        <p className="text-xs text-muted-foreground mb-1">With {business3WayResult.profiles?.p2?.name}</p>
                        <p className={`text-2xl font-bold ${getScoreColor(business3WayResult.pair23?.summary?.overall_score)}`}>
                          {business3WayResult.pair23?.summary?.overall_score}%
                        </p>
                        <p className="text-xs capitalize mt-1">{business3WayResult.pair23?.summary?.compatibility_level}</p>
                      </div>
                    </div>

                    {/* P3 Strengths */}
                    <div>
                      <h4 className="font-semibold mb-2 flex items-center gap-2 text-green-700 dark:text-green-400">
                        <CheckCircle className="w-4 h-4" />
                        Key Strengths in Team
                      </h4>
                      <ul className="space-y-2 text-sm">
                        {[
                          ...new Set([
                            ...(business3WayResult.pair13?.summary?.strengths || []),
                            ...(business3WayResult.pair23?.summary?.strengths || []),
                          ]),
                        ]
                          .slice(0, 4)
                          .map((strength: any, idx: number) => (
                            <li key={idx} className="flex items-start gap-2 p-2 rounded bg-green-50 dark:bg-green-900/20">
                              <ArrowRight className="w-4 h-4 mt-0.5 text-green-600 flex-shrink-0" />
                              <span>{strength}</span>
                            </li>
                          ))}
                      </ul>
                    </div>

                    {/* P3 Challenges */}
                    <div>
                      <h4 className="font-semibold mb-2 flex items-center gap-2 text-orange-700 dark:text-orange-400">
                        <AlertCircle className="w-4 h-4" />
                        Areas to Navigate
                      </h4>
                      <ul className="space-y-2 text-sm">
                        {[
                          ...new Set([
                            ...(business3WayResult.pair13?.summary?.challenges || []),
                            ...(business3WayResult.pair23?.summary?.challenges || []),
                          ]),
                        ]
                          .slice(0, 4)
                          .map((challenge: any, idx: number) => (
                            <li key={idx} className="flex items-start gap-2 p-2 rounded bg-orange-50 dark:bg-orange-900/20">
                              <ArrowRight className="w-4 h-4 mt-0.5 text-orange-600 flex-shrink-0" />
                              <span>{challenge}</span>
                            </li>
                          ))}
                      </ul>
                    </div>

                    {/* P3 Compatibility Factors */}
                    {business3WayResult.pair13?.compatibility_factors && (
                      <div>
                        <h4 className="font-semibold mb-2">Compatibility Factors Breakdown</h4>
                        <div className="grid grid-cols-2 gap-3 text-xs">
                          {Object.entries(business3WayResult.pair13.compatibility_factors).map(([factor, data]: [string, any]) => (
                            <div key={factor} className="p-3 rounded-lg border bg-card">
                              <p className="font-medium capitalize mb-1">{factor.replace('_', ' ')}</p>
                              <div className="flex items-center gap-2">
                                <div className={`text-lg font-bold ${getScoreColor(data.score)}`}>
                                  {data.score}%
                                </div>
                                <span className="text-muted-foreground">{data.interpretation}</span>
                              </div>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}
                  </CardContent>
                </Card>

                {/* Team Dynamics Summary */}
                <Card className="bg-gradient-to-br from-yellow-50 to-orange-50 dark:from-yellow-900/20 dark:to-orange-900/20">
                  <CardHeader>
                    <CardTitle>Team Dynamics Summary</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-4">
                      <div>
                        <h4 className="font-semibold mb-2 flex items-center gap-2">
                          <CheckCircle className="w-4 h-4 text-green-600" />
                          Overall Team Strengths
                        </h4>
                        <ul className="space-y-1 text-sm">
                          {[
                            ...new Set([
                              ...(business3WayResult.pair12?.summary?.strengths || []),
                              ...(business3WayResult.pair13?.summary?.strengths || []),
                              ...(business3WayResult.pair23?.summary?.strengths || []),
                            ]),
                          ]
                            .slice(0, 5)
                            .map((strength: any, idx: number) => (
                              <li key={idx} className="flex items-start gap-2">
                                <ArrowRight className="w-4 h-4 mt-0.5 text-green-600 flex-shrink-0" />
                                <span>{strength}</span>
                              </li>
                            ))}
                        </ul>
                      </div>

                      <div>
                        <h4 className="font-semibold mb-2 flex items-center gap-2">
                          <AlertCircle className="w-4 h-4 text-orange-600" />
                          Team Challenges
                        </h4>
                        <ul className="space-y-1 text-sm">
                          {[
                            ...new Set([
                              ...(business3WayResult.pair12?.summary?.challenges || []),
                              ...(business3WayResult.pair13?.summary?.challenges || []),
                              ...(business3WayResult.pair23?.summary?.challenges || []),
                            ]),
                          ]
                            .slice(0, 5)
                            .map((challenge: any, idx: number) => (
                              <li key={idx} className="flex items-start gap-2">
                                <ArrowRight className="w-4 h-4 mt-0.5 text-orange-600 flex-shrink-0" />
                                <span>{challenge}</span>
                              </li>
                            ))}
                        </ul>
                      </div>

                      <div className="pt-4 border-t">
                        <h4 className="font-semibold mb-2">Average Team Compatibility</h4>
                        <div className="flex items-center gap-4">
                          <div className={`text-4xl font-bold ${getScoreColor(
                            (
                              (business3WayResult.pair12?.summary?.overall_score +
                                business3WayResult.pair13?.summary?.overall_score +
                                business3WayResult.pair23?.summary?.overall_score) /
                              3
                            )
                          )}`}>
                            {(
                              (business3WayResult.pair12?.summary?.overall_score +
                                business3WayResult.pair13?.summary?.overall_score +
                                business3WayResult.pair23?.summary?.overall_score) /
                              3
                            ).toFixed(1)}
                            %
                          </div>
                          <div className="text-sm text-muted-foreground">
                            <p>This indicates the overall team synergy</p>
                            <p>across all partnership combinations</p>
                          </div>
                        </div>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              </div>
            )}
          </TabsContent>
        )}
      </Tabs>
    </div>
  )
}
