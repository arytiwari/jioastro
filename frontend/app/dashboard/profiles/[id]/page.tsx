'use client'

import { useEffect, useState } from 'react'
import { useParams, useRouter } from 'next/navigation'
import { useQuery } from '@/lib/query'
import { apiClient } from '@/lib/api'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { BirthChartNew as BirthChart } from '@/components/chart/BirthChartNew'
import { PlanetPositions } from '@/components/chart/PlanetPositions'
import { YogaList } from '@/components/chart/YogaList'
import { VimshottariDashaTable } from '@/components/chart/VimshottariDashaTable'
import { ArrowLeft, Calendar, MapPin, Sparkles } from '@/components/icons'
import Link from 'next/link'
import { formatDate, formatTime } from '@/lib/utils'

export default function ProfileViewPage() {
  const params = useParams()
  const router = useRouter()
  const profileId = params.id as string

  // Fetch profile
  const { data: profile, isLoading: profileLoading } = useQuery({
    queryKey: ['profile', profileId],
    queryFn: async () => {
      const response = await apiClient.getProfile(profileId)
      return response.data
    },
  })

  // Fetch D1 chart
  const { data: d1Chart, isLoading: d1Loading } = useQuery({
    queryKey: ['chart', profileId, 'D1'],
    queryFn: async () => {
      try {
        // Try to get existing chart
        const response = await apiClient.getChart(profileId, 'D1')
        return response.data
      } catch (error: any) {
        // If not found, calculate it
        if (error.response?.status === 404) {
          const response = await apiClient.calculateChart(profileId, 'D1')
          return response.data
        }
        throw error
      }
    },
    enabled: !!profile,
  })

  // Fetch D9 chart
  const { data: d9Chart, isLoading: d9Loading } = useQuery({
    queryKey: ['chart', profileId, 'D9'],
    queryFn: async () => {
      try {
        const response = await apiClient.getChart(profileId, 'D9')
        return response.data
      } catch (error: any) {
        if (error.response?.status === 404) {
          const response = await apiClient.calculateChart(profileId, 'D9')
          return response.data
        }
        throw error
      }
    },
    enabled: !!profile,
  })

  if (profileLoading) {
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
        <p className="text-red-600">Profile not found</p>
        <Button className="mt-4" onClick={() => router.push('/dashboard/profiles')}>
          Back to Profiles
        </Button>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          <Link href="/dashboard/profiles">
            <Button variant="ghost" size="icon">
              <ArrowLeft className="w-4 h-4" />
            </Button>
          </Link>
          <div>
            <h1 className="text-3xl font-bold text-gray-900 flex items-center gap-2">
              {profile.name}
              {profile.is_primary && (
                <span className="text-sm bg-jio-100 text-jio-700 px-2 py-1 rounded font-normal">
                  Primary
                </span>
              )}
            </h1>
            <div className="flex items-center gap-4 text-gray-600 mt-2">
              <span className="flex items-center gap-1">
                <Calendar className="w-4 h-4" />
                {formatDate(profile.birth_date)} at {formatTime(profile.birth_time)}
              </span>
              {profile.birth_city && (
                <span className="flex items-center gap-1">
                  <MapPin className="w-4 h-4" />
                  {profile.birth_city}
                </span>
              )}
            </div>
          </div>
        </div>

        <Link href="/dashboard/ask">
          <Button>
            <Sparkles className="w-4 h-4 mr-2" />
            Ask Question
          </Button>
        </Link>
      </div>

      {/* Charts Tabs */}
      <Tabs defaultValue="d1" className="w-full">
        <TabsList className="grid w-full max-w-md grid-cols-2">
          <TabsTrigger value="d1">D1 - Rashi Chart</TabsTrigger>
          <TabsTrigger value="d9">D9 - Navamsa</TabsTrigger>
        </TabsList>

        {/* D1 Chart */}
        <TabsContent value="d1" className="space-y-6">
          {d1Loading ? (
            <Card>
              <CardContent className="text-center py-12">
                <div className="w-8 h-8 border-4 border-jio-600 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
                <p className="text-gray-600">Calculating birth chart...</p>
              </CardContent>
            </Card>
          ) : d1Chart ? (
            <>
              {/* Chart Visualization */}
              <Card>
                <CardHeader>
                  <CardTitle>Birth Chart (Rashi - D1)</CardTitle>
                  <CardDescription>
                    Your main birth chart showing planetary positions at birth
                  </CardDescription>
                </CardHeader>
                <CardContent className="flex justify-center">
                  <BirthChart
                    key="d1-chart"
                    chartData={d1Chart.chart_data}
                    chartType="D1"
                    width={500}
                    height={500}
                  />
                </CardContent>
              </Card>

              {/* Planetary Positions */}
              <PlanetPositions planets={d1Chart.chart_data.planets} />

              {/* Vimshottari Dasha Table */}
              {d1Chart.chart_data.dasha && (
                <VimshottariDashaTable dasha={d1Chart.chart_data.dasha} />
              )}

              {/* Yogas */}
              {d1Chart.chart_data.yogas && d1Chart.chart_data.yogas.length > 0 && (
                <YogaList yogas={d1Chart.chart_data.yogas} />
              )}
            </>
          ) : (
            <Card>
              <CardContent className="text-center py-12">
                <p className="text-red-600">Failed to load chart</p>
              </CardContent>
            </Card>
          )}
        </TabsContent>

        {/* D9 Chart */}
        <TabsContent value="d9" className="space-y-6">
          {d9Loading ? (
            <Card>
              <CardContent className="text-center py-12">
                <div className="w-8 h-8 border-4 border-jio-600 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
                <p className="text-gray-600">Calculating Navamsa chart...</p>
              </CardContent>
            </Card>
          ) : d9Chart ? (
            <>
              <Card>
                <CardHeader>
                  <CardTitle>Navamsa Chart (D9)</CardTitle>
                  <CardDescription>
                    The D9 chart reveals the deeper layers of your karma, especially related to
                    marriage, spirituality, and the second half of life
                  </CardDescription>
                </CardHeader>
                <CardContent className="flex justify-center">
                  <BirthChart
                    key="d9-chart"
                    chartData={d9Chart.chart_data}
                    chartType="D9"
                    width={500}
                    height={500}
                  />
                </CardContent>
              </Card>

              {/* Navamsa Planetary Positions */}
              <PlanetPositions planets={d9Chart.chart_data.planets} />

              <Card className="bg-blue-50">
                <CardContent className="py-6">
                  <h3 className="font-semibold mb-2">About Navamsa (D9)</h3>
                  <p className="text-sm text-gray-700">
                    The Navamsa chart is one of the most important divisional charts in Vedic astrology.
                    It shows:
                  </p>
                  <ul className="text-sm text-gray-700 list-disc list-inside mt-2 space-y-1">
                    <li>The strength of planets in the birth chart</li>
                    <li>Insights about marriage and relationships</li>
                    <li>Spiritual inclinations and dharma</li>
                    <li>The fruits of karma in the second half of life</li>
                  </ul>
                </CardContent>
              </Card>
            </>
          ) : (
            <Card>
              <CardContent className="text-center py-12">
                <p className="text-red-600">Failed to load Navamsa chart</p>
              </CardContent>
            </Card>
          )}
        </TabsContent>
      </Tabs>
    </div>
  )
}
