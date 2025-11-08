'use client'

import { useState, useEffect } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Zap, CheckCircle, Clock, MapPin, User as UserIcon, Calendar as CalendarIcon, ArrowRight, LogIn } from '@/components/icons'
import { apiClient } from '@/lib/api'
import { CityAutocomplete } from '@/components/CityAutocomplete'
import { ChartSelector } from '@/components/chart/ChartSelector'
import { EnhancedDashaTimeline } from '@/components/chart/EnhancedDashaTimeline'
import { YogaDisplay } from '@/components/chart/YogaDisplay'
import Link from 'next/link'

interface ChartData {
  profile_id: string
  name: string
  birth_date?: string
  generated_at: string
  summary: {
    planets: Record<string, any>
    houses: any[]
    ascendant: any
  }
}

export default function InstantOnboardingPage() {
  const [step, setStep] = useState<'form' | 'generating' | 'result'>('form')
  const [formData, setFormData] = useState({
    name: '',
    gender: '',
    birth_date: '',
    birth_time: '',
    birth_place: '',
    latitude: '',
    longitude: ''
  })
  const [chartData, setChartData] = useState<ChartData | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [generating, setGenerating] = useState(false)
  const [isAuthenticated, setIsAuthenticated] = useState(false)
  const [showSavePrompt, setShowSavePrompt] = useState(false)
  const [isSavingProfile, setIsSavingProfile] = useState(false)
  const [profileSaved, setProfileSaved] = useState(false)

  // Check authentication status and restore saved data on mount
  useEffect(() => {
    const checkAuth = async () => {
      try {
        // Load token from Supabase session
        await apiClient.loadToken()

        // Import getSession to check if user is actually authenticated
        const { getSession } = await import('@/lib/supabase')
        const session = getSession()

        // Only set authenticated if there's a valid session with access token
        if (session && session.access_token) {
          setIsAuthenticated(true)
        } else {
          setIsAuthenticated(false)
        }
      } catch (error) {
        console.log('Auth check failed:', error)
        setIsAuthenticated(false)
      }
    }

    // Restore saved chart data from localStorage if it exists
    const restoreSavedData = () => {
      try {
        const savedData = localStorage.getItem('instant_onboarding_data')
        if (savedData) {
          const { formData: savedFormData, chartData: savedChartData, timestamp } = JSON.parse(savedData)

          // Only restore if data is less than 1 hour old
          const oneHour = 60 * 60 * 1000
          if (Date.now() - timestamp < oneHour) {
            setFormData(savedFormData)
            if (savedChartData) {
              setChartData(savedChartData)
              setStep('result')
            }
            console.log('✅ Restored saved chart data from localStorage')
          } else {
            // Clear expired data
            localStorage.removeItem('instant_onboarding_data')
          }
        }
      } catch (error) {
        console.error('Failed to restore saved data:', error)
        localStorage.removeItem('instant_onboarding_data')
      }
    }

    checkAuth()
    restoreSavedData()
  }, [])

  const handleInputChange = (field: string, value: string) => {
    setFormData(prev => ({ ...prev, [field]: value }))
    setError(null)
  }

  const handleCitySelect = (city: { id: number; name: string; state: string; latitude: number; longitude: number; display_name: string }) => {
    setFormData(prev => ({
      ...prev,
      birth_place: city.display_name,
      latitude: city.latitude.toString(),
      longitude: city.longitude.toString(),
    }))
  }

  const validateForm = () => {
    if (!formData.name.trim()) return 'Name is required'
    if (!formData.birth_date) return 'Birth date is required'
    if (!formData.birth_time) return 'Birth time is required'
    if (!formData.birth_place.trim()) return 'Birth place is required'
    if (!formData.latitude || !formData.longitude) return 'Please select a city from the dropdown'
    return null
  }

  const generateQuickChart = async () => {
    const validationError = validateForm()
    if (validationError) {
      setError(validationError)
      return
    }

    setGenerating(true)
    setError(null)
    setStep('generating')

    try {
      // Ensure token is loaded for authenticated users
      if (isAuthenticated) {
        await apiClient.loadToken()
      }

      const response = await apiClient.post('/api/v2/instant-onboarding/quick-chart', {
        name: formData.name,
        gender: formData.gender || undefined, // Send undefined if empty to omit from request
        birth_date: formData.birth_date,
        birth_time: formData.birth_time + ':00', // Add seconds to match HH:MM:SS format
        birth_place: formData.birth_place,
        latitude: parseFloat(formData.latitude),
        longitude: parseFloat(formData.longitude),
        timezone: 'Asia/Kolkata' // Use timezone string instead of offset
      })

      setChartData(response.data)
      setStep('result')

      // Save to localStorage for persistence across login flow
      localStorage.setItem('instant_onboarding_data', JSON.stringify({
        formData,
        chartData: response.data,
        timestamp: Date.now()
      }))
      console.log('✅ Saved chart data to localStorage')

      // Show save prompt for authenticated users
      if (isAuthenticated) {
        setShowSavePrompt(true)
      }
    } catch (error: any) {
      console.error('Error generating chart:', error)
      setError(error.response?.data?.detail || 'Failed to generate chart. Please try again.')
      setStep('form')
    } finally {
      setGenerating(false)
    }
  }

  // Save data to localStorage before navigating to login
  const handleLoginRedirect = () => {
    if (chartData) {
      localStorage.setItem('instant_onboarding_data', JSON.stringify({
        formData,
        chartData,
        timestamp: Date.now()
      }))
      console.log('✅ Saved chart data before login redirect')
    }
  }

  // Save profile to database
  const saveProfileToDatabase = async () => {
    setIsSavingProfile(true)
    try {
      await apiClient.loadToken()

      const profileData = {
        name: formData.name,
        gender: formData.gender || undefined, // Send undefined if empty to omit from request
        birth_date: formData.birth_date,
        birth_time: formData.birth_time + ':00',
        birth_lat: parseFloat(formData.latitude),
        birth_lon: parseFloat(formData.longitude),
        birth_city: formData.birth_place,
        birth_timezone: 'Asia/Kolkata',
        is_primary: false
      }

      await apiClient.createProfile(profileData)
      setProfileSaved(true)
      setShowSavePrompt(false)
      console.log('✅ Profile saved successfully')

      // Clear localStorage after successful save
      localStorage.removeItem('instant_onboarding_data')
    } catch (error: any) {
      console.error('Error saving profile:', error)
      setError(error.response?.data?.detail || 'Failed to save profile. Please try again.')
    } finally {
      setIsSavingProfile(false)
    }
  }

  const resetForm = () => {
    setStep('form')
    setFormData({
      name: '',
      gender: '',
      birth_date: '',
      birth_time: '',
      birth_place: '',
      latitude: '',
      longitude: ''
    })
    setChartData(null)
    setError(null)
  }

  return (
    <div className="container mx-auto px-4 py-8">
      {/* Header */}
      <div className="mb-8">
        <div className="flex items-center gap-3 mb-2">
          <div className="p-2 bg-blue-100 rounded-lg">
            <Zap className="w-6 h-6 text-blue-600" />
          </div>
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Instant Onboarding</h1>
            <p className="text-gray-600">Get your birth chart in 90 seconds</p>
          </div>
        </div>
      </div>

      {/* Progress Steps */}
      <div className="mb-8 flex items-center justify-center gap-4">
        <div className={`flex items-center gap-2 ${step === 'form' ? 'text-blue-600' : step !== 'form' ? 'text-green-600' : 'text-gray-400'}`}>
          <div className={`w-8 h-8 rounded-full flex items-center justify-center ${step === 'form' ? 'bg-blue-100' : step !== 'form' ? 'bg-green-100' : 'bg-gray-100'}`}>
            {step !== 'form' ? <CheckCircle className="w-5 h-5" /> : '1'}
          </div>
          <span className="font-medium">Enter Details</span>
        </div>
        <div className="w-12 h-0.5 bg-gray-300"></div>
        <div className={`flex items-center gap-2 ${step === 'generating' ? 'text-blue-600' : step === 'result' ? 'text-green-600' : 'text-gray-400'}`}>
          <div className={`w-8 h-8 rounded-full flex items-center justify-center ${step === 'generating' ? 'bg-blue-100' : step === 'result' ? 'bg-green-100' : 'bg-gray-100'}`}>
            {step === 'result' ? <CheckCircle className="w-5 h-5" /> : '2'}
          </div>
          <span className="font-medium">Generate Chart</span>
        </div>
        <div className="w-12 h-0.5 bg-gray-300"></div>
        <div className={`flex items-center gap-2 ${step === 'result' ? 'text-blue-600' : 'text-gray-400'}`}>
          <div className={`w-8 h-8 rounded-full flex items-center justify-center ${step === 'result' ? 'bg-blue-100' : 'bg-gray-100'}`}>
            3
          </div>
          <span className="font-medium">View Chart</span>
        </div>
      </div>

      {error && (
        <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg text-red-800">
          {error}
        </div>
      )}

      {/* Form Step */}
      {step === 'form' && (
        <Card className="max-w-2xl mx-auto">
          <CardHeader>
            <CardTitle>Enter Birth Information</CardTitle>
            <CardDescription>We'll generate your chart instantly</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {/* Name */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  <UserIcon className="w-4 h-4 inline mr-1" />
                  Full Name
                </label>
                <input
                  type="text"
                  value={formData.name}
                  onChange={(e) => handleInputChange('name', e.target.value)}
                  className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="Enter your full name"
                />
              </div>

              {/* Gender (Optional) */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Gender (Optional)
                </label>
                <select
                  value={formData.gender}
                  onChange={(e) => handleInputChange('gender', e.target.value)}
                  className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                >
                  <option value="">Select gender (optional)</option>
                  <option value="male">Male</option>
                  <option value="female">Female</option>
                  <option value="other">Other</option>
                </select>
                <p className="text-xs text-gray-500 mt-1">
                  Gender helps provide more personalized astrological interpretations
                </p>
              </div>

              {/* Birth Date */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  <CalendarIcon className="w-4 h-4 inline mr-1" />
                  Birth Date
                </label>
                <input
                  type="date"
                  value={formData.birth_date}
                  onChange={(e) => handleInputChange('birth_date', e.target.value)}
                  className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
              </div>

              {/* Birth Time */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  <Clock className="w-4 h-4 inline mr-1" />
                  Birth Time
                </label>
                <input
                  type="time"
                  value={formData.birth_time}
                  onChange={(e) => handleInputChange('birth_time', e.target.value)}
                  className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
              </div>

              {/* City Selection */}
              <CityAutocomplete
                onCitySelect={handleCitySelect}
                disabled={generating}
                initialValue={formData.birth_place}
              />

              <Button
                onClick={generateQuickChart}
                disabled={generating}
                className="w-full"
              >
                {generating ? (
                  <>
                    <Zap className="w-4 h-4 mr-2 animate-pulse" />
                    Generating...
                  </>
                ) : (
                  <>
                    <Zap className="w-4 h-4 mr-2" />
                    Generate Chart Instantly
                  </>
                )}
              </Button>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Generating Step */}
      {step === 'generating' && (
        <Card className="max-w-2xl mx-auto">
          <CardContent className="py-12">
            <div className="text-center">
              <Zap className="w-16 h-16 mx-auto mb-4 text-blue-600 animate-pulse" />
              <h2 className="text-2xl font-bold mb-2">Generating Your Chart...</h2>
              <p className="text-gray-600">This will only take a moment</p>
              <div className="mt-6 flex justify-center">
                <div className="w-8 h-8 border-4 border-blue-600 border-t-transparent rounded-full animate-spin"></div>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Result Step */}
      {step === 'result' && chartData && (
        <div className="space-y-6">
          <Card className="border-green-200 bg-green-50">
            <CardContent className="py-6">
              <div className="text-center">
                <CheckCircle className="w-16 h-16 mx-auto mb-4 text-green-600" />
                <h2 className="text-2xl font-bold text-green-900 mb-2">Chart Generated Successfully!</h2>
                <p className="text-green-700">Your Vedic birth chart has been created</p>
              </div>
            </CardContent>
          </Card>

          {/* Birth Details Card */}
          <Card>
            <CardHeader>
              <CardTitle>Birth Details</CardTitle>
              <CardDescription>
                {isAuthenticated
                  ? 'Your chart has been saved to your profile'
                  : 'Login to save this chart permanently'}
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <p className="text-sm text-gray-600">Name</p>
                  <p className="font-semibold">{chartData.name}</p>
                </div>
                <div>
                  <p className="text-sm text-gray-600">Birth Date</p>
                  <p className="font-semibold">{chartData.birth_date ? new Date(chartData.birth_date).toLocaleDateString() : '-'}</p>
                </div>
                <div>
                  <p className="text-sm text-gray-600">Generated</p>
                  <p className="font-semibold">{chartData.generated_at ? new Date(chartData.generated_at).toLocaleString() : 'Just now'}</p>
                </div>
                <div>
                  <p className="text-sm text-gray-600">Ascendant</p>
                  <p className="font-semibold">{chartData.summary?.ascendant?.sign || 'Calculating...'}</p>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Chart Display */}
          <Card>
            <CardHeader>
              <CardTitle>Birth Chart (D1 - Rashi)</CardTitle>
              <CardDescription>
                Switch between North Indian, South Indian, and Western circular chart styles
              </CardDescription>
            </CardHeader>
            <CardContent>
              <ChartSelector chartData={chartData.summary} defaultChart="north" />
            </CardContent>
          </Card>

          {/* Planetary Yogas */}
          {chartData.summary?.yogas && chartData.summary.yogas.length > 0 && (
            <YogaDisplay yogas={chartData.summary.yogas} />
          )}

          {/* Vimshottari Dasha Timeline */}
          {chartData.summary?.dasha && (
            <EnhancedDashaTimeline dashaData={chartData.summary.dasha} />
          )}

          {/* Quick Info Cards */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <Card>
              <CardHeader className="pb-3">
                <CardTitle className="text-sm font-medium">Ascendant</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold text-blue-700">
                  {chartData.summary?.ascendant?.sign || 'N/A'}
                </div>
                <p className="text-xs text-gray-500 mt-1">Rising sign at birth</p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="pb-3">
                <CardTitle className="text-sm font-medium">Moon Sign</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold text-indigo-700">
                  {chartData.moon_sign}
                </div>
                <p className="text-xs text-gray-500 mt-1">Emotional nature</p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="pb-3">
                <CardTitle className="text-sm font-medium">Sun Sign</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold text-amber-700">
                  {chartData.sun_sign}
                </div>
                <p className="text-xs text-gray-500 mt-1">Core personality</p>
              </CardContent>
            </Card>
          </div>

          {/* Save Profile Prompt - Show for authenticated users */}
          {isAuthenticated && showSavePrompt && !profileSaved && (
            <Card className="border-2 border-green-500 bg-gradient-to-r from-green-50 to-blue-50">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <CheckCircle className="w-5 h-5 text-green-600" />
                  Save to Birth Profiles?
                </CardTitle>
                <CardDescription>
                  Would you like to save this chart to your Birth Profiles for easy access later?
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="flex gap-3">
                  <Button
                    onClick={saveProfileToDatabase}
                    disabled={isSavingProfile}
                    className="bg-green-600 hover:bg-green-700"
                  >
                    {isSavingProfile ? 'Saving...' : 'Yes, Save Profile'}
                  </Button>
                  <Button
                    variant="outline"
                    onClick={() => setShowSavePrompt(false)}
                    disabled={isSavingProfile}
                  >
                    No, Thanks
                  </Button>
                </div>
              </CardContent>
            </Card>
          )}

          {/* Profile Saved Success Message */}
          {isAuthenticated && profileSaved && (
            <Card className="border-2 border-green-500 bg-green-50">
              <CardContent className="py-4">
                <div className="flex items-center gap-2 text-green-700">
                  <CheckCircle className="w-5 h-5" />
                  <p className="font-medium">Profile saved successfully to your Birth Profiles!</p>
                </div>
              </CardContent>
            </Card>
          )}

          {/* Login CTA for Unauthenticated Users */}
          {!isAuthenticated && (
            <Card className="border-2 border-blue-500 bg-gradient-to-r from-blue-50 to-purple-50">
              <CardContent className="py-8">
                <div className="text-center">
                  <LogIn className="w-12 h-12 mx-auto mb-4 text-blue-600" />
                  <h3 className="text-xl font-bold text-gray-900 mb-2">Want to Save Your Chart?</h3>
                  <p className="text-gray-700 mb-6">
                    Login to save this chart permanently, access full features, and ask AI-powered questions about your chart
                  </p>
                  <div className="flex gap-3 justify-center">
                    <Link href="/auth/login" onClick={handleLoginRedirect}>
                      <Button size="lg" className="bg-blue-600 hover:bg-blue-700">
                        <LogIn className="w-4 h-4 mr-2" />
                        Login to Save Chart
                      </Button>
                    </Link>
                    <Link href="/auth/signup" onClick={handleLoginRedirect}>
                      <Button size="lg" variant="outline" className="border-blue-600 text-blue-700 hover:bg-blue-50">
                        Create Account
                      </Button>
                    </Link>
                  </div>
                </div>
              </CardContent>
            </Card>
          )}

          {/* Next Steps Card */}
          <Card>
            <CardHeader>
              <CardTitle>Next Steps</CardTitle>
              <CardDescription>What would you like to do?</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {isAuthenticated ? (
                  <>
                    <Link href="/dashboard/profiles">
                      <Button className="w-full">
                        <ArrowRight className="w-4 h-4 mr-2" />
                        View My Profiles
                      </Button>
                    </Link>
                    <Link href="/dashboard">
                      <Button variant="outline" className="w-full">
                        Go to Dashboard
                      </Button>
                    </Link>
                  </>
                ) : (
                  <>
                    <Link href="/auth/login" onClick={handleLoginRedirect}>
                      <Button className="w-full">
                        <LogIn className="w-4 h-4 mr-2" />
                        Login to Save & Access Full Features
                      </Button>
                    </Link>
                  </>
                )}
                <Button variant="outline" className="w-full" onClick={resetForm}>
                  Generate Another Chart
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>
      )}
    </div>
  )
}
