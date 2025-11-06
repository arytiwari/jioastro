'use client'

import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@/lib/query'
import Link from 'next/link'
import { apiClient } from '@/lib/api'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Select } from '@/components/ui/select'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { NumerologyCard } from '@/components/numerology/NumerologyCard'
import { Sparkles, Calendar, User, Star, History, Plus, AlertTriangle } from '@/components/icons'
import { formatDate } from '@/lib/utils'

interface NumerologyFormData {
  fullName: string
  birthDate: string
  system: 'western' | 'vedic' | 'chaldean' | 'both'
  profileId?: string
}

export default function NumerologyPage() {
  const queryClient = useQueryClient()
  const [formData, setFormData] = useState<NumerologyFormData>({
    fullName: '',
    birthDate: '',
    system: 'both',
  })
  const [calculationResult, setCalculationResult] = useState<any>(null)

  // Fetch birth profiles for linking
  const { data: profiles } = useQuery({
    queryKey: ['profiles'],
    queryFn: async () => {
      const response = await apiClient.getProfiles()
      return response.data
    },
  })

  // Fetch saved numerology profiles
  const { data: savedProfiles, isLoading: isLoadingProfiles } = useQuery({
    queryKey: ['numerology-profiles'],
    queryFn: async () => {
      const response = await apiClient.getNumerologyProfiles()
      return response.data
    },
  })

  // Calculate numerology mutation
  const calculateMutation = useMutation({
    mutationFn: async (data: NumerologyFormData) => {
      const response = await apiClient.calculateNumerology({
        full_name: data.fullName,
        birth_date: data.birthDate,
        system: data.system,
        profile_id: data.profileId,
      })
      return response.data
    },
    onSuccess: (data) => {
      setCalculationResult(data)
    },
    onError: (error: any) => {
      alert(error?.message || 'Failed to calculate numerology')
    },
  })

  // Save profile mutation
  const saveProfileMutation = useMutation({
    mutationFn: async (data: NumerologyFormData) => {
      const response = await apiClient.createNumerologyProfile({
        full_name: data.fullName,
        birth_date: data.birthDate,
        system: data.system,
        profile_id: data.profileId,
      })
      return response.data
    },
    onSuccess: () => {
      queryClient.invalidateQueries(['numerology-profiles'])
      alert('Numerology profile saved successfully!')
    },
    onError: (error: any) => {
      alert(error?.message || 'Failed to save profile')
    },
  })

  const handleCalculate = () => {
    if (!formData.fullName || !formData.birthDate) {
      alert('Please enter your name and birth date')
      return
    }
    calculateMutation.mutate(formData)
  }

  const handleSaveProfile = () => {
    if (!calculationResult) {
      alert('Please calculate first before saving')
      return
    }
    saveProfileMutation.mutate(formData)
  }

  const loadFromProfile = (profile: any) => {
    setFormData({
      ...formData,
      fullName: profile.name,
      birthDate: profile.birth_date.split('T')[0],
      profileId: profile.id,
    })
  }

  const loadSavedProfile = (profile: any) => {
    setFormData({
      fullName: profile.full_name,
      birthDate: profile.birth_date,
      system: profile.system,
      profileId: profile.profile_id,
    })
    setCalculationResult({
      western: profile.western_data,
      vedic: profile.vedic_data,
      system: profile.system,
    })
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 flex items-center gap-2">
            <Sparkles className="w-8 h-8 text-purple-600" />
            Numerology Calculator
          </h1>
          <p className="text-gray-600 mt-2">
            Discover the hidden meanings in your name and birth date
          </p>
        </div>
        <Link href="/dashboard/numerology/compare">
          <Button variant="default">
            <Plus className="w-4 h-4 mr-2" />
            Compare Names
          </Button>
        </Link>
      </div>

      {/* System Information Banner */}
      <Card className="border-blue-200 bg-blue-50">
        <CardContent className="py-3">
          <div className="flex items-center gap-2 text-xs text-blue-900">
            <Sparkles className="w-4 h-4 flex-shrink-0" />
            <p>
              <span className="font-semibold">Vedic Astrology System:</span> All astrological calculations use the{' '}
              <span className="font-semibold">Sidereal Zodiac</span> with{' '}
              <span className="font-semibold">Lahiri Ayanamsa</span> (Government of India standard).
            </p>
          </div>
        </CardContent>
      </Card>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left Column: Input Form */}
        <div className="lg:col-span-1 space-y-6">
          {/* Calculator Form */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <User className="w-5 h-5" />
                Your Information
              </CardTitle>
              <CardDescription>Enter your details to calculate numerology</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <Label htmlFor="fullName">Full Name</Label>
                <Input
                  id="fullName"
                  type="text"
                  placeholder="John Doe"
                  value={formData.fullName}
                  onChange={(e) => setFormData({ ...formData, fullName: e.target.value })}
                />
              </div>

              <div>
                <Label htmlFor="birthDate">Birth Date</Label>
                <Input
                  id="birthDate"
                  type="date"
                  value={formData.birthDate}
                  onChange={(e) => setFormData({ ...formData, birthDate: e.target.value })}
                />
              </div>

              <div>
                <Label htmlFor="system">Numerology System</Label>
                <select
                  id="system"
                  className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background file:border-0 file:bg-transparent file:text-sm file:font-medium placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
                  value={formData.system}
                  onChange={(e) =>
                    setFormData({
                      ...formData,
                      system: e.target.value as 'western' | 'vedic' | 'chaldean' | 'both',
                    })
                  }
                >
                  <option value="both">Both (Western + Vedic)</option>
                  <option value="western">Western (Pythagorean)</option>
                  <option value="vedic">Vedic (Chaldean)</option>
                </select>
              </div>

              {/* Birth Profile Link Status */}
              {formData.profileId ? (
                <div className="p-3 bg-green-50 border border-green-200 rounded-md">
                  <div className="flex items-center gap-2 text-sm text-green-800">
                    <Star className="w-4 h-4 flex-shrink-0" />
                    <p>
                      <span className="font-semibold">Linked to birth profile</span> - AI readings will include both astrology and numerology insights
                    </p>
                  </div>
                </div>
              ) : profiles && profiles.length > 0 ? (
                <div className="p-3 bg-yellow-50 border border-yellow-200 rounded-md">
                  <div className="flex items-center gap-2 text-sm text-yellow-800">
                    <AlertTriangle className="w-4 h-4 flex-shrink-0" />
                    <p>
                      <span className="font-semibold">Not linked to birth profile</span> - Load from a birth profile below for AI readings with combined insights
                    </p>
                  </div>
                </div>
              ) : null}

              <div className="flex gap-2">
                <Button
                  onClick={handleCalculate}
                  disabled={calculateMutation.isPending}
                  className="flex-1"
                >
                  {calculateMutation.isPending ? (
                    <>
                      <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin mr-2"></div>
                      Calculating...
                    </>
                  ) : (
                    <>
                      <Sparkles className="w-4 h-4 mr-2" />
                      Calculate
                    </>
                  )}
                </Button>

                {calculationResult && (
                  <Button
                    variant="default"
                    onClick={handleSaveProfile}
                    disabled={saveProfileMutation.isPending}
                  >
                    {saveProfileMutation.isPending ? 'Saving...' : 'Save'}
                  </Button>
                )}
              </div>
            </CardContent>
          </Card>

          {/* Link to Birth Profiles */}
          {!profiles || profiles.length === 0 ? (
            <Card className="border-yellow-200 bg-yellow-50/30">
              <CardHeader>
                <CardTitle className="flex items-center gap-2 text-sm">
                  <AlertTriangle className="w-4 h-4" />
                  No Birth Profiles
                </CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-xs text-gray-600 mb-3">
                  Create a birth profile first to link your numerology data with your birth chart.
                  This enables AI readings that combine both astrology and numerology insights.
                </p>
                <Link href="/dashboard/profiles">
                  <Button variant="outline" size="sm" className="w-full">
                    <Plus className="w-3 h-3 mr-2" />
                    Create Birth Profile
                  </Button>
                </Link>
              </CardContent>
            </Card>
          ) : profiles && profiles.length > 0 && (
            <Card className="border-blue-200 bg-blue-50/30">
              <CardHeader>
                <CardTitle className="flex items-center gap-2 text-sm">
                  <Calendar className="w-4 h-4" />
                  Load from Birth Profile
                </CardTitle>
                <CardDescription className="text-xs">
                  Link numerology to your birth chart for combined AI readings
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-2">
                  {profiles.slice(0, 3).map((profile: any) => (
                    <button
                      key={profile.id}
                      onClick={() => loadFromProfile(profile)}
                      className={`w-full text-left px-3 py-2 text-sm border rounded transition-colors ${
                        formData.profileId === profile.id
                          ? 'bg-blue-100 border-blue-300 font-medium'
                          : 'bg-white hover:bg-gray-50'
                      }`}
                    >
                      <div className="font-medium flex items-center justify-between">
                        {profile.name}
                        {formData.profileId === profile.id && (
                          <Star className="w-3 h-3 text-blue-600 fill-blue-600" />
                        )}
                      </div>
                      <div className="text-xs text-gray-500">{formatDate(profile.birth_date)}</div>
                    </button>
                  ))}
                  {profiles.length > 3 && (
                    <Link href="/dashboard/profiles">
                      <Button variant="link" className="w-full text-xs p-0 h-auto">
                        View all {profiles.length} profiles →
                      </Button>
                    </Link>
                  )}
                </div>
              </CardContent>
            </Card>
          )}

          {/* Saved Profiles */}
          {savedProfiles?.profiles && savedProfiles.profiles.length > 0 && (
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2 text-sm">
                  <History className="w-4 h-4" />
                  Saved Numerology Profiles
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-2">
                  {savedProfiles.profiles.slice(0, 5).map((profile: any) => (
                    <button
                      key={profile.id}
                      onClick={() => loadSavedProfile(profile)}
                      className="w-full text-left px-3 py-2 text-sm border rounded hover:bg-gray-50 transition-colors"
                    >
                      <div className="font-medium">{profile.full_name}</div>
                      <div className="text-xs text-gray-500">
                        {formatDate(profile.birth_date)} • {profile.system}
                      </div>
                    </button>
                  ))}
                </div>
              </CardContent>
            </Card>
          )}
        </div>

        {/* Right Column: Results */}
        <div className="lg:col-span-2">
          {!calculationResult ? (
            <Card>
              <CardContent className="text-center py-12">
                <div className="mb-4">
                  <Star className="w-16 h-16 text-gray-300 mx-auto" />
                </div>
                <h3 className="text-lg font-semibold mb-2">Calculate Your Numerology</h3>
                <p className="text-gray-600 mb-4">
                  Enter your name and birth date to discover your numerology numbers and their
                  meanings
                </p>
                <div className="text-sm text-gray-500">
                  <p>✨ Life Path Number</p>
                  <p>✨ Expression Number</p>
                  <p>✨ Soul Urge Number</p>
                  <p>✨ Psychic & Destiny Numbers (Vedic)</p>
                </div>
              </CardContent>
            </Card>
          ) : (
            <Tabs defaultValue={calculationResult.system === 'both' ? 'western' : calculationResult.system}>
              <TabsList className="grid w-full grid-cols-2">
                {(calculationResult.system === 'both' || calculationResult.system === 'western') && (
                  <TabsTrigger value="western">Western (Pythagorean)</TabsTrigger>
                )}
                {(calculationResult.system === 'both' || calculationResult.system === 'vedic') && (
                  <TabsTrigger value="vedic">Vedic (Chaldean)</TabsTrigger>
                )}
              </TabsList>

              {/* Western Results */}
              {calculationResult.western && (
                <TabsContent value="western" className="space-y-6 mt-6">
                  <div>
                    <h3 className="text-xl font-bold mb-4">Core Numbers</h3>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <NumerologyCard
                        title="Life Path"
                        number={calculationResult.western.core_numbers.life_path.number}
                        description="Your life's purpose and journey"
                        isMaster={calculationResult.western.core_numbers.life_path.is_master}
                        karmicDebt={calculationResult.western.core_numbers.life_path.karmic_debt}
                        meaning={calculationResult.western.core_numbers.life_path.meaning}
                      />
                      <NumerologyCard
                        title="Expression"
                        number={calculationResult.western.core_numbers.expression.number}
                        description="Your natural talents and abilities"
                        isMaster={calculationResult.western.core_numbers.expression.is_master}
                        meaning={calculationResult.western.core_numbers.expression.meaning}
                      />
                      <NumerologyCard
                        title="Soul Urge"
                        number={calculationResult.western.core_numbers.soul_urge.number}
                        description="Your inner desires and motivations"
                        isMaster={calculationResult.western.core_numbers.soul_urge.is_master}
                        meaning={calculationResult.western.core_numbers.soul_urge.meaning}
                      />
                      <NumerologyCard
                        title="Personality"
                        number={calculationResult.western.core_numbers.personality.number}
                        description="How others perceive you"
                        isMaster={calculationResult.western.core_numbers.personality.is_master}
                        meaning={calculationResult.western.core_numbers.personality.meaning}
                      />
                    </div>
                  </div>

                  <div>
                    <h3 className="text-xl font-bold mb-4">Current Cycles</h3>
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                      <NumerologyCard
                        title="Personal Year"
                        number={calculationResult.western.current_cycles.personal_year.number}
                        description="This year's theme and opportunities"
                        meaning={calculationResult.western.current_cycles.personal_year.meaning}
                      />
                      <NumerologyCard
                        title="Personal Month"
                        number={calculationResult.western.current_cycles.personal_month.number}
                        description="This month's focus"
                        meaning={calculationResult.western.current_cycles.personal_month.meaning}
                      />
                      <NumerologyCard
                        title="Personal Day"
                        number={calculationResult.western.current_cycles.personal_day.number}
                        description="Today's energy"
                        meaning={calculationResult.western.current_cycles.personal_day.meaning}
                      />
                    </div>
                  </div>
                </TabsContent>
              )}

              {/* Vedic Results */}
              {calculationResult.vedic && (
                <TabsContent value="vedic" className="space-y-6 mt-6">
                  <div>
                    <h3 className="text-xl font-bold mb-4">Vedic Numbers</h3>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <NumerologyCard
                        title="Psychic Number (Moolank)"
                        number={calculationResult.vedic.psychic_number.number}
                        description={`Ruled by ${calculationResult.vedic.psychic_number.planet}`}
                        meaning={calculationResult.vedic.psychic_number.meaning}
                        favorableAttributes={[
                          `Days: ${calculationResult.vedic.psychic_number.favorable_dates?.join(', ') || 'N/A'}`,
                          `Colors: ${calculationResult.vedic.psychic_number.favorable_colors?.join(', ') || 'N/A'}`,
                        ]}
                      />
                      <NumerologyCard
                        title="Destiny Number (Bhagyank)"
                        number={calculationResult.vedic.destiny_number.number}
                        description={`Ruled by ${calculationResult.vedic.destiny_number.planet}`}
                        meaning={calculationResult.vedic.destiny_number.meaning}
                        favorableAttributes={[
                          `Days: ${calculationResult.vedic.destiny_number.favorable_dates?.join(', ') || 'N/A'}`,
                          `Colors: ${calculationResult.vedic.destiny_number.favorable_colors?.join(', ') || 'N/A'}`,
                        ]}
                      />
                    </div>
                  </div>

                  {calculationResult.vedic.name_number && (
                    <div>
                      <h3 className="text-xl font-bold mb-4">Name Number</h3>
                      <NumerologyCard
                        title="Name Number"
                        number={calculationResult.vedic.name_number.number}
                        description="Influence of your name"
                        meaning={calculationResult.vedic.name_number.meaning}
                      />
                    </div>
                  )}
                </TabsContent>
              )}
            </Tabs>
          )}
        </div>
      </div>
    </div>
  )
}
