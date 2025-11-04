'use client'

import { useState } from 'react'
import { apiClient } from '@/lib/api'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Sparkles, Clock, Calendar, Plus, X, Award, AlertTriangle } from '@/components/icons'

const EVENT_TYPES = [
  { id: 'marriage', label: 'Marriage' },
  { id: 'divorce', label: 'Divorce/Separation' },
  { id: 'job_start', label: 'Job Start' },
  { id: 'job_loss', label: 'Job Loss' },
  { id: 'childbirth', label: 'Childbirth' },
  { id: 'education_start', label: 'Education Start' },
  { id: 'education_end', label: 'Education Completion' },
  { id: 'accident', label: 'Accident/Injury' },
  { id: 'illness', label: 'Serious Illness' },
  { id: 'property_gain', label: 'Property Gain' },
  { id: 'property_loss', label: 'Property Loss' },
  { id: 'travel_abroad', label: 'Travel Abroad' },
  { id: 'spiritual_initiation', label: 'Spiritual Initiation' },
]

interface EventAnchor {
  event_type: string
  event_date: string
  significance: number
  description: string
}

interface RectificationResult {
  rectified_time: string
  confidence: number
  top_candidates: Array<{
    time: string
    score: number
    event_matches: any[]
  }>
}

export default function RectificationPage() {
  const [name, setName] = useState('')
  const [birthDate, setBirthDate] = useState('')
  const [approximateTime, setApproximateTime] = useState('')
  const [timeWindow, setTimeWindow] = useState(60)
  const [city, setCity] = useState('')
  const [latitude, setLatitude] = useState('')
  const [longitude, setLongitude] = useState('')
  const [timezone, setTimezone] = useState('UTC')
  const [events, setEvents] = useState<EventAnchor[]>([
    { event_type: '', event_date: '', significance: 3, description: '' }
  ])
  const [calculating, setCalculating] = useState(false)
  const [error, setError] = useState('')
  const [result, setResult] = useState<RectificationResult | null>(null)

  const addEvent = () => {
    setEvents([...events, { event_type: '', event_date: '', significance: 3, description: '' }])
  }

  const removeEvent = (index: number) => {
    setEvents(events.filter((_, i) => i !== index))
  }

  const updateEvent = (index: number, field: keyof EventAnchor, value: any) => {
    const updated = [...events]
    updated[index] = { ...updated[index], [field]: value }
    setEvents(updated)
  }

  const handleCalculate = async () => {
    if (!name || !birthDate || !approximateTime || !city) {
      setError('Please fill in all required fields')
      return
    }

    if (!latitude || !longitude) {
      setError('Please provide location coordinates')
      return
    }

    const validEvents = events.filter(e => e.event_type && e.event_date)
    if (validEvents.length === 0) {
      setError('Please add at least one life event')
      return
    }

    setError('')
    setCalculating(true)
    setResult(null)

    try {
      const response = await apiClient.rectifyBirthTime({
        name,
        birth_date: birthDate,
        approximate_time: approximateTime,
        time_window_minutes: timeWindow,
        latitude: parseFloat(latitude),
        longitude: parseFloat(longitude),
        timezone_str: timezone,
        city,
        event_anchors: validEvents,
      })

      setResult(response.data)
    } catch (err: any) {
      console.error('Failed to rectify birth time:', err)
      setError(err.message || 'Failed to rectify birth time. Please try again.')
    } finally {
      setCalculating(false)
    }
  }

  return (
    <div className="max-w-5xl mx-auto space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Birth Time Rectification</h1>
        <p className="text-gray-600 mt-2">
          Determine accurate birth time using significant life events
        </p>
      </div>

      {/* Birth Data Form */}
      <Card>
        <CardHeader>
          <CardTitle>Birth Information</CardTitle>
          <CardDescription>Enter approximate birth details</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          {error && (
            <div className="p-3 text-sm text-red-600 bg-red-50 rounded-md border border-red-200">
              {error}
            </div>
          )}

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="name">Name *</Label>
              <Input
                id="name"
                value={name}
                onChange={(e) => setName(e.target.value)}
                placeholder="Enter name"
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="birth-date">Birth Date *</Label>
              <Input
                id="birth-date"
                type="date"
                value={birthDate}
                onChange={(e) => setBirthDate(e.target.value)}
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="time">Approximate Birth Time *</Label>
              <Input
                id="time"
                type="time"
                value={approximateTime}
                onChange={(e) => setApproximateTime(e.target.value)}
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="window">Time Window: ±{timeWindow} minutes</Label>
              <input
                id="window"
                type="range"
                min="5"
                max="120"
                value={timeWindow}
                onChange={(e) => setTimeWindow(parseInt(e.target.value))}
                className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer accent-jio-600"
              />
              <div className="flex justify-between text-xs text-gray-600">
                <span>±5 min</span>
                <span>±120 min</span>
              </div>
            </div>

            <div className="space-y-2">
              <Label htmlFor="city">City *</Label>
              <Input
                id="city"
                value={city}
                onChange={(e) => setCity(e.target.value)}
                placeholder="Birth city"
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="timezone">Timezone</Label>
              <Input
                id="timezone"
                value={timezone}
                onChange={(e) => setTimezone(e.target.value)}
                placeholder="e.g., Asia/Kolkata"
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="latitude">Latitude *</Label>
              <Input
                id="latitude"
                type="number"
                step="0.0001"
                value={latitude}
                onChange={(e) => setLatitude(e.target.value)}
                placeholder="e.g., 28.6139"
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="longitude">Longitude *</Label>
              <Input
                id="longitude"
                type="number"
                step="0.0001"
                value={longitude}
                onChange={(e) => setLongitude(e.target.value)}
                placeholder="e.g., 77.2090"
              />
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Life Events */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle>Life Events (Event Anchors)</CardTitle>
              <CardDescription>Add significant life events to improve accuracy</CardDescription>
            </div>
            <Button onClick={addEvent} size="sm">
              <Plus className="w-4 h-4 mr-1" />
              Add Event
            </Button>
          </div>
        </CardHeader>
        <CardContent className="space-y-4">
          {events.map((event, index) => (
            <Card key={index} className="border-2">
              <CardContent className="pt-6">
                <div className="flex items-start gap-4">
                  <div className="flex-1 grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div className="space-y-2">
                      <Label>Event Type *</Label>
                      <Select
                        value={event.event_type}
                        onValueChange={(value) => updateEvent(index, 'event_type', value)}
                      >
                        <SelectTrigger>
                          <SelectValue placeholder="Select event type" />
                        </SelectTrigger>
                        <SelectContent>
                          {EVENT_TYPES.map((type) => (
                            <SelectItem key={type.id} value={type.id}>
                              {type.label}
                            </SelectItem>
                          ))}
                        </SelectContent>
                      </Select>
                    </div>

                    <div className="space-y-2">
                      <Label>Event Date *</Label>
                      <Input
                        type="date"
                        value={event.event_date}
                        onChange={(e) => updateEvent(index, 'event_date', e.target.value)}
                      />
                    </div>

                    <div className="space-y-2 md:col-span-2">
                      <Label>Description (Optional)</Label>
                      <Input
                        value={event.description}
                        onChange={(e) => updateEvent(index, 'description', e.target.value)}
                        placeholder="Additional details about this event"
                      />
                    </div>

                    <div className="space-y-2 md:col-span-2">
                      <Label>Significance: {event.significance}/5</Label>
                      <input
                        type="range"
                        min="1"
                        max="5"
                        value={event.significance}
                        onChange={(e) => updateEvent(index, 'significance', parseInt(e.target.value))}
                        className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer accent-jio-600"
                      />
                      <div className="flex justify-between text-xs text-gray-600">
                        <span>Minor</span>
                        <span>Very Significant</span>
                      </div>
                    </div>
                  </div>

                  {events.length > 1 && (
                    <button
                      onClick={() => removeEvent(index)}
                      className="p-2 hover:bg-red-50 rounded text-red-600"
                    >
                      <X className="w-5 h-5" />
                    </button>
                  )}
                </div>
              </CardContent>
            </Card>
          ))}
        </CardContent>
      </Card>

      {/* Calculate Button */}
      <Button
        onClick={handleCalculate}
        className="w-full"
        disabled={calculating}
        size="lg"
      >
        {calculating ? (
          <>
            <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin mr-2"></div>
            Analyzing {timeWindow * 2 / 2} time candidates...
          </>
        ) : (
          <>
            <Clock className="w-5 h-5 mr-2" />
            Calculate Rectified Birth Time
          </>
        )}
      </Button>

      {/* Results */}
      {result && (
        <div className="space-y-4">
          <h2 className="text-2xl font-bold text-gray-900">Rectification Results</h2>

          {/* Best Match */}
          <Card className="border-2 border-green-500 bg-green-50">
            <CardHeader>
              <div className="flex items-center justify-between">
                <CardTitle className="flex items-center gap-2">
                  <Award className="w-6 h-6 text-green-600" />
                  Recommended Birth Time
                </CardTitle>
                <span className="text-sm font-medium px-3 py-1 bg-green-100 text-green-800 rounded-full">
                  {(result.confidence * 100).toFixed(0)}% confidence
                </span>
              </div>
            </CardHeader>
            <CardContent>
              <p className="text-3xl font-bold text-gray-900 mb-2">{result.rectified_time}</p>
              <p className="text-sm text-gray-600">
                Based on analysis of {events.filter(e => e.event_type && e.event_date).length} life events
              </p>
            </CardContent>
          </Card>

          {/* Top Candidates */}
          <Card>
            <CardHeader>
              <CardTitle>Top 3 Candidate Times</CardTitle>
              <CardDescription>Alternative birth times with high correlation scores</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {result.top_candidates.slice(0, 3).map((candidate, index) => (
                  <div key={index} className="p-4 border rounded-lg flex items-center justify-between">
                    <div className="flex-1">
                      <div className="flex items-center gap-3 mb-2">
                        <span className={`w-8 h-8 rounded-full flex items-center justify-center font-bold ${
                          index === 0 ? 'bg-gold-100 text-gold-800' :
                          index === 1 ? 'bg-gray-200 text-gray-800' :
                          'bg-amber-100 text-amber-800'
                        }`}>
                          #{index + 1}
                        </span>
                        <p className="text-xl font-bold text-gray-900">{candidate.time}</p>
                      </div>
                      <p className="text-sm text-gray-600 ml-11">
                        {candidate.event_matches.length} event matches • Score: {candidate.score.toFixed(2)}
                      </p>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Info Box */}
      <div className="p-4 bg-yellow-50 border border-yellow-200 rounded-lg">
        <div className="flex items-start gap-3">
          <AlertTriangle className="w-5 h-5 text-yellow-800 flex-shrink-0 mt-0.5" />
          <div>
            <h4 className="font-semibold text-yellow-900 mb-1">Important Notes</h4>
            <ul className="text-sm text-yellow-800 space-y-1 list-disc list-inside">
              <li>Birth time rectification is probabilistic, not absolute</li>
              <li>More significant life events increase accuracy</li>
              <li>Exact event dates are crucial for accurate correlation</li>
              <li>Results should be verified with other astrological techniques</li>
              <li>Consider consulting a professional astrologer for confirmation</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  )
}
