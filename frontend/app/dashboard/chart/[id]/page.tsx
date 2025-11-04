'use client'

import { useEffect, useState } from 'react'
import { useParams, useRouter } from 'next/navigation'
import { useQuery } from '@/lib/query'
import { apiClient } from '@/lib/api'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { ChartSelector } from '@/components/chart/ChartSelector'
import { DasaTimeline } from '@/components/chart/DasaTimeline'
import { YogaDisplay } from '@/components/chart/YogaDisplay'
import { PlanetaryPositionsTable } from '@/components/chart/PlanetaryPositionsTable'
import { ArrowLeft, Calendar, MapPin, Sparkles, Download, RefreshCw } from '@/components/icons'
import Link from 'next/link'
import { formatDate, formatTime } from '@/lib/utils'

export default function EnhancedChartPage() {
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

  // Fetch D1 chart (existing service)
  const { data: d1Chart, isLoading: d1Loading, error: d1Error } = useQuery({
    queryKey: ['chart', profileId, 'D1'],
    queryFn: async () => {
      try {
        const response = await apiClient.getChart(profileId, 'D1')
        return response.data
      } catch (error: any) {
        // Check for 404 status and auto-calculate if chart doesn't exist
        if (error.status === 404) {
          console.log('D1 chart not found, calculating...')
          const response = await apiClient.calculateChart(profileId, 'D1')
          return response.data
        }
        throw error
      }
    },
    enabled: !!profile,
  })

  // Fetch D9 chart (existing service)
  const { data: d9Chart, isLoading: d9Loading, error: d9Error } = useQuery({
    queryKey: ['chart', profileId, 'D9'],
    queryFn: async () => {
      try {
        const response = await apiClient.getChart(profileId, 'D9')
        return response.data
      } catch (error: any) {
        // Check for 404 status and auto-calculate if chart doesn't exist
        if (error.status === 404) {
          console.log('D9 chart not found, calculating...')
          const response = await apiClient.calculateChart(profileId, 'D9')
          return response.data
        }
        throw error
      }
    },
    enabled: !!profile,
  })

  // Fetch Moon chart
  const { data: moonChart, isLoading: moonLoading, error: moonError } = useQuery({
    queryKey: ['chart', profileId, 'Moon'],
    queryFn: async () => {
      try {
        const response = await apiClient.getChart(profileId, 'Moon')
        return response.data
      } catch (error: any) {
        // Check for 404 status and auto-calculate if chart doesn't exist
        if (error.status === 404) {
          console.log('Moon chart not found, calculating...')
          const response = await apiClient.calculateChart(profileId, 'Moon')
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
      <div className="flex items-center justify-between flex-wrap gap-4">
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
            <div className="flex items-center gap-4 text-gray-600 mt-2 flex-wrap">
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

        <div className="flex gap-2">
          <Link href="/dashboard/ask">
            <Button>
              <Sparkles className="w-4 h-4 mr-2" />
              Ask Question
            </Button>
          </Link>
        </div>
      </div>

      {/* Main Content Tabs */}
      <Tabs defaultValue="overview" className="w-full">
        <TabsList className="grid w-full max-w-3xl grid-cols-5">
          <TabsTrigger value="overview">Overview</TabsTrigger>
          <TabsTrigger value="d1">D1 Chart</TabsTrigger>
          <TabsTrigger value="moon">Moon Chart</TabsTrigger>
          <TabsTrigger value="d9">D9 Chart</TabsTrigger>
          <TabsTrigger value="dasha">Dasha</TabsTrigger>
        </TabsList>

        {/* Overview Tab - Comprehensive View */}
        <TabsContent value="overview" className="space-y-6">
          {d1Loading ? (
            <Card>
              <CardContent className="text-center py-12">
                <div className="w-8 h-8 border-4 border-jio-600 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
                <p className="text-gray-600">Calculating birth chart...</p>
              </CardContent>
            </Card>
          ) : d1Chart ? (
            <>
              {/* Chart with Selector */}
              <Card>
                <CardHeader>
                  <CardTitle>Birth Chart (Multiple Styles)</CardTitle>
                  <CardDescription>
                    Switch between North Indian, South Indian, and Western circular chart styles
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <ChartSelector chartData={d1Chart.chart_data} defaultChart="north" />
                </CardContent>
              </Card>

              {/* Yogas */}
              {d1Chart.chart_data.yogas && d1Chart.chart_data.yogas.length > 0 && (
                <YogaDisplay yogas={d1Chart.chart_data.yogas} />
              )}

              {/* Dasha Timeline */}
              {d1Chart.chart_data.dasha && (
                <DasaTimeline dashaData={d1Chart.chart_data.dasha} />
              )}

              {/* Quick Info Cards */}
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <Card>
                  <CardHeader className="pb-3">
                    <CardTitle className="text-sm font-medium">Ascendant</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="text-2xl font-bold text-jio-700">
                      {d1Chart.chart_data.ascendant.sign}
                    </div>
                    <p className="text-xs text-gray-500 mt-1">Rising sign at birth</p>
                  </CardContent>
                </Card>

                <Card>
                  <CardHeader className="pb-3">
                    <CardTitle className="text-sm font-medium">Moon Sign</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="text-2xl font-bold text-blue-700">
                      {d1Chart.chart_data.planets.Moon?.sign || 'N/A'}
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
                      {d1Chart.chart_data.planets.Sun?.sign || 'N/A'}
                    </div>
                    <p className="text-xs text-gray-500 mt-1">Core personality</p>
                  </CardContent>
                </Card>
              </div>
            </>
          ) : (
            <Card>
              <CardContent className="text-center py-12">
                <p className="text-red-600">Failed to load chart</p>
              </CardContent>
            </Card>
          )}
        </TabsContent>

        {/* D1 Chart Tab */}
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
              <Card>
                <CardHeader>
                  <CardTitle>Birth Chart (Rashi - D1)</CardTitle>
                  <CardDescription>
                    Your main birth chart showing planetary positions at birth
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <ChartSelector chartData={d1Chart.chart_data} defaultChart="north" />
                </CardContent>
              </Card>

              {/* Planetary Positions Table */}
              <PlanetaryPositionsTable
                planets={d1Chart.chart_data.planets}
                title="Planetary Positions"
                description="Detailed positions of all planets in the birth chart"
              />
            </>
          ) : null}
        </TabsContent>

        {/* Moon Chart Tab */}
        <TabsContent value="moon" className="space-y-6">
          {moonLoading ? (
            <Card>
              <CardContent className="text-center py-12">
                <div className="w-8 h-8 border-4 border-jio-600 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
                <p className="text-gray-600">Calculating Moon chart...</p>
              </CardContent>
            </Card>
          ) : moonError ? (
            <Card>
              <CardContent className="text-center py-12">
                <p className="text-red-600 mb-4">Failed to calculate Moon chart</p>
                <p className="text-sm text-gray-600">{(moonError as Error).message}</p>
              </CardContent>
            </Card>
          ) : moonChart ? (
            <>
              <Card>
                <CardHeader>
                  <CardTitle>Moon Chart (Chandra Kundali)</CardTitle>
                  <CardDescription>
                    Chart with Moon's sign as the ascendant - shows emotional nature, mind, and life from lunar perspective
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <ChartSelector chartData={moonChart.chart_data} defaultChart="north" />
                </CardContent>
              </Card>

              <Card className="bg-blue-50">
                <CardContent className="py-6">
                  <h3 className="font-semibold mb-2">About Moon Chart (Chandra Kundali)</h3>
                  <p className="text-sm text-gray-700">
                    The Moon chart is fundamental in Vedic astrology, treating the Moon's sign as the ascendant. It reveals:
                  </p>
                  <ul className="text-sm text-gray-700 list-disc list-inside mt-2 space-y-1">
                    <li>Emotional nature and mental patterns</li>
                    <li>Relationship with mother and maternal influences</li>
                    <li>Public life and general fortune</li>
                    <li>Mind, feelings, and subconscious tendencies</li>
                  </ul>
                </CardContent>
              </Card>

              {/* Planetary Positions Table */}
              <PlanetaryPositionsTable
                planets={moonChart.chart_data.planets}
                title="Planetary Positions in Moon Chart"
                description="All planets positioned relative to the Moon's sign"
              />

              {/* Yogas from Moon */}
              {moonChart.chart_data.yogas && moonChart.chart_data.yogas.length > 0 && (
                <YogaDisplay yogas={moonChart.chart_data.yogas} />
              )}
            </>
          ) : null}
        </TabsContent>

        {/* D9 Chart Tab */}
        <TabsContent value="d9" className="space-y-6">
          {d9Loading ? (
            <Card>
              <CardContent className="text-center py-12">
                <div className="w-8 h-8 border-4 border-jio-600 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
                <p className="text-gray-600">Calculating Navamsa chart...</p>
              </CardContent>
            </Card>
          ) : d9Error ? (
            <Card>
              <CardContent className="text-center py-12">
                <p className="text-red-600 mb-4">Failed to calculate D9 chart</p>
                <p className="text-sm text-gray-600">{(d9Error as Error).message}</p>
              </CardContent>
            </Card>
          ) : d9Chart ? (
            <>
              <Card>
                <CardHeader>
                  <CardTitle>Navamsa Chart (D9)</CardTitle>
                  <CardDescription>
                    The D9 chart reveals deeper karma, marriage, spirituality, and second half of life
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <ChartSelector chartData={d9Chart.chart_data} defaultChart="north" />
                </CardContent>
              </Card>

              <Card className="bg-blue-50">
                <CardContent className="py-6">
                  <h3 className="font-semibold mb-2">About Navamsa (D9)</h3>
                  <p className="text-sm text-gray-700">
                    The Navamsa chart is one of the most important divisional charts in Vedic astrology. It shows:
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
          ) : null}
        </TabsContent>

        {/* Dasha Tab */}
        <TabsContent value="dasha" className="space-y-6">
          {d1Loading ? (
            <Card>
              <CardContent className="text-center py-12">
                <div className="w-8 h-8 border-4 border-jio-600 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
                <p className="text-gray-600">Loading dasha periods...</p>
              </CardContent>
            </Card>
          ) : d1Chart && d1Chart.chart_data.dasha ? (
            <>
              <DasaTimeline dashaData={d1Chart.chart_data.dasha} />

              <Card className="bg-amber-50">
                <CardContent className="py-6">
                  <h3 className="font-semibold mb-2">About Vimshottari Dasha</h3>
                  <p className="text-sm text-gray-700">
                    Vimshottari Dasha is a 120-year planetary period system based on the Moon's position
                    at birth. Each planet rules for a specific number of years, bringing its unique
                    energy and events. The current Mahadasha (major period) and Antardasha (sub-period)
                    significantly influence life events.
                  </p>
                </CardContent>
              </Card>
            </>
          ) : (
            <Card>
              <CardContent className="text-center py-12">
                <p className="text-gray-600">Dasha information not available</p>
              </CardContent>
            </Card>
          )}
        </TabsContent>
      </Tabs>
    </div>
  )
}
