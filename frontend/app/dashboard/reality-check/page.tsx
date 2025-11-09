"use client"

import { useState, useEffect } from 'react'
import { useToast } from '@/hooks/use-toast'
import { apiClient } from '@/lib/api'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Progress } from "@/components/ui/progress"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog"
import { Label } from "@/components/ui/label"
import { Textarea } from "@/components/ui/textarea"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Input } from "@/components/ui/input"
import { Checkbox } from "@/components/ui/checkbox"
import {
  CheckCircle2,
  XCircle,
  Clock,
  TrendingUp,
  TrendingDown,
  Award,
  Target,
  AlertCircle,
  Lightbulb,
  BarChart3,
  Calendar
} from 'lucide-react'


interface UserStats {
  total_predictions: number
  verified_predictions: number
  pending_predictions: number
  overall_accuracy_rate: number | null
  avg_helpfulness_rating: number | null
  trust_rate: number | null
  best_category: string | null
  best_category_accuracy: number | null
  worst_category: string | null
  worst_category_accuracy: number | null
  category_breakdown: Record<string, any>
}

interface Prediction {
  id: string
  prediction_type: string
  prediction_category: string
  prediction_text: string
  prediction_summary: string | null
  confidence_level: string
  expected_timeframe_start: string | null
  expected_timeframe_end: string | null
  timeframe_description: string | null
  status: string
  created_at: string
}

interface Outcome {
  id: string
  prediction_id: string
  outcome_occurred: boolean
  actual_date: string | null
  outcome_description: string
  accuracy_score: number | null
  timing_accuracy: string | null
  severity_match: string | null
  helpfulness_rating: number
  would_trust_again: boolean
  created_at: string
}

interface LearningInsight {
  id: string
  insight_type: string
  category: string
  title: string
  description: string
  sample_size: number
  accuracy_rate: number | null
  impact_level: string
  actionable_recommendations: string[]
}

interface CategoryAccuracy {
  category: string
  total_predictions: number
  verified_predictions: number
  accuracy_rate: number | null
}


export default function RealityCheckPage() {
  const { toast } = useToast()
  const [loading, setLoading] = useState(true)
  const [userStats, setUserStats] = useState<UserStats | null>(null)
  const [predictions, setPredictions] = useState<Prediction[]>([])
  const [pendingPredictions, setPendingPredictions] = useState<Prediction[]>([])
  const [insights, setInsights] = useState<LearningInsight[]>([])
  const [selectedPrediction, setSelectedPrediction] = useState<Prediction | null>(null)
  const [outcomeDialogOpen, setOutcomeDialogOpen] = useState(false)

  // Outcome form state
  const [outcomeForm, setOutcomeForm] = useState({
    outcome_occurred: false,
    actual_date: '',
    outcome_description: '',
    timing_accuracy: 'on_time',
    severity_match: 'accurate',
    what_matched: '',
    what_differed: '',
    additional_events: '',
    helpfulness_rating: 3,
    would_trust_again: true,
  })

  useEffect(() => {
    loadDashboardData()
  }, [])

  const loadDashboardData = async () => {
    try {
      setLoading(true)

      // Load user stats
      const statsResponse = await apiClient.get('/reality-check/stats')
      setUserStats(statsResponse.data)

      // Load recent predictions
      const predictionsResponse = await apiClient.get('/reality-check/predictions?limit=10')
      setPredictions(predictionsResponse.data.predictions || [])

      // Load pending predictions
      const pendingResponse = await apiClient.get('/reality-check/predictions?status=active&limit=10')
      setPendingPredictions(pendingResponse.data.predictions || [])

      // Load insights
      const insightsResponse = await apiClient.get('/reality-check/insights?limit=5')
      setInsights(insightsResponse.data.insights || [])

    } catch (error: any) {
      toast({
        title: "Error",
        description: error.response?.data?.detail || "Failed to load dashboard data",
        variant: "destructive"
      })
    } finally {
      setLoading(false)
    }
  }

  const openOutcomeDialog = (prediction: Prediction) => {
    setSelectedPrediction(prediction)
    setOutcomeForm({
      outcome_occurred: false,
      actual_date: '',
      outcome_description: '',
      timing_accuracy: 'on_time',
      severity_match: 'accurate',
      what_matched: '',
      what_differed: '',
      additional_events: '',
      helpfulness_rating: 3,
      would_trust_again: true,
    })
    setOutcomeDialogOpen(true)
  }

  const submitOutcome = async () => {
    if (!selectedPrediction) return

    try {
      await apiClient.post('/reality-check/outcomes', {
        prediction_id: selectedPrediction.id,
        ...outcomeForm
      })

      toast({
        title: "Success",
        description: "Outcome recorded successfully"
      })

      setOutcomeDialogOpen(false)
      loadDashboardData()
    } catch (error: any) {
      toast({
        title: "Error",
        description: error.response?.data?.detail || "Failed to record outcome",
        variant: "destructive"
      })
    }
  }

  const getConfidenceBadgeColor = (level: string) => {
    switch (level) {
      case 'very_high': return 'bg-green-600'
      case 'high': return 'bg-blue-600'
      case 'medium': return 'bg-yellow-600'
      case 'low': return 'bg-gray-600'
      default: return 'bg-gray-600'
    }
  }

  const getCategoryBadgeColor = (category: string) => {
    const colors: Record<string, string> = {
      career: 'bg-purple-600',
      relationships: 'bg-pink-600',
      health: 'bg-green-600',
      finances: 'bg-emerald-600',
      spiritual: 'bg-indigo-600',
      general: 'bg-gray-600'
    }
    return colors[category] || 'bg-gray-600'
  }

  if (loading) {
    return (
      <div className="p-6">
        <div className="flex items-center justify-center h-64">
          <div className="text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-gray-900 mx-auto mb-4"></div>
            <p className="text-gray-600">Loading Reality Check Dashboard...</p>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold mb-2">Reality Check Loop</h1>
        <p className="text-gray-600">Track predictions, record outcomes, and learn from feedback</p>
      </div>

      {/* Stats Overview */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-gray-600">Total Predictions</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold">{userStats?.total_predictions || 0}</div>
            <p className="text-xs text-gray-500 mt-1">
              {userStats?.pending_predictions || 0} pending verification
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-gray-600">Overall Accuracy</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold">
              {userStats?.overall_accuracy_rate !== null && userStats?.overall_accuracy_rate !== undefined
                ? `${userStats.overall_accuracy_rate.toFixed(1)}%`
                : 'N/A'}
            </div>
            <Progress
              value={userStats?.overall_accuracy_rate || 0}
              className="mt-2"
            />
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-gray-600">Helpfulness</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold">
              {userStats?.avg_helpfulness_rating !== null && userStats?.avg_helpfulness_rating !== undefined
                ? `${userStats.avg_helpfulness_rating.toFixed(1)}/5`
                : 'N/A'}
            </div>
            <div className="flex items-center mt-2 text-xs text-gray-500">
              <Award className="h-3 w-3 mr-1" />
              Average user rating
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-gray-600">Trust Rate</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold">
              {userStats?.trust_rate !== null && userStats?.trust_rate !== undefined
                ? `${userStats.trust_rate.toFixed(1)}%`
                : 'N/A'}
            </div>
            <p className="text-xs text-gray-500 mt-1">
              Would trust again
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Best/Worst Categories */}
      {userStats?.best_category && userStats?.best_category_accuracy !== null && userStats?.best_category_accuracy !== undefined && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <Card className="border-green-200 bg-green-50">
            <CardHeader>
              <CardTitle className="text-sm font-medium flex items-center gap-2">
                <TrendingUp className="h-4 w-4 text-green-600" />
                Best Category
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-lg font-bold capitalize">{userStats.best_category}</p>
                  <p className="text-sm text-gray-600">
                    {userStats.best_category_accuracy.toFixed(1)}% accuracy
                  </p>
                </div>
                <Badge className={getCategoryBadgeColor(userStats.best_category)}>
                  Strength
                </Badge>
              </div>
            </CardContent>
          </Card>

          {userStats?.worst_category && userStats?.worst_category_accuracy !== null && userStats?.worst_category_accuracy !== undefined && (
            <Card className="border-orange-200 bg-orange-50">
              <CardHeader>
                <CardTitle className="text-sm font-medium flex items-center gap-2">
                  <TrendingDown className="h-4 w-4 text-orange-600" />
                  Needs Improvement
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-lg font-bold capitalize">{userStats.worst_category}</p>
                    <p className="text-sm text-gray-600">
                      {userStats.worst_category_accuracy.toFixed(1)}% accuracy
                    </p>
                  </div>
                  <Badge className={getCategoryBadgeColor(userStats.worst_category)}>
                    Growth Area
                  </Badge>
                </div>
              </CardContent>
            </Card>
          )}
        </div>
      )}

      {/* Main Tabs */}
      <Tabs defaultValue="pending" className="space-y-4">
        <TabsList>
          <TabsTrigger value="pending" className="flex items-center gap-2">
            <Clock className="h-4 w-4" />
            Pending Outcomes ({pendingPredictions.length})
          </TabsTrigger>
          <TabsTrigger value="recent" className="flex items-center gap-2">
            <BarChart3 className="h-4 w-4" />
            Recent Predictions
          </TabsTrigger>
          <TabsTrigger value="insights" className="flex items-center gap-2">
            <Lightbulb className="h-4 w-4" />
            Learning Insights
          </TabsTrigger>
        </TabsList>

        {/* Pending Outcomes Tab */}
        <TabsContent value="pending" className="space-y-4">
          {pendingPredictions.length === 0 ? (
            <Card>
              <CardContent className="pt-6 text-center text-gray-500">
                <AlertCircle className="h-12 w-12 mx-auto mb-2 opacity-50" />
                <p>No pending predictions to verify</p>
              </CardContent>
            </Card>
          ) : (
            pendingPredictions.map((prediction) => (
              <Card key={prediction.id}>
                <CardHeader>
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="flex items-center gap-2 mb-2">
                        <Badge className={getCategoryBadgeColor(prediction.prediction_category)}>
                          {prediction.prediction_category}
                        </Badge>
                        <Badge className={getConfidenceBadgeColor(prediction.confidence_level)} variant="outline">
                          {prediction.confidence_level.replace('_', ' ')}
                        </Badge>
                      </div>
                      <CardTitle className="text-lg">
                        {prediction.prediction_summary || 'Prediction'}
                      </CardTitle>
                      <CardDescription className="mt-2">
                        {prediction.prediction_text}
                      </CardDescription>
                    </div>
                  </div>
                </CardHeader>
                <CardContent>
                  <div className="space-y-3">
                    {prediction.timeframe_description && (
                      <div className="flex items-center gap-2 text-sm text-gray-600">
                        <Calendar className="h-4 w-4" />
                        <span>{prediction.timeframe_description}</span>
                      </div>
                    )}
                    <div className="flex items-center gap-2 text-xs text-gray-500">
                      <span>Created: {new Date(prediction.created_at).toLocaleDateString()}</span>
                    </div>
                    <Button
                      onClick={() => openOutcomeDialog(prediction)}
                      className="w-full"
                    >
                      Record Outcome
                    </Button>
                  </div>
                </CardContent>
              </Card>
            ))
          )}
        </TabsContent>

        {/* Recent Predictions Tab */}
        <TabsContent value="recent" className="space-y-4">
          {predictions.length === 0 ? (
            <Card>
              <CardContent className="pt-6 text-center text-gray-500">
                <AlertCircle className="h-12 w-12 mx-auto mb-2 opacity-50" />
                <p>No predictions yet</p>
              </CardContent>
            </Card>
          ) : (
            predictions.map((prediction) => (
              <Card key={prediction.id}>
                <CardHeader>
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <Badge className={getCategoryBadgeColor(prediction.prediction_category)}>
                        {prediction.prediction_category}
                      </Badge>
                      {prediction.status === 'verified' && (
                        <CheckCircle2 className="h-5 w-5 text-green-600" />
                      )}
                      {prediction.status === 'rejected' && (
                        <XCircle className="h-5 w-5 text-red-600" />
                      )}
                    </div>
                    <Badge variant="outline">{prediction.status}</Badge>
                  </div>
                  <CardTitle className="text-base mt-2">
                    {prediction.prediction_summary || prediction.prediction_type}
                  </CardTitle>
                  <CardDescription>
                    {prediction.prediction_text.substring(0, 200)}
                    {prediction.prediction_text.length > 200 ? '...' : ''}
                  </CardDescription>
                </CardHeader>
              </Card>
            ))
          )}
        </TabsContent>

        {/* Learning Insights Tab */}
        <TabsContent value="insights" className="space-y-4">
          {insights.length === 0 ? (
            <Card>
              <CardContent className="pt-6 text-center text-gray-500">
                <Lightbulb className="h-12 w-12 mx-auto mb-2 opacity-50" />
                <p>No insights available yet</p>
                <p className="text-sm mt-1">Insights will appear as more outcomes are recorded</p>
              </CardContent>
            </Card>
          ) : (
            insights.map((insight) => (
              <Card key={insight.id}>
                <CardHeader>
                  <div className="flex items-center justify-between">
                    <CardTitle className="text-lg">{insight.title}</CardTitle>
                    <Badge className={
                      insight.impact_level === 'high' ? 'bg-red-600' :
                      insight.impact_level === 'medium' ? 'bg-yellow-600' :
                      'bg-gray-600'
                    }>
                      {insight.impact_level} impact
                    </Badge>
                  </div>
                  <CardDescription>
                    <Badge variant="outline" className="mr-2">{insight.category}</Badge>
                    <Badge variant="outline">{insight.insight_type}</Badge>
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-3">
                  <p className="text-sm">{insight.description}</p>

                  <div className="flex items-center gap-4 text-sm text-gray-600">
                    <div className="flex items-center gap-1">
                      <Target className="h-4 w-4" />
                      <span>Sample: {insight.sample_size} predictions</span>
                    </div>
                    {insight.accuracy_rate !== null && (
                      <div className="flex items-center gap-1">
                        <BarChart3 className="h-4 w-4" />
                        <span>Accuracy: {insight.accuracy_rate.toFixed(1)}%</span>
                      </div>
                    )}
                  </div>

                  {insight.actionable_recommendations.length > 0 && (
                    <div className="mt-3 p-3 bg-blue-50 rounded-lg">
                      <p className="text-sm font-medium mb-2">Recommendations:</p>
                      <ul className="list-disc list-inside text-sm space-y-1">
                        {insight.actionable_recommendations.map((rec, idx) => (
                          <li key={idx}>{rec}</li>
                        ))}
                      </ul>
                    </div>
                  )}
                </CardContent>
              </Card>
            ))
          )}
        </TabsContent>
      </Tabs>

      {/* Outcome Recording Dialog */}
      <Dialog open={outcomeDialogOpen} onOpenChange={setOutcomeDialogOpen}>
        <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle>Record Prediction Outcome</DialogTitle>
            <DialogDescription>
              {selectedPrediction?.prediction_summary || 'Prediction'}
            </DialogDescription>
          </DialogHeader>

          <div className="space-y-4 py-4">
            {/* Did it occur? */}
            <div className="flex items-center space-x-2">
              <Checkbox
                id="outcome_occurred"
                checked={outcomeForm.outcome_occurred}
                onCheckedChange={(checked) =>
                  setOutcomeForm({ ...outcomeForm, outcome_occurred: checked as boolean })
                }
              />
              <Label htmlFor="outcome_occurred" className="font-medium">
                This prediction occurred
              </Label>
            </div>

            {/* Actual Date */}
            {outcomeForm.outcome_occurred && (
              <div className="space-y-2">
                <Label htmlFor="actual_date">When did it occur?</Label>
                <Input
                  id="actual_date"
                  type="date"
                  value={outcomeForm.actual_date}
                  onChange={(e) => setOutcomeForm({ ...outcomeForm, actual_date: e.target.value })}
                />
              </div>
            )}

            {/* Outcome Description */}
            <div className="space-y-2">
              <Label htmlFor="outcome_description">What actually happened?</Label>
              <Textarea
                id="outcome_description"
                placeholder="Describe what actually occurred..."
                value={outcomeForm.outcome_description}
                onChange={(e) => setOutcomeForm({ ...outcomeForm, outcome_description: e.target.value })}
                rows={4}
                required
              />
            </div>

            {outcomeForm.outcome_occurred && (
              <>
                {/* Timing Accuracy */}
                <div className="space-y-2">
                  <Label htmlFor="timing_accuracy">Timing Accuracy</Label>
                  <Select
                    value={outcomeForm.timing_accuracy}
                    onValueChange={(value) => setOutcomeForm({ ...outcomeForm, timing_accuracy: value })}
                  >
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="on_time">On Time</SelectItem>
                      <SelectItem value="early">Early</SelectItem>
                      <SelectItem value="late">Late</SelectItem>
                      <SelectItem value="significantly_late">Significantly Late</SelectItem>
                    </SelectContent>
                  </Select>
                </div>

                {/* Severity Match */}
                <div className="space-y-2">
                  <Label htmlFor="severity_match">Severity Match</Label>
                  <Select
                    value={outcomeForm.severity_match}
                    onValueChange={(value) => setOutcomeForm({ ...outcomeForm, severity_match: value })}
                  >
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="accurate">Accurate</SelectItem>
                      <SelectItem value="understated">Understated (less severe than predicted)</SelectItem>
                      <SelectItem value="overstated">Overstated (more severe than predicted)</SelectItem>
                    </SelectContent>
                  </Select>
                </div>

                {/* What Matched */}
                <div className="space-y-2">
                  <Label htmlFor="what_matched">What matched the prediction?</Label>
                  <Textarea
                    id="what_matched"
                    placeholder="Aspects that aligned with the prediction..."
                    value={outcomeForm.what_matched}
                    onChange={(e) => setOutcomeForm({ ...outcomeForm, what_matched: e.target.value })}
                    rows={2}
                  />
                </div>

                {/* What Differed */}
                <div className="space-y-2">
                  <Label htmlFor="what_differed">What was different?</Label>
                  <Textarea
                    id="what_differed"
                    placeholder="Aspects that differed from the prediction..."
                    value={outcomeForm.what_differed}
                    onChange={(e) => setOutcomeForm({ ...outcomeForm, what_differed: e.target.value })}
                    rows={2}
                  />
                </div>
              </>
            )}

            {/* Helpfulness Rating */}
            <div className="space-y-2">
              <Label htmlFor="helpfulness_rating">
                Helpfulness Rating: {outcomeForm.helpfulness_rating}/5
              </Label>
              <input
                id="helpfulness_rating"
                type="range"
                min="1"
                max="5"
                value={outcomeForm.helpfulness_rating}
                onChange={(e) => setOutcomeForm({ ...outcomeForm, helpfulness_rating: parseInt(e.target.value) })}
                className="w-full"
              />
            </div>

            {/* Would Trust Again */}
            <div className="flex items-center space-x-2">
              <Checkbox
                id="would_trust_again"
                checked={outcomeForm.would_trust_again}
                onCheckedChange={(checked) =>
                  setOutcomeForm({ ...outcomeForm, would_trust_again: checked as boolean })
                }
              />
              <Label htmlFor="would_trust_again">
                I would trust similar predictions in the future
              </Label>
            </div>
          </div>

          <div className="flex justify-end gap-2">
            <Button variant="outline" onClick={() => setOutcomeDialogOpen(false)}>
              Cancel
            </Button>
            <Button onClick={submitOutcome} disabled={!outcomeForm.outcome_description}>
              Submit Outcome
            </Button>
          </div>
        </DialogContent>
      </Dialog>
    </div>
  )
}
