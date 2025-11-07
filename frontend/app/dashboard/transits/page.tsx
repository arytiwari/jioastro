'use client'

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { apiClient } from '@/lib/api'
import { Button } from '@/components/ui/button'
import { Label } from '@/components/ui/label'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Sparkles, Sun, Calendar, TrendingUp, AlertCircle, Home, Clock, RefreshCw } from '@/components/icons'
import { formatDate } from '@/lib/utils'

interface Profile {
  id: string
  name: string
  is_primary?: boolean
}

interface TransitData {
  transit_planets: Record<string, any>
  significant_aspects: any[]
  house_transits: any[]
  upcoming_sign_changes: any[]
  interpretation?: string
}

const ASPECT_COLORS: Record<string, string> = {
  conjunction: 'bg-purple-100 text-purple-800',
  opposition: 'bg-red-100 text-red-800',
  trine: 'bg-green-100 text-green-800',
  square: 'bg-orange-100 text-orange-800',
  sextile: 'bg-blue-100 text-blue-800',
}

export default function TransitsPage() {
  const router = useRouter()
  const [profiles, setProfiles] = useState<Profile[]>([])
  const [selectedProfile, setSelectedProfile] = useState('')
  const [loading, setLoading] = useState(true)
  const [calculating, setCalculating] = useState(false)
  const [error, setError] = useState('')
  const [transitData, setTransitData] = useState<TransitData | null>(null)
  const [currentDate, setCurrentDate] = useState(new Date().toISOString().split('T')[0])

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

  const handleCalculate = async () => {
    console.log('🎯 Transits: handleCalculate called')
    console.log('🎯 Selected profile:', selectedProfile)

    if (!selectedProfile) {
      setError('Please select a birth profile')
      return
    }

    setError('')
    setCalculating(true)
    setTransitData(null)

    try {
      // Use new profile-based API (automatically fetches chart)
      const response = await apiClient.getCurrentTransitsForProfile({
        profile_id: selectedProfile,
        transit_date: currentDate ? `${currentDate}T12:00:00` : undefined,
        include_timeline: true,
      })
      console.log('🎯 Transits: Response received:', response)
      setTransitData(response.data)
    } catch (err: any) {
      console.error('Failed to calculate transits:', err)
      setError(err.message || 'Failed to calculate transits. Please try again.')
    } finally {
      setCalculating(false)
    }
  }

  const handleToday = () => {
    setCurrentDate(new Date().toISOString().split('T')[0])
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
            You need to create a birth profile to view transits
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
        <h1 className="text-3xl font-bold text-gray-900">Planetary Transits</h1>
        <p className="text-gray-600 mt-2">
          View current planetary positions and their aspects to your birth chart
        </p>
      </div>

      {/* Configuration */}
      <Card>
        <CardHeader>
          <CardTitle>Calculate Transits</CardTitle>
          <CardDescription>Select profile and date to view current transits</CardDescription>
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

            <div className="space-y-2">
              <Label htmlFor="date">Transit Date</Label>
              <div className="flex gap-2">
                <input
                  id="date"
                  type="date"
                  value={currentDate}
                  onChange={(e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => setCurrentDate(e.target.value)}
                  className="flex-1 px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-jio-500"
                />
                <Button variant="outline" size="sm" onClick={handleToday}>
                  Today
                </Button>
              </div>
            </div>
          </div>

          <Button
            onClick={handleCalculate}
            className="w-full"
            disabled={calculating || !selectedProfile}
            size="lg"
          >
            {calculating ? (
              <>
                <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin mr-2"></div>
                Calculating Transits...
              </>
            ) : (
              <>
                <RefreshCw className="w-5 h-5 mr-2" />
                Calculate Transits
              </>
            )}
          </Button>
        </CardContent>
      </Card>

      {/* Transit Results */}
      {transitData && (
        <div className="space-y-6">
          {/* Current Planetary Positions */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Sun className="w-5 h-5 text-yellow-600" />
                Current Planetary Positions
              </CardTitle>
              <CardDescription>
                Planetary positions on {new Date(currentDate).toLocaleDateString()}
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
                {Object.entries(transitData.transit_planets).map(([planet, data]: [string, any]) => (
                  <div key={planet} className="p-3 border rounded-lg">
                    <div className="flex items-center justify-between mb-1">
                      <p className="font-semibold text-gray-900">{planet}</p>
                      <span className="text-xs text-gray-600">{data.sign}</span>
                    </div>
                    <p className="text-sm text-gray-600">
                      {data.degree?.toFixed(2)}° {data.sign}
                    </p>
                    {data.is_retrograde && (
                      <span className="inline-block mt-1 text-xs px-2 py-0.5 bg-red-100 text-red-700 rounded">
                        Retrograde
                      </span>
                    )}
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>

          {/* Significant Aspects */}
          {transitData.significant_aspects && transitData.significant_aspects.length > 0 && (
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <TrendingUp className="w-5 h-5 text-blue-600" />
                  Significant Aspects
                </CardTitle>
                <CardDescription>
                  Current transiting planets forming aspects to natal planets
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  {transitData.significant_aspects.map((aspect: any, index: number) => (
                    <div key={index} className="p-4 border rounded-lg">
                      <div className="flex items-start justify-between mb-2">
                        <div>
                          <p className="font-semibold text-gray-900">
                            Transit {aspect.transit_planet} {aspect.aspect_type} Natal {aspect.natal_planet}
                          </p>
                          <p className="text-sm text-gray-600 mt-1">
                            Orb: {aspect.orb?.toFixed(2)}° • Strength: {(aspect.strength * 100).toFixed(0)}%
                          </p>
                        </div>
                        <span className={`text-xs font-medium px-2 py-1 rounded ${ASPECT_COLORS[aspect.aspect_type]}`}>
                          {aspect.aspect_type}
                        </span>
                      </div>
                      {aspect.interpretation && (
                        <p className="text-sm text-gray-700 mt-2">{aspect.interpretation}</p>
                      )}
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          )}

          {/* House Transits */}
          {transitData.house_transits && transitData.house_transits.length > 0 && (
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Home className="w-5 h-5 text-green-600" />
                  House Transits
                </CardTitle>
                <CardDescription>
                  Planets transiting through your birth chart houses
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                  {transitData.house_transits.map((transit: any, index: number) => (
                    <div key={index} className="p-3 border rounded-lg">
                      <p className="font-semibold text-gray-900">
                        {transit.planet} in House {transit.house}
                      </p>
                      <p className="text-sm text-gray-600 mt-1">
                        {transit.interpretation || `${transit.planet} is currently transiting your ${transit.house}th house`}
                      </p>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          )}

          {/* Upcoming Sign Changes */}
          {transitData.upcoming_sign_changes && transitData.upcoming_sign_changes.length > 0 && (
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Calendar className="w-5 h-5 text-purple-600" />
                  Upcoming Sign Changes
                </CardTitle>
                <CardDescription>
                  Planetary sign changes in the next 30 days
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-2">
                  {transitData.upcoming_sign_changes.map((change: any, index: number) => (
                    <div key={index} className="flex items-center justify-between p-3 border rounded-lg">
                      <div>
                        <p className="font-semibold text-gray-900">
                          {change.planet}: {change.from_sign} → {change.to_sign}
                        </p>
                        {change.interpretation && (
                          <p className="text-xs text-gray-600 mt-1">{change.interpretation}</p>
                        )}
                      </div>
                      <div className="text-right">
                        <p className="text-sm font-medium text-gray-900">
                          {new Date(change.date).toLocaleDateString()}
                        </p>
                        <p className="text-xs text-gray-600">
                          {Math.ceil((new Date(change.date).getTime() - new Date().getTime()) / (1000 * 60 * 60 * 24))} days
                        </p>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          )}

          {/* Overall Interpretation */}
          {transitData.interpretation && (
            <Card className="border-2 border-jio-200 bg-jio-50">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Sparkles className="w-5 h-5 text-jio-600" />
                  Overall Transit Interpretation
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="prose prose-sm max-w-none">
                  <p className="text-gray-700 leading-relaxed whitespace-pre-wrap">
                    {transitData.interpretation}
                  </p>
                </div>
              </CardContent>
            </Card>
          )}
        </div>
      )}

      {/* Info Box */}
      <div className="p-4 bg-blue-50 border border-blue-200 rounded-lg">
        <h4 className="font-semibold text-blue-900 mb-2 flex items-center gap-2">
          <AlertCircle className="w-4 h-4" />
          About Transits
        </h4>
        <p className="text-sm text-blue-800">
          Transits show how current planetary positions interact with your birth chart.
          Significant aspects can indicate important periods for action, reflection, or caution in various life areas.
        </p>
      </div>
    </div>
  )
}
