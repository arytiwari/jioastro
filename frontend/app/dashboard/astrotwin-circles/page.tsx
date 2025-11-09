'use client'

import { useState, useEffect } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Badge } from '@/components/ui/badge'
import {
  Users,
  Search,
  TrendingUp,
  Lock,
  Globe,
  BarChart3,
  MessageCircle,
  CheckCircle,
  Clock,
  Star
} from '@/components/icons'
import { UserPlus } from 'lucide-react'
import { apiClient } from '@/lib/api'

interface Profile {
  id: string
  name: string
  birth_date: string
  birth_place: string
}

interface AstroTwinMatch {
  profile_id: string
  similarity_score: number
  feature_metadata: {
    sun_sign?: string
    moon_sign?: string
    ascendant?: string
    dominant_planets?: string[]
    major_yogas?: string[]
    life_stage?: string
    saturn_phase?: string
  }
  shared_features: string[]
}

interface Circle {
  id: string
  circle_name: string
  circle_description: string
  circle_type: string
  is_private: boolean
  member_count: number
  user_role?: string
  user_join_status?: string
  tags: string[]
}

interface Stats {
  total_twins_found: number
  circles_joined: number
  outcomes_reported: number
  discovery_enabled: boolean
  most_similar_twin_score?: number
}

export default function AstroTwinCirclesPage() {
  const [activeTab, setActiveTab] = useState('discovery')
  const [profiles, setProfiles] = useState<Profile[]>([])
  const [selectedProfile, setSelectedProfile] = useState<string>('')
  const [discoveryEnabled, setDiscoveryEnabled] = useState(false)
  const [twins, setTwins] = useState<AstroTwinMatch[]>([])
  const [circles, setCircles] = useState<Circle[]>([])
  const [stats, setStats] = useState<Stats | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  // Load user data on mount
  useEffect(() => {
    loadProfiles()
    loadStats()
    loadCircles()
  }, [])

  const loadProfiles = async () => {
    try {
      const response = await apiClient.get('/profiles')
      setProfiles(response.data || [])
      if (response.data && response.data.length > 0) {
        setSelectedProfile(response.data[0].id)
      }
    } catch (err: any) {
      console.error('Failed to load profiles:', err)
    }
  }

  const loadStats = async () => {
    try {
      const response = await apiClient.get('/astrotwin/stats')
      setStats(response.data)
      setDiscoveryEnabled(response.data.discovery_enabled)
    } catch (err: any) {
      console.log('Stats not available yet')
    }
  }

  const loadCircles = async () => {
    try {
      const response = await apiClient.get('/astrotwin/circles')
      setCircles(response.data.circles || [])
    } catch (err: any) {
      console.error('Failed to load circles:', err)
    }
  }

  const enableDiscovery = async () => {
    if (!selectedProfile) {
      setError('Please select a profile first')
      return
    }

    setLoading(true)
    setError(null)

    try {
      await apiClient.post(`/astrotwin/enable-discovery?profile_id=${selectedProfile}`, {
        privacy_opt_in: true,
        visible_in_search: true,
        allow_pattern_learning: false
      })

      setDiscoveryEnabled(true)
      await loadStats()
      alert('Discovery enabled successfully! You can now find AstroTwins.')
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to enable discovery')
    } finally {
      setLoading(false)
    }
  }

  const findTwins = async () => {
    setLoading(true)
    setError(null)

    try {
      const response = await apiClient.post('/astrotwin/find-twins', {
        similarity_threshold: 0.3,
        limit: 50
      })

      setTwins(response.data.matches || [])
      if (response.data.matches.length === 0) {
        setError('No AstroTwins found yet. Check back later as more users join!')
      }
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to find twins')
    } finally {
      setLoading(false)
    }
  }

  const joinCircle = async (circleId: string) => {
    setLoading(true)
    setError(null)

    try {
      await apiClient.post(`/astrotwin/circles/${circleId}/join`, {
        circle_id: circleId,
        share_outcomes: false
      })

      alert('Join request sent! Waiting for approval.')
      await loadCircles()
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to join circle')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="container mx-auto px-4 py-8 max-w-7xl">
      <div className="mb-8">
        <h1 className="text-4xl font-bold mb-3 bg-gradient-to-r from-purple-600 to-pink-600 bg-clip-text text-transparent">
          AstroTwin Circles
        </h1>
        <p className="text-muted-foreground text-lg">
          Find people with similar birth charts and learn from shared life patterns
        </p>
      </div>

      {error && (
        <Card className="mb-6 border-red-500 bg-red-50 dark:bg-red-950">
          <CardContent className="pt-6">
            <p className="text-red-600 dark:text-red-400">{error}</p>
          </CardContent>
        </Card>
      )}

      <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-6">
        <TabsList className="grid w-full grid-cols-4">
          <TabsTrigger value="discovery" className="flex items-center gap-2">
            <TrendingUp className="w-4 h-4" />
            Discovery
          </TabsTrigger>
          <TabsTrigger value="find" className="flex items-center gap-2" disabled={!discoveryEnabled}>
            <Search className="w-4 h-4" />
            Find Twins
          </TabsTrigger>
          <TabsTrigger value="circles" className="flex items-center gap-2">
            <Users className="w-4 h-4" />
            Circles
          </TabsTrigger>
          <TabsTrigger value="stats" className="flex items-center gap-2">
            <BarChart3 className="w-4 h-4" />
            Stats
          </TabsTrigger>
        </TabsList>

        {/* Discovery Tab */}
        <TabsContent value="discovery">
          <Card>
            <CardHeader>
              <CardTitle>Enable AstroTwin Discovery</CardTitle>
              <CardDescription>
                Allow the system to analyze your birth chart and find people with similar astrological patterns
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              {discoveryEnabled ? (
                <div className="flex items-center gap-3 p-4 bg-green-50 dark:bg-green-950 rounded-lg border border-green-200 dark:border-green-800">
                  <CheckCircle className="w-6 h-6 text-green-600" />
                  <div>
                    <p className="font-semibold text-green-900 dark:text-green-100">Discovery Enabled</p>
                    <p className="text-sm text-green-700 dark:text-green-300">
                      Your chart is being compared with others to find AstroTwins
                    </p>
                  </div>
                </div>
              ) : (
                <>
                  <div className="space-y-4">
                    <div>
                      <label className="block text-sm font-medium mb-2">Select Profile</label>
                      <select
                        value={selectedProfile}
                        onChange={(e) => setSelectedProfile(e.target.value)}
                        className="w-full p-3 border rounded-lg bg-background"
                      >
                        <option value="">Choose a profile...</option>
                        {profiles.map((profile) => (
                          <option key={profile.id} value={profile.id}>
                            {profile.name} - {new Date(profile.birth_date).toLocaleDateString()}
                          </option>
                        ))}
                      </select>
                    </div>

                    <div className="bg-blue-50 dark:bg-blue-950 p-4 rounded-lg border border-blue-200 dark:border-blue-800">
                      <h4 className="font-semibold text-blue-900 dark:text-blue-100 mb-2">Privacy & Features</h4>
                      <ul className="space-y-2 text-sm text-blue-800 dark:text-blue-200">
                        <li className="flex items-start gap-2">
                          <Lock className="w-4 h-4 mt-0.5 flex-shrink-0" />
                          <span>Your personal details remain private - only chart patterns are compared</span>
                        </li>
                        <li className="flex items-start gap-2">
                          <Users className="w-4 h-4 mt-0.5 flex-shrink-0" />
                          <span>Find people with similar planetary positions, yogas, and life stages</span>
                        </li>
                        <li className="flex items-start gap-2">
                          <Globe className="w-4 h-4 mt-0.5 flex-shrink-0" />
                          <span>Join circles and learn from shared experiences</span>
                        </li>
                      </ul>
                    </div>
                  </div>

                  <Button
                    onClick={enableDiscovery}
                    disabled={loading || !selectedProfile}
                    className="w-full"
                    size="lg"
                  >
                    {loading ? 'Enabling...' : 'Enable Discovery'}
                  </Button>
                </>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        {/* Find Twins Tab */}
        <TabsContent value="find">
          <Card>
            <CardHeader>
              <CardTitle>Find Your AstroTwins</CardTitle>
              <CardDescription>
                Discover people with similar birth charts and astrological patterns
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              <Button onClick={findTwins} disabled={loading} size="lg">
                {loading ? 'Searching...' : 'Find AstroTwins'}
              </Button>

              {twins.length > 0 && (
                <div className="space-y-4">
                  <h3 className="font-semibold text-lg">Found {twins.length} AstroTwins</h3>
                  {twins.map((twin, index) => (
                    <Card key={index} className="border-purple-200 dark:border-purple-800">
                      <CardContent className="pt-6">
                        <div className="flex items-start justify-between mb-4">
                          <div className="flex-1">
                            <div className="flex items-center gap-3 mb-2">
                              <Badge variant="secondary" className="text-lg px-3 py-1">
                                {Math.round(twin.similarity_score * 100)}% Match
                              </Badge>
                              <Star className="w-5 h-5 text-yellow-500" />
                            </div>
                            <div className="grid grid-cols-3 gap-4 mt-4">
                              {twin.feature_metadata.sun_sign && (
                                <div>
                                  <p className="text-xs text-muted-foreground">Sun</p>
                                  <p className="font-semibold">{twin.feature_metadata.sun_sign}</p>
                                </div>
                              )}
                              {twin.feature_metadata.moon_sign && (
                                <div>
                                  <p className="text-xs text-muted-foreground">Moon</p>
                                  <p className="font-semibold">{twin.feature_metadata.moon_sign}</p>
                                </div>
                              )}
                              {twin.feature_metadata.ascendant && (
                                <div>
                                  <p className="text-xs text-muted-foreground">Ascendant</p>
                                  <p className="font-semibold">{twin.feature_metadata.ascendant}</p>
                                </div>
                              )}
                            </div>
                          </div>
                        </div>

                        {twin.shared_features.length > 0 && (
                          <div className="mt-4">
                            <p className="text-sm font-medium mb-2">Shared Features:</p>
                            <div className="flex flex-wrap gap-2">
                              {twin.shared_features.map((feature, idx) => (
                                <Badge key={idx} variant="outline">{feature}</Badge>
                              ))}
                            </div>
                          </div>
                        )}
                      </CardContent>
                    </Card>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        {/* Circles Tab */}
        <TabsContent value="circles">
          <div className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle>Browse AstroTwin Circles</CardTitle>
                <CardDescription>
                  Join communities of people with similar charts and life experiences
                </CardDescription>
              </CardHeader>
              <CardContent>
                {circles.length === 0 ? (
                  <p className="text-center text-muted-foreground py-8">
                    No circles available yet. Check back later!
                  </p>
                ) : (
                  <div className="grid gap-4">
                    {circles.map((circle) => (
                      <Card key={circle.id} className="border-2">
                        <CardHeader>
                          <div className="flex items-start justify-between">
                            <div>
                              <CardTitle className="text-xl">{circle.circle_name}</CardTitle>
                              <CardDescription className="mt-2">
                                {circle.circle_description}
                              </CardDescription>
                            </div>
                            <Badge variant={circle.is_private ? "secondary" : "default"}>
                              {circle.is_private ? (
                                <><Lock className="w-3 h-3 mr-1" /> Private</>
                              ) : (
                                <><Globe className="w-3 h-3 mr-1" /> Public</>
                              )}
                            </Badge>
                          </div>
                        </CardHeader>
                        <CardContent>
                          <div className="flex items-center justify-between">
                            <div className="flex items-center gap-4 text-sm text-muted-foreground">
                              <span className="flex items-center gap-1">
                                <Users className="w-4 h-4" />
                                {circle.member_count} members
                              </span>
                              <Badge variant="outline">{circle.circle_type}</Badge>
                            </div>

                            {circle.user_join_status === 'active' ? (
                              <Button variant="outline" disabled>
                                <CheckCircle className="w-4 h-4 mr-2" />
                                Joined
                              </Button>
                            ) : circle.user_join_status === 'pending' ? (
                              <Button variant="outline" disabled>
                                <Clock className="w-4 h-4 mr-2" />
                                Pending
                              </Button>
                            ) : (
                              <Button onClick={() => joinCircle(circle.id)} disabled={loading}>
                                <UserPlus className="w-4 h-4 mr-2" />
                                Join Circle
                              </Button>
                            )}
                          </div>
                        </CardContent>
                      </Card>
                    ))}
                  </div>
                )}
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        {/* Stats Tab */}
        <TabsContent value="stats">
          <div className="grid gap-6 md:grid-cols-2">
            <Card>
              <CardHeader>
                <CardTitle>Discovery Stats</CardTitle>
                <CardDescription>Your AstroTwin activity overview</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="flex items-center justify-between p-4 bg-purple-50 dark:bg-purple-950 rounded-lg">
                  <div>
                    <p className="text-sm text-muted-foreground">AstroTwins Found</p>
                    <p className="text-3xl font-bold text-purple-600">{stats?.total_twins_found || 0}</p>
                  </div>
                  <Users className="w-10 h-10 text-purple-600" />
                </div>

                <div className="flex items-center justify-between p-4 bg-blue-50 dark:bg-blue-950 rounded-lg">
                  <div>
                    <p className="text-sm text-muted-foreground">Circles Joined</p>
                    <p className="text-3xl font-bold text-blue-600">{stats?.circles_joined || 0}</p>
                  </div>
                  <Globe className="w-10 h-10 text-blue-600" />
                </div>

                {stats?.most_similar_twin_score && (
                  <div className="flex items-center justify-between p-4 bg-green-50 dark:bg-green-950 rounded-lg">
                    <div>
                      <p className="text-sm text-muted-foreground">Best Match</p>
                      <p className="text-3xl font-bold text-green-600">
                        {Math.round(stats.most_similar_twin_score * 100)}%
                      </p>
                    </div>
                    <Star className="w-10 h-10 text-green-600" />
                  </div>
                )}
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>How It Works</CardTitle>
                <CardDescription>Understanding AstroTwin matching</CardDescription>
              </CardHeader>
              <CardContent className="space-y-3 text-sm">
                <div className="flex gap-3">
                  <div className="w-8 h-8 rounded-full bg-purple-100 dark:bg-purple-900 flex items-center justify-center flex-shrink-0">
                    <span className="font-bold text-purple-600">1</span>
                  </div>
                  <div>
                    <p className="font-semibold">Chart Analysis</p>
                    <p className="text-muted-foreground">
                      Your chart is converted to a 384-dimensional vector encoding planets, houses, yogas, and dashas
                    </p>
                  </div>
                </div>

                <div className="flex gap-3">
                  <div className="w-8 h-8 rounded-full bg-purple-100 dark:bg-purple-900 flex items-center justify-center flex-shrink-0">
                    <span className="font-bold text-purple-600">2</span>
                  </div>
                  <div>
                    <p className="font-semibold">Similarity Search</p>
                    <p className="text-muted-foreground">
                      Advanced vector similarity finds charts with matching astrological patterns
                    </p>
                  </div>
                </div>

                <div className="flex gap-3">
                  <div className="w-8 h-8 rounded-full bg-purple-100 dark:bg-purple-900 flex items-center justify-center flex-shrink-0">
                    <span className="font-bold text-purple-600">3</span>
                  </div>
                  <div>
                    <p className="font-semibold">Community Learning</p>
                    <p className="text-muted-foreground">
                      Join circles to share experiences and discover patterns in life outcomes
                    </p>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>
      </Tabs>
    </div>
  )
}
