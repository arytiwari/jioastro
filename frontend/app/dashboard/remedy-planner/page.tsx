'use client'

import { useState, useEffect } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Badge } from '@/components/ui/badge'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Search, TrendingUp, Calendar, Award, CheckCircle2, Flame, Target, Book, Plus } from '@/components/icons'
import { apiClient } from '@/lib/api'
import { format } from 'date-fns'

interface Remedy {
  id: string
  remedy_name: string
  remedy_type: string
  description: string
  planet?: string
  dosha?: string
  frequency: string
  duration_days: number
  difficulty_level: string
  cost_estimate: string
  benefits: string[]
  materials_needed: string[]
}

interface Assignment {
  id: string
  remedy: Remedy
  status: string
  start_date: string
  target_date?: string
  current_streak: number
  longest_streak: number
  days_completed: number
  last_completion_date?: string
  streak_at_risk: boolean
  completion_rate: number
}

interface DashboardStats {
  today_completions: number
  active_assignments: number
  total_completed: number
  active_streaks: StreakInfo[]
  week_completion_rate: number
  month_completion_rate: number
  recent_achievements: Achievement[]
  total_days_practiced: number
}

interface StreakInfo {
  assignment_id: string
  remedy_name: string
  current_streak: number
  at_risk: boolean
}

interface Achievement {
  achievement_type: string
  title: string
  description: string
  unlocked_at: string
  icon: string
}

const REMEDY_TYPES = [
  { value: 'all', label: 'All Types' },
  { value: 'mantra', label: 'Mantra' },
  { value: 'gemstone', label: 'Gemstone' },
  { value: 'charity', label: 'Charity' },
  { value: 'fasting', label: 'Fasting' },
  { value: 'puja', label: 'Puja/Ritual' },
  { value: 'yantra', label: 'Yantra' },
  { value: 'meditation', label: 'Meditation' },
  { value: 'food', label: 'Food/Diet' },
  { value: 'lifestyle', label: 'Lifestyle' }
]

const PLANETS = [
  { value: 'all', label: 'All Planets' },
  { value: 'Sun', label: 'Sun' },
  { value: 'Moon', label: 'Moon' },
  { value: 'Mars', label: 'Mars' },
  { value: 'Mercury', label: 'Mercury' },
  { value: 'Jupiter', label: 'Jupiter' },
  { value: 'Venus', label: 'Venus' },
  { value: 'Saturn', label: 'Saturn' },
  { value: 'Rahu', label: 'Rahu' },
  { value: 'Ketu', label: 'Ketu' }
]

export default function RemedyPlannerPage() {
  const [activeTab, setActiveTab] = useState('dashboard')
  const [remedies, setRemedies] = useState<Remedy[]>([])
  const [assignments, setAssignments] = useState<Assignment[]>([])
  const [dashboard, setDashboard] = useState<DashboardStats | null>(null)
  const [searchQuery, setSearchQuery] = useState('')
  const [filterType, setFilterType] = useState('all')
  const [filterPlanet, setFilterPlanet] = useState('all')
  const [loading, setLoading] = useState(false)
  const [selectedRemedy, setSelectedRemedy] = useState<Remedy | null>(null)

  useEffect(() => {
    loadDashboard()
    loadAssignments()
  }, [])

  const loadDashboard = async () => {
    try {
      const response = await apiClient.get('/remedy-planner/dashboard')
      setDashboard(response.data)
    } catch (error) {
      console.error('Failed to load dashboard:', error)
    }
  }

  const loadAssignments = async () => {
    try {
      const response = await apiClient.get('/remedy-planner/assignments')
      setAssignments(response.data.assignments || [])
    } catch (error) {
      console.error('Failed to load assignments:', error)
    }
  }

  const searchRemedies = async () => {
    setLoading(true)
    try {
      const params: any = { limit: 20 }
      if (searchQuery) params.query = searchQuery
      if (filterType !== 'all') params.remedy_type = filterType
      if (filterPlanet !== 'all') params.planet = filterPlanet

      const response = await apiClient.post('/remedy-planner/remedies/search', params)
      setRemedies(response.data.remedies || [])
    } catch (error) {
      console.error('Failed to search remedies:', error)
    } finally {
      setLoading(false)
    }
  }

  const assignRemedy = async (remedyId: string) => {
    try {
      await apiClient.post('/remedy-planner/assignments', {
        remedy_id: remedyId,
        target_duration_days: 40,
        reminder_enabled: true
      })
      loadAssignments()
      loadDashboard()
      setSelectedRemedy(null)
    } catch (error) {
      console.error('Failed to assign remedy:', error)
    }
  }

  const trackCompletion = async (assignmentId: string) => {
    try {
      await apiClient.post('/remedy-planner/tracking', {
        assignment_id: assignmentId,
        completed: true,
        quality_rating: 4,
        tracking_date: format(new Date(), 'yyyy-MM-dd')
      })
      loadAssignments()
      loadDashboard()
    } catch (error) {
      console.error('Failed to track completion:', error)
    }
  }

  const getDifficultyColor = (difficulty: string) => {
    switch (difficulty) {
      case 'easy': return 'bg-green-500'
      case 'medium': return 'bg-yellow-500'
      case 'hard': return 'bg-red-500'
      default: return 'bg-gray-500'
    }
  }

  const getStreakColor = (streak: number, atRisk: boolean) => {
    if (atRisk) return 'text-orange-500'
    if (streak >= 30) return 'text-purple-500'
    if (streak >= 7) return 'text-blue-500'
    return 'text-gray-500'
  }

  return (
    <div className="container mx-auto p-6 space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold mb-2">Remedy Planner</h1>
        <p className="text-muted-foreground">
          Track Vedic remedies with habit streaks, achievements, and personalized guidance
        </p>
      </div>

      <Tabs value={activeTab} onValueChange={setActiveTab}>
        <TabsList className="grid w-full grid-cols-3">
          <TabsTrigger value="dashboard">Dashboard</TabsTrigger>
          <TabsTrigger value="catalog">Remedy Catalog</TabsTrigger>
          <TabsTrigger value="tracking">My Remedies</TabsTrigger>
        </TabsList>

        {/* Dashboard Tab */}
        <TabsContent value="dashboard" className="space-y-6">
          {dashboard && (
            <>
              {/* Stats Grid */}
              <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                <Card>
                  <CardHeader>
                    <CardTitle className="text-sm">Today's Practice</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="text-3xl font-bold">{dashboard.today_completions}</div>
                    <div className="text-sm text-muted-foreground">completions</div>
                  </CardContent>
                </Card>

                <Card>
                  <CardHeader>
                    <CardTitle className="text-sm">Active Remedies</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="text-3xl font-bold">{dashboard.active_assignments}</div>
                    <div className="text-sm text-muted-foreground">in progress</div>
                  </CardContent>
                </Card>

                <Card>
                  <CardHeader>
                    <CardTitle className="text-sm">Week Completion</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="text-3xl font-bold">{Math.round(dashboard.week_completion_rate)}%</div>
                    <div className="text-sm text-muted-foreground">this week</div>
                  </CardContent>
                </Card>

                <Card>
                  <CardHeader>
                    <CardTitle className="text-sm">Total Days</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="text-3xl font-bold">{dashboard.total_days_practiced}</div>
                    <div className="text-sm text-muted-foreground">practiced</div>
                  </CardContent>
                </Card>
              </div>

              {/* Active Streaks */}
              {dashboard.active_streaks.length > 0 && (
                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      <Flame className="h-5 w-5" />
                      Active Streaks
                    </CardTitle>
                    <CardDescription>Keep your practice consistent</CardDescription>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-3">
                      {dashboard.active_streaks.map((streak, index) => (
                        <div key={index} className="flex items-center justify-between p-3 bg-secondary/50 rounded-lg">
                          <div className="flex items-center gap-3">
                            <Flame className={`h-6 w-6 ${getStreakColor(streak.current_streak, streak.at_risk)}`} />
                            <div>
                              <div className="font-medium">{streak.remedy_name}</div>
                              {streak.at_risk && (
                                <div className="text-sm text-orange-500">⚠️ Streak at risk - complete today!</div>
                              )}
                            </div>
                          </div>
                          <div className={`text-2xl font-bold ${getStreakColor(streak.current_streak, streak.at_risk)}`}>
                            {streak.current_streak}
                          </div>
                        </div>
                      ))}
                    </div>
                  </CardContent>
                </Card>
              )}

              {/* Recent Achievements */}
              {dashboard.recent_achievements.length > 0 && (
                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      <Award className="h-5 w-5" />
                      Recent Achievements
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                      {dashboard.recent_achievements.map((achievement, index) => (
                        <div key={index} className="flex items-start gap-3 p-3 bg-gradient-to-r from-yellow-500/10 to-orange-500/10 rounded-lg border border-yellow-500/20">
                          <div className="text-3xl">{achievement.icon}</div>
                          <div>
                            <div className="font-semibold">{achievement.title}</div>
                            <div className="text-sm text-muted-foreground">{achievement.description}</div>
                            <div className="text-xs text-muted-foreground mt-1">
                              {format(new Date(achievement.unlocked_at), 'MMM d, yyyy')}
                            </div>
                          </div>
                        </div>
                      ))}
                    </div>
                  </CardContent>
                </Card>
              )}
            </>
          )}
        </TabsContent>

        {/* Catalog Tab */}
        <TabsContent value="catalog" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Search Remedies</CardTitle>
              <CardDescription>
                Browse 40+ authentic Vedic remedies from ancient scriptures
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div>
                  <Label>Search</Label>
                  <div className="relative">
                    <Search className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
                    <Input
                      placeholder="Search remedies..."
                      value={searchQuery}
                      onChange={(e) => setSearchQuery(e.target.value)}
                      className="pl-10"
                    />
                  </div>
                </div>

                <div>
                  <Label>Type</Label>
                  <Select value={filterType} onValueChange={setFilterType}>
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      {REMEDY_TYPES.map(type => (
                        <SelectItem key={type.value} value={type.value}>
                          {type.label}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>

                <div>
                  <Label>Planet</Label>
                  <Select value={filterPlanet} onValueChange={setFilterPlanet}>
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      {PLANETS.map(planet => (
                        <SelectItem key={planet.value} value={planet.value}>
                          {planet.label}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
              </div>

              <Button onClick={searchRemedies} className="w-full md:w-auto">
                <Search className="h-4 w-4 mr-2" />
                Search Remedies
              </Button>
            </CardContent>
          </Card>

          {/* Remedy Results */}
          {remedies.length > 0 && (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {remedies.map((remedy) => (
                <Card key={remedy.id} className="hover:shadow-lg transition-shadow">
                  <CardHeader>
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <CardTitle className="text-lg">{remedy.remedy_name}</CardTitle>
                        <div className="flex gap-2 mt-2">
                          <Badge variant="outline">{remedy.remedy_type}</Badge>
                          {remedy.planet && <Badge>{remedy.planet}</Badge>}
                          <Badge className={getDifficultyColor(remedy.difficulty_level)}>
                            {remedy.difficulty_level}
                          </Badge>
                        </div>
                      </div>
                    </div>
                  </CardHeader>
                  <CardContent className="space-y-3">
                    <p className="text-sm">{remedy.description}</p>

                    <div className="space-y-2 text-sm">
                      <div><strong>Frequency:</strong> {remedy.frequency}</div>
                      <div><strong>Duration:</strong> {remedy.duration_days} days</div>
                      <div><strong>Cost:</strong> {remedy.cost_estimate}</div>
                    </div>

                    {remedy.benefits.length > 0 && (
                      <div>
                        <div className="font-medium text-sm mb-1">Benefits:</div>
                        <ul className="text-sm space-y-1">
                          {remedy.benefits.slice(0, 3).map((benefit, index) => (
                            <li key={index} className="text-muted-foreground">• {benefit}</li>
                          ))}
                        </ul>
                      </div>
                    )}

                    <Button onClick={() => assignRemedy(remedy.id)} className="w-full">
                      <Plus className="h-4 w-4 mr-2" />
                      Assign to Me
                    </Button>
                  </CardContent>
                </Card>
              ))}
            </div>
          )}

          {loading && (
            <Card>
              <CardContent className="p-12 text-center">
                <div className="text-muted-foreground">Searching remedies...</div>
              </CardContent>
            </Card>
          )}
        </TabsContent>

        {/* My Remedies Tab */}
        <TabsContent value="tracking" className="space-y-6">
          {assignments.length > 0 ? (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {assignments.map((assignment) => (
                <Card key={assignment.id} className="relative overflow-hidden">
                  {/* Streak indicator */}
                  {assignment.current_streak >= 7 && (
                    <div className="absolute top-4 right-4">
                      <div className={`flex items-center gap-1 px-2 py-1 rounded-full ${assignment.current_streak >= 30 ? 'bg-purple-500' : 'bg-blue-500'} text-white text-sm font-bold`}>
                        <Flame className="h-4 w-4" />
                        {assignment.current_streak}
                      </div>
                    </div>
                  )}

                  <CardHeader>
                    <CardTitle>{assignment.remedy.remedy_name}</CardTitle>
                    <div className="flex gap-2">
                      <Badge>{assignment.status}</Badge>
                      <Badge variant="outline">{assignment.remedy.remedy_type}</Badge>
                    </div>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <div className="grid grid-cols-2 gap-4 text-sm">
                      <div>
                        <div className="text-muted-foreground">Days Completed</div>
                        <div className="text-2xl font-bold">{assignment.days_completed}</div>
                      </div>
                      <div>
                        <div className="text-muted-foreground">Completion Rate</div>
                        <div className="text-2xl font-bold">{Math.round(assignment.completion_rate)}%</div>
                      </div>
                    </div>

                    <div className="grid grid-cols-2 gap-4 text-sm">
                      <div>
                        <div className="text-muted-foreground">Current Streak</div>
                        <div className={`text-xl font-bold ${getStreakColor(assignment.current_streak, assignment.streak_at_risk)}`}>
                          {assignment.current_streak} days
                        </div>
                      </div>
                      <div>
                        <div className="text-muted-foreground">Best Streak</div>
                        <div className="text-xl font-bold text-green-500">{assignment.longest_streak} days</div>
                      </div>
                    </div>

                    {assignment.streak_at_risk && (
                      <div className="bg-orange-500/10 border border-orange-500/20 rounded-lg p-3 text-sm text-orange-600">
                        ⚠️ Your streak is at risk! Complete this remedy today to maintain it.
                      </div>
                    )}

                    {assignment.status === 'active' && (
                      <Button onClick={() => trackCompletion(assignment.id)} className="w-full">
                        <CheckCircle2 className="h-4 w-4 mr-2" />
                        Mark as Completed Today
                      </Button>
                    )}
                  </CardContent>
                </Card>
              ))}
            </div>
          ) : (
            <Card>
              <CardContent className="p-12 text-center space-y-4">
                <Book className="h-16 w-16 mx-auto text-muted-foreground" />
                <div>
                  <h3 className="text-lg font-semibold mb-2">No Active Remedies</h3>
                  <p className="text-muted-foreground mb-4">
                    Start your spiritual journey by exploring the remedy catalog
                  </p>
                  <Button onClick={() => setActiveTab('catalog')}>
                    Browse Remedies
                  </Button>
                </div>
              </CardContent>
            </Card>
          )}
        </TabsContent>
      </Tabs>
    </div>
  )
}
