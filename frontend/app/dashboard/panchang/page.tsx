'use client'

import { useState, useEffect } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Badge } from '@/components/ui/badge'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Calendar, MapPin, Sun, Moon, Clock, AlertTriangle, Sparkles, Star, CloudMoon } from '@/components/icons'
import { apiClient } from '@/lib/api'
import { format } from 'date-fns'

interface TithiInfo {
  tithi_name: string
  tithi_number: number
  paksha: string
  start_time: string
  end_time: string
  tithi_quality: string
}

interface NakshatraInfo {
  nakshatra_name: string
  nakshatra_number: number
  pada: number
  ruling_deity: string
  ruling_planet: string
  start_time: string
  end_time: string
}

interface SunMoonData {
  sunrise: string
  sunset: string
  moonrise?: string
  moonset?: string
  moon_phase: string
  moon_illumination: number
}

interface HoraInfo {
  planet: string
  start_time: string
  end_time: string
  is_favorable: boolean
}

interface InauspiciousTime {
  name: string
  start_time: string
  end_time: string
  description: string
}

interface AuspiciousTime {
  name: string
  start_time: string
  end_time: string
  description: string
}

interface Panchang {
  panchang_date: string
  location_name?: string
  tithi: TithiInfo
  nakshatra: NakshatraInfo
  yoga: {
    yoga_name: string
    yoga_number: number
  }
  karana: {
    karana_name: string
    karana_number: number
  }
  vara: {
    day_name: string
    ruling_planet: string
  }
  sun_moon: SunMoonData
  rahukaal_start: string
  rahukaal_end: string
  abhijit_muhurta_start?: string
  abhijit_muhurta_end?: string
  brahma_muhurta_start?: string
  brahma_muhurta_end?: string
  dur_muhurtam: InauspiciousTime[]
  hora_sequence: HoraInfo[]
  special_days: string[]
  ritu: string
  is_auspicious_day: boolean
}

const TIMEZONES = [
  { value: 'Asia/Kolkata', label: 'India (IST)' },
  { value: 'America/New_York', label: 'New York (EST)' },
  { value: 'America/Los_Angeles', label: 'Los Angeles (PST)' },
  { value: 'Europe/London', label: 'London (GMT)' },
  { value: 'Asia/Dubai', label: 'Dubai (GST)' },
  { value: 'Asia/Singapore', label: 'Singapore (SGT)' }
]

export default function PanchangPage() {
  const [panchang, setPanchang] = useState<Panchang | null>(null)
  const [loading, setLoading] = useState(false)
  const [selectedDate, setSelectedDate] = useState(format(new Date(), 'yyyy-MM-dd'))
  const [location, setLocation] = useState({
    latitude: 28.6139,
    longitude: 77.2090,
    timezone: 'Asia/Kolkata',
    location_name: 'New Delhi'
  })
  const [activeTab, setActiveTab] = useState('today')

  useEffect(() => {
    loadPanchang()
  }, [selectedDate, location])

  const loadPanchang = async () => {
    setLoading(true)
    try {
      const response = await apiClient.post('/panchang/calculate', {
        panchang_date: selectedDate,
        ...location
      })
      setPanchang(response.data)
    } catch (error) {
      console.error('Failed to load panchang:', error)
    } finally {
      setLoading(false)
    }
  }

  const getCurrentLocation = () => {
    if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(
        (position) => {
          setLocation({
            ...location,
            latitude: position.coords.latitude,
            longitude: position.coords.longitude,
            location_name: 'Current Location'
          })
        },
        (error) => {
          console.error('Geolocation error:', error)
        }
      )
    }
  }

  const getPakshaColor = (paksha: string) => {
    return paksha === 'Shukla' ? 'bg-yellow-500' : 'bg-blue-500'
  }

  const getMoonPhaseIcon = (phase: string) => {
    if (phase.includes('Full')) return '🌕'
    if (phase.includes('New')) return '🌑'
    if (phase.includes('Waxing Crescent')) return '🌒'
    if (phase.includes('Waxing Gibbous')) return '🌔'
    if (phase.includes('Waning Gibbous')) return '🌖'
    if (phase.includes('Waning Crescent')) return '🌘'
    return '🌓'
  }

  return (
    <div className="container mx-auto p-6 space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold mb-2">Hyperlocal Panchang</h1>
        <p className="text-muted-foreground">
          Daily Vedic calendar with auspicious timings personalized for your location
        </p>
      </div>

      {/* Location & Date Selector */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <MapPin className="h-5 w-5" />
            Location & Date
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <Label>Date</Label>
              <Input
                type="date"
                value={selectedDate}
                onChange={(e) => setSelectedDate(e.target.value)}
              />
            </div>

            <div>
              <Label>Timezone</Label>
              <Select value={location.timezone} onValueChange={(value) => setLocation({ ...location, timezone: value })}>
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  {TIMEZONES.map(tz => (
                    <SelectItem key={tz.value} value={tz.value}>
                      {tz.label}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            <div>
              <Label>Latitude</Label>
              <Input
                type="number"
                step="0.0001"
                value={location.latitude}
                onChange={(e) => setLocation({ ...location, latitude: parseFloat(e.target.value) })}
              />
            </div>

            <div>
              <Label>Longitude</Label>
              <Input
                type="number"
                step="0.0001"
                value={location.longitude}
                onChange={(e) => setLocation({ ...location, longitude: parseFloat(e.target.value) })}
              />
            </div>
          </div>

          <div className="flex gap-2">
            <Button onClick={getCurrentLocation} variant="outline">
              <MapPin className="h-4 w-4 mr-2" />
              Use Current Location
            </Button>
            <Button onClick={loadPanchang}>
              Calculate Panchang
            </Button>
          </div>
        </CardContent>
      </Card>

      {panchang && !loading && (() => {
        // Build auspicious times array from flat fields
        const auspicious_times: AuspiciousTime[] = []
        if (panchang.abhijit_muhurta_start && panchang.abhijit_muhurta_end) {
          auspicious_times.push({
            name: 'Abhijit Muhurta',
            start_time: panchang.abhijit_muhurta_start,
            end_time: panchang.abhijit_muhurta_end,
            description: 'Most auspicious time for all activities'
          })
        }
        if (panchang.brahma_muhurta_start && panchang.brahma_muhurta_end) {
          auspicious_times.push({
            name: 'Brahma Muhurta',
            start_time: panchang.brahma_muhurta_start,
            end_time: panchang.brahma_muhurta_end,
            description: 'Best time for meditation and spiritual practices'
          })
        }

        // Use dur_muhurtam for inauspicious times
        const inauspicious_times = panchang.dur_muhurtam || []

        return (
        <Tabs value={activeTab} onValueChange={setActiveTab}>
          <TabsList className="grid w-full grid-cols-3">
            <TabsTrigger value="today">Day's Panchang</TabsTrigger>
            <TabsTrigger value="times">Auspicious Times</TabsTrigger>
            <TabsTrigger value="hora">Hora (Planetary Hours)</TabsTrigger>
          </TabsList>

          {/* Day's Panchang Tab */}
          <TabsContent value="today" className="space-y-6">
            {/* Special Days Banner */}
            {panchang.special_days.length > 0 && (
              <Card className="bg-gradient-to-r from-yellow-500/10 to-orange-500/10 border-yellow-500/20">
                <CardContent className="p-4">
                  <div className="flex items-center gap-3">
                    <Star className="h-6 w-6 text-yellow-500 fill-yellow-500" />
                    <div>
                      <div className="font-semibold">Special Day</div>
                      <div className="text-sm">{panchang.special_days.join(', ')}</div>
                    </div>
                  </div>
                </CardContent>
              </Card>
            )}

            {/* Sun & Moon */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Sun className="h-5 w-5 text-orange-500" />
                    Sun Times
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-2">
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">Sunrise</span>
                    <span className="font-medium">{panchang.sun_moon.sunrise}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">Sunset</span>
                    <span className="font-medium">{panchang.sun_moon.sunset}</span>
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Moon className="h-5 w-5 text-blue-500" />
                    Moon Times
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-2">
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">Phase</span>
                    <span className="font-medium">
                      {getMoonPhaseIcon(panchang.sun_moon.moon_phase)} {panchang.sun_moon.moon_phase}
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">Illumination</span>
                    <span className="font-medium">{Math.round(panchang.sun_moon.moon_illumination)}%</span>
                  </div>
                  {panchang.sun_moon.moonrise && (
                    <div className="flex justify-between">
                      <span className="text-muted-foreground">Moonrise</span>
                      <span className="font-medium">{panchang.sun_moon.moonrise}</span>
                    </div>
                  )}
                </CardContent>
              </Card>
            </div>

            {/* Panchang Elements */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
              <Card>
                <CardHeader>
                  <CardTitle className="text-sm">Tithi</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-2">
                    <div className="flex items-center gap-2">
                      <Badge className={getPakshaColor(panchang.tithi.paksha)}>
                        {panchang.tithi.paksha} Paksha
                      </Badge>
                    </div>
                    <div className="font-semibold text-lg">{panchang.tithi.tithi_name}</div>
                    <div className="text-sm text-muted-foreground">
                      {panchang.tithi.start_time} - {panchang.tithi.end_time}
                    </div>
                    <div className="text-xs text-muted-foreground">{panchang.tithi.tithi_quality}</div>
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle className="text-sm">Nakshatra</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-2">
                    <div className="font-semibold text-lg">{panchang.nakshatra.nakshatra_name}</div>
                    <div className="text-sm">Pada {panchang.nakshatra.pada}</div>
                    <div className="text-sm text-muted-foreground">
                      Lord: {panchang.nakshatra.ruling_planet}
                    </div>
                    <div className="text-xs text-muted-foreground">
                      Deity: {panchang.nakshatra.ruling_deity}
                    </div>
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle className="text-sm">Yoga</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="font-semibold text-lg">{panchang.yoga.yoga_name}</div>
                  <div className="text-sm text-muted-foreground">#{panchang.yoga.yoga_number}</div>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle className="text-sm">Karana</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="font-semibold text-lg">{panchang.karana.karana_name}</div>
                  <div className="text-sm text-muted-foreground">#{panchang.karana.karana_number}</div>
                </CardContent>
              </Card>
            </div>

            {/* Vara & Ritu */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <Card>
                <CardHeader>
                  <CardTitle>Vara (Weekday)</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="flex items-center justify-between">
                    <div>
                      <div className="font-semibold text-lg">{panchang.vara.day_name}</div>
                      <div className="text-sm text-muted-foreground">
                        Ruled by {panchang.vara.ruling_planet}
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle>Season</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="font-semibold text-lg">{panchang.ritu}</div>
                </CardContent>
              </Card>
            </div>
          </TabsContent>

          {/* Auspicious Times Tab */}
          <TabsContent value="times" className="space-y-6">
            {/* Rahukaal Warning */}
            <Card className="bg-red-500/10 border-red-500/20">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <AlertTriangle className="h-5 w-5 text-red-500" />
                  Rahukaal (Inauspicious)
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-lg font-semibold">
                  {panchang.rahukaal_start} - {panchang.rahukaal_end}
                </div>
                <div className="text-sm text-muted-foreground mt-2">
                  Avoid starting new ventures during this period
                </div>
              </CardContent>
            </Card>

            {/* Auspicious Times */}
            {auspicious_times.length > 0 && (
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Sparkles className="h-5 w-5 text-green-500" />
                    Auspicious Times
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-3">
                    {auspicious_times.map((time, index) => (
                      <div key={index} className="flex items-start justify-between p-3 bg-green-500/10 rounded-lg border border-green-500/20">
                        <div>
                          <div className="font-medium">{time.name}</div>
                          <div className="text-sm text-muted-foreground">{time.description}</div>
                        </div>
                        <div className="text-sm font-medium">
                          {time.start_time} - {time.end_time}
                        </div>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            )}

            {/* Inauspicious Times */}
            {inauspicious_times.length > 0 && (
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <AlertTriangle className="h-5 w-5 text-orange-500" />
                    Other Inauspicious Times
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-3">
                    {inauspicious_times.map((time, index) => (
                      <div key={index} className="flex items-start justify-between p-3 bg-orange-500/10 rounded-lg border border-orange-500/20">
                        <div>
                          <div className="font-medium">{time.name}</div>
                          <div className="text-sm text-muted-foreground">{time.description}</div>
                        </div>
                        <div className="text-sm font-medium">
                          {time.start_time} - {time.end_time}
                        </div>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            )}
          </TabsContent>

          {/* Hora Tab */}
          <TabsContent value="hora" className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Clock className="h-5 w-5" />
                  24-Hour Planetary Hora Sequence
                </CardTitle>
                <CardDescription>
                  Each hour is ruled by a different planet, influencing activities during that time
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
                  {panchang.hora_sequence.map((hora, index) => (
                    <div
                      key={index}
                      className={`p-3 rounded-lg border ${
                        hora.is_favorable
                          ? 'bg-green-500/10 border-green-500/20'
                          : 'bg-gray-500/10 border-gray-500/20'
                      }`}
                    >
                      <div className="flex items-center justify-between">
                        <div>
                          <div className="font-medium">{hora.planet}</div>
                          <div className="text-xs text-muted-foreground">
                            {hora.start_time} - {hora.end_time}
                          </div>
                        </div>
                        {hora.is_favorable && (
                          <Sparkles className="h-4 w-4 text-green-500" />
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
        )
      })()}

      {loading && (
        <Card>
          <CardContent className="p-12 text-center">
            <div className="text-muted-foreground">Loading Panchang...</div>
          </CardContent>
        </Card>
      )}
    </div>
  )
}
