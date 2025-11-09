"use client"

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Loader2, AlertCircle, Star, Target, Home, Sparkles } from 'lucide-react'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { apiClient } from '@/lib/api'

interface Profile {
  id: string
  name: string
  date_of_birth: string
  birth_time: string
  birth_city: string
}

interface CharaKaraka {
  planet: string
  karaka: string
  longitude: number
  significance: string
  strength: string
}

interface Karakamsha {
  sign: string
  lord: string
  planets_in_karakamsha: string[]
  interpretation: string
  spiritual_path: string
}

interface ArudhaPada {
  pada: string
  sign: string
  house: number
  significance: string
  interpretation: string
}

export default function JaiminiPage() {
  const router = useRouter()

  const [profiles, setProfiles] = useState<Profile[]>([])
  const [selectedProfile, setSelectedProfile] = useState<string>('')
  const [loading, setLoading] = useState(true)
  const [analyzing, setAnalyzing] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const [charaKarakas, setCharaKarakas] = useState<CharaKaraka[]>([])
  const [karakamsha, setKarakamsha] = useState<Karakamsha | null>(null)
  const [arudhaPadas, setArudhaPadas] = useState<ArudhaPada[]>([])
  const [activeTab, setActiveTab] = useState('chara-karakas')

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

  const analyzeJaimini = async () => {
    if (!selectedProfile) {
      setError('Please select a profile')
      return
    }

    try {
      setAnalyzing(true)
      setError(null)

      // Fetch all Jaimini data
      const [karakasRes, karakamshaRes, padasRes] = await Promise.all([
        apiClient.getCharaKarakas(selectedProfile),
        apiClient.getKarakamsha(selectedProfile),
        apiClient.getArudhaPadas(selectedProfile)
      ])

      // Handle response data - check if it's an array or has nested data property
      const karakasData = Array.isArray(karakasRes.data)
        ? karakasRes.data
        : Array.isArray(karakasRes.data?.chara_karakas)
          ? karakasRes.data.chara_karakas
          : []

      const karakamshaData = karakamshaRes.data?.karakamsha
        ? karakamshaRes.data.karakamsha
        : (typeof karakamshaRes.data === 'object' && karakamshaRes.data !== null && !Array.isArray(karakamshaRes.data) && 'sign' in karakamshaRes.data)
          ? karakamshaRes.data
          : null

      const padasData = Array.isArray(padasRes.data)
        ? padasRes.data
        : Array.isArray(padasRes.data?.arudha_padas)
          ? padasRes.data.arudha_padas
          : []

      setCharaKarakas(karakasData)
      setKarakamsha(karakamshaData)
      setArudhaPadas(padasData)
    } catch (err: any) {
      console.error('Error analyzing Jaimini:', err)
      setError(err.message || 'Failed to analyze Jaimini system')
      if (err.status === 401) {
        router.push('/auth/login')
      }
    } finally {
      setAnalyzing(false)
    }
  }

  const getKarakaColor = (karaka: string) => {
    const colors: Record<string, string> = {
      'AK': 'bg-purple-500',
      'AmK': 'bg-blue-500',
      'BK': 'bg-green-500',
      'MK': 'bg-yellow-500',
      'PK': 'bg-orange-500',
      'GK': 'bg-pink-500',
      'DK': 'bg-red-500'
    }
    return colors[karaka] || 'bg-gray-500'
  }

  const getStrengthBadge = (strength: string) => {
    const variants: Record<string, string> = {
      'Strong': 'default',
      'Moderate': 'secondary',
      'Weak': 'outline'
    }
    return variants[strength] || 'secondary'
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
              You need to create a profile to perform Jaimini analysis.
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
        <h1 className="text-3xl font-bold tracking-tight">Jaimini Astrology</h1>
        <p className="text-muted-foreground mt-2">
          Advanced Vedic system focusing on Chara Karakas, Karakamsha, and Arudha Padas
        </p>
      </div>

      {/* Profile Selection */}
      <Card>
        <CardHeader>
          <div className="flex items-center gap-2">
            <Target className="h-5 w-5 text-primary" />
            <CardTitle>Select Profile</CardTitle>
          </div>
          <CardDescription>Choose a profile to analyze using Jaimini system</CardDescription>
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
            onClick={analyzeJaimini}
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
                <Sparkles className="mr-2 h-4 w-4" />
                Analyze with Jaimini System
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
      {(charaKarakas.length > 0 || karakamsha || arudhaPadas.length > 0) && (
        <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-6">
          <TabsList className="grid w-full grid-cols-3">
            <TabsTrigger value="chara-karakas">Chara Karakas</TabsTrigger>
            <TabsTrigger value="karakamsha">Karakamsha</TabsTrigger>
            <TabsTrigger value="arudha-padas">Arudha Padas</TabsTrigger>
          </TabsList>

          {/* Chara Karakas Tab */}
          <TabsContent value="chara-karakas" className="space-y-4">
            <Card>
              <CardHeader>
                <div className="flex items-center gap-2">
                  <Star className="h-5 w-5 text-primary" />
                  <CardTitle>Chara Karakas (Temporal Significators)</CardTitle>
                </div>
                <CardDescription>
                  7 planets ranked by longitude showing life significators
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  {charaKarakas.map((karaka, index) => (
                    <div key={index} className="p-4 border rounded-lg bg-gradient-to-r from-background to-muted/20">
                      <div className="flex items-start justify-between">
                        <div className="flex-1">
                          <div className="flex items-center gap-3 mb-2">
                            <Badge className={`${getKarakaColor(karaka.karaka)} text-white`}>
                              {karaka.karaka}
                            </Badge>
                            <span className="text-lg font-bold">{karaka.planet}</span>
                            <Badge variant={getStrengthBadge(karaka.strength)}>
                              {karaka.strength}
                            </Badge>
                          </div>
                          <div className="text-sm font-medium text-muted-foreground mb-1">
                            {karaka.significance}
                          </div>
                          <div className="text-xs text-muted-foreground">
                            Longitude: {karaka.longitude.toFixed(2)}°
                          </div>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>

                {/* Info box */}
                <div className="mt-6 p-4 bg-muted/50 rounded-lg">
                  <h4 className="font-semibold mb-2">Understanding Chara Karakas:</h4>
                  <ul className="text-sm space-y-1 text-muted-foreground">
                    <li><strong>AK (Atmakaraka):</strong> Soul indicator, highest degree planet</li>
                    <li><strong>AmK (Amatyakaraka):</strong> Career and minister</li>
                    <li><strong>BK (Bhratrikaraka):</strong> Siblings and courage</li>
                    <li><strong>MK (Matrikaraka):</strong> Mother and emotions</li>
                    <li><strong>PK (Putrakaraka):</strong> Children and creativity</li>
                    <li><strong>GK (Gnatikaraka):</strong> Obstacles and enemies</li>
                    <li><strong>DK (Darakaraka):</strong> Spouse and partnerships</li>
                  </ul>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Karakamsha Tab */}
          <TabsContent value="karakamsha" className="space-y-4">
            {karakamsha && (
              <Card>
                <CardHeader>
                  <div className="flex items-center gap-2">
                    <Home className="h-5 w-5 text-primary" />
                    <CardTitle>Karakamsha Analysis</CardTitle>
                  </div>
                  <CardDescription>
                    D9 position of Atmakaraka - shows soul's desires and spiritual path
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div className="p-4 border rounded-lg bg-gradient-to-br from-purple-500/10 to-blue-500/10">
                      <div className="text-sm text-muted-foreground mb-1">Karakamsha Sign</div>
                      <div className="text-2xl font-bold">{karakamsha.sign}</div>
                      <div className="text-sm mt-2">
                        Lord: <span className="font-semibold">{karakamsha.lord}</span>
                      </div>
                    </div>

                    <div className="p-4 border rounded-lg">
                      <div className="text-sm text-muted-foreground mb-2">Planets in Karakamsha</div>
                      <div className="flex flex-wrap gap-2">
                        {karakamsha.planets_in_karakamsha.length > 0 ? (
                          karakamsha.planets_in_karakamsha.map((planet, idx) => (
                            <Badge key={idx} variant="secondary">{planet}</Badge>
                          ))
                        ) : (
                          <span className="text-sm text-muted-foreground">None</span>
                        )}
                      </div>
                    </div>
                  </div>

                  <div className="p-4 border rounded-lg bg-gradient-to-r from-background to-primary/5">
                    <h4 className="font-semibold mb-2">Interpretation:</h4>
                    <p className="text-sm text-muted-foreground mb-3">
                      {karakamsha.interpretation}
                    </p>
                    <div className="p-3 bg-muted/50 rounded">
                      <h5 className="text-sm font-semibold mb-1">Spiritual Path:</h5>
                      <p className="text-sm text-muted-foreground">
                        {karakamsha.spiritual_path}
                      </p>
                    </div>
                  </div>

                  <div className="p-4 bg-muted/50 rounded-lg">
                    <h4 className="font-semibold mb-2">About Karakamsha:</h4>
                    <p className="text-sm text-muted-foreground">
                      Karakamsha is the Navamsa (D9) position of the Atmakaraka planet. It reveals the soul's deepest desires,
                      spiritual inclinations, and the path of self-realization. Planets placed in or aspecting Karakamsha significantly
                      influence one's spiritual journey and life purpose.
                    </p>
                  </div>
                </CardContent>
              </Card>
            )}
          </TabsContent>

          {/* Arudha Padas Tab */}
          <TabsContent value="arudha-padas" className="space-y-4">
            <Card>
              <CardHeader>
                <div className="flex items-center gap-2">
                  <Sparkles className="h-5 w-5 text-primary" />
                  <CardTitle>Arudha Padas (Perception Points)</CardTitle>
                </div>
                <CardDescription>
                  How different life areas are perceived by others
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {arudhaPadas.map((pada, index) => (
                    <div key={index} className="p-4 border rounded-lg hover:bg-muted/30 transition-colors">
                      <div className="flex items-center gap-2 mb-2">
                        <Badge variant="outline" className="font-mono">{pada.pada}</Badge>
                        <span className="font-bold">{pada.sign}</span>
                        <span className="text-sm text-muted-foreground">(House {pada.house})</span>
                      </div>
                      <div className="text-sm font-medium text-primary mb-1">
                        {pada.significance}
                      </div>
                      <div className="text-sm text-muted-foreground">
                        {pada.interpretation}
                      </div>
                    </div>
                  ))}
                </div>

                <div className="mt-6 p-4 bg-muted/50 rounded-lg">
                  <h4 className="font-semibold mb-2">Understanding Arudha Padas:</h4>
                  <p className="text-sm text-muted-foreground mb-2">
                    Arudha Padas show how different aspects of life are perceived by the external world,
                    as opposed to the actual reality shown by the houses themselves.
                  </p>
                  <ul className="text-sm space-y-1 text-muted-foreground">
                    <li><strong>AL (Arudha Lagna):</strong> Overall image and personality perception</li>
                    <li><strong>UL (Upapada Lagna):</strong> Marriage and relationship perception</li>
                    <li><strong>A2-A12:</strong> Perceptions of wealth, siblings, mother, children, obstacles, spouse, career, gains, etc.</li>
                  </ul>
                </div>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      )}

      {/* Educational Info */}
      <Card className="bg-gradient-to-r from-purple-500/10 to-blue-500/10 border-primary/20">
        <CardHeader>
          <CardTitle>About Jaimini Astrology</CardTitle>
        </CardHeader>
        <CardContent className="space-y-2 text-sm">
          <p>
            <strong>Jaimini</strong> is an ancient Vedic astrology system revealed by Sage Jaimini. Unlike Parashara,
            it uses sign-based aspects (Rashi Drishti) and focuses on Chara Karakas (temporal significators).
          </p>
          <p>
            <strong>Key Features:</strong> Chara Dasha (sign-based periods), Arudha Padas (perception points),
            Karakamsha (soul's navamsa position), and unique yogas for prediction.
          </p>
          <p>
            <strong>Application:</strong> Excellent for timing events, understanding perception vs reality,
            and spiritual evolution through multiple lifetimes.
          </p>
        </CardContent>
      </Card>
    </div>
  )
}
