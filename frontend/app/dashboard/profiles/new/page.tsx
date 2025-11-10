'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import { apiClient } from '@/lib/api'
import { useMutation, useQueryClient } from '@/lib/query'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { CityAutocomplete } from '@/components/CityAutocomplete'
import { useToast } from '@/hooks/use-toast'

const TIMEZONES = [
  'UTC',
  'Asia/Kolkata',
  'America/New_York',
  'America/Los_Angeles',
  'Europe/London',
  'Asia/Dubai',
  'Asia/Singapore',
  'Australia/Sydney',
]

export default function NewProfilePage() {
  const router = useRouter()
  const queryClient = useQueryClient()
  const { toast } = useToast()
  const [error, setError] = useState('')

  const [formData, setFormData] = useState({
    name: '',
    gender: '',
    birth_date: '',
    birth_time: '',
    birth_city: '',
    birth_lat: '',
    birth_lon: '',
    birth_timezone: 'Asia/Kolkata',
    is_primary: false,
  })

  const handleCitySelect = (city: { id: number; name: string; state: string; latitude: number; longitude: number; display_name: string }) => {
    setFormData(prev => ({
      ...prev,
      birth_city: city.display_name,
      birth_lat: city.latitude.toString(),
      birth_lon: city.longitude.toString(),
    }))
  }

  const createProfileMutation = useMutation({
    mutationFn: async (payload: typeof formData) => {
      // Parse city and state from birth_city (format: "City, State" or just "City")
      const birthCityParts = payload.birth_city.split(',').map(s => s.trim())
      const cityName = birthCityParts[0] || payload.birth_city
      const stateName = birthCityParts[1] || 'Unknown'

      // Find or create city in database for persistence
      let cityId: number | undefined
      try {
        const cityResponse = await apiClient.findOrCreateCity({
          name: cityName,
          state: stateName,
          latitude: parseFloat(payload.birth_lat),
          longitude: parseFloat(payload.birth_lon),
          display_name: payload.birth_city
        })
        cityId = cityResponse.data.id
        console.log('✅ City saved/found:', cityResponse.data.display_name)
      } catch (cityError) {
        console.warn('Failed to save city, proceeding without city_id:', cityError)
        // Continue with profile creation even if city save fails
      }

      const data = {
        ...payload,
        birth_lat: parseFloat(payload.birth_lat),
        birth_lon: parseFloat(payload.birth_lon),
        gender: payload.gender || undefined, // Send undefined if empty to omit from request
        city_id: cityId, // NEW: Link to cities table
      }
      const response = await apiClient.createProfile(data)
      return response.data
    },
    onSuccess: (data) => {
      // Invalidate profiles cache so the list refreshes
      queryClient.invalidateQueries(['profiles'])
      // Show success toast
      toast({
        title: "Profile Created!",
        description: `${data.name}'s profile has been created successfully`,
        variant: "success"
      })
      // Redirect to the new profile's chart page
      router.push(`/dashboard/chart/${data.id}`)
    },
    onError: (err: any) => {
      const errorMsg = err.response?.data?.detail || 'Failed to create profile'
      setError(errorMsg)
      // Show error toast
      toast({
        title: "Failed to create profile",
        description: errorMsg,
        variant: "destructive"
      })
    },
  })

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    createProfileMutation.mutate(formData)
  }

  return (
    <div className="max-w-2xl mx-auto">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Create Birth Profile</h1>
        <p className="text-gray-600 mt-2">
          Enter your birth details to generate your Vedic birth chart
        </p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Birth Information</CardTitle>
          <CardDescription>
            All fields are required for accurate astrological calculations
          </CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-6">
            {error && (
              <div className="p-3 text-sm text-red-600 bg-red-50 rounded-md">
                {error}
              </div>
            )}

            {/* Name */}
            <div className="space-y-2">
              <Label htmlFor="name">Full Name</Label>
              <Input
                id="name"
                value={formData.name}
                onChange={(e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => setFormData({ ...formData, name: e.target.value })}
                placeholder="John Doe"
                required
                disabled={createProfileMutation.isPending}
              />
            </div>

            {/* Gender (Optional) */}
            <div className="space-y-2">
              <Label htmlFor="gender">Gender (Optional)</Label>
              <Select
                value={formData.gender}
                onValueChange={(value) => setFormData({ ...formData, gender: value })}
                disabled={createProfileMutation.isPending}
              >
                <SelectTrigger>
                  <SelectValue placeholder="Select gender (optional)" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="male">Male</SelectItem>
                  <SelectItem value="female">Female</SelectItem>
                  <SelectItem value="other">Other</SelectItem>
                </SelectContent>
              </Select>
              <p className="text-xs text-gray-500">
                Gender helps provide more personalized astrological interpretations
              </p>
            </div>

            {/* Birth Date and Time */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="birth_date">Birth Date</Label>
                <Input
                  id="birth_date"
                  type="date"
                  value={formData.birth_date}
                  onChange={(e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => setFormData({ ...formData, birth_date: e.target.value })}
                  required
                  disabled={createProfileMutation.isPending}
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="birth_time">Birth Time</Label>
                <Input
                  id="birth_time"
                  type="time"
                  value={formData.birth_time}
                  onChange={(e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => setFormData({ ...formData, birth_time: e.target.value })}
                  required
                  disabled={createProfileMutation.isPending}
                />
                <p className="text-xs text-gray-500">Use 24-hour format (HH:MM)</p>
              </div>
            </div>

            {/* City Selection */}
            <CityAutocomplete
              onCitySelect={handleCitySelect}
              disabled={createProfileMutation.isPending}
              initialValue={formData.birth_city}
            />

            {/* Coordinates */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="birth_lat">Latitude</Label>
                <Input
                  id="birth_lat"
                  type="number"
                  step="0.000001"
                  value={formData.birth_lat}
                  onChange={(e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => setFormData({ ...formData, birth_lat: e.target.value })}
                  placeholder="19.0760"
                  required
                  disabled={createProfileMutation.isPending}
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="birth_lon">Longitude</Label>
                <Input
                  id="birth_lon"
                  type="number"
                  step="0.000001"
                  value={formData.birth_lon}
                  onChange={(e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => setFormData({ ...formData, birth_lon: e.target.value })}
                  placeholder="72.8777"
                  required
                  disabled={createProfileMutation.isPending}
                />
              </div>
            </div>

            {/* Timezone */}
            <div className="space-y-2">
              <Label htmlFor="timezone">Timezone</Label>
              <Select
                value={formData.birth_timezone}
                onValueChange={(value) => setFormData({ ...formData, birth_timezone: value })}
                disabled={createProfileMutation.isPending}
              >
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  {TIMEZONES.map((tz) => (
                    <SelectItem key={tz} value={tz}>
                      {tz}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            {/* Primary Profile */}
            <div className="flex items-center space-x-2">
              <input
                type="checkbox"
                id="is_primary"
                checked={formData.is_primary}
                onChange={(e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => setFormData({ ...formData, is_primary: e.target.checked })}
                className="rounded border-gray-300"
                disabled={createProfileMutation.isPending}
              />
              <Label htmlFor="is_primary" className="font-normal cursor-pointer">
                Set as primary profile
              </Label>
            </div>

            <div className="flex gap-4">
              <Button
                type="submit"
                disabled={createProfileMutation.isPending}
                className="flex-1"
              >
                {createProfileMutation.isPending ? 'Creating...' : 'Create Profile & Generate Chart'}
              </Button>
              <Button
                type="button"
                variant="outline"
                onClick={() => router.back()}
                disabled={createProfileMutation.isPending}
              >
                Cancel
              </Button>
            </div>
          </form>
        </CardContent>
      </Card>

      <div className="mt-6 p-4 bg-blue-50 rounded-lg">
        <p className="text-sm text-gray-700">
          <strong>Tip:</strong> For accurate birth time, check your birth certificate or hospital records.
          Even a few minutes can make a difference in Vedic astrology.
        </p>
      </div>
    </div>
  )
}
