'use client'

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { apiClient } from '@/lib/api'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Progress } from '@/components/ui/progress'
import { Skeleton } from '@/components/ui/skeleton'
import { Zap, TrendingUp, Share2, Calendar, Users, CheckCircle2, XCircle, Loader2, Instagram, MessageCircle } from 'lucide-react'
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts'
import { format, parseISO } from 'date-fns'

interface Profile {
  id: string
  name: string
  date_of_birth: string
}

interface CosmicScore {
  score: number
  level: string
  color: string
  emoji: string
  best_for: string[]
  avoid: string[]
  breakdown: {
    dasha_strength: number
    jupiter_transit: number
    saturn_transit: number
    moon_nakshatra: number
    weekday_lord: number
    hourly_modifier: number
  }
  calculated_at: string
  valid_for_date: string
}

interface DailyTrend {
  date: string
  score: number
  level: string
  emoji: string
}

export default function CosmicEnergyPage() {
  const router = useRouter()
  const [profiles, setProfiles] = useState<Profile[]>([])
  const [selectedProfile, setSelectedProfile] = useState<string>('')
  const [selectedDate, setSelectedDate] = useState<string>(format(new Date(), 'yyyy-MM-dd'))
  const [cosmicScore, setCosmicScore] = useState<CosmicScore | null>(null)
  const [trend, setTrend] = useState<DailyTrend[]>([])
  const [loading, setLoading] = useState(false)
  const [loadingTrend, setLoadingTrend] = useState(false)
  const [sharing, setSharing] = useState(false)

  // Fetch user profiles
  useEffect(() => {
    const fetchProfiles = async () => {
      try {
        const response = await apiClient.getProfiles()
        // Response is an array of profiles directly, not wrapped in {success, data}
        if (Array.isArray(response) && response.length > 0) {
          setProfiles(response)
          setSelectedProfile(response[0].id)
        } else if (response && response.data && Array.isArray(response.data)) {
          // Fallback for wrapped response format
          setProfiles(response.data)
          if (response.data.length > 0) {
            setSelectedProfile(response.data[0].id)
          }
        }
      } catch (error) {
        console.error('Error fetching profiles:', error)
      }
    }
    fetchProfiles()
  }, [])

  // Fetch cosmic score when profile or date changes
  useEffect(() => {
    console.log('🔄 Profile/Date changed:', { selectedProfile, selectedDate })
    if (selectedProfile) {
      console.log('✅ Fetching cosmic score and trend...')
      fetchCosmicScore()
      fetchTrend()
    } else {
      console.log('⚠️ No profile selected')
    }
  }, [selectedProfile, selectedDate])

  const fetchCosmicScore = async () => {
    console.log('📞 fetchCosmicScore called', { selectedProfile, selectedDate })
    if (!selectedProfile) {
      console.log('⚠️ No profile, returning')
      return
    }
    setLoading(true)
    try {
      console.log('🌐 Calling apiClient.getMyCosmicScore...')
      const response = await apiClient.getMyCosmicScore(selectedProfile, selectedDate)
      console.log('📦 Got response:', response)
      if (response && response.data) {
        console.log('✅ Setting cosmic score with data:', response.data)
        setCosmicScore(response.data)
      } else if (response && !response.data) {
        // Handle case where response is already unwrapped
        console.log('✅ Setting cosmic score (unwrapped):', response)
        setCosmicScore(response)
      }
    } catch (error) {
      console.error('❌ Error fetching cosmic score:', error)
    } finally {
      setLoading(false)
    }
  }

  const fetchTrend = async () => {
    if (!selectedProfile) return
    setLoadingTrend(true)
    try {
      const response = await apiClient.get30DayTrend(selectedProfile, selectedDate)
      if (response && response.data) {
        setTrend(response.data)
      } else if (response && !response.data) {
        // Handle case where response is already unwrapped
        setTrend(response)
      }
    } catch (error) {
      console.error('Error fetching trend:', error)
    } finally {
      setLoadingTrend(false)
    }
  }

  const handleShare = async (templateType: 'instagram_story' | 'whatsapp_status') => {
    if (!selectedProfile || !cosmicScore) return
    setSharing(true)
    try {
      const response = await apiClient.generateShareTemplate(selectedProfile, templateType, selectedDate)
      if (response.success) {
        // Copy share text to clipboard
        if (navigator.clipboard) {
          await navigator.clipboard.writeText(response.share_text)
        }
        alert(`Share template generated! Text copied to clipboard.\n\n${response.share_text}`)
      }
    } catch (error) {
      console.error('Error generating share template:', error)
      alert('Failed to generate share template')
    } finally {
      setSharing(false)
    }
  }

  const getColorClass = (color: string) => {
    switch (color) {
      case 'green':
        return 'text-green-500 border-green-500'
      case 'yellow':
        return 'text-yellow-500 border-yellow-500'
      case 'red':
        return 'text-red-500 border-red-500'
      default:
        return 'text-gray-500 border-gray-500'
    }
  }

  const getBackgroundClass = (color: string) => {
    switch (color) {
      case 'green':
        return 'bg-green-50 dark:bg-green-950'
      case 'yellow':
        return 'bg-yellow-50 dark:bg-yellow-950'
      case 'red':
        return 'bg-red-50 dark:bg-red-950'
      default:
        return 'bg-gray-50 dark:bg-gray-950'
    }
  }

  return (
    <div className="container mx-auto p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold flex items-center gap-2">
            <Zap className="h-8 w-8 text-yellow-500" />
            Cosmic Energy Score™
          </h1>
          <p className="text-muted-foreground mt-1">
            Your daily astrological energy level
          </p>
        </div>
        <div className="flex items-center gap-3">
          <Select value={selectedProfile} onValueChange={setSelectedProfile}>
            <SelectTrigger className="w-[200px]">
              <SelectValue placeholder="Select profile" />
            </SelectTrigger>
            <SelectContent>
              {profiles.map((profile) => (
                <SelectItem key={profile.id} value={profile.id}>
                  {profile.name}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
          <input
            type="date"
            value={selectedDate}
            onChange={(e) => setSelectedDate(e.target.value)}
            className="px-3 py-2 border rounded-md"
          />
        </div>
      </div>

      {/* Main Score Card */}
      {loading ? (
        <Card>
          <CardContent className="p-8">
            <div className="flex flex-col items-center gap-4">
              <Skeleton className="h-32 w-32 rounded-full" />
              <Skeleton className="h-8 w-48" />
              <Skeleton className="h-4 w-64" />
            </div>
          </CardContent>
        </Card>
      ) : cosmicScore ? (
        <Card className={`${getBackgroundClass(cosmicScore.color)} border-2 ${getColorClass(cosmicScore.color)}`}>
          <CardContent className="p-8">
            <div className="flex flex-col items-center gap-6">
              {/* Score Circle */}
              <div className="relative">
                <svg className="transform -rotate-90" width="200" height="200">
                  <circle
                    cx="100"
                    cy="100"
                    r="90"
                    stroke="currentColor"
                    strokeWidth="12"
                    fill="none"
                    className="text-gray-200 dark:text-gray-800"
                  />
                  <circle
                    cx="100"
                    cy="100"
                    r="90"
                    stroke="currentColor"
                    strokeWidth="12"
                    fill="none"
                    strokeDasharray={`${2 * Math.PI * 90}`}
                    strokeDashoffset={`${2 * Math.PI * 90 * (1 - cosmicScore.score / 100)}`}
                    className={getColorClass(cosmicScore.color)}
                    strokeLinecap="round"
                  />
                </svg>
                <div className="absolute inset-0 flex flex-col items-center justify-center">
                  <span className="text-6xl font-bold">{cosmicScore.score}</span>
                  <span className="text-sm text-muted-foreground">/ 100</span>
                </div>
              </div>

              {/* Level Badge */}
              <div className="flex items-center gap-2">
                <span className="text-4xl">{cosmicScore.emoji}</span>
                <span className="text-2xl font-semibold">{cosmicScore.level}</span>
              </div>

              {/* Best For & Avoid */}
              <div className="grid md:grid-cols-2 gap-8 w-full max-w-2xl mt-4">
                {/* Best For */}
                <div>
                  <h3 className="font-semibold text-lg mb-3 flex items-center gap-2">
                    <CheckCircle2 className="h-5 w-5 text-green-500" />
                    Best For
                  </h3>
                  <ul className="space-y-2">
                    {(cosmicScore.best_for || []).map((item, idx) => (
                      <li key={idx} className="flex items-start gap-2">
                        <CheckCircle2 className="h-4 w-4 text-green-500 mt-0.5 flex-shrink-0" />
                        <span>{item}</span>
                      </li>
                    ))}
                  </ul>
                </div>

                {/* Avoid */}
                <div>
                  <h3 className="font-semibold text-lg mb-3 flex items-center gap-2">
                    <XCircle className="h-5 w-5 text-red-500" />
                    Avoid
                  </h3>
                  <ul className="space-y-2">
                    {(cosmicScore.avoid || []).map((item, idx) => (
                      <li key={idx} className="flex items-start gap-2">
                        <XCircle className="h-4 w-4 text-red-500 mt-0.5 flex-shrink-0" />
                        <span>{item}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              </div>

              {/* Share Buttons */}
              <div className="flex gap-3 mt-4">
                <Button
                  onClick={() => handleShare('instagram_story')}
                  disabled={sharing}
                  className="gap-2"
                >
                  {sharing ? (
                    <Loader2 className="h-4 w-4 animate-spin" />
                  ) : (
                    <Instagram className="h-4 w-4" />
                  )}
                  Share to Instagram
                </Button>
                <Button
                  onClick={() => handleShare('whatsapp_status')}
                  disabled={sharing}
                  variant="outline"
                  className="gap-2"
                >
                  {sharing ? (
                    <Loader2 className="h-4 w-4 animate-spin" />
                  ) : (
                    <MessageCircle className="h-4 w-4" />
                  )}
                  Share to WhatsApp
                </Button>
              </div>
            </div>
          </CardContent>
        </Card>
      ) : (
        <Card>
          <CardContent className="p-8 text-center">
            <p className="text-muted-foreground">Select a profile to view your cosmic energy score</p>
          </CardContent>
        </Card>
      )}

      {/* Score Breakdown */}
      {cosmicScore && (
        <Card>
          <CardHeader>
            <CardTitle>Score Breakdown</CardTitle>
            <CardDescription>
              How your score is calculated from different astrological factors
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            {Object.entries(cosmicScore.breakdown || {}).map(([key, value]) => (
              <div key={key} className="space-y-2">
                <div className="flex justify-between text-sm">
                  <span className="font-medium capitalize">
                    {key.replace(/_/g, ' ')}
                  </span>
                  <span className="text-muted-foreground">{value}%</span>
                </div>
                <Progress value={value as number} className="h-2" />
              </div>
            ))}
          </CardContent>
        </Card>
      )}

      {/* 30-Day Trend */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <TrendingUp className="h-5 w-5" />
            30-Day Trend
          </CardTitle>
          <CardDescription>
            Your cosmic energy forecast for the next 30 days
          </CardDescription>
        </CardHeader>
        <CardContent>
          {loadingTrend ? (
            <div className="h-[300px] flex items-center justify-center">
              <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
            </div>
          ) : trend.length > 0 ? (
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={trend}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis
                  dataKey="date"
                  tickFormatter={(date) => format(parseISO(date), 'MMM d')}
                />
                <YAxis domain={[0, 100]} />
                <Tooltip
                  labelFormatter={(date) => format(parseISO(date as string), 'PPP')}
                  formatter={(value: number) => [`${value}%`, 'Score']}
                />
                <Line
                  type="monotone"
                  dataKey="score"
                  stroke="#8884d8"
                  strokeWidth={2}
                  dot={{ r: 4 }}
                  activeDot={{ r: 6 }}
                />
              </LineChart>
            </ResponsiveContainer>
          ) : (
            <div className="h-[300px] flex items-center justify-center text-muted-foreground">
              No trend data available
            </div>
          )}
        </CardContent>
      </Card>

      {/* Friends Comparison (Phase 2 Placeholder) */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Users className="h-5 w-5" />
            Friends Comparison
          </CardTitle>
          <CardDescription>
            Compare your cosmic energy with friends
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="text-center py-8">
            <Users className="h-12 w-12 mx-auto text-muted-foreground mb-3" />
            <p className="text-muted-foreground mb-4">
              Invite friends to compare your cosmic energy scores!
            </p>
            <Button disabled variant="outline">
              Coming Soon in Phase 2
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
