"use client"

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Loader2, AlertCircle, Grid3x3, BarChart3, TrendingUp } from 'lucide-react'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { apiClient } from '@/lib/api'

interface Profile {
  id: string
  name: string
  date_of_birth: string
  birth_time: string
  birth_city: string
}

interface BhinnaAshtakavarga {
  planet: string
  total_points: number
  sign_points: Record<string, number>
  strength_analysis: string
}

interface SarvaAshtakavarga {
  sign_points: Record<string, number>
  total_points: number
  strongest_signs: string[]
  weakest_signs: string[]
  interpretation: string
}

export default function AshtakavargaPage() {
  const router = useRouter()

  const [profiles, setProfiles] = useState<Profile[]>([])
  const [selectedProfile, setSelectedProfile] = useState<string>('')
  const [loading, setLoading] = useState(true)
  const [analyzing, setAnalyzing] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const [bhinnaData, setBhinnaData] = useState<BhinnaAshtakavarga[]>([])
  const [sarvaData, setSarvaData] = useState<SarvaAshtakavarga | null>(null)
  const [activeTab, setActiveTab] = useState('bhinna')

  const signs = ['Aries', 'Taurus', 'Gemini', 'Cancer', 'Leo', 'Virgo', 'Libra', 'Scorpio', 'Sagittarius', 'Capricorn', 'Aquarius', 'Pisces']

  useEffect(() => {
    fetchProfiles()
  }, [])

  const fetchProfiles = async () => {
    try {
      setLoading(true)
      const response = await apiClient.getProfiles()
      setProfiles(response.data || [])
    } catch (err: any) {
      console.error('Error fetching profiles:', err)
      setError(err.message || 'Failed to load profiles')
      if (err.status === 401) {
        router.push('/auth/login')
      }
    } finally {
      setLoading(false)
    }
  }

  const analyzeAshtakavarga = async () => {
    if (!selectedProfile) {
      setError('Please select a profile')
      return
    }

    try {
      setAnalyzing(true)
      setError(null)

      const [bhinnaRes, sarvaRes] = await Promise.all([
        apiClient.getBhinnaAshtakavarga(selectedProfile),
        apiClient.getSarvaAshtakavarga(selectedProfile)
      ])

      // Handle response data - check if it's an array or has nested data property
      const bhinnaResponseData = Array.isArray(bhinnaRes.data)
        ? bhinnaRes.data
        : Array.isArray(bhinnaRes.data?.bhinna_ashtakavarga)
          ? bhinnaRes.data.bhinna_ashtakavarga
          : bhinnaRes.data?.bhinna_ashtakavarga
            ? [bhinnaRes.data.bhinna_ashtakavarga]
            : []

      const sarvaResponseData = sarvaRes.data?.sarva_ashtakavarga
        ? sarvaRes.data.sarva_ashtakavarga
        : (typeof sarvaRes.data === 'object' && sarvaRes.data !== null && !Array.isArray(sarvaRes.data) && 'sign_points' in sarvaRes.data)
          ? sarvaRes.data
          : null

      setBhinnaData(bhinnaResponseData)
      setSarvaData(sarvaResponseData)
    } catch (err: any) {
      console.error('Error analyzing Ashtakavarga:', err)
      setError(err.message || 'Failed to analyze Ashtakavarga')
      if (err.status === 401) {
        router.push('/auth/login')
      }
    } finally {
      setAnalyzing(false)
    }
  }

  const getPointsColor = (points: number, maxPoints: number = 8) => {
    const percentage = (points / maxPoints) * 100
    if (percentage >= 75) return 'text-green-600 bg-green-50 border-green-200'
    if (percentage >= 50) return 'text-blue-600 bg-blue-50 border-blue-200'
    if (percentage >= 25) return 'text-yellow-600 bg-yellow-50 border-yellow-200'
    return 'text-red-600 bg-red-50 border-red-200'
  }

  const getStrengthBadge = (points: number, maxPoints: number = 8) => {
    const percentage = (points / maxPoints) * 100
    if (percentage >= 75) return { variant: 'default' as const, label: 'Strong' }
    if (percentage >= 50) return { variant: 'secondary' as const, label: 'Moderate' }
    if (percentage >= 25) return { variant: 'outline' as const, label: 'Weak' }
    return { variant: 'destructive' as const, label: 'Very Weak' }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <Loader2 className="h-8 w-8 animate-spin text-primary" />
      </div>
    )
  }

  if (profiles.length === 0) {
    return (
      <div className="container mx-auto p-6">
        <Card>
          <CardHeader>
            <CardTitle>No Profiles Found</CardTitle>
            <CardDescription>
              You need to create a profile to perform Ashtakavarga analysis.
            </CardDescription>
          </CardHeader>
          <CardContent>
            <Button onClick={() => router.push('/dashboard/profiles')}>
              Create Profile
            </Button>
          </CardContent>
        </Card>
      </div>
    )
  }

  return (
    <div className="container mx-auto p-6 space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Ashtakavarga System</h1>
        <p className="text-muted-foreground mt-2">
          Predictive point system measuring planetary strength through 337 bindus
        </p>
      </div>

      {/* Profile Selection */}
      <Card>
        <CardHeader>
          <div className="flex items-center gap-2">
            <Grid3x3 className="h-5 w-5 text-primary" />
            <CardTitle>Select Profile</CardTitle>
          </div>
          <CardDescription>Choose a profile to analyze using Ashtakavarga system</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <Select value={selectedProfile} onValueChange={setSelectedProfile}>
            <SelectTrigger>
              <SelectValue placeholder="Select a profile">
                {selectedProfile && profiles.find(p => p.id === selectedProfile)?.name}
              </SelectValue>
            </SelectTrigger>
            <SelectContent>
              {profiles.map((profile) => (
                <SelectItem key={profile.id} value={profile.id}>
                  {profile.name} ({profile.date_of_birth})
                </SelectItem>
              ))}
            </SelectContent>
          </Select>

          <Button
            onClick={analyzeAshtakavarga}
            disabled={!selectedProfile || analyzing}
            className="w-full"
          >
            {analyzing ? (
              <>
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                Analyzing...
              </>
            ) : (
              <>
                <BarChart3 className="mr-2 h-4 w-4" />
                Analyze Ashtakavarga
              </>
            )}
          </Button>

          {error && (
            <Alert variant="destructive">
              <AlertCircle className="h-4 w-4" />
              <AlertDescription>{error}</AlertDescription>
            </Alert>
          )}
        </CardContent>
      </Card>

      {/* Analysis Results */}
      {(bhinnaData.length > 0 || sarvaData) && (
        <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-6">
          <TabsList className="grid w-full grid-cols-2">
            <TabsTrigger value="bhinna">Bhinna Ashtakavarga</TabsTrigger>
            <TabsTrigger value="sarva">Sarva Ashtakavarga</TabsTrigger>
          </TabsList>

          {/* Bhinna Ashtakavarga Tab */}
          <TabsContent value="bhinna" className="space-y-4">
            <Card>
              <CardHeader>
                <div className="flex items-center gap-2">
                  <Grid3x3 className="h-5 w-5 text-primary" />
                  <CardTitle>Bhinna Ashtakavarga (Individual Planet Charts)</CardTitle>
                </div>
                <CardDescription>
                  Benefic points for each planet across all 12 signs
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-6">
                {bhinnaData.map((planetData, index) => (
                  <div key={index} className="border rounded-lg p-4 bg-gradient-to-r from-background to-muted/20">
                    <div className="flex items-center justify-between mb-4">
                      <div>
                        <h3 className="text-xl font-bold">{planetData.planet}</h3>
                        <p className="text-sm text-muted-foreground">
                          Total Points: {planetData.total_points}/337
                        </p>
                      </div>
                      <Badge {...getStrengthBadge(planetData.total_points, 337)}>
                        {getStrengthBadge(planetData.total_points, 337).label}
                      </Badge>
                    </div>

                    {/* Points Grid */}
                    <div className="grid grid-cols-3 md:grid-cols-4 lg:grid-cols-6 gap-2 mb-4">
                      {signs.map((sign) => {
                        const points = planetData.sign_points?.[sign] || 0
                        return (
                          <div
                            key={sign}
                            className={`p-3 border rounded text-center transition-all hover:scale-105 ${getPointsColor(points)}`}
                          >
                            <div className="text-xs font-medium mb-1">{sign}</div>
                            <div className="text-2xl font-bold">{points}</div>
                          </div>
                        )
                      })}
                    </div>

                    {planetData.strength_analysis && (
                      <div className="p-3 bg-muted/50 rounded">
                        <p className="text-sm">{planetData.strength_analysis}</p>
                      </div>
                    )}
                  </div>
                ))}

                <div className="p-4 bg-muted/50 rounded-lg">
                  <h4 className="font-semibold mb-2">Understanding Bhinna Ashtakavarga:</h4>
                  <p className="text-sm text-muted-foreground mb-2">
                    Bhinna means "individual" - this shows how many benefic points (bindus) each planet contributes
                    to each sign. Points are given based on house positions from 7 reference points (the planet itself,
                    Sun, Moon, Mars, Mercury, Jupiter, Venus, Saturn).
                  </p>
                  <ul className="text-sm space-y-1 text-muted-foreground">
                    <li><strong>0-2 points:</strong> Very weak - avoid important activities</li>
                    <li><strong>3-4 points:</strong> Moderate - average results</li>
                    <li><strong>5-6 points:</strong> Good - favorable outcomes</li>
                    <li><strong>7-8 points:</strong> Excellent - highly auspicious</li>
                  </ul>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Sarva Ashtakavarga Tab */}
          <TabsContent value="sarva" className="space-y-4">
            {sarvaData && (
              <Card>
                <CardHeader>
                  <div className="flex items-center gap-2">
                    <TrendingUp className="h-5 w-5 text-primary" />
                    <CardTitle>Sarva Ashtakavarga (Collective Chart)</CardTitle>
                  </div>
                  <CardDescription>
                    Combined benefic points from all planets (Total: {sarvaData.total_points || 0}/337)
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-6">
                  {/* Overall Summary */}
                  <div className="p-4 bg-gradient-to-r from-blue-500/10 to-purple-500/10 border border-blue-500/20 rounded-lg">
                    <div className="flex items-center justify-between mb-3">
                      <div>
                        <h3 className="text-2xl font-bold">Total Bindus</h3>
                        <p className="text-sm text-muted-foreground">Across all 12 signs</p>
                      </div>
                      <div className="text-4xl font-bold text-primary">
                        {sarvaData.total_points || 0}
                      </div>
                    </div>
                  </div>

                  {/* Sign Points Grid */}
                  <div>
                    <h4 className="font-semibold mb-3">Points per Sign:</h4>
                    <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-3">
                      {signs.map((sign) => {
                        const points = sarvaData.sign_points?.[sign] || 0
                        const isStrongest = sarvaData.strongest_signs?.includes(sign) || false
                        const isWeakest = sarvaData.weakest_signs?.includes(sign) || false
                        return (
                          <div
                            key={sign}
                            className={`p-4 border-2 rounded-lg text-center transition-all hover:scale-105 ${
                              isStrongest
                                ? 'border-green-500 bg-green-50'
                                : isWeakest
                                ? 'border-red-500 bg-red-50'
                                : getPointsColor(points, 50)
                            }`}
                          >
                            <div className="text-sm font-medium mb-2">{sign}</div>
                            <div className="text-3xl font-bold mb-1">{points}</div>
                            {isStrongest && (
                              <Badge className="bg-green-500 text-white text-xs">Strongest</Badge>
                            )}
                            {isWeakest && (
                              <Badge className="bg-red-500 text-white text-xs">Weakest</Badge>
                            )}
                          </div>
                        )
                      })}
                    </div>
                  </div>

                  {/* Strongest Signs */}
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div className="p-4 border border-green-500/50 rounded-lg bg-green-500/5">
                      <h4 className="font-semibold mb-2 flex items-center gap-2 text-green-700">
                        <TrendingUp className="h-4 w-4" />
                        Strongest Signs
                      </h4>
                      <div className="flex flex-wrap gap-2">
                        {sarvaData.strongest_signs?.map((sign, idx) => (
                          <Badge key={idx} className="bg-green-500 text-white">
                            {sign} ({sarvaData.sign_points?.[sign] || 0} pts)
                          </Badge>
                        ))}
                      </div>
                      <p className="text-sm text-muted-foreground mt-2">
                        Best periods for major activities and decision-making
                      </p>
                    </div>

                    <div className="p-4 border border-red-500/50 rounded-lg bg-red-500/5">
                      <h4 className="font-semibold mb-2 flex items-center gap-2 text-red-700">
                        <AlertCircle className="h-4 w-4" />
                        Weakest Signs
                      </h4>
                      <div className="flex flex-wrap gap-2">
                        {sarvaData.weakest_signs?.map((sign, idx) => (
                          <Badge key={idx} variant="destructive">
                            {sign} ({sarvaData.sign_points?.[sign] || 0} pts)
                          </Badge>
                        ))}
                      </div>
                      <p className="text-sm text-muted-foreground mt-2">
                        Exercise caution during these periods
                      </p>
                    </div>
                  </div>

                  {/* Interpretation */}
                  {sarvaData.interpretation && (
                    <div className="p-4 bg-muted/50 rounded-lg">
                      <h4 className="font-semibold mb-2">Overall Interpretation:</h4>
                      <p className="text-sm text-muted-foreground">{sarvaData.interpretation}</p>
                    </div>
                  )}

                  <div className="p-4 bg-gradient-to-r from-purple-500/10 to-blue-500/10 rounded-lg">
                    <h4 className="font-semibold mb-2">Understanding Sarva Ashtakavarga:</h4>
                    <p className="text-sm text-muted-foreground mb-2">
                      Sarva means "total" - this combines all Bhinna Ashtakavarga charts to show the overall
                      strength of each sign in your chart. Maximum possible is 337 points across all signs.
                    </p>
                    <ul className="text-sm space-y-1 text-muted-foreground">
                      <li><strong>Less than 25 points:</strong> Weak sign - challenges likely</li>
                      <li><strong>25-28 points:</strong> Average - mixed results</li>
                      <li><strong>29-32 points:</strong> Good - favorable outcomes</li>
                      <li><strong>33+ points:</strong> Excellent - highly auspicious</li>
                    </ul>
                    <p className="text-sm text-muted-foreground mt-3">
                      <strong>Transit Use:</strong> When planets transit through signs with high Sarva Ashtakavarga points,
                      they give better results. Use this for Muhurta (electional astrology) and timing major events.
                    </p>
                  </div>
                </CardContent>
              </Card>
            )}
          </TabsContent>
        </Tabs>
      )}

      {/* Educational Info */}
      <Card className="bg-gradient-to-r from-blue-500/10 to-purple-500/10 border-blue-500/20">
        <CardHeader>
          <CardTitle>About Ashtakavarga System</CardTitle>
        </CardHeader>
        <CardContent className="space-y-2 text-sm">
          <p>
            <strong>Ashtakavarga</strong> (अष्टकवर्ग) is a mathematical prediction system in Vedic astrology
            that assigns benefic points (bindus) to signs based on planetary positions.
          </p>
          <p>
            <strong>System:</strong> For each of the 7 planets (Sun through Saturn), points are assigned to signs
            based on 8 reference points (Ashta = 8, Varga = division). Total maximum = 337 points.
          </p>
          <p>
            <strong>Applications:</strong> Transit analysis (when to expect good/bad results), Dasha analysis
            (strength of planetary periods), Muhurta (choosing auspicious times), and longevity calculations.
          </p>
          <p>
            <strong>Accuracy:</strong> Considered one of the most reliable predictive techniques, especially for
            timing events and assessing planetary strength during transits.
          </p>
        </CardContent>
      </Card>
    </div>
  )
}
