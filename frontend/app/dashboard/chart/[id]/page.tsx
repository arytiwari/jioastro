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
import { ArrowLeft, Calendar, MapPin, Sparkles, Download, RefreshCw } from 'lucide-react'
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
  const { data: d1Chart, isLoading: d1Loading } = useQuery({
    queryKey: ['chart', profileId, 'D1'],
    queryFn: async () => {
      try {
        const response = await apiClient.getChart(profileId, 'D1')
        return response.data
      } catch (error: any) {
        if (error.response?.status === 404) {
          const response = await apiClient.calculateChart(profileId, 'D1')
          return response.data
        }
        throw error
      }
    },
    enabled: !!profile,
  })

  // Fetch D9 chart (existing service)
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
        <TabsList className="grid w-full max-w-2xl grid-cols-4">
          <TabsTrigger value="overview">Overview</TabsTrigger>
          <TabsTrigger value="d1">D1 Chart</TabsTrigger>
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
              <Card>
                <CardHeader>
                  <CardTitle>Planetary Positions</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="overflow-x-auto">
                    <table className="w-full text-sm">
                      <thead>
                        <tr className="border-b">
                          <th className="text-left py-2 px-3 font-semibold">Planet</th>
                          <th className="text-left py-2 px-3 font-semibold">Sign</th>
                          <th className="text-left py-2 px-3 font-semibold">House</th>
                          <th className="text-left py-2 px-3 font-semibold">Position</th>
                          <th className="text-left py-2 px-3 font-semibold">Status</th>
                        </tr>
                      </thead>
                      <tbody>
                        {Object.entries(d1Chart.chart_data.planets).map(([name, data]: [string, any]) => (
                          <tr key={name} className="border-b">
                            <td className="py-2 px-3 font-medium">{name}</td>
                            <td className="py-2 px-3">{data.sign}</td>
                            <td className="py-2 px-3">{data.house}</td>
                            <td className="py-2 px-3">{data.position.toFixed(2)}°</td>
                            <td className="py-2 px-3">
                              {data.retrograde && (
                                <span className="text-xs bg-red-100 text-red-800 px-2 py-1 rounded">
                                  Retrograde
                                </span>
                              )}
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </CardContent>
              </Card>
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
