"use client"

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Progress } from '@/components/ui/progress'
import { Loader2, AlertCircle, Heart, Users, CheckCircle, XCircle } from 'lucide-react'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { apiClient } from '@/lib/api'

interface Profile {
  id: string
  name: string
  date_of_birth: string
  birth_time: string
  birth_city: string
}

interface GunaFactor {
  name: string
  max_points: number
  obtained_points: number
  boy_value?: string
  girl_value?: string
  compatible: boolean
  description: string
}

interface CompatibilityData {
  boy_nakshatra: {
    name: string
    number: number
    pada: number
  }
  girl_nakshatra: {
    name: string
    number: number
    pada: number
  }
  guna_milan: {
    total_points: number
    max_points: number
    percentage: number
    factors: GunaFactor[]
    level: string
  }
  manglik_analysis: {
    boy_manglik: any
    girl_manglik: any
    compatible: boolean
    note?: string
  }
  overall_compatibility: {
    level: string
    recommendation: string
    summary: string
  }
}

export default function CompatibilityPage() {
  const router = useRouter()

  const [profiles, setProfiles] = useState<Profile[]>([])
  const [boyProfile, setBoyProfile] = useState<string>('')
  const [girlProfile, setGirlProfile] = useState<string>('')
  const [loading, setLoading] = useState(true)
  const [analyzing, setAnalyzing] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [compatibility, setCompatibility] = useState<CompatibilityData | null>(null)

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

      // If authentication fails, the apiClient will automatically redirect
      // But we can also handle it here if needed
      if (err.status === 401) {
        router.push('/auth/login')
      }
    } finally {
      setLoading(false)
    }
  }

  const analyzeCompatibility = async () => {
    if (!boyProfile || !girlProfile) {
      setError('Please select both profiles')
      return
    }

    if (boyProfile === girlProfile) {
      setError('Please select different profiles')
      return
    }

    try {
      setAnalyzing(true)
      setError(null)

      const response = await apiClient.analyzeCompatibility({
        boy_profile_id: boyProfile,
        girl_profile_id: girlProfile
      })

      setCompatibility(response.data.compatibility_analysis)
    } catch (err: any) {
      console.error('Error analyzing compatibility:', err)
      setError(err.message || 'Failed to analyze compatibility')

      // If authentication fails, the apiClient will automatically redirect
      if (err.status === 401) {
        router.push('/auth/login')
      }
    } finally {
      setAnalyzing(false)
    }
  }

  const getCompatibilityColor = (level: string) => {
    switch (level) {
      case 'excellent': return 'bg-green-500'
      case 'very_good': return 'bg-blue-500'
      case 'good': return 'bg-yellow-500'
      case 'average': return 'bg-orange-500'
      case 'poor': return 'bg-red-500'
      default: return 'bg-gray-500'
    }
  }

  const getCompatibilityLabel = (level: string) => {
    return level.split('_').map(w => w.charAt(0).toUpperCase() + w.slice(1)).join(' ')
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <Loader2 className="h-8 w-8 animate-spin text-primary" />
      </div>
    )
  }

  if (profiles.length < 2) {
    return (
      <div className="container mx-auto p-6">
        <Card>
          <CardHeader>
            <CardTitle>Need More Profiles</CardTitle>
            <CardDescription>
              You need at least 2 profiles to perform compatibility matching.
            </CardDescription>
          </CardHeader>
          <CardContent>
            <Button onClick={() => router.push('/dashboard/profiles')}>
              Create Profiles
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
        <h1 className="text-3xl font-bold tracking-tight">Compatibility Matching</h1>
        <p className="text-muted-foreground mt-2">
          Ashtakoot Guna Milan and Manglik Dosha analysis
        </p>
      </div>

      {/* Profile Selection */}
      <Card>
        <CardHeader>
          <div className="flex items-center gap-2">
            <Users className="h-5 w-5 text-primary" />
            <CardTitle>Select Profiles</CardTitle>
          </div>
          <CardDescription>Choose two profiles to analyze compatibility</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="space-y-2">
              <label className="text-sm font-medium">Boy's Profile</label>
              <Select value={boyProfile} onValueChange={setBoyProfile}>
                <SelectTrigger>
                  <SelectValue placeholder="Select boy's profile">
                    {boyProfile && profiles.find(p => p.id === boyProfile)?.name}
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
            </div>

            <div className="space-y-2">
              <label className="text-sm font-medium">Girl's Profile</label>
              <Select value={girlProfile} onValueChange={setGirlProfile}>
                <SelectTrigger>
                  <SelectValue placeholder="Select girl's profile">
                    {girlProfile && profiles.find(p => p.id === girlProfile)?.name}
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
            </div>
          </div>

          <Button
            onClick={analyzeCompatibility}
            disabled={!boyProfile || !girlProfile || analyzing}
            className="w-full"
          >
            {analyzing ? (
              <>
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                Analyzing...
              </>
            ) : (
              <>
                <Heart className="mr-2 h-4 w-4" />
                Analyze Compatibility
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

      {/* Compatibility Results */}
      {compatibility && (
        <div className="space-y-6">
          {/* Overall Compatibility */}
          <Card className="border-primary">
            <CardHeader>
              <div className="flex items-center gap-2">
                <Heart className="h-5 w-5 text-primary" />
                <CardTitle>Overall Compatibility</CardTitle>
              </div>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex items-center justify-between">
                <div className="space-y-1">
                  <div className="text-4xl font-bold text-primary">
                    {compatibility.guna_milan.total_points}/{compatibility.guna_milan.max_points}
                  </div>
                  <div className="text-sm text-muted-foreground">
                    {compatibility.guna_milan.percentage}% Match
                  </div>
                </div>
                <Badge className={`text-lg px-4 py-2 ${getCompatibilityColor(compatibility.overall_compatibility.level)}`}>
                  {getCompatibilityLabel(compatibility.overall_compatibility.level)}
                </Badge>
              </div>

              <Progress value={compatibility.guna_milan.percentage} className="h-3" />

              <Alert>
                <AlertDescription className="text-sm">
                  {compatibility.overall_compatibility.summary}
                </AlertDescription>
              </Alert>

              <div className="p-4 bg-muted rounded-lg">
                <p className="font-medium mb-2">Recommendation:</p>
                <p className="text-sm text-muted-foreground">
                  {compatibility.overall_compatibility.recommendation}
                </p>
              </div>
            </CardContent>
          </Card>

          {/* Nakshatra Information */}
          <Card>
            <CardHeader>
              <CardTitle>Birth Stars (Nakshatra)</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="p-4 border rounded-lg">
                  <div className="text-sm text-muted-foreground mb-1">Boy's Nakshatra</div>
                  <div className="text-xl font-bold">{compatibility.boy_nakshatra.name}</div>
                  <div className="text-sm mt-1">
                    Pada: {compatibility.boy_nakshatra.pada}
                  </div>
                </div>
                <div className="p-4 border rounded-lg">
                  <div className="text-sm text-muted-foreground mb-1">Girl's Nakshatra</div>
                  <div className="text-xl font-bold">{compatibility.girl_nakshatra.name}</div>
                  <div className="text-sm mt-1">
                    Pada: {compatibility.girl_nakshatra.pada}
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Guna Milan Factors */}
          <Card>
            <CardHeader>
              <CardTitle>Ashtakoot (Guna Milan) Analysis</CardTitle>
              <CardDescription>8-factor compatibility scoring system</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {compatibility.guna_milan.factors.map((factor, index) => (
                  <div key={index} className="flex items-center justify-between p-3 border rounded-lg">
                    <div className="flex-1">
                      <div className="flex items-center gap-2">
                        <div className="font-medium">{factor.name}</div>
                        {factor.compatible ? (
                          <CheckCircle className="h-4 w-4 text-green-500" />
                        ) : (
                          <XCircle className="h-4 w-4 text-red-500" />
                        )}
                      </div>
                      <div className="text-sm text-muted-foreground mt-1">
                        {factor.description}
                      </div>
                      {factor.boy_value && factor.girl_value && (
                        <div className="text-xs text-muted-foreground mt-1">
                          Boy: {factor.boy_value} | Girl: {factor.girl_value}
                        </div>
                      )}
                    </div>
                    <div className="text-right ml-4">
                      <div className="text-lg font-bold">
                        {factor.obtained_points}/{factor.max_points}
                      </div>
                      <Progress
                        value={(factor.obtained_points / factor.max_points) * 100}
                        className="w-20 h-2 mt-1"
                      />
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>

          {/* Manglik Dosha */}
          <Card>
            <CardHeader>
              <CardTitle>Manglik Dosha Analysis</CardTitle>
              <CardDescription>Mars placement and compatibility</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className={`p-4 border-2 rounded-lg ${compatibility.manglik_analysis.boy_manglik.is_manglik ? 'border-orange-500' : 'border-green-500'}`}>
                    <div className="flex items-center justify-between mb-2">
                      <div className="font-medium">Boy's Status</div>
                      <Badge variant={compatibility.manglik_analysis.boy_manglik.is_manglik ? 'destructive' : 'default'}>
                        {compatibility.manglik_analysis.boy_manglik.is_manglik ? 'Manglik' : 'Non-Manglik'}
                      </Badge>
                    </div>
                    <div className="text-sm text-muted-foreground">
                      {compatibility.manglik_analysis.boy_manglik.description}
                    </div>
                  </div>

                  <div className={`p-4 border-2 rounded-lg ${compatibility.manglik_analysis.girl_manglik.is_manglik ? 'border-orange-500' : 'border-green-500'}`}>
                    <div className="flex items-center justify-between mb-2">
                      <div className="font-medium">Girl's Status</div>
                      <Badge variant={compatibility.manglik_analysis.girl_manglik.is_manglik ? 'destructive' : 'default'}>
                        {compatibility.manglik_analysis.girl_manglik.is_manglik ? 'Manglik' : 'Non-Manglik'}
                      </Badge>
                    </div>
                    <div className="text-sm text-muted-foreground">
                      {compatibility.manglik_analysis.girl_manglik.description}
                    </div>
                  </div>
                </div>

                <Alert variant={compatibility.manglik_analysis.compatible ? 'default' : 'destructive'}>
                  <AlertDescription>
                    {compatibility.manglik_analysis.compatible ? (
                      <div className="flex items-center gap-2">
                        <CheckCircle className="h-4 w-4" />
                        Manglik compatibility is favorable
                      </div>
                    ) : (
                      <div className="flex items-center gap-2">
                        <XCircle className="h-4 w-4" />
                        Manglik incompatibility detected - remedies recommended
                      </div>
                    )}
                    {compatibility.manglik_analysis.note && (
                      <div className="mt-2 text-sm">{compatibility.manglik_analysis.note}</div>
                    )}
                  </AlertDescription>
                </Alert>
              </div>
            </CardContent>
          </Card>

          {/* Information Card */}
          <Card className="bg-muted/50">
            <CardHeader>
              <CardTitle className="text-lg">Understanding Compatibility Matching</CardTitle>
            </CardHeader>
            <CardContent className="space-y-2 text-sm">
              <p><strong>Guna Milan:</strong> Traditional 36-point compatibility system. 18+ points is considered acceptable, 24+ is good, 28+ is excellent.</p>
              <p><strong>Ashtakoot Factors:</strong> 8 factors including Varna (spiritual), Vashya (attraction), Tara (destiny), Yoni (intimacy), Graha Maitri (friendship), Gana (temperament), Bhakoot (prosperity), and Nadi (health).</p>
              <p><strong>Manglik Dosha:</strong> Occurs when Mars is in houses 1, 4, 7, 8, or 12. Can be cancelled if both partners are Manglik or through specific planetary positions.</p>
            </CardContent>
          </Card>
        </div>
      )}
    </div>
  )
}
