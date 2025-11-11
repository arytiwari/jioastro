'use client'

import { useEffect, useState } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Checkbox } from '@/components/ui/checkbox'
import { apiClient } from '@/lib/api'
import {
  Loader2,
  Users,
  ArrowLeft,
  TrendingUp,
  Target,
  Sparkles,
  AlertCircle,
  CheckCircle2,
  XCircle,
} from 'lucide-react'
import Link from 'next/link'

interface Profile {
  id: string
  name: string
  birth_date: string
}

interface ProfileComparison {
  profile_id: string
  profile_name: string
  total_yogas: number
  yoga_names: string[]
  strongest_yogas: string[]
  bphs_statistics: Record<string, number>
  classical_count: number
  practical_count: number
}

interface UniqueYogas {
  profile_id: string
  profile_name: string
  unique_yogas: string[]
  unique_count: number
}

interface ComparisonResult {
  comparison_results: ProfileComparison[]
  common_yogas: string[]
  unique_yogas_per_profile: UniqueYogas[]
  similarity_matrix: Record<string, Record<string, number>>
}

export default function YogaComparePage() {
  const [profiles, setProfiles] = useState<Profile[]>([])
  const [selectedProfiles, setSelectedProfiles] = useState<string[]>([])
  const [comparisonResult, setComparisonResult] = useState<ComparisonResult | null>(null)
  const [loading, setLoading] = useState(false)
  const [loadingProfiles, setLoadingProfiles] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    loadProfiles()
  }, [])

  const loadProfiles = async () => {
    try {
      setLoadingProfiles(true)
      const response = await apiClient.getProfiles()
      setProfiles(response.data)
    } catch (err: any) {
      console.error('Failed to load profiles:', err)
      setError('Failed to load profiles')
    } finally {
      setLoadingProfiles(false)
    }
  }

  const handleProfileToggle = (profileId: string) => {
    setSelectedProfiles((prev) => {
      if (prev.includes(profileId)) {
        return prev.filter((id) => id !== profileId)
      } else {
        if (prev.length >= 5) {
          setError('Maximum 5 profiles can be compared')
          return prev
        }
        return [...prev, profileId]
      }
    })
    setError(null)
  }

  const handleCompare = async () => {
    if (selectedProfiles.length < 2) {
      setError('Please select at least 2 profiles to compare')
      return
    }

    try {
      setLoading(true)
      setError(null)
      const response = await apiClient.compareYogasAcrossProfiles(selectedProfiles)
      setComparisonResult(response.data)
    } catch (err: any) {
      console.error('Failed to compare yogas:', err)
      setError(err.message || 'Failed to compare yogas')
      setComparisonResult(null)
    } finally {
      setLoading(false)
    }
  }

  const resetComparison = () => {
    setSelectedProfiles([])
    setComparisonResult(null)
    setError(null)
  }

  if (loadingProfiles) {
    return (
      <div className="container max-w-7xl mx-auto px-4 py-8">
        <div className="flex items-center justify-center min-h-[400px]">
          <div className="text-center">
            <Loader2 className="h-8 w-8 animate-spin text-primary mx-auto mb-4" />
            <p className="text-gray-600">Loading profiles...</p>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="container max-w-7xl mx-auto px-4 py-8">
      {/* Header */}
      <div className="mb-8">
        <Link href="/dashboard/yogas">
          <Button variant="ghost" size="sm" className="mb-4">
            <ArrowLeft className="h-4 w-4 mr-2" />
            Back to Yogas
          </Button>
        </Link>
        <div className="flex items-start justify-between flex-wrap gap-4">
          <div>
            <h1 className="text-3xl font-bold text-gray-900 mb-2">Multi-Profile Yoga Comparison</h1>
            <p className="text-gray-600">
              Compare yogas across family members, partners, or friends (2-5 profiles)
            </p>
          </div>
          {selectedProfiles.length > 0 && (
            <Badge variant="outline" className="bg-purple-50 text-purple-700 border-purple-300 text-lg px-4 py-2">
              {selectedProfiles.length} selected
            </Badge>
          )}
        </div>
      </div>

      {/* Profile Selection */}
      {!comparisonResult && (
        <Card className="mb-8">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Users className="h-5 w-5 text-purple-600" />
              Select Profiles to Compare
            </CardTitle>
            <CardDescription>
              Choose 2-5 profiles to analyze common and unique yogas
            </CardDescription>
          </CardHeader>
          <CardContent>
            {profiles.length === 0 ? (
              <div className="text-center py-8">
                <AlertCircle className="h-12 w-12 text-gray-300 mx-auto mb-4" />
                <p className="text-gray-600 mb-4">No profiles found. Create a profile first.</p>
                <Link href="/dashboard/profiles">
                  <Button>Create Profile</Button>
                </Link>
              </div>
            ) : (
              <>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 mb-6">
                  {profiles.map((profile) => {
                    const isSelected = selectedProfiles.includes(profile.id)
                    return (
                      <div
                        key={profile.id}
                        className={`p-4 rounded-lg border-2 cursor-pointer transition-all ${
                          isSelected
                            ? 'border-purple-500 bg-purple-50'
                            : 'border-gray-200 hover:border-purple-300 hover:bg-gray-50'
                        }`}
                        onClick={() => handleProfileToggle(profile.id)}
                      >
                        <div className="flex items-start justify-between">
                          <div className="flex-1">
                            <h3 className="font-semibold text-gray-900">{profile.name}</h3>
                            <p className="text-sm text-gray-600 mt-1">
                              {new Date(profile.birth_date).toLocaleDateString()}
                            </p>
                          </div>
                          <Checkbox
                            checked={isSelected}
                            onCheckedChange={() => handleProfileToggle(profile.id)}
                          />
                        </div>
                      </div>
                    )
                  })}
                </div>

                {error && (
                  <div className="mb-4 p-4 rounded-lg bg-red-50 border border-red-200">
                    <div className="flex items-start gap-3">
                      <AlertCircle className="h-5 w-5 text-red-600 mt-0.5 shrink-0" />
                      <p className="text-red-900">{error}</p>
                    </div>
                  </div>
                )}

                <div className="flex justify-center">
                  <Button
                    onClick={handleCompare}
                    disabled={selectedProfiles.length < 2 || loading}
                    size="lg"
                  >
                    {loading ? (
                      <Loader2 className="h-5 w-5 animate-spin mr-2" />
                    ) : (
                      <TrendingUp className="h-5 w-5 mr-2" />
                    )}
                    {loading ? 'Comparing...' : `Compare ${selectedProfiles.length} Profiles`}
                  </Button>
                </div>
              </>
            )}
          </CardContent>
        </Card>
      )}

      {/* Comparison Results */}
      {comparisonResult && (
        <>
          {/* Summary Header */}
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-2xl font-bold text-gray-900">Comparison Results</h2>
            <Button variant="outline" onClick={resetComparison}>
              <XCircle className="h-4 w-4 mr-2" />
              New Comparison
            </Button>
          </div>

          {/* Common Yogas */}
          <Card className="mb-8 border-emerald-200 bg-emerald-50/50">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <CheckCircle2 className="h-5 w-5 text-emerald-600" />
                Common Yogas ({comparisonResult.common_yogas.length})
              </CardTitle>
              <CardDescription>Yogas shared by all selected profiles</CardDescription>
            </CardHeader>
            <CardContent>
              {comparisonResult.common_yogas.length === 0 ? (
                <p className="text-gray-600 text-center py-4">
                  No yogas are common across all profiles
                </p>
              ) : (
                <div className="flex flex-wrap gap-2">
                  {comparisonResult.common_yogas.map((yoga, index) => (
                    <Badge
                      key={index}
                      variant="secondary"
                      className="bg-emerald-100 text-emerald-800 border border-emerald-300"
                    >
                      {yoga}
                    </Badge>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>

          {/* Per-Profile Analysis */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
            {comparisonResult.comparison_results.map((result, index) => (
              <Card key={index} className="border-purple-200">
                <CardHeader>
                  <CardTitle className="text-lg">{result.profile_name}</CardTitle>
                  <CardDescription>
                    {result.total_yogas} total yogas • {result.classical_count} classical •{' '}
                    {result.practical_count} practical
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  {/* BPHS Statistics */}
                  <div>
                    <h4 className="font-medium text-gray-900 mb-2 text-sm">BPHS Categories</h4>
                    <div className="space-y-1">
                      {Object.entries(result.bphs_statistics).map(([category, count]) => (
                        <div key={category} className="flex items-center justify-between text-sm">
                          <span className="text-gray-600">{category}</span>
                          <Badge variant="secondary" className="ml-2">
                            {count}
                          </Badge>
                        </div>
                      ))}
                    </div>
                  </div>

                  {/* Strongest Yogas */}
                  {result.strongest_yogas.length > 0 && (
                    <div>
                      <h4 className="font-medium text-gray-900 mb-2 text-sm flex items-center gap-1">
                        <Sparkles className="h-3 w-3 text-amber-600" />
                        Very Strong Yogas
                      </h4>
                      <div className="flex flex-wrap gap-1">
                        {result.strongest_yogas.slice(0, 5).map((yoga, i) => (
                          <Badge
                            key={i}
                            variant="outline"
                            className="bg-amber-50 text-amber-800 border-amber-300 text-xs"
                          >
                            {yoga}
                          </Badge>
                        ))}
                        {result.strongest_yogas.length > 5 && (
                          <Badge variant="outline" className="text-xs">
                            +{result.strongest_yogas.length - 5} more
                          </Badge>
                        )}
                      </div>
                    </div>
                  )}
                </CardContent>
              </Card>
            ))}
          </div>

          {/* Unique Yogas */}
          <Card className="border-blue-200 bg-blue-50/50">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Target className="h-5 w-5 text-blue-600" />
                Unique Yogas
              </CardTitle>
              <CardDescription>Yogas unique to each profile (not shared with others)</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {comparisonResult.unique_yogas_per_profile.map((uniqueResult, index) => (
                  <div key={index} className="p-4 rounded-lg bg-white border border-blue-200">
                    <div className="flex items-center justify-between mb-3">
                      <h3 className="font-semibold text-gray-900">{uniqueResult.profile_name}</h3>
                      <Badge variant="outline" className="bg-blue-100 text-blue-800 border-blue-300">
                        {uniqueResult.unique_count} unique
                      </Badge>
                    </div>
                    {uniqueResult.unique_yogas.length === 0 ? (
                      <p className="text-sm text-gray-600">
                        No unique yogas (all yogas are shared with at least one other profile)
                      </p>
                    ) : (
                      <div className="flex flex-wrap gap-2">
                        {uniqueResult.unique_yogas.map((yoga, i) => (
                          <Badge
                            key={i}
                            variant="secondary"
                            className="bg-blue-100 text-blue-800"
                          >
                            {yoga}
                          </Badge>
                        ))}
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>

          {/* Similarity Matrix */}
          {comparisonResult.similarity_matrix &&
            Object.keys(comparisonResult.similarity_matrix).length > 0 && (
              <Card className="mt-8 border-purple-200">
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <TrendingUp className="h-5 w-5 text-purple-600" />
                    Similarity Matrix
                  </CardTitle>
                  <CardDescription>
                    Percentage of shared yogas between each pair of profiles
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="overflow-x-auto">
                    <table className="w-full">
                      <thead>
                        <tr>
                          <th className="p-2 text-left text-sm font-medium text-gray-700">
                            Profile
                          </th>
                          {comparisonResult.comparison_results.map((result) => (
                            <th
                              key={result.profile_id}
                              className="p-2 text-center text-sm font-medium text-gray-700"
                            >
                              {result.profile_name.split(' ')[0]}
                            </th>
                          ))}
                        </tr>
                      </thead>
                      <tbody>
                        {comparisonResult.comparison_results.map((rowResult) => (
                          <tr key={rowResult.profile_id} className="border-t border-gray-200">
                            <td className="p-2 text-sm font-medium text-gray-900">
                              {rowResult.profile_name}
                            </td>
                            {comparisonResult.comparison_results.map((colResult) => {
                              const similarity =
                                comparisonResult.similarity_matrix[rowResult.profile_id]?.[
                                  colResult.profile_id
                                ] || 0
                              const isSelf = rowResult.profile_id === colResult.profile_id
                              return (
                                <td
                                  key={colResult.profile_id}
                                  className="p-2 text-center text-sm"
                                >
                                  {isSelf ? (
                                    <span className="text-gray-400">-</span>
                                  ) : (
                                    <Badge
                                      variant="secondary"
                                      className={
                                        similarity >= 70
                                          ? 'bg-emerald-100 text-emerald-800'
                                          : similarity >= 50
                                          ? 'bg-blue-100 text-blue-800'
                                          : 'bg-gray-100 text-gray-800'
                                      }
                                    >
                                      {similarity.toFixed(0)}%
                                    </Badge>
                                  )}
                                </td>
                              )
                            })}
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                  <p className="text-xs text-gray-600 mt-4">
                    Higher percentages indicate more yogas in common between profiles
                  </p>
                </CardContent>
              </Card>
            )}
        </>
      )}
    </div>
  )
}
