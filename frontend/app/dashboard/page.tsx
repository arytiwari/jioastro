'use client'

import { useEffect, useState } from 'react'
import Link from 'next/link'
import { useQuery, useQueryClient } from '@/lib/query'
import { apiClient } from '@/lib/api'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import {
  Plus,
  User,
  MessageSquare,
  Star,
  Trash2,
  Clock,
  Sunrise,
  Moon,
  Sparkles,
  Calendar,
  TrendingUp,
  Zap,
  Heart,
  DollarSign,
  Briefcase,
  Activity,
  Eye,
} from '@/components/icons'

export default function DashboardPage() {
  const [deletingProfile, setDeletingProfile] = useState<string | null>(null)
  const [currentTime, setCurrentTime] = useState(new Date())
  const queryClient = useQueryClient()

  // Update time every second for real-time clock
  useEffect(() => {
    const timer = setInterval(() => setCurrentTime(new Date()), 1000)
    return () => clearInterval(timer)
  }, [])

  const { data: profiles, isLoading: profilesLoading } = useQuery({
    queryKey: ['profiles'],
    queryFn: async () => {
      const response = await apiClient.getProfiles()
      return response.data
    },
  })

  const { data: queries, isLoading: queriesLoading } = useQuery({
    queryKey: ['recent-queries'],
    queryFn: async () => {
      const response = await apiClient.getQueries(5, 0)
      return response.data
    },
  })

  const { data: feedbackStats } = useQuery({
    queryKey: ['feedback-stats'],
    queryFn: async () => {
      const response = await apiClient.getFeedbackStats()
      return response.data
    },
  })

  // Fetch panchang data for primary profile
  const primaryProfile = profiles?.find((p: any) => p.is_primary) || profiles?.[0]

  const { data: panchangData } = useQuery({
    queryKey: ['panchang-today', primaryProfile?.id],
    queryFn: async () => {
      if (!primaryProfile) return null
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL}/panchang/today?latitude=${primaryProfile.birth_lat}&longitude=${primaryProfile.birth_lon}&timezone=${primaryProfile.timezone || 'Asia/Kolkata'}`
      )
      return response.json()
    },
    enabled: !!primaryProfile,
  })

  // Fetch life threads (dasha) data
  const { data: lifeThreadsData } = useQuery({
    queryKey: ['life-threads', primaryProfile?.id],
    queryFn: async () => {
      if (!primaryProfile) return null
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL}/life-threads/${primaryProfile.id}/timeline`
      )
      return response.json()
    },
    enabled: !!primaryProfile,
  })

  // Helper functions
  const getGreeting = () => {
    const hour = currentTime.getHours()
    if (hour < 12) return { text: 'Good Morning', icon: Sunrise, emoji: '🌅' }
    if (hour < 17) return { text: 'Good Afternoon', icon: Sun, emoji: '☀️' }
    if (hour < 21) return { text: 'Good Evening', icon: Sunset, emoji: '🌆' }
    return { text: 'Good Night', icon: Moon, emoji: '🌙' }
  }

  const getMoonPhase = () => {
    if (!panchangData?.panchang_data) return '🌑 New Moon'
    const tithi = panchangData.panchang_data.tithi?.name || ''
    if (tithi.includes('Purnima') || tithi.includes('15')) return '🌕 Full Moon'
    if (tithi.includes('Amavasya') || tithi.includes('30')) return '🌑 New Moon'
    if (parseInt(tithi) <= 7) return '🌒 Waxing Crescent'
    if (parseInt(tithi) <= 14) return '🌓 Waxing Gibbous'
    if (parseInt(tithi) <= 22) return '🌘 Waning Crescent'
    return '🌗 Waning Gibbous'
  }

  const getTimeBasedGradient = () => {
    const hour = currentTime.getHours()
    if (hour < 6) return 'from-indigo-900 via-purple-900 to-blue-900' // Night
    if (hour < 12) return 'from-orange-400 via-pink-400 to-blue-400' // Morning
    if (hour < 17) return 'from-blue-400 via-cyan-300 to-blue-300' // Afternoon
    if (hour < 20) return 'from-purple-500 via-orange-400 to-pink-400' // Evening
    return 'from-blue-900 via-purple-900 to-indigo-900' // Night
  }

  const getCurrentDasha = () => {
    if (!lifeThreadsData?.current_dasha) return null
    return lifeThreadsData.current_dasha
  }

  const formatTime = (date: Date) => {
    return date.toLocaleTimeString('en-IN', {
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit',
      hour12: true,
    })
  }

  const formatDate = (date: Date) => {
    return date.toLocaleDateString('en-IN', {
      weekday: 'long',
      year: 'numeric',
      month: 'long',
      day: 'numeric',
    })
  }

  const greeting = getGreeting()
  const GreetingIcon = greeting.icon
  const currentDasha = getCurrentDasha()

  const handleDeleteProfile = async (profileId: string, profileName: string) => {
    const confirmed = window.confirm(
      `Are you sure you want to delete "${profileName}"?\n\nThis will permanently delete:\n• Birth profile\n• All associated charts (D1, D9, Moon)\n• All chart calculations\n\nThis action cannot be undone.`
    )

    if (!confirmed) return

    try {
      setDeletingProfile(profileId)
      await apiClient.deleteProfile(profileId)
      queryClient.invalidateQueries(['profiles'])
      alert('Profile deleted successfully!')
    } catch (error) {
      console.error('Failed to delete profile:', error)
      alert('Failed to delete profile. Please try again.')
    } finally {
      setDeletingProfile(null)
    }
  }

  return (
    <div className="space-y-6">
      {/* PHASE 1: HERO SECTION - Your Moment in the Cosmos */}
      <Card className={`bg-gradient-to-br ${getTimeBasedGradient()} border-none text-white overflow-hidden relative`}>
        <div className="absolute inset-0 bg-[url('/stars.png')] opacity-20"></div>
        <CardContent className="pt-8 pb-8 relative z-10">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center gap-3">
              <GreetingIcon className="w-8 h-8" />
              <div>
                <h1 className="text-3xl font-bold">
                  {greeting.emoji} {greeting.text}!
                </h1>
                <p className="text-white/80 text-sm mt-1">
                  {getMoonPhase()} • {panchangData?.panchang_data?.nakshatra?.name || 'Loading...'} Nakshatra
                </p>
              </div>
            </div>
            <div className="text-right">
              <div className="text-2xl font-mono font-bold">{formatTime(currentTime)}</div>
              <div className="text-sm text-white/80">{formatDate(currentTime)}</div>
            </div>
          </div>

          {primaryProfile && (
            <div className="mt-4 flex items-center gap-2 text-sm text-white/90">
              <User className="w-4 h-4" />
              <span>Viewing insights for: <strong>{primaryProfile.name}</strong></span>
            </div>
          )}
        </CardContent>
      </Card>

      {/* PHASE 1: TODAY'S PANCHANG */}
      {panchangData && primaryProfile && (
        <Card className="border-2 border-jio-200 shadow-lg">
          <CardHeader>
            <div className="flex items-center justify-between">
              <div>
                <CardTitle className="text-2xl flex items-center gap-2">
                  <Calendar className="w-6 h-6 text-jio-600" />
                  Today's Cosmic Energy
                </CardTitle>
                <CardDescription>Daily Panchang for {primaryProfile.city?.display_name || primaryProfile.birth_city}</CardDescription>
              </div>
              <Badge variant="outline" className="text-lg">
                <Sparkles className="w-4 h-4 mr-1" />
                Live
              </Badge>
            </div>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
              <div className="p-4 bg-gradient-to-br from-blue-50 to-cyan-50 rounded-lg border border-blue-200">
                <div className="flex items-center gap-2 mb-2">
                  <Moon className="w-5 h-5 text-blue-600" />
                  <p className="text-sm font-semibold text-gray-600">Tithi</p>
                </div>
                <p className="text-lg font-bold text-gray-900">
                  {panchangData.panchang_data?.tithi?.name || 'N/A'}
                </p>
                <p className="text-xs text-gray-600 mt-1">
                  {panchangData.panchang_data?.tithi?.paksha || 'Lunar Day'}
                </p>
              </div>

              <div className="p-4 bg-gradient-to-br from-purple-50 to-pink-50 rounded-lg border border-purple-200">
                <div className="flex items-center gap-2 mb-2">
                  <Star className="w-5 h-5 text-purple-600" />
                  <p className="text-sm font-semibold text-gray-600">Nakshatra</p>
                </div>
                <p className="text-lg font-bold text-gray-900">
                  {panchangData.panchang_data?.nakshatra?.name || 'N/A'}
                </p>
                <p className="text-xs text-gray-600 mt-1">
                  {panchangData.panchang_data?.nakshatra?.lord || 'Star Constellation'}
                </p>
              </div>

              <div className="p-4 bg-gradient-to-br from-green-50 to-emerald-50 rounded-lg border border-green-200">
                <div className="flex items-center gap-2 mb-2">
                  <Activity className="w-5 h-5 text-green-600" />
                  <p className="text-sm font-semibold text-gray-600">Yoga</p>
                </div>
                <p className="text-lg font-bold text-gray-900">
                  {panchangData.panchang_data?.yoga?.name || 'N/A'}
                </p>
                <p className="text-xs text-gray-600 mt-1">
                  {panchangData.panchang_data?.yoga?.quality || 'Union'}
                </p>
              </div>

              <div className="p-4 bg-gradient-to-br from-orange-50 to-yellow-50 rounded-lg border border-orange-200">
                <div className="flex items-center gap-2 mb-2">
                  <Zap className="w-5 h-5 text-orange-600" />
                  <p className="text-sm font-semibold text-gray-600">Karana</p>
                </div>
                <p className="text-lg font-bold text-gray-900">
                  {panchangData.panchang_data?.karana?.name || 'N/A'}
                </p>
                <p className="text-xs text-gray-600 mt-1">Half Tithi</p>
              </div>
            </div>

            {/* Auspicious Times */}
            {panchangData.auspicious_times && (
              <div className="mt-6 p-4 bg-gradient-to-r from-green-50 to-emerald-50 rounded-lg border-2 border-green-300">
                <h3 className="font-semibold text-green-900 mb-3 flex items-center gap-2">
                  <Clock className="w-5 h-5" />
                  Auspicious & Inauspicious Times
                </h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
                  {panchangData.auspicious_times.abhijit_muhurta && (
                    <div>
                      <p className="font-medium text-green-800">✅ Abhijit Muhurta (Most Auspicious)</p>
                      <p className="text-green-700">
                        {panchangData.auspicious_times.abhijit_muhurta.start} - {panchangData.auspicious_times.abhijit_muhurta.end}
                      </p>
                    </div>
                  )}
                  {panchangData.inauspicious_times?.rahu_kaal && (
                    <div>
                      <p className="font-medium text-red-800">⚠️ Rahu Kaal (Avoid Important Work)</p>
                      <p className="text-red-700">
                        {panchangData.inauspicious_times.rahu_kaal.start} - {panchangData.inauspicious_times.rahu_kaal.end}
                      </p>
                    </div>
                  )}
                </div>
              </div>
            )}

            <div className="mt-4 flex justify-center">
              <Link href="/dashboard/panchang">
                <Button variant="outline" className="gap-2">
                  <Eye className="w-4 h-4" />
                  View Full Panchang
                </Button>
              </Link>
            </div>
          </CardContent>
        </Card>
      )}

      {/* PHASE 1: CURRENT DASHA TIMELINE */}
      {currentDasha && primaryProfile && (
        <Card className="border-2 border-purple-200 shadow-lg">
          <CardHeader>
            <CardTitle className="text-2xl flex items-center gap-2">
              <TrendingUp className="w-6 h-6 text-purple-600" />
              Your Current Life Chapter
            </CardTitle>
            <CardDescription>Active Planetary Period (Dasha System)</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {/* Mahadasha */}
              <div className="p-5 bg-gradient-to-br from-purple-50 to-indigo-50 rounded-lg border-2 border-purple-300">
                <div className="flex items-center justify-between mb-3">
                  <h3 className="text-xl font-bold text-purple-900">
                    🪐 {currentDasha.mahadasha?.planet || 'Unknown'} Mahadasha
                  </h3>
                  <Badge className="bg-purple-600">Active</Badge>
                </div>

                <div className="mb-4">
                  <div className="flex justify-between text-sm text-purple-700 mb-2">
                    <span>{currentDasha.mahadasha?.start_date || 'N/A'}</span>
                    <span>{currentDasha.mahadasha?.end_date || 'N/A'}</span>
                  </div>
                  <div className="w-full bg-purple-200 rounded-full h-3 overflow-hidden">
                    <div
                      className="bg-gradient-to-r from-purple-500 to-indigo-600 h-full rounded-full transition-all duration-1000"
                      style={{
                        width: `${currentDasha.mahadasha?.progress_percentage || 0}%`
                      }}
                    ></div>
                  </div>
                  <p className="text-sm text-purple-700 mt-2 text-center">
                    {currentDasha.mahadasha?.progress_percentage?.toFixed(1) || 0}% Complete
                  </p>
                </div>

                {/* Antardasha */}
                {currentDasha.antardasha && (
                  <div className="p-4 bg-white/70 rounded-lg border border-purple-200">
                    <p className="text-sm font-semibold text-gray-600 mb-2">Current Sub-Period:</p>
                    <p className="text-lg font-bold text-purple-900">
                      {currentDasha.antardasha.planet} Antardasha
                    </p>
                    <p className="text-sm text-gray-600 mt-1">
                      {currentDasha.antardasha.start_date} - {currentDasha.antardasha.end_date}
                    </p>
                  </div>
                )}

                {/* Pratyantar Dasha */}
                {currentDasha.pratyantardasha && (
                  <div className="p-4 bg-white/70 rounded-lg border border-purple-200 mt-3">
                    <p className="text-sm font-semibold text-gray-600 mb-2">Micro Sub-Period:</p>
                    <p className="text-lg font-bold text-purple-900">
                      {currentDasha.pratyantardasha.planet} Pratyantardasha
                    </p>
                    <p className="text-sm text-gray-600 mt-1">
                      {currentDasha.pratyantardasha.start_date} - {currentDasha.pratyantardasha.end_date}
                    </p>
                  </div>
                )}
              </div>

              {/* Quick insights */}
              <div className="p-4 bg-gradient-to-r from-amber-50 to-orange-50 rounded-lg border border-amber-200">
                <h4 className="font-semibold text-amber-900 mb-2 flex items-center gap-2">
                  <Sparkles className="w-4 h-4" />
                  What This Phase Brings
                </h4>
                <ul className="text-sm text-amber-800 space-y-1">
                  <li>• {getPlanetaryInfluence(currentDasha.mahadasha?.planet || '')}</li>
                  <li>• Focus on {getPlanetaryFocus(currentDasha.mahadasha?.planet || '')}</li>
                  <li>• Key themes: {getPlanetaryThemes(currentDasha.mahadasha?.planet || '')}</li>
                </ul>
              </div>

              <div className="flex gap-3">
                <Link href={`/dashboard/chart/${primaryProfile.id}`} className="flex-1">
                  <Button className="w-full gap-2">
                    <Eye className="w-4 h-4" />
                    View Life Threads Timeline
                  </Button>
                </Link>
                <Link href="/dashboard/ask" className="flex-1">
                  <Button variant="outline" className="w-full gap-2">
                    <MessageSquare className="w-4 h-4" />
                    Get Period Guidance
                  </Button>
                </Link>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* PHASE 1: QUICK ACTIONS GRID */}
      <Card>
        <CardHeader>
          <CardTitle className="text-2xl">Quick Actions</CardTitle>
          <CardDescription>One-click access to your cosmic tools</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
            <Link href={primaryProfile ? `/dashboard/chart/${primaryProfile.id}` : '/dashboard/profiles/new'}>
              <Button variant="outline" className="w-full h-24 flex flex-col gap-2 hover:bg-blue-50 hover:border-blue-300 transition-all">
                <Activity className="w-8 h-8 text-blue-600" />
                <span className="text-sm font-semibold">View Chart</span>
              </Button>
            </Link>

            <Link href="/dashboard/ask">
              <Button variant="outline" className="w-full h-24 flex flex-col gap-2 hover:bg-purple-50 hover:border-purple-300 transition-all">
                <MessageSquare className="w-8 h-8 text-purple-600" />
                <span className="text-sm font-semibold">Ask Question</span>
              </Button>
            </Link>

            <Link href="/dashboard/numerology">
              <Button variant="outline" className="w-full h-24 flex flex-col gap-2 hover:bg-green-50 hover:border-green-300 transition-all">
                <TrendingUp className="w-8 h-8 text-green-600" />
                <span className="text-sm font-semibold">Numerology</span>
              </Button>
            </Link>

            <Link href="/dashboard/compatibility">
              <Button variant="outline" className="w-full h-24 flex flex-col gap-2 hover:bg-pink-50 hover:border-pink-300 transition-all">
                <Heart className="w-8 h-8 text-pink-600" />
                <span className="text-sm font-semibold">Compatibility</span>
              </Button>
            </Link>

            <Link href="/dashboard/varshaphal">
              <Button variant="outline" className="w-full h-24 flex flex-col gap-2 hover:bg-orange-50 hover:border-orange-300 transition-all">
                <Calendar className="w-8 h-8 text-orange-600" />
                <span className="text-sm font-semibold">Varshaphal</span>
              </Button>
            </Link>

            <Link href="/dashboard/muhurta">
              <Button variant="outline" className="w-full h-24 flex flex-col gap-2 hover:bg-yellow-50 hover:border-yellow-300 transition-all">
                <Clock className="w-8 h-8 text-yellow-600" />
                <span className="text-sm font-semibold">Muhurta</span>
              </Button>
            </Link>

            <Link href="/dashboard/tarot">
              <Button variant="outline" className="w-full h-24 flex flex-col gap-2 hover:bg-indigo-50 hover:border-indigo-300 transition-all">
                <Star className="w-8 h-8 text-indigo-600" />
                <span className="text-sm font-semibold">Tarot</span>
              </Button>
            </Link>

            <Link href="/dashboard/profiles">
              <Button variant="outline" className="w-full h-24 flex flex-col gap-2 hover:bg-gray-50 hover:border-gray-300 transition-all">
                <User className="w-8 h-8 text-gray-600" />
                <span className="text-sm font-semibold">Profiles</span>
              </Button>
            </Link>
          </div>
        </CardContent>
      </Card>

      {/* Quick Stats */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium">Birth Profiles</CardTitle>
            <User className="w-4 h-4 text-jio-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{profiles?.length || 0}</div>
            <p className="text-xs text-gray-600 mt-1">
              {profiles?.length === 0 ? 'Create your first profile' : 'Active profiles'}
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium">Questions Asked</CardTitle>
            <MessageSquare className="w-4 h-4 text-jio-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{queries?.length || 0}</div>
            <p className="text-xs text-gray-600 mt-1">AI-powered insights</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium">Average Rating</CardTitle>
            <Star className="w-4 h-4 text-jio-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {feedbackStats?.average_rating
                ? `${feedbackStats.average_rating} ⭐`
                : 'N/A'}
            </div>
            <p className="text-xs text-gray-600 mt-1">Your feedback</p>
          </CardContent>
        </Card>
      </div>

      {/* Profiles Section */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <Card>
          <CardHeader>
            <CardTitle>Birth Profiles</CardTitle>
            <CardDescription>Manage your birth charts</CardDescription>
          </CardHeader>
          <CardContent>
            {profilesLoading ? (
              <div className="text-center py-8">
                <div className="w-6 h-6 border-3 border-jio-600 border-t-transparent rounded-full animate-spin mx-auto"></div>
              </div>
            ) : profiles && profiles.length > 0 ? (
              <div className="space-y-3">
                {profiles.slice(0, 3).map((profile: any) => (
                  <div key={profile.id} className="p-3 border rounded-lg hover:border-jio-300 transition-colors">
                    <div className="flex items-center justify-between mb-2">
                      <div>
                        <p className="font-semibold">{profile.name}</p>
                        <p className="text-xs text-gray-600">
                          {new Date(profile.birth_date).toLocaleDateString()} at {profile.birth_time?.slice(0, 5) || 'N/A'}
                        </p>
                      </div>
                      {profile.is_primary && (
                        <Badge className="bg-jio-600">Primary</Badge>
                      )}
                    </div>
                    <div className="grid grid-cols-2 gap-2">
                      <Link href={`/dashboard/chart/${profile.id}`} className="w-full">
                        <Button variant="default" size="sm" className="w-full">
                          View Chart
                        </Button>
                      </Link>
                      <Button
                        variant="destructive"
                        size="sm"
                        className="w-full"
                        onClick={() => handleDeleteProfile(profile.id, profile.name)}
                        disabled={deletingProfile === profile.id}
                      >
                        {deletingProfile === profile.id ? 'Deleting...' : 'Delete'}
                      </Button>
                    </div>
                  </div>
                ))}
                {profiles.length > 3 && (
                  <Link href="/dashboard/profiles">
                    <Button variant="ghost" className="w-full text-sm">
                      View all {profiles.length} profiles →
                    </Button>
                  </Link>
                )}
              </div>
            ) : (
              <div className="text-center py-8">
                <p className="text-gray-600 mb-4">No profiles yet</p>
                <Link href="/dashboard/profiles/new">
                  <Button>
                    <Plus className="w-4 h-4 mr-2" />
                    Create Your First Profile
                  </Button>
                </Link>
              </div>
            )}
          </CardContent>
        </Card>

        {/* Recent Questions */}
        <Card>
          <CardHeader>
            <CardTitle>Recent Questions</CardTitle>
            <CardDescription>Your latest insights</CardDescription>
          </CardHeader>
          <CardContent>
            {queriesLoading ? (
              <div className="text-center py-8">
                <div className="w-6 h-6 border-3 border-jio-600 border-t-transparent rounded-full animate-spin mx-auto"></div>
              </div>
            ) : queries && queries.length > 0 ? (
              <div className="space-y-3">
                {queries.slice(0, 3).map((item: any, index: number) => {
                  const query = item?.query ?? item
                  if (!query) return null
                  const createdAt = query.created_at ?? item?.created_at
                  const key = query.id ?? item?.id ?? `query-${index}`

                  return (
                    <div key={key} className="p-3 border rounded-lg">
                      <p className="text-sm font-medium line-clamp-2">
                        {query.question ?? 'Question unavailable'}
                      </p>
                      {createdAt && (
                        <p className="text-xs text-gray-500 mt-1">
                          {new Date(createdAt).toLocaleDateString()}
                        </p>
                      )}
                    </div>
                  )
                })}
                <Link href="/dashboard/history">
                  <Button variant="ghost" className="w-full text-sm">
                    View all history →
                  </Button>
                </Link>
              </div>
            ) : (
              <div className="text-center py-8">
                <p className="text-gray-600 mb-4">No questions yet</p>
                <Link href="/dashboard/ask">
                  <Button>
                    <MessageSquare className="w-4 h-4 mr-2" />
                    Ask Your First Question
                  </Button>
                </Link>
              </div>
            )}
          </CardContent>
        </Card>
      </div>

      {/* Getting Started Guide (shown if no profiles) */}
      {!profilesLoading && (!profiles || profiles.length === 0) && (
        <Card className="bg-gradient-to-r from-jio-50 to-blue-50 border-jio-200">
          <CardHeader>
            <CardTitle>Getting Started</CardTitle>
            <CardDescription>Begin your astrological journey</CardDescription>
          </CardHeader>
          <CardContent>
            <ol className="space-y-4">
              <li className="flex items-start gap-3">
                <div className="flex-shrink-0 w-6 h-6 rounded-full bg-jio-600 text-white flex items-center justify-center text-sm font-bold">
                  1
                </div>
                <div>
                  <p className="font-semibold">Create Your Birth Profile</p>
                  <p className="text-sm text-gray-600">
                    Enter your birth details to generate your Vedic birth chart
                  </p>
                </div>
              </li>
              <li className="flex items-start gap-3">
                <div className="flex-shrink-0 w-6 h-6 rounded-full bg-jio-600 text-white flex items-center justify-center text-sm font-bold">
                  2
                </div>
                <div>
                  <p className="font-semibold">View Your Chart</p>
                  <p className="text-sm text-gray-600">
                    Explore planetary positions, yogas, and dasha timeline
                  </p>
                </div>
              </li>
              <li className="flex items-start gap-3">
                <div className="flex-shrink-0 w-6 h-6 rounded-full bg-jio-600 text-white flex items-center justify-center text-sm font-bold">
                  3
                </div>
                <div>
                  <p className="font-semibold">Ask Questions</p>
                  <p className="text-sm text-gray-600">
                    Get AI-powered insights about your life path
                  </p>
                </div>
              </li>
            </ol>
            <div className="mt-6">
              <Link href="/dashboard/profiles/new">
                <Button size="lg" className="w-full md:w-auto">
                  <Plus className="w-4 h-4 mr-2" />
                  Create Your First Profile
                </Button>
              </Link>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  )
}

// Helper functions for planetary insights
function getPlanetaryInfluence(planet: string): string {
  const influences: Record<string, string> = {
    Sun: 'Leadership, vitality, and recognition in your life',
    Moon: 'Emotional growth, intuition, and nurturing energy',
    Mars: 'Action, courage, and assertive energy',
    Mercury: 'Communication, learning, and intellectual pursuits',
    Jupiter: 'Wisdom, expansion, and fortunate opportunities',
    Venus: 'Love, beauty, and material comfort',
    Saturn: 'Discipline, responsibility, and structured growth',
    Rahu: 'Unconventional path, sudden changes, and innovation',
    Ketu: 'Spiritual growth, detachment, and inner wisdom',
  }
  return influences[planet] || 'Transformative energy and personal growth'
}

function getPlanetaryFocus(planet: string): string {
  const focus: Record<string, string> = {
    Sun: 'career advancement and personal authority',
    Moon: 'emotional well-being and family matters',
    Mars: 'taking bold actions and overcoming obstacles',
    Mercury: 'business, communication, and skill development',
    Jupiter: 'education, spirituality, and mentorship',
    Venus: 'relationships, creativity, and financial gains',
    Saturn: 'hard work, patience, and long-term planning',
    Rahu: 'breaking boundaries and exploring new territories',
    Ketu: 'spiritual practices and letting go of attachments',
  }
  return focus[planet] || 'personal development and growth'
}

function getPlanetaryThemes(planet: string): string {
  const themes: Record<string, string> = {
    Sun: 'Self-expression, confidence, government',
    Moon: 'Family, emotions, public image',
    Mars: 'Energy, competition, real estate',
    Mercury: 'Trade, writing, adaptability',
    Jupiter: 'Teaching, law, higher learning',
    Venus: 'Romance, arts, luxury',
    Saturn: 'Structure, karma, delays',
    Rahu: 'Technology, foreign lands, ambition',
    Ketu: 'Moksha, research, intuition',
  }
  return themes[planet] || 'Growth and transformation'
}

// Add missing icon component
function Sun(props: any) {
  return <Sunrise {...props} />
}

function Sunset(props: any) {
  return <Sunrise {...props} />
}
