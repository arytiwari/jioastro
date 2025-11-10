'use client'

import { useState, useEffect } from 'react'
import { useRouter, useParams } from 'next/navigation'
import { apiClient } from '@/lib/api'
import { useQuery, useMutation, useQueryClient } from '@/lib/query'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { CityAutocomplete } from '@/components/CityAutocomplete'
import { useToast } from '@/hooks/use-toast'

export default function EditProfilePage() {
  const router = useRouter()
  const params = useParams()
  const profileId = params.id as string
  const queryClient = useQueryClient()
  const { toast } = useToast()
  const [error, setError] = useState('')

  const [formData, setFormData] = useState({
    name: '',
    gender: '',
    is_primary: false,
    birth_city: '',
    birth_lat: 0,
    birth_lon: 0,
  })

  // Fetch existing profile data
  const { data: profile, isLoading } = useQuery({
    queryKey: ['profile', profileId],
    queryFn: async () => {
      const response = await apiClient.getProfile(profileId)
      return response.data
    },
  })

  // Update form data when profile loads
  useEffect(() => {
    if (profile) {
      setFormData({
        name: profile.name || '',
        gender: profile.gender || '',
        is_primary: profile.is_primary || false,
        birth_city: profile.city?.display_name || profile.birth_city || '',
        birth_lat: profile.birth_lat || 0,
        birth_lon: profile.birth_lon || 0,
      })
    }
  }, [profile])

  const handleCitySelect = (city: { id: number; name: string; state: string; latitude: number; longitude: number; display_name: string }) => {
    setFormData(prev => ({
      ...prev,
      birth_city: city.display_name,
      birth_lat: city.latitude,
      birth_lon: city.longitude,
    }))
  }

  const updateProfileMutation = useMutation({
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
          latitude: payload.birth_lat,
          longitude: payload.birth_lon,
          display_name: payload.birth_city
        })
        cityId = cityResponse.data.id
        console.log('✅ City saved/found:', cityResponse.data.display_name)
      } catch (cityError) {
        console.warn('Failed to save city, proceeding without city_id:', cityError)
        // Continue with profile update even if city save fails
      }

      const data = {
        name: payload.name,
        gender: payload.gender || undefined,
        is_primary: payload.is_primary,
        birth_city: payload.birth_city,
        city_id: cityId,
      }
      const response = await apiClient.updateProfile(profileId, data)
      return response.data
    },
    onSuccess: (data) => {
      // Invalidate queries to refresh data
      queryClient.invalidateQueries(['profiles'])
      queryClient.invalidateQueries(['profile', profileId])

      // Show success toast
      toast({
        title: "Profile Updated!",
        description: `${data.name}'s profile has been updated successfully`,
        variant: "success"
      })

      // Redirect back to chart page
      router.push(`/dashboard/chart/${profileId}`)
    },
    onError: (err: any) => {
      const errorMsg = err.response?.data?.detail || 'Failed to update profile'
      setError(errorMsg)
      toast({
        title: "Failed to update profile",
        description: errorMsg,
        variant: "destructive"
      })
    },
  })

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    updateProfileMutation.mutate(formData)
  }

  if (isLoading) {
    return (
      <div className="max-w-2xl mx-auto">
        <div className="text-center py-12">
          <div className="w-8 h-8 border-4 border-jio-600 border-t-transparent rounded-full animate-spin mx-auto"></div>
          <p className="text-gray-600 mt-4">Loading profile...</p>
        </div>
      </div>
    )
  }

  if (!profile) {
    return (
      <div className="max-w-2xl mx-auto">
        <Card>
          <CardContent className="text-center py-12">
            <p className="text-red-600">Profile not found</p>
            <Button onClick={() => router.push('/dashboard/profiles')} className="mt-4">
              Back to Profiles
            </Button>
          </CardContent>
        </Card>
      </div>
    )
  }

  return (
    <div className="max-w-2xl mx-auto">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Edit Profile</h1>
        <p className="text-gray-600 mt-2">
          Update profile information for {profile.name}
        </p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Profile Information</CardTitle>
          <CardDescription>
            You can update name, gender, city, and primary profile status
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
                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                placeholder="John Doe"
                required
                disabled={updateProfileMutation.isPending}
              />
            </div>

            {/* Gender */}
            <div className="space-y-2">
              <Label htmlFor="gender">Gender (Optional)</Label>
              <Select
                value={formData.gender}
                onValueChange={(value) => setFormData({ ...formData, gender: value })}
                disabled={updateProfileMutation.isPending}
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

            {/* City Selection */}
            <div className="space-y-2">
              <Label>Birth City</Label>
              <CityAutocomplete
                onCitySelect={handleCitySelect}
                disabled={updateProfileMutation.isPending}
                initialValue={formData.birth_city}
              />
              <p className="text-xs text-gray-500">
                Update the birth city to ensure it's saved in the database
              </p>
            </div>

            {/* Current Coordinates (read-only) */}
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label>Current Latitude</Label>
                <Input
                  type="text"
                  value={formData.birth_lat.toFixed(6)}
                  disabled
                  className="bg-gray-50"
                />
              </div>
              <div className="space-y-2">
                <Label>Current Longitude</Label>
                <Input
                  type="text"
                  value={formData.birth_lon.toFixed(6)}
                  disabled
                  className="bg-gray-50"
                />
              </div>
            </div>

            {/* Primary Profile */}
            <div className="flex items-center space-x-2">
              <input
                type="checkbox"
                id="is_primary"
                checked={formData.is_primary}
                onChange={(e) => setFormData({ ...formData, is_primary: e.target.checked })}
                className="rounded border-gray-300"
                disabled={updateProfileMutation.isPending}
              />
              <Label htmlFor="is_primary" className="font-normal cursor-pointer">
                Set as primary profile
              </Label>
            </div>

            <div className="flex gap-4">
              <Button
                type="submit"
                disabled={updateProfileMutation.isPending}
                className="flex-1"
              >
                {updateProfileMutation.isPending ? 'Updating...' : 'Update Profile'}
              </Button>
              <Button
                type="button"
                variant="outline"
                onClick={() => router.back()}
                disabled={updateProfileMutation.isPending}
              >
                Cancel
              </Button>
            </div>
          </form>
        </CardContent>
      </Card>

      <div className="mt-6 p-4 bg-blue-50 rounded-lg">
        <p className="text-sm text-gray-700">
          <strong>Note:</strong> Birth date, time, and coordinates cannot be changed as they affect all astrological calculations. If you need to change these, please create a new profile.
        </p>
      </div>
    </div>
  )
}
