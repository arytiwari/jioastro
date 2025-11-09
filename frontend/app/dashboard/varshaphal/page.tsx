'use client'

import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@/lib/query'
import Link from 'next/link'
import { apiClient } from '@/lib/api'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Skeleton } from '@/components/ui/skeleton'
import { Select } from '@/components/ui/select'
import { Calendar, Sun, Plus, Trash2, RefreshCw, AlertCircle, Sparkles } from '@/components/icons'
import { formatDate } from '@/lib/utils'

export default function VarshapalPage() {
  const queryClient = useQueryClient()
  const currentYear = new Date().getFullYear()
  const [selectedProfileId, setSelectedProfileId] = useState<string>('')
  const [selectedYear, setSelectedYear] = useState<number>(currentYear)

  // Fetch profiles
  const { data: profiles } = useQuery({
    queryKey: ['profiles'],
    queryFn: async () => {
      const response = await apiClient.getProfiles()
      return response.data
    },
  })

  // Fetch varshaphals
  const { data: varshaphals, isLoading } = useQuery({
    queryKey: ['varshaphals', selectedProfileId],
    queryFn: async () => {
      const response = await apiClient.listVarshaphals({
        profile_id: selectedProfileId || undefined,
      })
      return response.data
    },
  })

  // Generate varshaphal mutation
  const generateMutation = useMutation({
    mutationFn: async (data: { profile_id: string; target_year: number }) => {
      const response = await apiClient.generateVarshaphal(data)
      return response.data
    },
    onSuccess: () => {
      queryClient.invalidateQueries(['varshaphals'])
      alert('Varshaphal generated successfully!')
    },
    onError: (error: any) => {
      alert(error?.message || 'Failed to generate Varshaphal')
    },
  })

  // Delete varshaphal mutation
  const deleteMutation = useMutation({
    mutationFn: async (varshaphalId: string) => {
      await apiClient.deleteVarshaphal(varshaphalId)
    },
    onSuccess: () => {
      queryClient.invalidateQueries(['varshaphals'])
    },
    onError: (error: any) => {
      alert(error?.message || 'Failed to delete Varshaphal')
    },
  })

  const handleGenerate = () => {
    if (!selectedProfileId) {
      alert('Please select a profile first')
      return
    }
    generateMutation.mutate({
      profile_id: selectedProfileId,
      target_year: selectedYear,
    })
  }

  const handleDelete = (varshaphalId: string) => {
    if (confirm('Are you sure you want to delete this Varshaphal?')) {
      deleteMutation.mutate(varshaphalId)
    }
  }

  const getProfileName = (profileId: string) => {
    const profile = profiles?.find((p: any) => p.id === profileId)
    return profile?.name || 'Unknown'
  }

  const getQualityColor = (quality: string) => {
    switch (quality.toLowerCase()) {
      case 'excellent':
        return 'text-green-600 bg-green-100'
      case 'mixed':
        return 'text-yellow-600 bg-yellow-100'
      case 'challenging':
        return 'text-red-600 bg-red-100'
      default:
        return 'text-gray-600 bg-gray-100'
    }
  }

  if (isLoading) {
    return (
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <div>
            <Skeleton className="h-9 w-64 mb-2" />
            <Skeleton className="h-5 w-96" />
          </div>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {[1, 2, 3].map((i) => (
            <Card key={i}>
              <CardHeader>
                <Skeleton className="h-6 w-32 mb-2" />
                <Skeleton className="h-4 w-48" />
              </CardHeader>
              <CardContent>
                <Skeleton className="h-4 w-full mb-2" />
                <Skeleton className="h-4 w-32" />
              </CardContent>
            </Card>
          ))}
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-gray-900 flex items-center gap-2">
          <Sun className="w-8 h-8 text-jio-600" />
          Varshaphal (Annual Predictions)
        </h1>
        <p className="text-gray-600 mt-2">
          Solar return charts with yearly predictions, yogas, and remedies
        </p>
      </div>

      {/* Generate New Varshaphal */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Sparkles className="w-5 h-5" />
            Generate New Varshaphal
          </CardTitle>
          <CardDescription>
            Select a profile and year to generate your annual predictions
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="space-y-2">
              <label className="text-sm font-medium">Profile</label>
              <select
                className="w-full px-3 py-2 border rounded-md"
                value={selectedProfileId}
                onChange={(e) => setSelectedProfileId(e.target.value)}
              >
                <option value="">Select a profile</option>
                {profiles?.map((profile: any) => (
                  <option key={profile.id} value={profile.id}>
                    {profile.name}
                  </option>
                ))}
              </select>
            </div>
            <div className="space-y-2">
              <label className="text-sm font-medium">Year</label>
              <select
                className="w-full px-3 py-2 border rounded-md"
                value={selectedYear}
                onChange={(e) => setSelectedYear(Number(e.target.value))}
              >
                {Array.from({ length: 5 }, (_, i) => currentYear - 1 + i).map((year) => (
                  <option key={year} value={year}>
                    {year}
                  </option>
                ))}
              </select>
            </div>
            <div className="flex items-end">
              <Button
                onClick={handleGenerate}
                disabled={!selectedProfileId || generateMutation.isLoading}
                className="w-full"
              >
                {generateMutation.isLoading ? (
                  <>
                    <RefreshCw className="w-4 h-4 mr-2 animate-spin" />
                    Generating...
                  </>
                ) : (
                  <>
                    <Plus className="w-4 h-4 mr-2" />
                    Generate
                  </>
                )}
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Filter */}
      {profiles && profiles.length > 0 && (
        <div className="flex items-center gap-4">
          <label className="text-sm font-medium">Filter by profile:</label>
          <select
            className="px-3 py-2 border rounded-md"
            value={selectedProfileId}
            onChange={(e) => setSelectedProfileId(e.target.value)}
          >
            <option value="">All profiles</option>
            {profiles.map((profile: any) => (
              <option key={profile.id} value={profile.id}>
                {profile.name}
              </option>
            ))}
          </select>
        </div>
      )}

      {/* Varshaphal List */}
      {!varshaphals?.varshaphals || varshaphals.varshaphals.length === 0 ? (
        <Card>
          <CardContent className="text-center py-12">
            <div className="mb-4">
              <Sun className="w-12 h-12 text-gray-400 mx-auto" />
            </div>
            <h3 className="text-lg font-semibold mb-2">No Varshaphals Yet</h3>
            <p className="text-gray-600 mb-6">
              Generate your first Varshaphal to see yearly predictions based on your solar return chart
            </p>
          </CardContent>
        </Card>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {varshaphals.varshaphals.map((varshaphal: any) => (
            <Card key={varshaphal.varshaphal_id} className="hover:shadow-lg transition-shadow">
              <CardHeader>
                <div className="flex items-start justify-between">
                  <div>
                    <CardTitle className="text-xl flex items-center gap-2">
                      <Calendar className="w-5 h-5" />
                      {varshaphal.target_year}
                    </CardTitle>
                    <CardDescription className="mt-2">
                      {varshaphal.profile_name}
                    </CardDescription>
                  </div>
                  <span
                    className={`px-2 py-1 rounded-full text-xs font-semibold ${getQualityColor(
                      varshaphal.overall_quality
                    )}`}
                  >
                    {varshaphal.overall_quality}
                  </span>
                </div>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  <div className="flex items-center justify-between text-sm">
                    <span className="text-gray-600">Yogas Detected:</span>
                    <span className="font-semibold">{varshaphal.yogas_count}</span>
                  </div>
                  <div className="flex items-center gap-2 text-xs text-gray-500">
                    <Calendar className="w-3 h-3" />
                    Generated: {new Date(varshaphal.generated_at).toLocaleDateString()}
                  </div>
                  {varshaphal.is_expired && (
                    <div className="flex items-center gap-2 text-xs text-orange-600">
                      <AlertCircle className="w-3 h-3" />
                      Cache expired - regenerate for fresh data
                    </div>
                  )}
                  <div className="flex gap-2 mt-4">
                    <Link href={`/dashboard/varshaphal/${varshaphal.varshaphal_id}`} className="flex-1">
                      <Button variant="default" className="w-full">
                        View Details
                      </Button>
                    </Link>
                    <Button
                      variant="outline"
                      size="icon"
                      onClick={() => handleDelete(varshaphal.varshaphal_id)}
                      disabled={deleteMutation.isLoading}
                    >
                      <Trash2 className="w-4 h-4" />
                    </Button>
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}

      {/* Info Card */}
      <Card className="bg-blue-50 border-blue-200">
        <CardContent className="pt-6">
          <h4 className="font-semibold mb-2 flex items-center gap-2">
            <AlertCircle className="w-4 h-4 text-blue-600" />
            About Varshaphal
          </h4>
          <p className="text-sm text-gray-700">
            Varshaphal is the ancient Vedic system of annual predictions based on your Solar Return chart
            (when the Sun returns to its exact natal position). It provides insights into the upcoming year
            through special Varshaphal yogas, Patyayini Dasha periods, and sensitive points (Sahams).
          </p>
        </CardContent>
      </Card>
    </div>
  )
}
