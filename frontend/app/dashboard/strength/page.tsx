'use client'

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { apiClient } from '@/lib/api'
import { Button } from '@/components/ui/button'
import { Label } from '@/components/ui/label'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Sparkles, Award, TrendingUp, TrendingDown, Info } from '@/components/icons'

interface Profile {
  id: string
  name: string
  is_primary?: boolean
}

interface PlanetStrength {
  planet: string
  total_strength: number
  required_minimum: number
  percentage_of_required: number
  rating: string
  components?: Array<{
    name: string
    value: number
    description: string
  }>
}

const STRENGTH_COLORS: Record<string, string> = {
  'Exceptional': 'bg-green-600',
  'Strong': 'bg-blue-600',
  'Average': 'bg-yellow-600',
  'Weak': 'bg-orange-600',
  'Very Weak': 'bg-red-600',
}

const STRENGTH_TEXT_COLORS: Record<string, string> = {
  'Exceptional': 'text-green-800',
  'Strong': 'text-blue-800',
  'Average': 'text-yellow-800',
  'Weak': 'text-orange-800',
  'Very Weak': 'text-red-800',
}

export default function PlanetaryStrengthPage() {
  const router = useRouter()
  const [profiles, setProfiles] = useState<Profile[]>([])
  const [selectedProfile, setSelectedProfile] = useState('')
  const [loading, setLoading] = useState(true)
  const [calculating, setCalculating] = useState(false)
  const [error, setError] = useState('')
  const [planetStrengths, setPlanetStrengths] = useState<PlanetStrength[]>([])

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
    console.log('🎯 Shadbala: handleCalculate called')
    console.log('🎯 Selected profile:', selectedProfile)

    if (!selectedProfile) {
      setError('Please select a birth profile')
      return
    }

    setError('')
    setCalculating(true)
    setPlanetStrengths([])

    try {
      // Use new profile-based API (automatically fetches chart)
      const response = await apiClient.calculateShadbalaForProfile({
        profile_id: selectedProfile,
        include_breakdown: true,
        comparison: true,
      })
      console.log('🎯 Shadbala: Response received:', response)

      const strengths = response.data.planetary_strengths || []
      console.log('🎯 Shadbala: Planet strengths:', strengths)
      setPlanetStrengths(strengths)
    } catch (err: any) {
      console.error('Failed to calculate strength:', err)
      setError(err.message || 'Failed to calculate planetary strength. Please try again.')
    } finally {
      setCalculating(false)
    }
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
            You need to create a birth profile to calculate planetary strength
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
        <h1 className="text-3xl font-bold text-gray-900">Planetary Strength (Shadbala)</h1>
        <p className="text-gray-600 mt-2">
          Six-fold analysis of planetary strength in your birth chart
        </p>
      </div>

      {/* Configuration */}
      <Card>
        <CardHeader>
          <CardTitle>Calculate Shadbala</CardTitle>
          <CardDescription>Select profile to analyze planetary strength</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          {error && (
            <div className="p-3 text-sm text-red-600 bg-red-50 rounded-md border border-red-200">
              {error}
            </div>
          )}

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

          <Button
            onClick={handleCalculate}
            className="w-full"
            disabled={calculating || !selectedProfile}
            size="lg"
          >
            {calculating ? (
              <>
                <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin mr-2"></div>
                Calculating Shadbala...
              </>
            ) : (
              <>
                <Award className="w-5 h-5 mr-2" />
                Calculate Planetary Strength
              </>
            )}
          </Button>
        </CardContent>
      </Card>

      {/* Results */}
      {planetStrengths.length > 0 && (
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="text-2xl font-bold text-gray-900">Planetary Strength Analysis</h2>
            <p className="text-sm text-gray-600">{planetStrengths.length} planets analyzed</p>
          </div>

          {/* Strength Cards */}
          {planetStrengths.map((strength, index) => (
            <Card key={index} className="border-l-4" style={{ borderLeftColor: STRENGTH_COLORS[strength.rating]?.replace('bg-', '') }}>
              <CardHeader>
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <CardTitle className="text-xl">{strength.planet}</CardTitle>
                    <div className="flex items-center gap-3 mt-2">
                      <span className={`inline-flex items-center px-3 py-1 rounded-full text-sm font-semibold ${STRENGTH_COLORS[strength.rating]} text-white`}>
                        {strength.rating}
                      </span>
                      <span className="text-sm text-gray-600">
                        {(strength.percentage_of_required ?? 0).toFixed(0)}% of required strength
                      </span>
                    </div>
                  </div>
                  <div className="text-right">
                    <p className="text-2xl font-bold text-gray-900">{(strength.total_strength ?? 0).toFixed(0)}</p>
                    <p className="text-xs text-gray-600">Required: {strength.required_minimum ?? 0}</p>
                  </div>
                </div>
              </CardHeader>
              <CardContent>
                {/* Progress Bar */}
                <div className="mb-4">
                  <div className="w-full bg-gray-200 rounded-full h-2.5">
                    <div
                      className={`h-2.5 rounded-full ${STRENGTH_COLORS[strength.rating]}`}
                      style={{ width: `${Math.min(strength.percentage_of_required ?? 0, 100)}%` }}
                    ></div>
                  </div>
                </div>

                {/* Component Breakdown */}
                {strength.components && strength.components.length > 0 && (
                  <div className="space-y-2">
                    <p className="text-sm font-semibold text-gray-700 mb-3">Six-Fold Strength Components:</p>
                    <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
                      {strength.components.map((component, idx) => (
                        <div key={idx} className="p-3 bg-gray-50 rounded border border-gray-200">
                          <p className="text-xs font-semibold text-gray-700">{component.name}</p>
                          <p className="text-lg font-bold text-gray-900">{(component.value ?? 0).toFixed(0)}</p>
                          <p className="text-xs text-gray-500">{component.description}</p>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </CardContent>
            </Card>
          ))}

          {/* Summary */}
          <Card className="bg-gradient-to-r from-jio-50 to-blue-50">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Info className="w-5 h-5" />
                Strength Summary
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="text-center p-4 bg-white rounded-lg">
                  <TrendingUp className="w-8 h-8 text-green-600 mx-auto mb-2" />
                  <p className="text-sm text-gray-600">Strongest Planet</p>
                  <p className="text-lg font-bold text-gray-900">
                    {[...planetStrengths].sort((a, b) => (b.percentage_of_required ?? 0) - (a.percentage_of_required ?? 0))[0]?.planet}
                  </p>
                  <p className="text-xs text-gray-600">
                    {([...planetStrengths].sort((a, b) => (b.percentage_of_required ?? 0) - (a.percentage_of_required ?? 0))[0]?.percentage_of_required ?? 0).toFixed(0)}% strength
                  </p>
                </div>
                <div className="text-center p-4 bg-white rounded-lg">
                  <TrendingDown className="w-8 h-8 text-red-600 mx-auto mb-2" />
                  <p className="text-sm text-gray-600">Weakest Planet</p>
                  <p className="text-lg font-bold text-gray-900">
                    {[...planetStrengths].sort((a, b) => (a.percentage_of_required ?? 0) - (b.percentage_of_required ?? 0))[0]?.planet}
                  </p>
                  <p className="text-xs text-gray-600">
                    {([...planetStrengths].sort((a, b) => (a.percentage_of_required ?? 0) - (b.percentage_of_required ?? 0))[0]?.percentage_of_required ?? 0).toFixed(0)}% strength
                  </p>
                </div>
                <div className="text-center p-4 bg-white rounded-lg">
                  <Award className="w-8 h-8 text-blue-600 mx-auto mb-2" />
                  <p className="text-sm text-gray-600">Average Strength</p>
                  <p className="text-lg font-bold text-gray-900">
                    {(planetStrengths.reduce((sum, p) => sum + (p.percentage_of_required ?? 0), 0) / planetStrengths.length).toFixed(0)}%
                  </p>
                  <p className="text-xs text-gray-600">
                    across {planetStrengths.length} planets
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Info Box */}
      <div className="p-4 bg-blue-50 border border-blue-200 rounded-lg">
        <h4 className="font-semibold text-blue-900 mb-2">What is Shadbala?</h4>
        <p className="text-sm text-blue-800 mb-3">
          Shadbala (six-fold strength) is a comprehensive system in Vedic astrology for measuring planetary strength:
        </p>
        <ul className="text-sm text-blue-800 space-y-1 list-disc list-inside">
          <li><strong>Sthana Bala:</strong> Strength from sign, house, exaltation/debilitation</li>
          <li><strong>Dig Bala:</strong> Strength from directional positioning</li>
          <li><strong>Kala Bala:</strong> Strength from time factors (day/night, ayana, etc.)</li>
          <li><strong>Chesta Bala:</strong> Strength from motion (direct/retrograde)</li>
          <li><strong>Naisargika Bala:</strong> Natural strength of the planet</li>
          <li><strong>Drik Bala:</strong> Strength from aspects received</li>
        </ul>
      </div>
    </div>
  )
}
