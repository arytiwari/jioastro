'use client'

import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@/lib/query'
import { apiClient } from '@/lib/api'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Badge } from '@/components/ui/badge'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Label } from '@/components/ui/label'
import { Progress } from '@/components/ui/progress'
import { Checkbox } from '@/components/ui/checkbox'
import { Compass, User, Home, MapPin, Palette, Star, CheckCircle2, Circle } from 'lucide-react'

export default function FengShuiPage() {
  const queryClient = useQueryClient()
  const [activeTab, setActiveTab] = useState('calculator')
  const [selectedProfileId, setSelectedProfileId] = useState<string | null>(null)
  const [spaceType, setSpaceType] = useState<string>('home')
  const [spaceOrientation, setSpaceOrientation] = useState<string>('')
  const [selectedAnalysisId, setSelectedAnalysisId] = useState<string | null>(null)

  // Fetch user profiles (REQUIRED for Kua calculation)
  const { data: profilesData } = useQuery({
    queryKey: ['profiles'],
    queryFn: async () => {
      const response = await apiClient.getProfiles()
      return response.data
    },
  })

  // Fetch user's analyses
  const { data: analysesData, isLoading: isLoadingAnalyses } = useQuery({
    queryKey: ['feng-shui-analyses'],
    queryFn: async () => {
      const response = await apiClient.getFengShuiAnalyses(20)
      return response.data
    },
  })

  // Calculate Kua mutation
  const kuaMutation = useMutation({
    mutationFn: async (profileId: string) => {
      const response = await apiClient.calculateKua(profileId)
      return response.data
    },
  })

  // Create analysis mutation
  const createAnalysisMutation = useMutation({
    mutationFn: async (data: {
      profile_id: string
      space_type?: string
      space_orientation?: string
    }) => {
      const response = await apiClient.createFengShuiAnalysis(data)
      return response.data
    },
    onSuccess: (data) => {
      queryClient.invalidateQueries(['feng-shui-analyses'])
      setSelectedAnalysisId(data.id)
      setActiveTab('analyses')
    },
  })

  const handleCalculateKua = () => {
    if (!selectedProfileId) return
    kuaMutation.mutate(selectedProfileId)
  }

  const handleCreateAnalysis = () => {
    if (!selectedProfileId) return
    createAnalysisMutation.mutate({
      profile_id: selectedProfileId,
      space_type: spaceType || undefined,
      space_orientation: spaceOrientation || undefined,
    })
  }

  const directions = ['N', 'NE', 'E', 'SE', 'S', 'SW', 'W', 'NW']

  return (
    <div className="container mx-auto p-6 max-w-7xl">
      {/* Header */}
      <div className="mb-8">
        <div className="flex items-center gap-3 mb-2">
          <Compass className="h-8 w-8 text-green-600" />
          <h1 className="text-4xl font-bold">Feng Shui Intelligence</h1>
        </div>
        <p className="text-muted-foreground text-lg">
          Harmonize your space with ancient Feng Shui wisdom and Kua number calculations
        </p>
      </div>

      {/* Profile Selector (REQUIRED) */}
      <Card className="mb-6 border-green-200">
        <CardHeader>
          <CardTitle className="text-lg flex items-center gap-2">
            <User className="h-5 w-5 text-green-600" />
            Birth Profile Required
          </CardTitle>
          <CardDescription>
            Feng Shui analysis requires your birth date and gender to calculate your Kua number
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-2">
            <Label htmlFor="profile-select-fs">Select Birth Profile *</Label>
            <Select
              value={selectedProfileId || ''}
              onValueChange={(value) => setSelectedProfileId(value)}
            >
              <SelectTrigger id="profile-select-fs">
                <SelectValue placeholder="Choose your birth profile" />
              </SelectTrigger>
              <SelectContent>
                {profilesData?.map((profile: any) => (
                  <SelectItem key={profile.id} value={profile.id}>
                    {profile.name} - Born {new Date(profile.birth_date).toLocaleDateString()} ({profile.gender})
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
            {!selectedProfileId && (
              <p className="text-sm text-amber-600">
                ⚠️ Profile selection is required to calculate your Kua number
              </p>
            )}
          </div>
        </CardContent>
      </Card>

      {/* Main Tabs */}
      <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-6">
        <TabsList className="grid w-full grid-cols-3 lg:w-auto">
          <TabsTrigger value="calculator" className="flex items-center gap-2">
            <Compass className="h-4 w-4" />
            <span className="hidden sm:inline">Kua Calculator</span>
          </TabsTrigger>
          <TabsTrigger value="analyzer" className="flex items-center gap-2">
            <Home className="h-4 w-4" />
            <span className="hidden sm:inline">Space Analyzer</span>
          </TabsTrigger>
          <TabsTrigger value="analyses" className="flex items-center gap-2">
            <MapPin className="h-4 w-4" />
            <span className="hidden sm:inline">My Analyses</span>
            {analysesData?.total_count > 0 && (
              <Badge variant="secondary" className="ml-1">
                {analysesData.total_count}
              </Badge>
            )}
          </TabsTrigger>
        </TabsList>

        {/* Kua Calculator Tab */}
        <TabsContent value="calculator" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Calculate Your Kua Number</CardTitle>
              <CardDescription>
                Discover your personal Kua number and favorable directions
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {!selectedProfileId ? (
                  <div className="text-center py-8">
                    <User className="h-12 w-12 mx-auto text-muted-foreground mb-4" />
                    <p className="text-muted-foreground">
                      Please select a birth profile above to calculate your Kua number
                    </p>
                  </div>
                ) : kuaMutation.isPending ? (
                  <div className="text-center py-12">
                    <Compass className="h-12 w-12 mx-auto text-green-600 animate-spin mb-4" />
                    <p className="text-muted-foreground">Calculating your Kua number...</p>
                  </div>
                ) : kuaMutation.data ? (
                  <KuaResults data={kuaMutation.data} />
                ) : (
                  <Button
                    onClick={handleCalculateKua}
                    className="w-full bg-green-600 hover:bg-green-700"
                    size="lg"
                  >
                    <Compass className="h-5 w-5 mr-2" />
                    Calculate My Kua Number
                  </Button>
                )}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Space Analyzer Tab */}
        <TabsContent value="analyzer" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Analyze Your Space</CardTitle>
              <CardDescription>
                Get personalized Feng Shui recommendations for your home or office
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              {!selectedProfileId ? (
                <div className="text-center py-8">
                  <User className="h-12 w-12 mx-auto text-muted-foreground mb-4" />
                  <p className="text-muted-foreground">
                    Please select a birth profile above to analyze your space
                  </p>
                </div>
              ) : (
                <>
                  <div className="space-y-2">
                    <Label htmlFor="space-type">Space Type</Label>
                    <Select value={spaceType} onValueChange={setSpaceType}>
                      <SelectTrigger id="space-type">
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="home">Home</SelectItem>
                        <SelectItem value="office">Office</SelectItem>
                        <SelectItem value="bedroom">Bedroom</SelectItem>
                        <SelectItem value="living_room">Living Room</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="space-orientation">Main Entrance Facing (Optional)</Label>
                    <Select value={spaceOrientation} onValueChange={setSpaceOrientation}>
                      <SelectTrigger id="space-orientation">
                        <SelectValue placeholder="Select direction" />
                      </SelectTrigger>
                      <SelectContent>
                        {directions.map((dir) => (
                          <SelectItem key={dir} value={dir}>{dir}</SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>

                  <Button
                    onClick={handleCreateAnalysis}
                    disabled={createAnalysisMutation.isPending}
                    className="w-full bg-green-600 hover:bg-green-700"
                    size="lg"
                  >
                    {createAnalysisMutation.isPending ? (
                      <>
                        <Compass className="h-5 w-5 mr-2 animate-spin" />
                        Analyzing...
                      </>
                    ) : (
                      <>
                        <Home className="h-5 w-5 mr-2" />
                        Analyze My Space
                      </>
                    )}
                  </Button>
                </>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        {/* Analyses History Tab */}
        <TabsContent value="analyses" className="space-y-6">
          {selectedAnalysisId ? (
            <div>
              <Button
                variant="outline"
                onClick={() => setSelectedAnalysisId(null)}
                className="mb-4"
              >
                ← Back to Analyses List
              </Button>
              <AnalysisDetail analysisId={selectedAnalysisId} />
            </div>
          ) : (
            <AnalysesList
              analyses={analysesData?.analyses || []}
              isLoading={isLoadingAnalyses}
              onAnalysisClick={setSelectedAnalysisId}
            />
          )}
        </TabsContent>
      </Tabs>
    </div>
  )
}

// Kua Results Component
function KuaResults({ data }: { data: any }) {
  return (
    <div className="space-y-6">
      {/* Kua Number Display */}
      <div className="text-center p-6 border-2 border-green-200 rounded-lg bg-green-50">
        <h3 className="text-sm font-medium text-muted-foreground mb-2">Your Kua Number</h3>
        <div className="text-6xl font-bold text-green-600 mb-2">{data.kua_number}</div>
        <Badge variant="outline" className="mb-4">{data.personal_element.toUpperCase()} Element</Badge>
        <p className="text-sm text-muted-foreground">{data.life_gua_group.toUpperCase()} Life Group</p>
      </div>

      {/* Description */}
      <div className="prose prose-sm max-w-none">
        <p>{data.description}</p>
      </div>

      {/* Favorable Directions */}
      <div>
        <h4 className="font-semibold mb-3 flex items-center gap-2">
          <CheckCircle2 className="h-5 w-5 text-green-600" />
          Favorable Directions
        </h4>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
          {Object.entries(data.favorable_directions).map(([key, dir]: [string, any]) => (
            <div key={key} className="p-3 border border-green-300 rounded-lg bg-green-50">
              <div className="text-xl font-bold text-green-600 text-center">{dir}</div>
              <div className="text-xs text-center mt-1 capitalize">{key.replace('_', ' ')}</div>
            </div>
          ))}
        </div>
      </div>

      {/* Unfavorable Directions */}
      <div>
        <h4 className="font-semibold mb-3 flex items-center gap-2">
          <Circle className="h-5 w-5 text-red-600" />
          Unfavorable Directions (Avoid)
        </h4>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
          {Object.entries(data.unfavorable_directions).map(([key, dir]: [string, any]) => (
            <div key={key} className="p-3 border border-red-300 rounded-lg bg-red-50">
              <div className="text-xl font-bold text-red-600 text-center">{dir}</div>
              <div className="text-xs text-center mt-1 capitalize">{key.replace('_', ' ')}</div>
            </div>
          ))}
        </div>
      </div>

      {/* Colors */}
      <div className="grid md:grid-cols-2 gap-4">
        <div>
          <h4 className="font-semibold mb-3 flex items-center gap-2">
            <Palette className="h-5 w-5 text-green-600" />
            Lucky Colors
          </h4>
          <div className="flex flex-wrap gap-2">
            {data.lucky_colors.map((color: string, idx: number) => (
              <Badge key={idx} variant="outline" className="capitalize">{color}</Badge>
            ))}
          </div>
        </div>
        <div>
          <h4 className="font-semibold mb-3 flex items-center gap-2">
            <Palette className="h-5 w-5 text-red-600" />
            Unlucky Colors (Avoid)
          </h4>
          <div className="flex flex-wrap gap-2">
            {data.unlucky_colors.map((color: string, idx: number) => (
              <Badge key={idx} variant="destructive" className="capitalize">{color}</Badge>
            ))}
          </div>
        </div>
      </div>
    </div>
  )
}

// Analyses List Component
function AnalysesList({
  analyses,
  isLoading,
  onAnalysisClick
}: {
  analyses: any[]
  isLoading: boolean
  onAnalysisClick: (id: string) => void
}) {
  if (isLoading) {
    return (
      <Card>
        <CardContent className="py-12 text-center">
          <Compass className="h-12 w-12 mx-auto text-green-600 animate-spin mb-4" />
          <p className="text-muted-foreground">Loading your analyses...</p>
        </CardContent>
      </Card>
    )
  }

  if (!analyses || analyses.length === 0) {
    return (
      <Card>
        <CardContent className="py-12 text-center">
          <Home className="h-12 w-12 mx-auto text-muted-foreground mb-4" />
          <p className="text-muted-foreground">No analyses yet. Analyze your first space!</p>
        </CardContent>
      </Card>
    )
  }

  return (
    <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
      {analyses.map((analysis: any) => (
        <Card
          key={analysis.id}
          className="cursor-pointer hover:border-green-300 transition-colors"
          onClick={() => onAnalysisClick(analysis.id)}
        >
          <CardHeader>
            <CardTitle className="text-lg flex items-center justify-between">
              Kua {analysis.kua_number}
              <Badge variant="outline">{analysis.personal_element}</Badge>
            </CardTitle>
            <CardDescription className="capitalize">
              {analysis.space_type || 'Space analysis'}
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              <div className="flex items-center justify-between text-sm">
                <span className="text-muted-foreground">Compatibility</span>
                <span className="font-semibold">{analysis.compatibility_score.toFixed(0)}%</span>
              </div>
              <Progress value={analysis.compatibility_score} className="h-2" />
              <p className="text-xs text-muted-foreground">
                {new Date(analysis.created_at).toLocaleDateString()}
              </p>
            </div>
          </CardContent>
        </Card>
      ))}
    </div>
  )
}

// Analysis Detail Component
function AnalysisDetail({ analysisId }: { analysisId: string }) {
  const { data: analysis, isLoading } = useQuery({
    queryKey: ['feng-shui-analysis', analysisId],
    queryFn: async () => {
      const response = await apiClient.getFengShuiAnalysis(analysisId)
      return response.data
    },
  })

  const { data: recommendationsData } = useQuery({
    queryKey: ['feng-shui-recommendations', analysisId],
    queryFn: async () => {
      const response = await apiClient.getFengShuiRecommendations(analysisId)
      return response.data
    },
    enabled: !!analysisId,
  })

  if (isLoading || !analysis) {
    return (
      <Card>
        <CardContent className="py-12 text-center">
          <Compass className="h-12 w-12 mx-auto text-green-600 animate-spin mb-4" />
          <p className="text-muted-foreground">Loading analysis...</p>
        </CardContent>
      </Card>
    )
  }

  return (
    <div className="space-y-6">
      {/* Kua Summary */}
      <Card>
        <CardHeader>
          <CardTitle className="text-2xl flex items-center justify-between">
            Feng Shui Analysis
            <Badge variant="outline" className="text-lg">Kua {analysis.kua_number}</Badge>
          </CardTitle>
          <CardDescription>{analysis.analysis_summary}</CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          {/* Compatibility Score */}
          <div>
            <div className="flex items-center justify-between mb-2">
              <span className="font-semibold">Space Compatibility</span>
              <span className="text-2xl font-bold text-green-600">{analysis.compatibility_score.toFixed(0)}%</span>
            </div>
            <Progress value={analysis.compatibility_score} className="h-3" />
          </div>

          {/* Holistic Harmony */}
          {analysis.astrology_feng_shui_harmony && (
            <div className="border-t pt-4">
              <h3 className="font-semibold mb-2 flex items-center gap-2">
                <Star className="h-4 w-4 text-green-600" />
                Astrological Harmony
              </h3>
              <p className="text-sm">{analysis.astrology_feng_shui_harmony}</p>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Recommendations */}
      {recommendationsData && (
        <RecommendationsList
          recommendations={recommendationsData.recommendations || []}
          analysisId={analysisId}
        />
      )}
    </div>
  )
}

// Recommendations List Component
function RecommendationsList({ recommendations, analysisId }: { recommendations: any[], analysisId: string }) {
  const queryClient = useQueryClient()

  const updateMutation = useMutation({
    mutationFn: async ({ id, is_implemented }: { id: string, is_implemented: boolean }) => {
      const response = await apiClient.updateFengShuiRecommendation(id, { is_implemented })
      return response.data
    },
    onSuccess: () => {
      queryClient.invalidateQueries(['feng-shui-recommendations', analysisId])
    },
  })

  const handleToggle = (id: string, currentState: boolean) => {
    updateMutation.mutate({ id, is_implemented: !currentState })
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>Recommendations ({recommendations.length})</CardTitle>
        <CardDescription>
          Track your implementation progress
        </CardDescription>
      </CardHeader>
      <CardContent>
        <div className="space-y-3">
          {recommendations.map((rec: any) => (
            <div key={rec.id} className="flex items-start gap-3 p-4 border rounded-lg hover:bg-accent transition-colors">
              <Checkbox
                checked={rec.is_implemented}
                onCheckedChange={() => handleToggle(rec.id, rec.is_implemented)}
                className="mt-1"
              />
              <div className="flex-1 space-y-1">
                <div className="flex items-start justify-between gap-2">
                  <h4 className="font-semibold">{rec.title}</h4>
                  <Badge variant={rec.priority === 'high' ? 'destructive' : rec.priority === 'medium' ? 'default' : 'outline'}>
                    {rec.priority}
                  </Badge>
                </div>
                <p className="text-sm text-muted-foreground">{rec.recommendation}</p>
                {rec.reason && (
                  <p className="text-xs text-muted-foreground italic">Why: {rec.reason}</p>
                )}
              </div>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  )
}
