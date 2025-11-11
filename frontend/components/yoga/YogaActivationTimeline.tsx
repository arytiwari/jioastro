"use client"

import { useState, useEffect } from 'react'
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Calendar, Clock, TrendingUp, AlertCircle, Sparkles } from 'lucide-react'
import { apiClient } from '@/lib/api'

interface Yoga {
  name: string
  description: string
  strength: string
  category: string
}

interface YogaTiming {
  yoga_name: string
  activation_status: string
  current_strength: string
  dasha_activation_periods: Array<{
    planet: string
    start_date: string
    end_date: string
    period_type: string
    intensity: string
  }>
  peak_periods: string[]
  general_activation_age: string
  recommendations: string[]
}

interface YogaActivationTimelineProps {
  yogas: Yoga[]
  profileId: string
}

interface TimelineEvent {
  yoga: Yoga
  timing: YogaTiming
  startDate?: Date
  endDate?: Date
}

const STRENGTH_COLORS: Record<string, string> = {
  'Very Strong': 'bg-red-500 border-red-600',
  'Strong': 'bg-orange-500 border-orange-600',
  'Medium': 'bg-blue-500 border-blue-600',
  'Weak': 'bg-gray-400 border-gray-500',
}

const INTENSITY_COLORS: Record<string, string> = {
  'High': 'bg-red-100 text-red-800 border-red-300',
  'Medium': 'bg-orange-100 text-orange-800 border-orange-300',
  'Low': 'bg-blue-100 text-blue-800 border-blue-300',
}

export function YogaActivationTimeline({ yogas, profileId }: YogaActivationTimelineProps) {
  const [loading, setLoading] = useState(true)
  const [loadingMore, setLoadingMore] = useState(false)
  const [timelineEvents, setTimelineEvents] = useState<TimelineEvent[]>([])
  const [error, setError] = useState<string | null>(null)
  const [activeView, setActiveView] = useState<'timeline' | 'list'>('timeline')
  const [visibleCount, setVisibleCount] = useState(5) // Initially load 5 yogas

  useEffect(() => {
    if (yogas.length > 0 && profileId) {
      fetchYogaTimings()
    }
  }, [yogas, profileId, visibleCount])

  const fetchYogaTimings = async () => {
    // Use loadingMore for subsequent loads, loading for initial load
    const isInitialLoad = timelineEvents.length === 0
    if (isInitialLoad) {
      setLoading(true)
    } else {
      setLoadingMore(true)
    }
    setError(null)

    try {
      // Fetch timing for significant yogas only (Strong and Very Strong)
      const significantYogas = yogas.filter(y =>
        y.strength === 'Very Strong' || y.strength === 'Strong'
      )

      // Only fetch the first `visibleCount` yogas for pagination
      const yogasToFetch = significantYogas.slice(0, visibleCount)

      const timingPromises = yogasToFetch.map(async (yoga) => {
        try {
          const response = await apiClient.get(`/enhancements/yoga-timing/${profileId}`, {
            params: { yoga_name: yoga.name }
          })
          return { yoga, timing: response.data }
        } catch (err) {
          console.error(`Failed to fetch timing for ${yoga.name}:`, err)
          return null
        }
      })

      const results = await Promise.all(timingPromises)
      const validEvents = results.filter(r => r !== null) as TimelineEvent[]

      // Parse dates for timeline
      validEvents.forEach(event => {
        if (event.timing.dasha_activation_periods && event.timing.dasha_activation_periods.length > 0) {
          const firstPeriod = event.timing.dasha_activation_periods[0]
          event.startDate = new Date(firstPeriod.start_date)
          event.endDate = new Date(firstPeriod.end_date)
        }
      })

      // Sort by start date
      validEvents.sort((a, b) => {
        if (!a.startDate || !b.startDate) return 0
        return a.startDate.getTime() - b.startDate.getTime()
      })

      setTimelineEvents(validEvents)
    } catch (err: any) {
      console.error('Failed to fetch yoga timings:', err)
      setError(err.message || 'Failed to load timeline')
    } finally {
      setLoading(false)
      setLoadingMore(false)
    }
  }

  const loadMore = () => {
    const significantYogas = yogas.filter(y =>
      y.strength === 'Very Strong' || y.strength === 'Strong'
    )
    setVisibleCount(Math.min(visibleCount + 5, significantYogas.length))
  }

  const formatDate = (dateStr: string) => {
    try {
      const date = new Date(dateStr)
      return date.toLocaleDateString('en-US', {
        month: 'short',
        day: 'numeric',
        year: 'numeric'
      })
    } catch {
      return dateStr
    }
  }

  if (loading) {
    return (
      <Card>
        <CardContent className="py-12 text-center">
          <div className="w-8 h-8 border-4 border-jio-600 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
          <p className="text-gray-600">Loading activation timeline...</p>
        </CardContent>
      </Card>
    )
  }

  if (error) {
    return (
      <Card>
        <CardContent className="py-8 text-center">
          <AlertCircle className="w-12 h-12 text-red-500 mx-auto mb-3" />
          <p className="text-red-600">{error}</p>
        </CardContent>
      </Card>
    )
  }

  if (timelineEvents.length === 0) {
    return (
      <Card>
        <CardContent className="py-8 text-center">
          <Calendar className="w-12 h-12 text-gray-300 mx-auto mb-3" />
          <p className="text-gray-600 font-medium mb-2">Yoga Activation Timeline</p>
          <p className="text-gray-500 text-sm">
            Timeline data is available for charts that have been saved. Navigate to the Chart page to calculate and save your birth chart, then return here to view yoga activation periods.
          </p>
        </CardContent>
      </Card>
    )
  }

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <div>
            <CardTitle className="flex items-center gap-2">
              <Clock className="w-5 h-5 text-jio-600" />
              Yoga Activation Timeline
            </CardTitle>
            <CardDescription>
              When your yogas will become active based on dasha periods
            </CardDescription>
          </div>
          <Tabs value={activeView} onValueChange={(v) => setActiveView(v as 'timeline' | 'list')}>
            <TabsList className="grid w-fit grid-cols-2">
              <TabsTrigger value="timeline">Timeline</TabsTrigger>
              <TabsTrigger value="list">List</TabsTrigger>
            </TabsList>
          </Tabs>
        </div>
      </CardHeader>

      <CardContent>
        {activeView === 'timeline' ? (
          <div className="space-y-6">
            {/* Timeline View */}
            <div className="relative">
              {/* Vertical line */}
              <div className="absolute left-4 top-0 bottom-0 w-0.5 bg-gray-300"></div>

              {/* Timeline events */}
              <div className="space-y-8">
                {timelineEvents.map((event, idx) => {
                  const strengthColor = STRENGTH_COLORS[event.yoga.strength] || STRENGTH_COLORS['Medium']

                  return (
                    <div key={idx} className="relative pl-12">
                      {/* Timeline dot */}
                      <div
                        className={`absolute left-2 w-5 h-5 rounded-full border-4 ${strengthColor}`}
                        style={{ top: '4px' }}
                      ></div>

                      {/* Event card */}
                      <div className="border rounded-lg p-4 bg-white hover:shadow-md transition-shadow">
                        <div className="flex items-start justify-between mb-2">
                          <div>
                            <h3 className="font-semibold text-lg text-gray-900">{event.yoga.name}</h3>
                            <p className="text-sm text-gray-600 mt-1">{event.yoga.category}</p>
                          </div>
                          <Badge className={`${STRENGTH_COLORS[event.yoga.strength]} text-white border`}>
                            {event.yoga.strength}
                          </Badge>
                        </div>

                        {/* Dasha periods */}
                        {event.timing.dasha_activation_periods && event.timing.dasha_activation_periods.length > 0 && (
                          <div className="mt-3 space-y-2">
                            <p className="text-xs font-semibold text-gray-700 uppercase">Activation Periods:</p>
                            {event.timing.dasha_activation_periods.slice(0, 3).map((period, pidx) => (
                              <div key={pidx} className="flex items-center justify-between p-2 bg-gray-50 rounded text-sm">
                                <div>
                                  <span className="font-medium">{period.planet} {period.period_type}</span>
                                  <span className="text-gray-600 ml-2">
                                    {formatDate(period.start_date)} - {formatDate(period.end_date)}
                                  </span>
                                </div>
                                <Badge className={`${INTENSITY_COLORS[period.intensity]} border text-xs`}>
                                  {period.intensity}
                                </Badge>
                              </div>
                            ))}
                            {event.timing.dasha_activation_periods.length > 3 && (
                              <p className="text-xs text-gray-500 ml-2">
                                +{event.timing.dasha_activation_periods.length - 3} more periods
                              </p>
                            )}
                          </div>
                        )}

                        {/* General activation age */}
                        {event.timing.general_activation_age && (
                          <div className="mt-3 p-2 bg-jio-50 rounded border border-jio-200">
                            <p className="text-sm">
                              <span className="font-semibold text-jio-900">Typical Activation: </span>
                              <span className="text-gray-700">{event.timing.general_activation_age}</span>
                            </p>
                          </div>
                        )}

                        {/* Recommendations */}
                        {event.timing.recommendations && event.timing.recommendations.length > 0 && (
                          <div className="mt-3">
                            <p className="text-xs font-semibold text-gray-700 uppercase mb-1">Key Recommendations:</p>
                            <ul className="space-y-1">
                              {event.timing.recommendations.slice(0, 2).map((rec, ridx) => (
                                <li key={ridx} className="text-xs text-gray-600 flex items-start gap-1">
                                  <span className="text-green-600 mt-0.5">✓</span>
                                  <span>{rec}</span>
                                </li>
                              ))}
                            </ul>
                          </div>
                        )}
                      </div>
                    </div>
                  )
                })}
              </div>
            </div>
          </div>
        ) : (
          <div className="space-y-3">
            {/* List View */}
            {timelineEvents.map((event, idx) => {
              const strengthColor = STRENGTH_COLORS[event.yoga.strength] || STRENGTH_COLORS['Medium']

              return (
                <div key={idx} className="border rounded-lg p-4 hover:shadow-md transition-shadow">
                  <div className="flex items-start justify-between mb-3">
                    <div className="flex items-center gap-3">
                      <div className={`w-3 h-3 rounded-full ${strengthColor}`}></div>
                      <div>
                        <h3 className="font-semibold text-gray-900">{event.yoga.name}</h3>
                        <p className="text-sm text-gray-600">{event.yoga.category}</p>
                      </div>
                    </div>
                    <Badge className={`${STRENGTH_COLORS[event.yoga.strength]} text-white border`}>
                      {event.yoga.strength}
                    </Badge>
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                    {/* Activation Age */}
                    {event.timing.general_activation_age && (
                      <div className="p-2 bg-gray-50 rounded">
                        <p className="text-xs font-semibold text-gray-700">Typical Activation</p>
                        <p className="text-sm text-gray-900">{event.timing.general_activation_age}</p>
                      </div>
                    )}

                    {/* Next Period */}
                    {event.timing.dasha_activation_periods && event.timing.dasha_activation_periods.length > 0 && (
                      <div className="p-2 bg-jio-50 rounded border border-jio-200">
                        <p className="text-xs font-semibold text-jio-900">Next Activation Period</p>
                        <p className="text-sm text-gray-900">
                          {event.timing.dasha_activation_periods[0].planet} {event.timing.dasha_activation_periods[0].period_type}
                        </p>
                        <p className="text-xs text-gray-600">
                          {formatDate(event.timing.dasha_activation_periods[0].start_date)}
                        </p>
                      </div>
                    )}
                  </div>
                </div>
              )
            })}
          </div>
        )}

        {/* Load More Button */}
        {(() => {
          const significantYogas = yogas.filter(y =>
            y.strength === 'Very Strong' || y.strength === 'Strong'
          )
          const hasMore = visibleCount < significantYogas.length

          return hasMore ? (
            <div className="flex justify-center mt-6">
              <Button
                onClick={loadMore}
                variant="outline"
                disabled={loadingMore}
                className="border-jio-500 text-jio-700 hover:bg-jio-50"
              >
                {loadingMore ? (
                  <>
                    <div className="w-4 h-4 border-2 border-jio-600 border-t-transparent rounded-full animate-spin mr-2"></div>
                    Loading more...
                  </>
                ) : (
                  <>
                    Load More ({significantYogas.length - visibleCount} remaining)
                  </>
                )}
              </Button>
            </div>
          ) : timelineEvents.length > 0 ? (
            <p className="text-center text-sm text-gray-600 mt-6">
              All {significantYogas.length} significant yogas loaded
            </p>
          ) : null
        })()}

        {/* Info note */}
        <div className="mt-6 p-3 bg-blue-50 border border-blue-200 rounded-lg">
          <div className="flex items-start gap-2">
            <Sparkles className="w-4 h-4 text-blue-600 mt-0.5" />
            <p className="text-xs text-blue-900">
              <strong>Note:</strong> Yogas become active during the dasha (planetary period) of the yoga-forming planets.
              The intensity indicates how strongly the yoga will manifest during that period.
            </p>
          </div>
        </div>
      </CardContent>
    </Card>
  )
}
