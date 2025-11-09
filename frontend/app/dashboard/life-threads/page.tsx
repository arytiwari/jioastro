'use client'

import { useState, useEffect } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Textarea } from '@/components/ui/textarea'
import { Badge } from '@/components/ui/badge'
import { Calendar, Plus, TrendingUp, Star, Clock, MapPin, User as UserIcon } from '@/components/icons'
import { apiClient } from '@/lib/api'
import { format } from 'date-fns'

interface Profile {
  id: string
  name: string
  date_of_birth: string
}

interface DashaPeriod {
  planet: string
  start_date: string
  end_date: string
  duration_years: number
  events: LifeEvent[]
}

interface LifeEvent {
  id: string
  event_name: string
  event_type: string
  event_date: string
  event_impact: string
  is_milestone: boolean
  event_description?: string
  tags: string[]
  dasha_period?: {
    mahadasha: string
    antardasha?: string
  }
}

interface Timeline {
  profile_id: string
  birth_date: string
  starting_dasha: string
  mahadasha_periods: DashaPeriod[]
  current_mahadasha: {
    planet: string
    start_date: string
    end_date: string
    remaining_years: number
  }
  cached_until: string
}

interface EventStatistics {
  total_events: number
  milestones_count: number
  event_type_distribution: Record<string, number>
  events_by_dasha: Record<string, number>
  most_active_dasha: {
    planet: string
    event_count: number
  }
  average_events_per_year: number
}

const EVENT_TYPES = [
  { value: 'career', label: 'Career' },
  { value: 'education', label: 'Education' },
  { value: 'relationship', label: 'Relationship' },
  { value: 'marriage', label: 'Marriage' },
  { value: 'childbirth', label: 'Childbirth' },
  { value: 'health', label: 'Health' },
  { value: 'relocation', label: 'Relocation' },
  { value: 'financial', label: 'Financial' },
  { value: 'spiritual', label: 'Spiritual' },
  { value: 'achievement', label: 'Achievement' },
  { value: 'loss', label: 'Loss' },
  { value: 'travel', label: 'Travel' },
  { value: 'property', label: 'Property' },
  { value: 'family', label: 'Family' },
  { value: 'other', label: 'Other' }
]

const EVENT_IMPACTS = [
  { value: 'very_positive', label: 'Very Positive' },
  { value: 'positive', label: 'Positive' },
  { value: 'neutral', label: 'Neutral' },
  { value: 'negative', label: 'Negative' },
  { value: 'very_negative', label: 'Very Negative' }
]

const PLANET_COLORS: Record<string, string> = {
  'Sun': 'bg-orange-500',
  'Moon': 'bg-blue-300',
  'Mars': 'bg-red-500',
  'Mercury': 'bg-green-500',
  'Jupiter': 'bg-yellow-500',
  'Venus': 'bg-pink-500',
  'Saturn': 'bg-gray-700',
  'Rahu': 'bg-purple-600',
  'Ketu': 'bg-indigo-600'
}

export default function LifeThreadsPage() {
  const [profiles, setProfiles] = useState<Profile[]>([])
  const [selectedProfile, setSelectedProfile] = useState<string>('')
  const [timeline, setTimeline] = useState<Timeline | null>(null)
  const [statistics, setStatistics] = useState<EventStatistics | null>(null)
  const [loading, setLoading] = useState(false)
  const [showAddEvent, setShowAddEvent] = useState(false)
  const [formData, setFormData] = useState({
    event_name: '',
    event_type: 'career',
    event_date: format(new Date(), 'yyyy-MM-dd'),
    event_description: '',
    event_impact: 'neutral',
    is_milestone: false,
    tags: ''
  })

  useEffect(() => {
    loadProfiles()
  }, [])

  useEffect(() => {
    if (selectedProfile) {
      loadTimeline()
      loadStatistics()
    }
  }, [selectedProfile])

  const loadProfiles = async () => {
    try {
      const response = await apiClient.get('/profiles/')
      setProfiles(response.data)
      // Don't auto-select - let user choose
    } catch (error) {
      console.error('Failed to load profiles:', error)
    }
  }

  const loadTimeline = async () => {
    if (!selectedProfile) return
    setLoading(true)
    try {
      const response = await apiClient.get(`/life-threads/timeline/${selectedProfile}`)
      setTimeline(response.data.timeline)
    } catch (error) {
      console.error('Failed to load timeline:', error)
    } finally {
      setLoading(false)
    }
  }

  const loadStatistics = async () => {
    if (!selectedProfile) return
    try {
      const response = await apiClient.get('/life-threads/statistics', {
        params: { profile_id: selectedProfile }
      })
      setStatistics(response.data)
    } catch (error) {
      console.error('Failed to load statistics:', error)
    }
  }

  const handleAddEvent = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!selectedProfile) return

    try {
      const tags = formData.tags ? formData.tags.split(',').map(t => t.trim()).filter(Boolean) : []

      await apiClient.post('/life-threads/events', {
        profile_id: selectedProfile,
        ...formData,
        tags
      })

      // Reset form and reload data
      setFormData({
        event_name: '',
        event_type: 'career',
        event_date: format(new Date(), 'yyyy-MM-dd'),
        event_description: '',
        event_impact: 'neutral',
        is_milestone: false,
        tags: ''
      })
      setShowAddEvent(false)
      loadTimeline()
      loadStatistics()
    } catch (error) {
      console.error('Failed to add event:', error)
    }
  }

  const getImpactColor = (impact: string) => {
    switch (impact) {
      case 'very_positive': return 'bg-green-600'
      case 'positive': return 'bg-green-400'
      case 'neutral': return 'bg-gray-400'
      case 'negative': return 'bg-orange-400'
      case 'very_negative': return 'bg-red-600'
      default: return 'bg-gray-400'
    }
  }

  return (
    <div className="container mx-auto p-6 space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold mb-2">Life Threads</h1>
        <p className="text-muted-foreground">
          Visualize your life journey through Vimshottari Dasha periods and map significant events to planetary cycles
        </p>
      </div>

      {/* Profile Selector */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <UserIcon className="h-5 w-5" />
            Select Profile
          </CardTitle>
        </CardHeader>
        <CardContent>
          <Select value={selectedProfile} onValueChange={setSelectedProfile}>
            <SelectTrigger>
              <SelectValue placeholder="Choose a profile" />
            </SelectTrigger>
            <SelectContent>
              {profiles.map(profile => {
                // Safely format date, handle invalid dates
                let dateStr = ''
                try {
                  if (profile.date_of_birth) {
                    const date = new Date(profile.date_of_birth)
                    if (!isNaN(date.getTime())) {
                      dateStr = format(date, 'MMM d, yyyy')
                    }
                  }
                } catch (e) {
                  console.error('Invalid date for profile:', profile.id, e)
                }

                return (
                  <SelectItem key={profile.id} value={profile.id}>
                    {profile.name} {dateStr && `(${dateStr})`}
                  </SelectItem>
                )
              })}
            </SelectContent>
          </Select>
        </CardContent>
      </Card>

      {selectedProfile && !loading && timeline && (
        <>
          {/* Current Dasha & Statistics */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {timeline.current_mahadasha?.planet && (
              <Card>
                <CardHeader>
                  <CardTitle className="text-sm">Current Mahadasha</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="flex items-center gap-3">
                    <div className={`w-12 h-12 rounded-full ${PLANET_COLORS[timeline.current_mahadasha.planet]} flex items-center justify-center text-white font-bold`}>
                      {timeline.current_mahadasha.planet[0]}
                    </div>
                    <div>
                      <div className="font-semibold">{timeline.current_mahadasha.planet}</div>
                      <div className="text-sm text-muted-foreground">
                        {timeline.current_mahadasha.remaining_years?.toFixed(1) || 'N/A'} years remaining
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>
            )}

            {statistics && (
              <>
                <Card>
                  <CardHeader>
                    <CardTitle className="text-sm">Life Events</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="text-3xl font-bold">{statistics.total_events || 0}</div>
                    <div className="text-sm text-muted-foreground">
                      {statistics.milestones_count || 0} milestones
                    </div>
                  </CardContent>
                </Card>

                {statistics.most_active_dasha?.planet && (
                  <Card>
                    <CardHeader>
                      <CardTitle className="text-sm">Most Active Dasha</CardTitle>
                    </CardHeader>
                    <CardContent>
                      <div className="font-semibold">{statistics.most_active_dasha.planet}</div>
                      <div className="text-sm text-muted-foreground">
                        {statistics.most_active_dasha.event_count || 0} events
                      </div>
                    </CardContent>
                  </Card>
                )}
              </>
            )}
          </div>

          {/* Add Event Button */}
          <div className="flex justify-end">
            <Button onClick={() => setShowAddEvent(!showAddEvent)}>
              <Plus className="h-4 w-4 mr-2" />
              Add Life Event
            </Button>
          </div>

          {/* Add Event Form */}
          {showAddEvent && (
            <Card>
              <CardHeader>
                <CardTitle>Add Life Event</CardTitle>
                <CardDescription>
                  Record a significant life event and map it to your Dasha period
                </CardDescription>
              </CardHeader>
              <CardContent>
                <form onSubmit={handleAddEvent} className="space-y-4">
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                      <Label htmlFor="event_name">Event Name *</Label>
                      <Input
                        id="event_name"
                        value={formData.event_name}
                        onChange={(e) => setFormData({ ...formData, event_name: e.target.value })}
                        required
                        placeholder="e.g., Started new job at Google"
                      />
                    </div>

                    <div>
                      <Label htmlFor="event_type">Event Type *</Label>
                      <Select
                        value={formData.event_type}
                        onValueChange={(value) => setFormData({ ...formData, event_type: value })}
                      >
                        <SelectTrigger>
                          <SelectValue />
                        </SelectTrigger>
                        <SelectContent>
                          {EVENT_TYPES.map(type => (
                            <SelectItem key={type.value} value={type.value}>
                              {type.label}
                            </SelectItem>
                          ))}
                        </SelectContent>
                      </Select>
                    </div>

                    <div>
                      <Label htmlFor="event_date">Event Date *</Label>
                      <Input
                        id="event_date"
                        type="date"
                        value={formData.event_date}
                        onChange={(e) => setFormData({ ...formData, event_date: e.target.value })}
                        required
                      />
                    </div>

                    <div>
                      <Label htmlFor="event_impact">Impact</Label>
                      <Select
                        value={formData.event_impact}
                        onValueChange={(value) => setFormData({ ...formData, event_impact: value })}
                      >
                        <SelectTrigger>
                          <SelectValue />
                        </SelectTrigger>
                        <SelectContent>
                          {EVENT_IMPACTS.map(impact => (
                            <SelectItem key={impact.value} value={impact.value}>
                              {impact.label}
                            </SelectItem>
                          ))}
                        </SelectContent>
                      </Select>
                    </div>
                  </div>

                  <div>
                    <Label htmlFor="event_description">Description</Label>
                    <Textarea
                      id="event_description"
                      value={formData.event_description}
                      onChange={(e) => setFormData({ ...formData, event_description: e.target.value })}
                      placeholder="Optional details about this event..."
                      rows={3}
                    />
                  </div>

                  <div>
                    <Label htmlFor="tags">Tags (comma-separated)</Label>
                    <Input
                      id="tags"
                      value={formData.tags}
                      onChange={(e) => setFormData({ ...formData, tags: e.target.value })}
                      placeholder="e.g., work, promotion, career-growth"
                    />
                  </div>

                  <div className="flex items-center gap-2">
                    <input
                      type="checkbox"
                      id="is_milestone"
                      checked={formData.is_milestone}
                      onChange={(e) => setFormData({ ...formData, is_milestone: e.target.checked })}
                      className="rounded"
                    />
                    <Label htmlFor="is_milestone" className="cursor-pointer">
                      Mark as milestone event
                    </Label>
                  </div>

                  <div className="flex gap-2">
                    <Button type="submit">Add Event</Button>
                    <Button type="button" variant="outline" onClick={() => setShowAddEvent(false)}>
                      Cancel
                    </Button>
                  </div>
                </form>
              </CardContent>
            </Card>
          )}

          {/* Dasha Timeline */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Clock className="h-5 w-5" />
                Vimshottari Dasha Timeline
              </CardTitle>
              <CardDescription>
                120-year planetary cycle starting from {timeline.starting_dasha} Mahadasha
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              {timeline.mahadasha_periods.map((period, index) => {
                const isPast = new Date(period.end_date) < new Date()
                const isCurrent = new Date(period.start_date) <= new Date() && new Date(period.end_date) >= new Date()

                return (
                  <div key={index} className={`border-l-4 pl-4 py-2 ${isCurrent ? PLANET_COLORS[period.planet] : 'border-gray-300'}`}>
                    <div className="flex items-start justify-between mb-2">
                      <div className="flex items-center gap-3">
                        <div className={`w-10 h-10 rounded-full ${PLANET_COLORS[period.planet]} flex items-center justify-center text-white font-bold text-sm`}>
                          {period.planet[0]}
                        </div>
                        <div>
                          <div className="font-semibold text-lg">{period.planet} Mahadasha</div>
                          <div className="text-sm text-muted-foreground">
                            {format(new Date(period.start_date), 'MMM yyyy')} - {format(new Date(period.end_date), 'MMM yyyy')} ({period.duration_years} years)
                          </div>
                        </div>
                      </div>
                      {isCurrent && (
                        <Badge variant="default">Current</Badge>
                      )}
                      {isPast && (
                        <Badge variant="secondary">Past</Badge>
                      )}
                    </div>

                    {/* Events in this Dasha */}
                    {period.events && period.events.length > 0 && (
                      <div className="mt-3 space-y-2 ml-13">
                        {period.events.map((event, eventIndex) => (
                          <div key={eventIndex} className="bg-secondary/50 p-3 rounded-lg">
                            <div className="flex items-start justify-between">
                              <div className="flex-1">
                                <div className="flex items-center gap-2">
                                  {event.is_milestone && (
                                    <Star className="h-4 w-4 text-yellow-500 fill-yellow-500" />
                                  )}
                                  <span className="font-medium">{event.event_name}</span>
                                  <Badge variant="outline" className="text-xs">
                                    {EVENT_TYPES.find(t => t.value === event.event_type)?.label}
                                  </Badge>
                                </div>
                                <div className="text-sm text-muted-foreground mt-1">
                                  <Calendar className="h-3 w-3 inline mr-1" />
                                  {format(new Date(event.event_date), 'MMMM d, yyyy')}
                                </div>
                                {event.event_description && (
                                  <p className="text-sm mt-2">{event.event_description}</p>
                                )}
                                {event.tags && event.tags.length > 0 && (
                                  <div className="flex gap-1 mt-2">
                                    {event.tags.map((tag, tagIndex) => (
                                      <Badge key={tagIndex} variant="secondary" className="text-xs">
                                        {tag}
                                      </Badge>
                                    ))}
                                  </div>
                                )}
                              </div>
                              {event.event_impact && (
                                <div className={`w-3 h-3 rounded-full ${getImpactColor(event.event_impact)}`} title={event.event_impact} />
                              )}
                            </div>
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                )
              })}
            </CardContent>
          </Card>
        </>
      )}

      {loading && (
        <Card>
          <CardContent className="p-12 text-center">
            <div className="text-muted-foreground">Loading timeline...</div>
          </CardContent>
        </Card>
      )}

      {!selectedProfile && !loading && (
        <Card>
          <CardContent className="p-12 text-center">
            <div className="text-muted-foreground">Please select a profile to view the life timeline</div>
          </CardContent>
        </Card>
      )}
    </div>
  )
}
