"use client"

import { useState, useEffect } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Loader2, AlertCircle, TrendingUp, TrendingDown, Activity } from 'lucide-react'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { getSession } from '@/lib/supabase'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import axios from 'axios'

interface AshtakavargaAnalysisProps {
  profileId: string
}

interface SarvaData {
  bindus_by_house: Record<string, number>
  total_bindus: number
  house_strength: Record<string, string>
  strongest_houses: number[]
  weakest_houses: number[]
}

interface BhinnaData {
  [planet: string]: {
    planet: string
    bindus_by_house: Record<string, number>
    total_bindus: number
    strongest_houses: number[]
    weakest_houses: number[]
  }
}

interface AshtakavargaData {
  sarva_ashtakavarga: SarvaData
  bhinna_ashtakavarga: BhinnaData
  summary: {
    total_bindus: number
    average_bindus_per_house: number
    strong_houses: number[]
    weak_houses: number[]
    overall_chart_strength: string
  }
  interpretation: string
}

export default function AshtakavargaAnalysis({ profileId }: AshtakavargaAnalysisProps) {
  const [data, setData] = useState<AshtakavargaData | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [selectedPlanet, setSelectedPlanet] = useState<string>('Sun')

  useEffect(() => {
    if (profileId) {
      fetchAshtakavargaData()
    }
  }, [profileId])

  const fetchAshtakavargaData = async () => {
    try {
      setLoading(true)
      setError(null)

      const session = getSession()
      if (!session) return

      const response = await axios.get(
        `${process.env.NEXT_PUBLIC_API_URL}/enhancements/ashtakavarga/analyze/${profileId}`,
        {
          headers: {
            Authorization: `Bearer ${session.access_token}`
          }
        }
      )

      setData(response.data.analysis)
    } catch (err: any) {
      console.error('Error fetching Ashtakavarga data:', err)
      setError(err.response?.data?.detail || err.message || 'Failed to load Ashtakavarga analysis')
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center py-12">
        <Loader2 className="h-8 w-8 animate-spin text-primary" />
      </div>
    )
  }

  if (error) {
    return (
      <Alert variant="destructive">
        <AlertCircle className="h-4 w-4" />
        <AlertDescription>{error}</AlertDescription>
      </Alert>
    )
  }

  if (!data) return null

  const getStrengthColor = (strength: string) => {
    switch (strength) {
      case 'very_strong': return 'bg-green-500'
      case 'good': return 'bg-blue-500'
      case 'average': return 'bg-yellow-500'
      case 'below_average': return 'bg-orange-500'
      case 'weak': return 'bg-red-500'
      default: return 'bg-gray-500'
    }
  }

  const getStrengthLabel = (strength: string) => {
    return strength.replace('_', ' ').split(' ').map(w => w.charAt(0).toUpperCase() + w.slice(1)).join(' ')
  }

  const planets = Object.keys(data.bhinna_ashtakavarga)

  return (
    <div className="space-y-6">
      {/* Summary Card */}
      <Card className="border-primary">
        <CardHeader>
          <div className="flex items-center gap-2">
            <Activity className="h-5 w-5 text-primary" />
            <CardTitle>Chart Summary</CardTitle>
          </div>
          <CardDescription>{data.interpretation}</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="text-center">
              <div className="text-3xl font-bold text-primary">{data.summary.total_bindus}</div>
              <div className="text-sm text-muted-foreground">Total Bindus</div>
            </div>
            <div className="text-center">
              <div className="text-3xl font-bold">{data.summary.average_bindus_per_house.toFixed(1)}</div>
              <div className="text-sm text-muted-foreground">Avg per House</div>
            </div>
            <div className="text-center">
              <Badge className="text-lg px-4 py-2">{data.summary.overall_chart_strength}</Badge>
              <div className="text-sm text-muted-foreground mt-1">Chart Strength</div>
            </div>
            <div className="text-center">
              <div className="text-3xl font-bold">{data.summary.strong_houses.length}</div>
              <div className="text-sm text-muted-foreground">Strong Houses</div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Tabs for Sarva and Bhinna */}
      <Tabs defaultValue="sarva" className="space-y-4">
        <TabsList className="grid w-full grid-cols-2">
          <TabsTrigger value="sarva">Sarva Ashtakavarga</TabsTrigger>
          <TabsTrigger value="bhinna">Bhinna Ashtakavarga</TabsTrigger>
        </TabsList>

        {/* Sarva Ashtakavarga */}
        <TabsContent value="sarva" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Sarva Ashtakavarga (Collective Chart)</CardTitle>
              <CardDescription>Combined bindus from all 7 planets - shows overall house strength</CardDescription>
            </CardHeader>
            <CardContent>
              {/* House Strengths Grid */}
              <div className="grid grid-cols-3 md:grid-cols-4 gap-3 mb-6">
                {Array.from({ length: 12 }, (_, i) => i + 1).map((house) => {
                  const bindus = data.sarva_ashtakavarga.bindus_by_house[house.toString()]
                  const strength = data.sarva_ashtakavarga.house_strength[house.toString()]
                  const isStrongest = data.sarva_ashtakavarga.strongest_houses.includes(house)
                  const isWeakest = data.sarva_ashtakavarga.weakest_houses.includes(house)

                  return (
                    <div
                      key={house}
                      className={`p-4 rounded-lg border-2 ${isStrongest ? 'border-green-500' : isWeakest ? 'border-red-500' : 'border-border'}`}
                    >
                      <div className="text-center">
                        <div className="text-xs text-muted-foreground mb-1">House {house}</div>
                        <div className="text-2xl font-bold">{bindus}</div>
                        <div className={`h-2 ${getStrengthColor(strength)} rounded-full mt-2`} />
                        <div className="text-xs mt-1">{getStrengthLabel(strength)}</div>
                      </div>
                    </div>
                  )
                })}
              </div>

              {/* Strength Legend */}
              <div className="flex flex-wrap gap-3 justify-center">
                <div className="flex items-center gap-2">
                  <div className="w-3 h-3 bg-green-500 rounded" />
                  <span className="text-xs">Very Strong (30+)</span>
                </div>
                <div className="flex items-center gap-2">
                  <div className="w-3 h-3 bg-blue-500 rounded" />
                  <span className="text-xs">Good (25-29)</span>
                </div>
                <div className="flex items-center gap-2">
                  <div className="w-3 h-3 bg-yellow-500 rounded" />
                  <span className="text-xs">Average (20-24)</span>
                </div>
                <div className="flex items-center gap-2">
                  <div className="w-3 h-3 bg-orange-500 rounded" />
                  <span className="text-xs">Below Avg (15-19)</span>
                </div>
                <div className="flex items-center gap-2">
                  <div className="w-3 h-3 bg-red-500 rounded" />
                  <span className="text-xs">Weak (&lt;15)</span>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Strongest and Weakest Houses */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <Card>
              <CardHeader>
                <div className="flex items-center gap-2">
                  <TrendingUp className="h-5 w-5 text-green-500" />
                  <CardTitle>Strongest Houses</CardTitle>
                </div>
              </CardHeader>
              <CardContent>
                <div className="space-y-2">
                  {data.sarva_ashtakavarga.strongest_houses.map((house) => (
                    <div key={house} className="flex items-center justify-between p-2 border rounded">
                      <span className="font-medium">House {house}</span>
                      <Badge variant="outline">{data.sarva_ashtakavarga.bindus_by_house[house.toString()]} bindus</Badge>
                    </div>
                  ))}
                </div>
                <p className="text-sm text-muted-foreground mt-3">
                  These areas of life will give best results and favorable outcomes.
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <div className="flex items-center gap-2">
                  <TrendingDown className="h-5 w-5 text-red-500" />
                  <CardTitle>Weakest Houses</CardTitle>
                </div>
              </CardHeader>
              <CardContent>
                <div className="space-y-2">
                  {data.sarva_ashtakavarga.weakest_houses.map((house) => (
                    <div key={house} className="flex items-center justify-between p-2 border rounded">
                      <span className="font-medium">House {house}</span>
                      <Badge variant="outline">{data.sarva_ashtakavarga.bindus_by_house[house.toString()]} bindus</Badge>
                    </div>
                  ))}
                </div>
                <p className="text-sm text-muted-foreground mt-3">
                  These areas may require extra effort and remedies for good results.
                </p>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        {/* Bhinna Ashtakavarga */}
        <TabsContent value="bhinna" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Bhinna Ashtakavarga (Individual Planet Charts)</CardTitle>
              <CardDescription>Each planet's contribution of bindus to houses</CardDescription>
            </CardHeader>
            <CardContent>
              {/* Planet Selector */}
              <div className="flex items-center gap-2 mb-6 flex-wrap">
                {planets.map((planet) => (
                  <Badge
                    key={planet}
                    variant={selectedPlanet === planet ? 'default' : 'outline'}
                    className="cursor-pointer"
                    onClick={() => setSelectedPlanet(planet)}
                  >
                    {planet}
                  </Badge>
                ))}
              </div>

              {/* Selected Planet's Bindus */}
              {data.bhinna_ashtakavarga[selectedPlanet] && (
                <div>
                  <div className="mb-4">
                    <div className="text-lg font-medium">{selectedPlanet}</div>
                    <div className="text-sm text-muted-foreground">
                      Total: {data.bhinna_ashtakavarga[selectedPlanet].total_bindus} bindus
                    </div>
                  </div>

                  <div className="grid grid-cols-3 md:grid-cols-4 gap-3">
                    {Array.from({ length: 12 }, (_, i) => i + 1).map((house) => {
                      const bindus = data.bhinna_ashtakavarga[selectedPlanet].bindus_by_house[house.toString()] || 0
                      const isStrongest = data.bhinna_ashtakavarga[selectedPlanet].strongest_houses.includes(house)
                      const isWeakest = data.bhinna_ashtakavarga[selectedPlanet].weakest_houses.includes(house)

                      return (
                        <div
                          key={house}
                          className={`p-3 rounded-lg border ${isStrongest ? 'border-green-500 bg-green-50' : isWeakest ? 'border-red-500 bg-red-50' : 'border-border'}`}
                        >
                          <div className="text-center">
                            <div className="text-xs text-muted-foreground">H{house}</div>
                            <div className="text-xl font-bold">{bindus}</div>
                          </div>
                        </div>
                      )
                    })}
                  </div>
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>

      {/* Information Card */}
      <Card className="bg-muted/50">
        <CardHeader>
          <CardTitle className="text-lg">Understanding Ashtakavarga</CardTitle>
        </CardHeader>
        <CardContent className="space-y-2 text-sm">
          <p><strong>Bindus (Points):</strong> Benefic points that indicate strength. More bindus = stronger house.</p>
          <p><strong>Sarva Ashtakavarga:</strong> Combined chart showing overall house strength (max 56 bindus per house).</p>
          <p><strong>Bhinna Ashtakavarga:</strong> Individual planet charts showing their specific contributions (max 8 per house).</p>
          <p><strong>Transit Use:</strong> When a planet transits a house with high bindus, it gives better results.</p>
          <p><strong>Interpretation:</strong> Houses with 30+ bindus are very strong and give excellent results throughout life.</p>
        </CardContent>
      </Card>
    </div>
  )
}
