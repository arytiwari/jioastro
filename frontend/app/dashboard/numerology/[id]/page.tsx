'use client'

import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@/lib/query'
import { useParams, useRouter } from 'next/navigation'
import Link from 'next/link'
import { apiClient } from '@/lib/api'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { NumerologyCard } from '@/components/numerology/NumerologyCard'
import { CyclesTimeline } from '@/components/numerology/CyclesTimeline'
import { PlanetAssociations } from '@/components/numerology/PlanetAssociations'
import { ArrowLeft, Sparkles, Edit, Trash2, Plus, Save } from '@/components/icons'
import { formatDate } from '@/lib/utils'

export default function NumerologyProfilePage() {
  const params = useParams()
  const router = useRouter()
  const queryClient = useQueryClient()
  const profileId = params.id as string

  const [isEditing, setIsEditing] = useState(false)
  const [editedName, setEditedName] = useState('')
  const [showNameTrialForm, setShowNameTrialForm] = useState(false)
  const [nameTrialData, setNameTrialData] = useState({
    trialName: '',
    notes: '',
  })

  // Fetch profile data
  const { data: profile, isLoading } = useQuery({
    queryKey: ['numerology-profile', profileId],
    queryFn: async () => {
      const response = await apiClient.getNumerologyProfile(profileId)
      return response.data
    },
  })

  // Fetch name trials
  const { data: nameTrials } = useQuery({
    queryKey: ['name-trials', profileId],
    queryFn: async () => {
      const response = await apiClient.getNameTrials(profileId)
      return response.data
    },
  })

  // Update profile mutation
  const updateMutation = useMutation({
    mutationFn: async (data: { full_name: string }) => {
      const response = await apiClient.updateNumerologyProfile(profileId, data)
      return response.data
    },
    onSuccess: () => {
      queryClient.invalidateQueries(['numerology-profile', profileId])
      setIsEditing(false)
      alert('Profile updated successfully!')
    },
    onError: (error: any) => {
      alert(error?.message || 'Failed to update profile')
    },
  })

  // Delete profile mutation
  const deleteMutation = useMutation({
    mutationFn: async () => {
      await apiClient.deleteNumerologyProfile(profileId)
    },
    onSuccess: () => {
      router.push('/dashboard/numerology')
    },
    onError: (error: any) => {
      alert(error?.message || 'Failed to delete profile')
    },
  })

  // Create name trial mutation
  const createNameTrialMutation = useMutation({
    mutationFn: async (data: { trial_name: string; system: string; notes?: string }) => {
      const response = await apiClient.createNameTrial(profileId, {
        trial_name: data.trial_name,
        system: data.system as 'western' | 'vedic' | 'chaldean',
        notes: data.notes,
      })
      return response.data
    },
    onSuccess: () => {
      queryClient.invalidateQueries(['name-trials', profileId])
      setShowNameTrialForm(false)
      setNameTrialData({ trialName: '', notes: '' })
      alert('Name trial created successfully!')
    },
    onError: (error: any) => {
      alert(error?.message || 'Failed to create name trial')
    },
  })

  const handleUpdate = () => {
    if (!editedName.trim()) {
      alert('Please enter a name')
      return
    }
    updateMutation.mutate({ full_name: editedName })
  }

  const handleDelete = () => {
    if (confirm('Are you sure you want to delete this numerology profile?')) {
      deleteMutation.mutate()
    }
  }

  const handleCreateNameTrial = () => {
    if (!nameTrialData.trialName.trim()) {
      alert('Please enter a trial name')
      return
    }
    createNameTrialMutation.mutate({
      trial_name: nameTrialData.trialName,
      system: profile.system,
      notes: nameTrialData.notes,
    })
  }

  if (isLoading) {
    return (
      <div className="text-center py-12">
        <div className="w-8 h-8 border-4 border-jio-600 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
        <p className="text-gray-600">Loading profile...</p>
      </div>
    )
  }

  if (!profile) {
    return (
      <div className="text-center py-12">
        <p className="text-gray-600">Profile not found</p>
        <Link href="/dashboard/numerology">
          <Button className="mt-4">Back to Numerology</Button>
        </Link>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          <Link href="/dashboard/numerology">
            <Button variant="default" size="sm">
              <ArrowLeft className="w-4 h-4 mr-2" />
              Back
            </Button>
          </Link>
          <div>
            <h1 className="text-3xl font-bold text-gray-900 flex items-center gap-2">
              <Sparkles className="w-8 h-8 text-purple-600" />
              {profile.full_name}
            </h1>
            <p className="text-gray-600 mt-1">
              {formatDate(profile.birth_date)} • {profile.system === 'both' ? 'Western + Vedic' : profile.system}
            </p>
          </div>
        </div>
        <div className="flex gap-2">
          <Button
            variant="default"
            size="sm"
            onClick={() => {
              setIsEditing(true)
              setEditedName(profile.full_name)
            }}
          >
            <Edit className="w-4 h-4 mr-2" />
            Edit
          </Button>
          <Button
            variant="default"
            size="sm"
            onClick={handleDelete}
            disabled={deleteMutation.isPending}
          >
            <Trash2 className="w-4 h-4 mr-2" />
            Delete
          </Button>
        </div>
      </div>

      {/* Edit Form */}
      {isEditing && (
        <Card>
          <CardHeader>
            <CardTitle>Edit Profile</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <Label htmlFor="editName">Full Name</Label>
              <Input
                id="editName"
                type="text"
                value={editedName}
                onChange={(e) => setEditedName(e.target.value)}
              />
            </div>
            <div className="flex gap-2">
              <Button onClick={handleUpdate} disabled={updateMutation.isPending}>
                <Save className="w-4 h-4 mr-2" />
                {updateMutation.isPending ? 'Saving...' : 'Save Changes'}
              </Button>
              <Button variant="default" onClick={() => setIsEditing(false)}>
                Cancel
              </Button>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Main Content */}
      <Tabs defaultValue={profile.system === 'both' ? 'western' : profile.system}>
        <TabsList className="grid w-full grid-cols-2">
          {(profile.system === 'both' || profile.system === 'western') && (
            <TabsTrigger value="western">Western (Pythagorean)</TabsTrigger>
          )}
          {(profile.system === 'both' || profile.system === 'vedic') && (
            <TabsTrigger value="vedic">Vedic (Chaldean)</TabsTrigger>
          )}
        </TabsList>

        {/* Western Tab */}
        {profile.western_data && (
          <TabsContent value="western" className="space-y-6 mt-6">
            {/* Core Numbers */}
            <div>
              <h3 className="text-xl font-bold mb-4">Core Numbers</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                <NumerologyCard
                  title="Life Path"
                  number={profile.western_data.core_numbers.life_path.number}
                  description="Your life's purpose and journey"
                  isMaster={profile.western_data.core_numbers.life_path.is_master}
                  karmicDebt={profile.western_data.core_numbers.life_path.karmic_debt}
                  meaning={profile.western_data.core_numbers.life_path.meaning}
                />
                <NumerologyCard
                  title="Expression"
                  number={profile.western_data.core_numbers.expression.number}
                  description="Your natural talents and abilities"
                  isMaster={profile.western_data.core_numbers.expression.is_master}
                  meaning={profile.western_data.core_numbers.expression.meaning}
                />
                <NumerologyCard
                  title="Soul Urge"
                  number={profile.western_data.core_numbers.soul_urge.number}
                  description="Your inner desires and motivations"
                  isMaster={profile.western_data.core_numbers.soul_urge.is_master}
                  meaning={profile.western_data.core_numbers.soul_urge.meaning}
                />
                <NumerologyCard
                  title="Personality"
                  number={profile.western_data.core_numbers.personality.number}
                  description="How others perceive you"
                  isMaster={profile.western_data.core_numbers.personality.is_master}
                  meaning={profile.western_data.core_numbers.personality.meaning}
                />
                <NumerologyCard
                  title="Maturity"
                  number={profile.western_data.core_numbers.maturity.number}
                  description="Your later life goals"
                  isMaster={profile.western_data.core_numbers.maturity.is_master}
                  meaning={profile.western_data.core_numbers.maturity.meaning}
                />
                <NumerologyCard
                  title="Birth Day"
                  number={profile.western_data.core_numbers.birth_day.number}
                  description="Special talents from birth day"
                  karmicDebt={profile.western_data.core_numbers.birth_day.karmic_debt}
                  meaning={profile.western_data.core_numbers.birth_day.meaning}
                />
              </div>
            </div>

            {/* Cycles Timeline */}
            <CyclesTimeline
              personalYear={profile.western_data.current_cycles?.personal_year}
              personalMonth={profile.western_data.current_cycles?.personal_month}
              personalDay={profile.western_data.current_cycles?.personal_day}
              pinnacles={profile.western_data.life_periods?.pinnacles}
              challenges={profile.western_data.life_periods?.challenges}
              universalYear={profile.western_data.current_cycles?.universal_year}
            />
          </TabsContent>
        )}

        {/* Vedic Tab */}
        {profile.vedic_data && (
          <TabsContent value="vedic" className="space-y-6 mt-6">
            {/* Vedic Numbers */}
            <div>
              <h3 className="text-xl font-bold mb-4">Vedic Numbers</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <NumerologyCard
                  title="Psychic Number (Moolank)"
                  number={profile.vedic_data.psychic_number.number}
                  description={`Ruled by ${profile.vedic_data.psychic_number.planet}`}
                  meaning={profile.vedic_data.psychic_number.meaning}
                />
                <NumerologyCard
                  title="Destiny Number (Bhagyank)"
                  number={profile.vedic_data.destiny_number.number}
                  description={`Ruled by ${profile.vedic_data.destiny_number.planet}`}
                  meaning={profile.vedic_data.destiny_number.meaning}
                />
                {profile.vedic_data.name_number && (
                  <NumerologyCard
                    title="Name Number"
                    number={profile.vedic_data.name_number.number}
                    description="Influence of your name"
                    meaning={profile.vedic_data.name_number.meaning}
                  />
                )}
              </div>
            </div>

            {/* Planet Associations */}
            <div>
              <h3 className="text-xl font-bold mb-4">Planetary Influences</h3>
              <PlanetAssociations
                psychicNumber={profile.vedic_data.psychic_number}
                destinyNumber={profile.vedic_data.destiny_number}
              />
            </div>
          </TabsContent>
        )}
      </Tabs>

      {/* Name Trials Section */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle>Name Trials</CardTitle>
              <CardDescription>Experiment with different name spellings</CardDescription>
            </div>
            <Button
              variant="default"
              size="sm"
              onClick={() => setShowNameTrialForm(!showNameTrialForm)}
            >
              <Plus className="w-4 h-4 mr-2" />
              New Trial
            </Button>
          </div>
        </CardHeader>
        <CardContent className="space-y-4">
          {showNameTrialForm && (
            <div className="border rounded-lg p-4 bg-gray-50">
              <div className="space-y-3">
                <div>
                  <Label htmlFor="trialName">Trial Name</Label>
                  <Input
                    id="trialName"
                    type="text"
                    placeholder="Alternative spelling..."
                    value={nameTrialData.trialName}
                    onChange={(e) =>
                      setNameTrialData({ ...nameTrialData, trialName: e.target.value })
                    }
                  />
                </div>
                <div>
                  <Label htmlFor="notes">Notes (Optional)</Label>
                  <Input
                    id="notes"
                    type="text"
                    placeholder="Why trying this name..."
                    value={nameTrialData.notes}
                    onChange={(e) =>
                      setNameTrialData({ ...nameTrialData, notes: e.target.value })
                    }
                  />
                </div>
                <div className="flex gap-2">
                  <Button
                    onClick={handleCreateNameTrial}
                    disabled={createNameTrialMutation.isPending}
                  >
                    {createNameTrialMutation.isPending ? 'Creating...' : 'Create Trial'}
                  </Button>
                  <Button variant="default" onClick={() => setShowNameTrialForm(false)}>
                    Cancel
                  </Button>
                </div>
              </div>
            </div>
          )}

          {nameTrials && nameTrials.length > 0 ? (
            <div className="space-y-3">
              {nameTrials.map((trial: any) => (
                <div key={trial.id} className="border rounded-lg p-4">
                  <div className="flex items-center justify-between">
                    <div>
                      <div className="font-semibold">{trial.trial_name}</div>
                      {trial.notes && <div className="text-sm text-gray-600 mt-1">{trial.notes}</div>}
                    </div>
                    {trial.is_preferred && (
                      <span className="text-xs bg-purple-100 text-purple-700 px-2 py-1 rounded font-semibold">
                        Preferred
                      </span>
                    )}
                  </div>
                  <div className="text-xs text-gray-500 mt-2">
                    Created {formatDate(trial.created_at)}
                  </div>
                </div>
              ))}
            </div>
          ) : (
            !showNameTrialForm && (
              <div className="text-center py-8 text-gray-500">
                No name trials yet. Create one to experiment with different spellings.
              </div>
            )
          )}
        </CardContent>
      </Card>
    </div>
  )
}
