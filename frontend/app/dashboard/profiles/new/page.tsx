'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import { apiClient } from '@/lib/api'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'

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

const INDIAN_CITIES = [
  { name: 'Mumbai', lat: 19.0760, lon: 72.8777 },
  { name: 'Delhi', lat: 28.7041, lon: 77.1025 },
  { name: 'Bangalore', lat: 12.9716, lon: 77.5946 },
  { name: 'Kolkata', lat: 22.5726, lon: 88.3639 },
  { name: 'Chennai', lat: 13.0827, lon: 80.2707 },
  { name: 'Hyderabad', lat: 17.3850, lon: 78.4867 },
  { name: 'Pune', lat: 18.5204, lon: 73.8567 },
  { name: 'Ahmedabad', lat: 23.0225, lon: 72.5714 },
]

export default function NewProfilePage() {
  const router = useRouter()
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const [formData, setFormData] = useState({
    name: '',
    birth_date: '',
    birth_time: '',
    birth_city: '',
    birth_lat: '',
    birth_lon: '',
    birth_timezone: 'Asia/Kolkata',
    is_primary: false,
  })

  const handleCitySelect = (cityName: string) => {
    const city = INDIAN_CITIES.find(c => c.name === cityName)
    if (city) {
      setFormData(prev => ({
        ...prev,
        birth_city: city.name,
        birth_lat: city.lat.toString(),
        birth_lon: city.lon.toString(),
      }))
    }
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    setLoading(true)

    try {
      const payload = {
        ...formData,
        birth_lat: parseFloat(formData.birth_lat),
        birth_lon: parseFloat(formData.birth_lon),
      }

      const response = await apiClient.createProfile(payload)

      // Redirect to the new profile's chart page
      router.push(`/dashboard/profiles/${response.data.id}`)
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to create profile')
    } finally {
      setLoading(false)
    }
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
                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                placeholder="John Doe"
                required
                disabled={loading}
              />
            </div>

            {/* Birth Date and Time */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="birth_date">Birth Date</Label>
                <Input
                  id="birth_date"
                  type="date"
                  value={formData.birth_date}
                  onChange={(e) => setFormData({ ...formData, birth_date: e.target.value })}
                  required
                  disabled={loading}
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="birth_time">Birth Time</Label>
                <Input
                  id="birth_time"
                  type="time"
                  value={formData.birth_time}
                  onChange={(e) => setFormData({ ...formData, birth_time: e.target.value })}
                  required
                  disabled={loading}
                />
                <p className="text-xs text-gray-500">Use 24-hour format (HH:MM)</p>
              </div>
            </div>

            {/* City Selection */}
            <div className="space-y-2">
              <Label htmlFor="city">Birth City (Quick Select)</Label>
              <Select onValueChange={handleCitySelect} disabled={loading}>
                <SelectTrigger>
                  <SelectValue placeholder="Select a city" />
                </SelectTrigger>
                <SelectContent>
                  {INDIAN_CITIES.map((city) => (
                    <SelectItem key={city.name} value={city.name}>
                      {city.name}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
              <p className="text-xs text-gray-500">
                Or enter custom coordinates below
              </p>
            </div>

            {/* Manual City Name */}
            <div className="space-y-2">
              <Label htmlFor="birth_city">City Name (Optional)</Label>
              <Input
                id="birth_city"
                value={formData.birth_city}
                onChange={(e) => setFormData({ ...formData, birth_city: e.target.value })}
                placeholder="City name"
                disabled={loading}
              />
            </div>

            {/* Coordinates */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="birth_lat">Latitude</Label>
                <Input
                  id="birth_lat"
                  type="number"
                  step="0.000001"
                  value={formData.birth_lat}
                  onChange={(e) => setFormData({ ...formData, birth_lat: e.target.value })}
                  placeholder="19.0760"
                  required
                  disabled={loading}
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="birth_lon">Longitude</Label>
                <Input
                  id="birth_lon"
                  type="number"
                  step="0.000001"
                  value={formData.birth_lon}
                  onChange={(e) => setFormData({ ...formData, birth_lon: e.target.value })}
                  placeholder="72.8777"
                  required
                  disabled={loading}
                />
              </div>
            </div>

            {/* Timezone */}
            <div className="space-y-2">
              <Label htmlFor="timezone">Timezone</Label>
              <Select
                value={formData.birth_timezone}
                onValueChange={(value) => setFormData({ ...formData, birth_timezone: value })}
                disabled={loading}
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
                onChange={(e) => setFormData({ ...formData, is_primary: e.target.checked })}
                className="rounded border-gray-300"
                disabled={loading}
              />
              <Label htmlFor="is_primary" className="font-normal cursor-pointer">
                Set as primary profile
              </Label>
            </div>

            <div className="flex gap-4">
              <Button
                type="submit"
                disabled={loading}
                className="flex-1"
              >
                {loading ? 'Creating...' : 'Create Profile & Generate Chart'}
              </Button>
              <Button
                type="button"
                variant="outline"
                onClick={() => router.back()}
                disabled={loading}
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
