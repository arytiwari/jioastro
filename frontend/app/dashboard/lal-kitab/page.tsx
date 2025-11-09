"use client"

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Loader2, AlertCircle, AlertTriangle, Lightbulb, Eye, Book } from 'lucide-react'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { apiClient } from '@/lib/api'

interface Profile {
  id: string
  name: string
  date_of_birth: string
  birth_time: string
  birth_city: string
}

interface PlanetaryDebt {
  debt_type: string
  planet: string
  severity: string
  description: string
  remedies: string[]
  indicators: string[]
}

interface BlindPlanet {
  planet: string
  is_blind: boolean
  blinding_factor?: string
  house: number
  effects: string[]
  remedies: string[]
}

export default function LalKitabPage() {
  const router = useRouter()

  const [profiles, setProfiles] = useState<Profile[]>([])
  const [selectedProfile, setSelectedProfile] = useState<string>('')
  const [loading, setLoading] = useState(true)
  const [analyzing, setAnalyzing] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const [planetaryDebts, setPlanetaryDebts] = useState<PlanetaryDebt[]>([])
  const [blindPlanets, setBlindPlanets] = useState<BlindPlanet[]>([])
  const [activeTab, setActiveTab] = useState('debts')

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

  const analyzeLalKitab = async () => {
    if (!selectedProfile) {
      setError('Please select a profile')
      return
    }

    try {
      setAnalyzing(true)
      setError(null)

      const [debtsRes, blindRes] = await Promise.all([
        apiClient.getPlanetaryDebts(selectedProfile),
        apiClient.getBlindPlanets(selectedProfile)
      ])

      // Handle response data - check if it's an array or has nested data property
      const debtsData = Array.isArray(debtsRes.data)
        ? debtsRes.data
        : Array.isArray(debtsRes.data?.planetary_debts)
          ? debtsRes.data.planetary_debts
          : Array.isArray(debtsRes.data?.debts)
            ? debtsRes.data.debts
            : []

      const blindData = Array.isArray(blindRes.data)
        ? blindRes.data
        : Array.isArray(blindRes.data?.blind_planets)
          ? blindRes.data.blind_planets
          : []

      setPlanetaryDebts(debtsData)
      setBlindPlanets(blindData)
    } catch (err: any) {
      console.error('Error analyzing Lal Kitab:', err)
      setError(err.message || 'Failed to analyze Lal Kitab')
      if (err.status === 401) {
        router.push('/auth/login')
      }
    } finally {
      setAnalyzing(false)
    }
  }

  const getSeverityColor = (severity: string) => {
    const colors: Record<string, string> = {
      'High': 'bg-red-500',
      'Medium': 'bg-orange-500',
      'Low': 'bg-yellow-500'
    }
    return colors[severity] || 'bg-gray-500'
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
              You need to create a profile to perform Lal Kitab analysis.
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
        <h1 className="text-3xl font-bold tracking-tight">Lal Kitab Astrology</h1>
        <p className="text-muted-foreground mt-2">
          Ancient karmic astrology system with practical remedies (Totke)
        </p>
      </div>

      {/* Profile Selection */}
      <Card>
        <CardHeader>
          <div className="flex items-center gap-2">
            <Book className="h-5 w-5 text-primary" />
            <CardTitle>Select Profile</CardTitle>
          </div>
          <CardDescription>Choose a profile to analyze using Lal Kitab system</CardDescription>
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
            onClick={analyzeLalKitab}
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
                <AlertTriangle className="mr-2 h-4 w-4" />
                Analyze with Lal Kitab
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
      {(planetaryDebts.length > 0 || blindPlanets.length > 0) && (
        <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-6">
          <TabsList className="grid w-full grid-cols-2">
            <TabsTrigger value="debts">Planetary Debts (Rins)</TabsTrigger>
            <TabsTrigger value="blind">Blind Planets</TabsTrigger>
          </TabsList>

          {/* Planetary Debts Tab */}
          <TabsContent value="debts" className="space-y-4">
            <Card>
              <CardHeader>
                <div className="flex items-center gap-2">
                  <AlertTriangle className="h-5 w-5 text-orange-500" />
                  <CardTitle>Planetary Debts (Rins)</CardTitle>
                </div>
                <CardDescription>
                  Karmic debts from past lives affecting current life challenges
                </CardDescription>
              </CardHeader>
              <CardContent>
                {planetaryDebts.length > 0 ? (
                  <div className="space-y-4">
                    {planetaryDebts.map((debt, index) => (
                      <div key={index} className="border rounded-lg p-4 space-y-3">
                        <div className="flex items-start justify-between">
                          <div>
                            <div className="flex items-center gap-2 mb-1">
                              <h3 className="font-bold text-lg">{debt.debt_type}</h3>
                              <Badge className={`${getSeverityColor(debt.severity)} text-white`}>
                                {debt.severity} Severity
                              </Badge>
                            </div>
                            <div className="text-sm text-muted-foreground">
                              Planet: <span className="font-semibold">{debt.planet}</span>
                            </div>
                          </div>
                        </div>

                        <div className="p-3 bg-muted/50 rounded">
                          <p className="text-sm">{debt.description}</p>
                        </div>

                        {debt.indicators && debt.indicators.length > 0 && (
                          <div>
                            <h4 className="text-sm font-semibold mb-2 flex items-center gap-1">
                              <Eye className="h-4 w-4" /> Indicators:
                            </h4>
                            <ul className="space-y-1">
                              {debt.indicators.map((indicator, idx) => (
                                <li key={idx} className="text-sm text-muted-foreground flex items-start gap-2">
                                  <span className="text-orange-500 mt-1">•</span>
                                  <span>{indicator}</span>
                                </li>
                              ))}
                            </ul>
                          </div>
                        )}

                        {debt.remedies && debt.remedies.length > 0 && (
                          <div className="p-3 bg-gradient-to-r from-green-500/10 to-blue-500/10 rounded border border-green-500/20">
                            <h4 className="text-sm font-semibold mb-2 flex items-center gap-1">
                              <Lightbulb className="h-4 w-4 text-green-600" /> Remedies (Totke):
                            </h4>
                            <ul className="space-y-1">
                              {debt.remedies.map((remedy, idx) => (
                                <li key={idx} className="text-sm flex items-start gap-2">
                                  <span className="text-green-600 mt-1">✓</span>
                                  <span>{remedy}</span>
                                </li>
                              ))}
                            </ul>
                          </div>
                        )}
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="text-center py-8 text-muted-foreground">
                    <AlertCircle className="h-12 w-12 mx-auto mb-3 opacity-20" />
                    <p>No significant planetary debts detected</p>
                  </div>
                )}

                <div className="mt-6 p-4 bg-muted/50 rounded-lg">
                  <h4 className="font-semibold mb-2">Understanding Planetary Debts (Rins):</h4>
                  <p className="text-sm text-muted-foreground mb-2">
                    In Lal Kitab, Rins (debts) represent karmic obligations from past lives that manifest as challenges in this life.
                    These debts are indicated by afflicted planets in specific positions.
                  </p>
                  <ul className="text-sm space-y-1 text-muted-foreground">
                    <li><strong>Father's Debt (Pitr Rin):</strong> Sun afflictions</li>
                    <li><strong>Mother's Debt (Matri Rin):</strong> Moon afflictions</li>
                    <li><strong>Brother's Debt (Bhatri Rin):</strong> Mars afflictions</li>
                    <li><strong>Guru's Debt (Guru Rin):</strong> Jupiter afflictions</li>
                    <li><strong>Wife's Debt (Stri Rin):</strong> Venus afflictions</li>
                  </ul>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Blind Planets Tab */}
          <TabsContent value="blind" className="space-y-4">
            <Card>
              <CardHeader>
                <div className="flex items-center gap-2">
                  <Eye className="h-5 w-5 text-primary" />
                  <CardTitle>Blind Planets (Andhe Graha)</CardTitle>
                </div>
                <CardDescription>
                  Planets that lose their power to see and protect in certain positions
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {blindPlanets.map((planetData, index) => (
                    <div
                      key={index}
                      className={`border rounded-lg p-4 ${
                        planetData.is_blind ? 'border-orange-500/50 bg-orange-500/5' : 'border-green-500/50 bg-green-500/5'
                      }`}
                    >
                      <div className="flex items-start justify-between mb-3">
                        <div>
                          <div className="flex items-center gap-2">
                            <h3 className="font-bold text-lg">{planetData.planet}</h3>
                            <Badge variant={planetData.is_blind ? 'destructive' : 'default'}>
                              {planetData.is_blind ? 'Blind' : 'Clear Vision'}
                            </Badge>
                          </div>
                          <div className="text-sm text-muted-foreground mt-1">
                            House: {planetData.house}
                          </div>
                        </div>
                      </div>

                      {planetData.is_blind && planetData.blinding_factor && (
                        <div className="p-3 bg-muted/50 rounded mb-3">
                          <div className="text-sm">
                            <strong>Blinding Factor:</strong> {planetData.blinding_factor}
                          </div>
                        </div>
                      )}

                      {planetData.effects && planetData.effects.length > 0 && (
                        <div className="mb-3">
                          <h4 className="text-sm font-semibold mb-2">Effects:</h4>
                          <ul className="space-y-1">
                            {planetData.effects.map((effect, idx) => (
                              <li key={idx} className="text-sm text-muted-foreground flex items-start gap-2">
                                <span className={`${planetData.is_blind ? 'text-orange-500' : 'text-green-500'} mt-1`}>•</span>
                                <span>{effect}</span>
                              </li>
                            ))}
                          </ul>
                        </div>
                      )}

                      {planetData.is_blind && planetData.remedies && planetData.remedies.length > 0 && (
                        <div className="p-3 bg-gradient-to-r from-green-500/10 to-blue-500/10 rounded border border-green-500/20">
                          <h4 className="text-sm font-semibold mb-2 flex items-center gap-1">
                            <Lightbulb className="h-4 w-4 text-green-600" /> Remedies:
                          </h4>
                          <ul className="space-y-1">
                            {planetData.remedies.map((remedy, idx) => (
                              <li key={idx} className="text-sm flex items-start gap-2">
                                <span className="text-green-600 mt-1">✓</span>
                                <span>{remedy}</span>
                              </li>
                            ))}
                          </ul>
                        </div>
                      )}
                    </div>
                  ))}
                </div>

                <div className="mt-6 p-4 bg-muted/50 rounded-lg">
                  <h4 className="font-semibold mb-2">Understanding Blind Planets:</h4>
                  <p className="text-sm text-muted-foreground mb-2">
                    A planet becomes "blind" (Andha Graha) in Lal Kitab when it is in certain positions that prevent it from
                    protecting its significations. Blind planets cannot see or protect the houses they rule or aspect.
                  </p>
                  <p className="text-sm text-muted-foreground">
                    For example, Jupiter in 7th house becomes blind and cannot protect its natural significations of knowledge,
                    children, and wealth. Such planets require specific remedies to restore their protective vision.
                  </p>
                </div>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      )}

      {/* Educational Info */}
      <Card className="bg-gradient-to-r from-orange-500/10 to-red-500/10 border-orange-500/20">
        <CardHeader>
          <CardTitle>About Lal Kitab</CardTitle>
        </CardHeader>
        <CardContent className="space-y-2 text-sm">
          <p>
            <strong>Lal Kitab</strong> (Red Book) is a unique system of Vedic astrology written in Urdu and Persian,
            published in the 19th century. It focuses on karmic debts and practical, affordable remedies.
          </p>
          <p>
            <strong>Key Features:</strong> Identifies planetary debts (Rins) from past lives, blind planets that lose
            protective power, exalted enemies, and provides simple household remedies (Totke) for afflictions.
          </p>
          <p>
            <strong>Remedies:</strong> Unlike expensive gemstones, Lal Kitab remedies include feeding animals,
            charity, using household items, and performing simple rituals. These are called "Totke" and are designed
            to be accessible to common people.
          </p>
          <p>
            <strong>Philosophy:</strong> Emphasizes that current life problems stem from karmic debts, and through
            selfless service and specific remedies, one can neutralize negative karma and improve life conditions.
          </p>
        </CardContent>
      </Card>
    </div>
  )
}
