'use client'

import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@/lib/query'
import { apiClient } from '@/lib/api'
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Badge } from '@/components/ui/badge'
import { Loader2, Calendar, Clock, Star, Sun, Moon, Brain, CheckCircle, XCircle, AlertTriangle } from 'lucide-react'

interface PanchangData {
  date: string
  time: string
  location: { latitude: number; longitude: number }
  sunrise?: string
  sunset?: string
  tithi: {
    tithi_name: string
    paksha: string
    progress_percent: number
    is_auspicious: boolean
    description: string
  }
  nakshatra: {
    nakshatra_name: string
    pada: number
    ruler: string
    deity: string
    nature: string
    is_auspicious: boolean
    favorable_for: string[]
  }
  yoga: {
    yoga_name: string
    quality: string
    is_auspicious: boolean
    description: string
  }
  karana: {
    karana_name: string
    nature: string
    is_auspicious: boolean
  }
  vara: {
    vara_name: string
    ruling_planet: string
    quality: string
    favorable_for: string[]
  }
  overall_quality: string
  auspicious_score: number
  summary: string
}

interface HoraData {
  current_time: string
  is_day: boolean
  hora_number: number
  ruling_planet: string
  hora_starts: string
  hora_ends: string
  progress_percent: number
  favorable_for: string[]
  unfavorable_for: string[]
  strength: string
}

interface MuhurtaResult {
  datetime: string
  date: string
  time_range: string
  score: number
  quality: string
  tithi: string
  nakshatra: string
  vara: string
  hora_ruler: string
  yoga: string
  karana: string
  reasons: string[]
  precautions: string[]
}

export default function MuhurtaPage() {
  const [activeTab, setActiveTab] = useState('panchang')

  // Panchang state
  const [panchangDate, setPanchangDate] = useState(new Date().toISOString().split('T')[0])
  const [panchangTime, setPanchangTime] = useState(new Date().toTimeString().split(' ')[0].substring(0, 5))
  const [panchangLat, setPanchangLat] = useState('28.6139')
  const [panchangLon, setPanchangLon] = useState('77.2090')
  const [panchangData, setPanchangData] = useState<PanchangData | null>(null)

  // Hora state
  const [horaDate, setHoraDate] = useState(new Date().toISOString().split('T')[0])
  const [horaTime, setHoraTime] = useState(new Date().toTimeString().split(' ')[0].substring(0, 5))
  const [horaLat, setHoraLat] = useState('28.6139')
  const [horaLon, setHoraLon] = useState('77.2090')
  const [horaData, setHoraData] = useState<HoraData | null>(null)

  // Muhurta Finder state
  const [activityType, setActivityType] = useState('marriage')
  const [startDate, setStartDate] = useState(new Date().toISOString().split('T')[0])
  const [endDate, setEndDate] = useState(
    new Date(Date.now() + 30 * 24 * 60 * 60 * 1000).toISOString().split('T')[0]
  )
  const [muhurtaLat, setMuhurtaLat] = useState('28.6139')
  const [muhurtaLon, setMuhurtaLon] = useState('77.2090')
  const [muhurtaResults, setMuhurtaResults] = useState<MuhurtaResult[] | null>(null)

  // Decision Copilot state
  const [copilotActivityType, setCopilotActivityType] = useState('marriage')
  const [copilotStartDate, setCopilotStartDate] = useState(new Date().toISOString().split('T')[0])
  const [copilotEndDate, setCopilotEndDate] = useState(
    new Date(Date.now() + 30 * 24 * 60 * 60 * 1000).toISOString().split('T')[0]
  )
  const [copilotLat, setCopilotLat] = useState('28.6139')
  const [copilotLon, setCopilotLon] = useState('77.2090')
  const [copilotResult, setCopilotResult] = useState<any | null>(null)

  // Error states
  const [panchangError, setPanchangError] = useState<string | null>(null)
  const [horaError, setHoraError] = useState<string | null>(null)
  const [muhurtaError, setMuhurtaError] = useState<string | null>(null)
  const [copilotError, setCopilotError] = useState<string | null>(null)

  // Panchang mutation
  const panchangMutation = useMutation({
    mutationFn: async () => {
      setPanchangError(null)
      const datetime = `${panchangDate}T${panchangTime}:00`
      const response = await apiClient.getPanchang({
        datetime,
        latitude: parseFloat(panchangLat),
        longitude: parseFloat(panchangLon),
      })
      return response.data
    },
    onSuccess: (data) => {
      setPanchangData(data)
      setPanchangError(null)
    },
    onError: (error: any) => {
      console.error('Panchang calculation error:', error)
      setPanchangError(error?.message || 'Failed to calculate Panchang. Please try again.')
    },
  })

  // Hora mutation
  const horaMutation = useMutation({
    mutationFn: async () => {
      setHoraError(null)
      const datetime = `${horaDate}T${horaTime}:00`
      console.log('Hora mutation: Calling API with', { datetime, lat: horaLat, lon: horaLon })
      const response = await apiClient.getHora({
        datetime,
        latitude: parseFloat(horaLat),
        longitude: parseFloat(horaLon),
      })
      console.log('Hora mutation: API response received', response)
      return response.data
    },
    onSuccess: (data) => {
      console.log('Hora mutation: onSuccess called with data:', data)
      try {
        setHoraData(data)
        setHoraError(null)
        console.log('Hora mutation: State updated successfully')
      } catch (err) {
        console.error('Hora mutation: Error in onSuccess:', err)
      }
    },
    onError: (error: any) => {
      console.error('Hora calculation error:', error)
      setHoraError(error?.message || 'Failed to calculate Hora. Please try again.')
    },
  })

  // Muhurta Finder mutation
  const muhurtaMutation = useMutation({
    mutationFn: async () => {
      setMuhurtaError(null)
      console.log('Muhurta mutation: Calling API with', { activityType, startDate, endDate, lat: muhurtaLat, lon: muhurtaLon })
      const response = await apiClient.findMuhurta({
        activity_type: activityType,
        start_date: startDate,
        end_date: endDate,
        latitude: parseFloat(muhurtaLat),
        longitude: parseFloat(muhurtaLon),
        max_results: 10,
      })
      console.log('Muhurta mutation: API response received', response)
      return response.data
    },
    onSuccess: (data) => {
      console.log('Muhurta mutation: onSuccess called with data:', data)
      try {
        setMuhurtaResults(data.results)
        setMuhurtaError(null)
        console.log('Muhurta mutation: State updated successfully')
      } catch (err) {
        console.error('Muhurta mutation: Error in onSuccess:', err)
      }
    },
    onError: (error: any) => {
      console.error('Muhurta finder error:', error)
      setMuhurtaError(error?.message || 'Failed to find Muhurta. Please try again.')
    },
  })

  // Decision Copilot mutation
  const copilotMutation = useMutation({
    mutationFn: async () => {
      setCopilotError(null)
      console.log('Decision Copilot: Calling API with', {
        copilotActivityType, copilotStartDate, copilotEndDate,
        lat: copilotLat, lon: copilotLon
      })
      const response = await apiClient.getDecisionCopilotGuidance({
        activity_type: copilotActivityType,
        start_date: copilotStartDate,
        end_date: copilotEndDate,
        latitude: parseFloat(copilotLat),
        longitude: parseFloat(copilotLon),
        max_results: 5,
        chart_id: null, // TODO: Add chart selector
      })
      console.log('Decision Copilot: API response received', response)
      return response.data
    },
    onSuccess: (data) => {
      console.log('Decision Copilot: onSuccess called with data:', data)
      try {
        setCopilotResult(data)
        setCopilotError(null)
        console.log('Decision Copilot: State updated successfully')
      } catch (err) {
        console.error('Decision Copilot: Error in onSuccess:', err)
      }
    },
    onError: (error: any) => {
      console.error('Decision Copilot error:', error)
      setCopilotError(error?.message || 'Failed to get Decision Copilot guidance. Please try again.')
    },
  })

  const getQualityColor = (quality: string) => {
    const q = quality.toLowerCase()
    if (q.includes('highly auspicious')) return 'bg-green-100 dark:bg-green-900 border-green-300'
    if (q.includes('auspicious') || q.includes('excellent')) return 'bg-emerald-100 dark:bg-emerald-900 border-emerald-300'
    if (q.includes('good')) return 'bg-blue-100 dark:bg-blue-900 border-blue-300'
    if (q.includes('mixed') || q.includes('moderate')) return 'bg-yellow-100 dark:bg-yellow-900 border-yellow-300'
    return 'bg-gray-100 dark:bg-gray-800 border-gray-300'
  }

  const formatTime = (isoString?: string) => {
    if (!isoString) return 'N/A'
    const date = new Date(isoString)
    return date.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' })
  }

  return (
    <div className="container mx-auto p-6">
      <div className="mb-6">
        <h1 className="text-3xl font-bold mb-2">Muhurta - Auspicious Time</h1>
        <p className="text-muted-foreground">
          Find auspicious times, check daily Panchang, and discover favorable planetary hours
        </p>
      </div>

      <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-6">
        <TabsList className="grid w-full grid-cols-4">
          <TabsTrigger value="panchang">Panchang</TabsTrigger>
          <TabsTrigger value="hora">Hora Calculator</TabsTrigger>
          <TabsTrigger value="finder">Muhurta Finder</TabsTrigger>
          <TabsTrigger value="copilot">🤖 Decision Copilot</TabsTrigger>
        </TabsList>

        {/* PANCHANG TAB */}
        <TabsContent value="panchang" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Calendar className="h-5 w-5" />
                Daily Panchang
              </CardTitle>
              <CardDescription>
                Get the 5 sacred elements (Tithi, Nakshatra, Yoga, Karana, Vara) for any date and location
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                <div>
                  <Label htmlFor="panchang-date">Date</Label>
                  <Input
                    id="panchang-date"
                    type="date"
                    value={panchangDate}
                    onChange={(e) => setPanchangDate(e.target.value)}
                  />
                </div>
                <div>
                  <Label htmlFor="panchang-time">Time</Label>
                  <Input
                    id="panchang-time"
                    type="time"
                    value={panchangTime}
                    onChange={(e) => setPanchangTime(e.target.value)}
                  />
                </div>
                <div>
                  <Label htmlFor="panchang-lat">Latitude</Label>
                  <Input
                    id="panchang-lat"
                    type="number"
                    step="0.0001"
                    value={panchangLat}
                    onChange={(e) => setPanchangLat(e.target.value)}
                    placeholder="28.6139"
                  />
                </div>
                <div>
                  <Label htmlFor="panchang-lon">Longitude</Label>
                  <Input
                    id="panchang-lon"
                    type="number"
                    step="0.0001"
                    value={panchangLon}
                    onChange={(e) => setPanchangLon(e.target.value)}
                    placeholder="77.2090"
                  />
                </div>
              </div>

              <Button
                onClick={() => panchangMutation.mutate()}
                disabled={panchangMutation.isPending}
                className="w-full"
              >
                {panchangMutation.isPending && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
                Calculate Panchang
              </Button>

              {panchangError && (
                <div className="p-4 rounded-lg border border-red-300 bg-red-50 dark:bg-red-900/20">
                  <p className="text-sm text-red-600 dark:text-red-400">{panchangError}</p>
                </div>
              )}

              {panchangData && (
                <div className="space-y-4 mt-6">
                  <div className={`p-4 rounded-lg border ${getQualityColor(panchangData.overall_quality)}`}>
                    <div className="flex items-center justify-between mb-2">
                      <h3 className="text-lg font-semibold">Overall Quality</h3>
                      <Badge variant="secondary">{panchangData.overall_quality}</Badge>
                    </div>
                    <p className="text-sm text-muted-foreground">{panchangData.summary}</p>
                    <div className="flex items-center gap-4 mt-2 text-sm">
                      <div className="flex items-center gap-1">
                        <Sun className="h-4 w-4" />
                        Sunrise: {formatTime(panchangData.sunrise)}
                      </div>
                      <div className="flex items-center gap-1">
                        <Moon className="h-4 w-4" />
                        Sunset: {formatTime(panchangData.sunset)}
                      </div>
                      <div>
                        Auspicious Score: {panchangData.auspicious_score}/4
                      </div>
                    </div>
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <Card>
                      <CardHeader className="pb-3">
                        <CardTitle className="text-base">Tithi (Lunar Day)</CardTitle>
                      </CardHeader>
                      <CardContent>
                        <div className="space-y-2">
                          <div className="flex justify-between">
                            <span className="font-medium">{panchangData.tithi.tithi_name}</span>
                            <Badge variant={panchangData.tithi.is_auspicious ? "default" : "secondary"}>
                              {panchangData.tithi.is_auspicious ? "Auspicious" : "Neutral"}
                            </Badge>
                          </div>
                          <div className="text-sm text-muted-foreground">
                            {panchangData.tithi.paksha} Paksha
                          </div>
                          <div className="text-sm">{panchangData.tithi.description}</div>
                          <div className="text-xs text-muted-foreground">
                            Progress: {panchangData.tithi.progress_percent.toFixed(1)}%
                          </div>
                        </div>
                      </CardContent>
                    </Card>

                    <Card>
                      <CardHeader className="pb-3">
                        <CardTitle className="text-base">Nakshatra (Lunar Mansion)</CardTitle>
                      </CardHeader>
                      <CardContent>
                        <div className="space-y-2">
                          <div className="flex justify-between">
                            <span className="font-medium">{panchangData.nakshatra.nakshatra_name}</span>
                            <Badge variant={panchangData.nakshatra.is_auspicious ? "default" : "secondary"}>
                              {panchangData.nakshatra.is_auspicious ? "Auspicious" : "Neutral"}
                            </Badge>
                          </div>
                          <div className="text-sm text-muted-foreground">
                            Ruled by {panchangData.nakshatra.ruler} | Pada {panchangData.nakshatra.pada}
                          </div>
                          <div className="text-sm">
                            Deity: {panchangData.nakshatra.deity} | Nature: {panchangData.nakshatra.nature}
                          </div>
                          <div className="text-xs">
                            Favorable for: {panchangData.nakshatra.favorable_for.slice(0, 3).join(', ')}
                          </div>
                        </div>
                      </CardContent>
                    </Card>

                    <Card>
                      <CardHeader className="pb-3">
                        <CardTitle className="text-base">Yoga</CardTitle>
                      </CardHeader>
                      <CardContent>
                        <div className="space-y-2">
                          <div className="flex justify-between">
                            <span className="font-medium">{panchangData.yoga.yoga_name}</span>
                            <Badge variant={panchangData.yoga.is_auspicious ? "default" : "secondary"}>
                              {panchangData.yoga.quality}
                            </Badge>
                          </div>
                          <div className="text-sm">{panchangData.yoga.description}</div>
                        </div>
                      </CardContent>
                    </Card>

                    <Card>
                      <CardHeader className="pb-3">
                        <CardTitle className="text-base">Karana & Vara</CardTitle>
                      </CardHeader>
                      <CardContent>
                        <div className="space-y-3">
                          <div>
                            <div className="flex justify-between mb-1">
                              <span className="text-sm font-medium">Karana:</span>
                              <span className="text-sm">{panchangData.karana.karana_name}</span>
                            </div>
                            <div className="text-xs text-muted-foreground">
                              Nature: {panchangData.karana.nature}
                            </div>
                          </div>
                          <div>
                            <div className="flex justify-between mb-1">
                              <span className="text-sm font-medium">Vara (Day):</span>
                              <span className="text-sm">{panchangData.vara.vara_name}</span>
                            </div>
                            <div className="text-xs text-muted-foreground">
                              Ruled by {panchangData.vara.ruling_planet} | {panchangData.vara.quality}
                            </div>
                          </div>
                        </div>
                      </CardContent>
                    </Card>
                  </div>
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        {/* HORA CALCULATOR TAB */}
        <TabsContent value="hora" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Clock className="h-5 w-5" />
                Hora Calculator
              </CardTitle>
              <CardDescription>
                Find the ruling planet for any time. Each day/night is divided into 12 planetary hours.
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                <div>
                  <Label htmlFor="hora-date">Date</Label>
                  <Input
                    id="hora-date"
                    type="date"
                    value={horaDate}
                    onChange={(e) => setHoraDate(e.target.value)}
                  />
                </div>
                <div>
                  <Label htmlFor="hora-time">Time</Label>
                  <Input
                    id="hora-time"
                    type="time"
                    value={horaTime}
                    onChange={(e) => setHoraTime(e.target.value)}
                  />
                </div>
                <div>
                  <Label htmlFor="hora-lat">Latitude</Label>
                  <Input
                    id="hora-lat"
                    type="number"
                    step="0.0001"
                    value={horaLat}
                    onChange={(e) => setHoraLat(e.target.value)}
                  />
                </div>
                <div>
                  <Label htmlFor="hora-lon">Longitude</Label>
                  <Input
                    id="hora-lon"
                    type="number"
                    step="0.0001"
                    value={horaLon}
                    onChange={(e) => setHoraLon(e.target.value)}
                  />
                </div>
              </div>

              <Button
                onClick={() => horaMutation.mutate()}
                disabled={horaMutation.isPending}
                className="w-full"
              >
                {horaMutation.isPending && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
                Calculate Hora
              </Button>

              {horaError && (
                <div className="p-4 rounded-lg border border-red-300 bg-red-50 dark:bg-red-900/20">
                  <p className="text-sm text-red-600 dark:text-red-400">{horaError}</p>
                </div>
              )}

              {horaData && (
                <div className="space-y-4 mt-6">
                  <Card className={getQualityColor(horaData.strength)}>
                    <CardContent className="pt-6">
                      <div className="text-center space-y-3">
                        <div className="text-lg font-semibold">
                          {new Date(horaData.current_time).toLocaleDateString('en-US', {
                            weekday: 'long',
                            year: 'numeric',
                            month: 'long',
                            day: 'numeric'
                          })}
                        </div>
                        <div className="text-sm text-muted-foreground">
                          {new Date(horaData.current_time).toLocaleTimeString('en-US', {
                            hour: '2-digit',
                            minute: '2-digit'
                          })}
                        </div>
                        <div className="text-sm text-muted-foreground">
                          {horaData.is_day ? "Day" : "Night"} Hora #{horaData.hora_number} of 12
                        </div>
                        <div className="text-3xl font-bold">{horaData.ruling_planet}</div>
                        <div className="text-sm">
                          {formatTime(horaData.hora_starts)} - {formatTime(horaData.hora_ends)}
                        </div>
                        <div className="text-xs text-muted-foreground">
                          Progress: {horaData.progress_percent.toFixed(1)}%
                        </div>
                        <Badge variant="secondary">{horaData.strength}</Badge>
                      </div>
                    </CardContent>
                  </Card>

                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <Card>
                      <CardHeader className="pb-3">
                        <CardTitle className="text-base text-green-600 dark:text-green-400">
                          Favorable Activities
                        </CardTitle>
                      </CardHeader>
                      <CardContent>
                        <ul className="list-disc list-inside space-y-1 text-sm">
                          {horaData.favorable_for.map((activity, i) => (
                            <li key={i}>{activity}</li>
                          ))}
                        </ul>
                      </CardContent>
                    </Card>

                    <Card>
                      <CardHeader className="pb-3">
                        <CardTitle className="text-base text-red-600 dark:text-red-400">
                          Unfavorable Activities
                        </CardTitle>
                      </CardHeader>
                      <CardContent>
                        <ul className="list-disc list-inside space-y-1 text-sm">
                          {horaData.unfavorable_for.map((activity, i) => (
                            <li key={i}>{activity}</li>
                          ))}
                        </ul>
                      </CardContent>
                    </Card>
                  </div>
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        {/* MUHURTA FINDER TAB */}
        <TabsContent value="finder" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Star className="h-5 w-5" />
                Muhurta Finder
              </CardTitle>
              <CardDescription>
                Find the most auspicious days for important activities. Shows the best time for each auspicious day (unique dates only).
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                <div>
                  <Label htmlFor="activity-type">Activity Type</Label>
                  <Select value={activityType} onValueChange={setActivityType}>
                    <SelectTrigger id="activity-type">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="marriage">Marriage Ceremony</SelectItem>
                      <SelectItem value="business">Business Start</SelectItem>
                      <SelectItem value="travel">Travel / Journey</SelectItem>
                      <SelectItem value="property">Property Purchase</SelectItem>
                      <SelectItem value="surgery">Medical Surgery</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                <div>
                  <Label htmlFor="start-date">Start Date</Label>
                  <Input
                    id="start-date"
                    type="date"
                    value={startDate}
                    onChange={(e) => setStartDate(e.target.value)}
                  />
                </div>
                <div>
                  <Label htmlFor="end-date">End Date (Max 90 days)</Label>
                  <Input
                    id="end-date"
                    type="date"
                    value={endDate}
                    onChange={(e) => setEndDate(e.target.value)}
                  />
                </div>
                <div>
                  <Label htmlFor="muhurta-lat">Latitude</Label>
                  <Input
                    id="muhurta-lat"
                    type="number"
                    step="0.0001"
                    value={muhurtaLat}
                    onChange={(e) => setMuhurtaLat(e.target.value)}
                  />
                </div>
                <div>
                  <Label htmlFor="muhurta-lon">Longitude</Label>
                  <Input
                    id="muhurta-lon"
                    type="number"
                    step="0.0001"
                    value={muhurtaLon}
                    onChange={(e) => setMuhurtaLon(e.target.value)}
                  />
                </div>
              </div>

              <Button
                onClick={() => muhurtaMutation.mutate()}
                disabled={muhurtaMutation.isPending}
                className="w-full"
              >
                {muhurtaMutation.isPending && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
                Find Auspicious Times
              </Button>

              {muhurtaError && (
                <div className="p-4 rounded-lg border border-red-300 bg-red-50 dark:bg-red-900/20">
                  <p className="text-sm text-red-600 dark:text-red-400">{muhurtaError}</p>
                </div>
              )}

              {muhurtaResults && (
                <div className="space-y-4 mt-6">
                  <div className="p-3 rounded-lg bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800">
                    <p className="text-sm font-medium text-blue-900 dark:text-blue-100">
                      Found {muhurtaResults.length} auspicious {muhurtaResults.length === 1 ? 'day' : 'days'} for {activityType}
                    </p>
                    <p className="text-xs text-blue-700 dark:text-blue-300 mt-1">
                      Showing the best time for each auspicious day. Each result represents a unique date.
                    </p>
                  </div>

                  {muhurtaResults.map((result, index) => (
                    <Card key={index} className={getQualityColor(result.quality)}>
                      <CardContent className="pt-6">
                        <div className="flex items-start justify-between mb-4">
                          <div>
                            <div className="text-lg font-semibold">{result.date}</div>
                            <div className="text-sm text-muted-foreground">{result.time_range}</div>
                          </div>
                          <div className="text-right">
                            <div className="text-2xl font-bold">{result.score}/100</div>
                            <Badge variant="secondary">{result.quality}</Badge>
                          </div>
                        </div>

                        <div className="grid grid-cols-2 md:grid-cols-4 gap-2 mb-4 text-sm">
                          <div>
                            <span className="text-muted-foreground">Tithi:</span> {result.tithi}
                          </div>
                          <div>
                            <span className="text-muted-foreground">Nakshatra:</span> {result.nakshatra}
                          </div>
                          <div>
                            <span className="text-muted-foreground">Vara:</span> {result.vara}
                          </div>
                          <div>
                            <span className="text-muted-foreground">Hora:</span> {result.hora_ruler}
                          </div>
                        </div>

                        {result.reasons.length > 0 && (
                          <div className="mb-2">
                            <div className="text-sm font-medium mb-1">Why this time is auspicious:</div>
                            <ul className="list-disc list-inside text-sm space-y-1">
                              {result.reasons.slice(0, 3).map((reason, i) => (
                                <li key={i} className="text-muted-foreground">{reason}</li>
                              ))}
                            </ul>
                          </div>
                        )}

                        {result.precautions.length > 0 && (
                          <div>
                            <div className="text-sm font-medium mb-1">Precautions:</div>
                            <ul className="list-disc list-inside text-sm space-y-1">
                              {result.precautions.slice(0, 2).map((precaution, i) => (
                                <li key={i} className="text-muted-foreground">{precaution}</li>
                              ))}
                            </ul>
                          </div>
                        )}
                      </CardContent>
                    </Card>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        {/* DECISION COPILOT TAB */}
        <TabsContent value="copilot" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Brain className="h-5 w-5 text-purple-600" />
                AI-Powered Decision Copilot
              </CardTitle>
              <CardDescription>
                Get AI-powered guidance to choose the best auspicious time with detailed comparison,
                pros/cons analysis, and personalized recommendations
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4">
                <div>
                  <Label htmlFor="copilot-activity">Activity</Label>
                  <Select value={copilotActivityType} onValueChange={setCopilotActivityType}>
                    <SelectTrigger id="copilot-activity">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="marriage">Marriage</SelectItem>
                      <SelectItem value="business">Business Start</SelectItem>
                      <SelectItem value="travel">Travel</SelectItem>
                      <SelectItem value="property">Property Purchase</SelectItem>
                      <SelectItem value="surgery">Surgery/Medical</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                <div>
                  <Label htmlFor="copilot-start-date">Start Date</Label>
                  <Input
                    id="copilot-start-date"
                    type="date"
                    value={copilotStartDate}
                    onChange={(e) => setCopilotStartDate(e.target.value)}
                  />
                </div>
                <div>
                  <Label htmlFor="copilot-end-date">End Date</Label>
                  <Input
                    id="copilot-end-date"
                    type="date"
                    value={copilotEndDate}
                    onChange={(e) => setCopilotEndDate(e.target.value)}
                  />
                </div>
                <div>
                  <Label htmlFor="copilot-lat">Latitude</Label>
                  <Input
                    id="copilot-lat"
                    type="number"
                    step="0.0001"
                    value={copilotLat}
                    onChange={(e) => setCopilotLat(e.target.value)}
                    placeholder="28.6139"
                  />
                </div>
                <div>
                  <Label htmlFor="copilot-lon">Longitude</Label>
                  <Input
                    id="copilot-lon"
                    type="number"
                    step="0.0001"
                    value={copilotLon}
                    onChange={(e) => setCopilotLon(e.target.value)}
                    placeholder="77.2090"
                  />
                </div>
              </div>

              <Button
                onClick={() => copilotMutation.mutate()}
                disabled={copilotMutation.isPending}
                className="w-full"
              >
                {copilotMutation.isPending && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
                Get AI Decision Guidance
              </Button>

              {copilotError && (
                <div className="bg-destructive/15 text-destructive px-4 py-3 rounded-lg">
                  {copilotError}
                </div>
              )}

              {copilotResult && copilotResult.ai_guidance && (
                <div className="space-y-6 mt-6">
                  {/* Best Time Recommendation */}
                  <Card className="border-2 border-green-500 bg-green-50 dark:bg-green-950">
                    <CardHeader className="bg-gradient-to-r from-green-100 to-emerald-100 dark:from-green-900 dark:to-emerald-900">
                      <CardTitle className="flex items-center gap-2 text-green-900 dark:text-green-100">
                        <Star className="h-5 w-5 fill-current" />
                        Recommended Best Time
                      </CardTitle>
                      <CardDescription className="text-green-800 dark:text-green-200">
                        {new Date(copilotResult.ai_guidance.best_time.datetime).toLocaleDateString('en-US', {
                          weekday: 'long', year: 'numeric', month: 'long', day: 'numeric'
                        })}
                      </CardDescription>
                    </CardHeader>
                    <CardContent className="pt-6">
                      <div className="space-y-4">
                        {/* Specific Time Period */}
                        {copilotResult.ai_guidance.best_time.specific_time && (
                          <div className="bg-amber-50 dark:bg-amber-950 p-3 rounded-lg border border-amber-200 dark:border-amber-800">
                            <div className="flex items-center gap-2">
                              <Clock className="h-4 w-4 text-amber-600 dark:text-amber-400" />
                              <span className="text-sm font-semibold text-amber-900 dark:text-amber-100">
                                Best Time Period:
                              </span>
                            </div>
                            <p className="text-sm text-amber-800 dark:text-amber-200 mt-1">
                              {copilotResult.ai_guidance.best_time.specific_time}
                            </p>
                          </div>
                        )}

                        {/* Rating */}
                        <div className="flex items-center justify-between">
                          <span className="text-sm font-medium">AI Rating:</span>
                          <div className="flex items-center gap-2">
                            <div className="flex">
                              {[...Array(10)].map((_, i) => (
                                <Star
                                  key={i}
                                  className={`h-4 w-4 ${
                                    i < copilotResult.ai_guidance.best_time.rating
                                      ? 'fill-yellow-400 text-yellow-400'
                                      : 'fill-gray-300 text-gray-300'
                                  }`}
                                />
                              ))}
                            </div>
                            <span className="font-bold text-lg">
                              {copilotResult.ai_guidance.best_time.rating}/10
                            </span>
                          </div>
                        </div>

                        {/* Reasoning */}
                        <div className="bg-white dark:bg-gray-900 p-4 rounded-lg">
                          <h4 className="font-semibold mb-2 flex items-center gap-2">
                            <Brain className="h-4 w-4" />
                            Why This Time?
                          </h4>
                          <p className="text-sm text-gray-700 dark:text-gray-300 leading-relaxed">
                            {copilotResult.ai_guidance.best_time.reasoning}
                          </p>
                        </div>

                        {/* Actionable Advice */}
                        <div className="bg-blue-50 dark:bg-blue-950 p-4 rounded-lg border border-blue-200 dark:border-blue-800">
                          <h4 className="font-semibold mb-2 text-blue-900 dark:text-blue-100">
                            📋 Actionable Guidance
                          </h4>
                          <p className="text-sm text-blue-800 dark:text-blue-200">
                            {copilotResult.ai_guidance.best_time.actionable_advice}
                          </p>
                        </div>

                        {/* Panchang Details */}
                        <div className="grid grid-cols-2 md:grid-cols-4 gap-2 text-sm">
                          <div>
                            <span className="text-muted-foreground">Tithi:</span>{' '}
                            <span className="font-medium">{copilotResult.ai_guidance.best_time.tithi}</span>
                          </div>
                          <div>
                            <span className="text-muted-foreground">Nakshatra:</span>{' '}
                            <span className="font-medium">{copilotResult.ai_guidance.best_time.nakshatra}</span>
                          </div>
                          <div>
                            <span className="text-muted-foreground">Vara:</span>{' '}
                            <span className="font-medium">{copilotResult.ai_guidance.best_time.vara}</span>
                          </div>
                          <div>
                            <span className="text-muted-foreground">Hora:</span>{' '}
                            <span className="font-medium">{copilotResult.ai_guidance.best_time.hora_ruler}</span>
                          </div>
                        </div>
                      </div>
                    </CardContent>
                  </Card>

                  {/* All Options Comparison */}
                  <Card>
                    <CardHeader>
                      <CardTitle>All Options Comparison</CardTitle>
                      <CardDescription>
                        Detailed AI analysis of {copilotResult.ai_guidance.total_options} time options
                      </CardDescription>
                    </CardHeader>
                    <CardContent>
                      <div className="space-y-4">
                        {copilotResult.ai_guidance.comparison.map((option: any, index: number) => (
                          <Card
                            key={index}
                            className={`${
                              index === copilotResult.ai_guidance.best_time.option_number - 1
                                ? 'border-2 border-green-500'
                                : ''
                            }`}
                          >
                            <CardHeader className="pb-3">
                              <div className="flex items-center justify-between">
                                <div>
                                  <CardTitle className="text-base flex items-center gap-2">
                                    Option {index + 1}
                                    {index === copilotResult.ai_guidance.best_time.option_number - 1 && (
                                      <Badge variant="default" className="bg-green-600">Best</Badge>
                                    )}
                                  </CardTitle>
                                  <CardDescription>
                                    {new Date(option.datetime).toLocaleDateString('en-US', {
                                      weekday: 'short', month: 'short', day: 'numeric'
                                    })}
                                  </CardDescription>
                                </div>
                                <div className="flex items-center gap-2">
                                  <div className="flex">
                                    {[...Array(10)].map((_, i) => (
                                      <Star
                                        key={i}
                                        className={`h-3 w-3 ${
                                          i < option.ai_rating
                                            ? 'fill-yellow-400 text-yellow-400'
                                            : 'fill-gray-300 text-gray-300'
                                        }`}
                                      />
                                    ))}
                                  </div>
                                  <span className="text-sm font-semibold">{option.ai_rating}/10</span>
                                </div>
                              </div>
                            </CardHeader>
                            <CardContent className="space-y-3">
                              {/* Best Time Within Day */}
                              {option.best_time_within_day && option.best_time_within_day !== 'Full day' && (
                                <div className="bg-sky-50 dark:bg-sky-950 p-2 rounded text-xs border border-sky-200 dark:border-sky-800">
                                  <div className="flex items-center gap-1">
                                    <Clock className="h-3 w-3 text-sky-600 dark:text-sky-400" />
                                    <span className="font-medium text-sky-900 dark:text-sky-100">
                                      {option.best_time_within_day}
                                    </span>
                                  </div>
                                </div>
                              )}

                              {/* Pros */}
                              {option.pros && option.pros.length > 0 && (
                                <div>
                                  <h5 className="text-sm font-semibold mb-1 flex items-center gap-1 text-green-700 dark:text-green-400">
                                    <CheckCircle className="h-4 w-4" />
                                    Pros
                                  </h5>
                                  <ul className="text-sm space-y-1">
                                    {option.pros.map((pro: string, i: number) => (
                                      <li key={i} className="flex items-start gap-2">
                                        <span className="text-green-600 dark:text-green-500 mt-0.5">✓</span>
                                        <span className="text-gray-700 dark:text-gray-300">{pro}</span>
                                      </li>
                                    ))}
                                  </ul>
                                </div>
                              )}

                              {/* Cons */}
                              {option.cons && option.cons.length > 0 && (
                                <div>
                                  <h5 className="text-sm font-semibold mb-1 flex items-center gap-1 text-orange-700 dark:text-orange-400">
                                    <AlertTriangle className="h-4 w-4" />
                                    Considerations
                                  </h5>
                                  <ul className="text-sm space-y-1">
                                    {option.cons.map((con: string, i: number) => (
                                      <li key={i} className="flex items-start gap-2">
                                        <span className="text-orange-600 dark:text-orange-500 mt-0.5">!</span>
                                        <span className="text-gray-700 dark:text-gray-300">{con}</span>
                                      </li>
                                    ))}
                                  </ul>
                                </div>
                              )}

                              {/* Personalization Note */}
                              {option.personalization_note && (
                                <div className="bg-purple-50 dark:bg-purple-950 p-3 rounded text-sm border border-purple-200 dark:border-purple-800">
                                  <p className="text-purple-900 dark:text-purple-100">
                                    <span className="font-medium">Personalization: </span>
                                    {option.personalization_note}
                                  </p>
                                </div>
                              )}
                            </CardContent>
                          </Card>
                        ))}
                      </div>
                    </CardContent>
                  </Card>
                </div>
              )}

              {copilotResult && copilotResult.message && !copilotResult.ai_guidance && (
                <div className="bg-yellow-50 dark:bg-yellow-950 p-4 rounded-lg border border-yellow-200 dark:border-yellow-800">
                  <p className="text-yellow-900 dark:text-yellow-100">{copilotResult.message}</p>
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  )
}
