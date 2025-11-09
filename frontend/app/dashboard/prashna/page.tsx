'use client'

import { useState } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Textarea } from '@/components/ui/textarea'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { apiClient } from '@/lib/api'
import { useMutation, useQuery } from '@/lib/query'
import { Loader2, Calendar, MapPin, HelpCircle, Save, Trash2, Clock, Star } from 'lucide-react'

export default function PrashnaPage() {
  // Form state
  const [question, setQuestion] = useState('')
  const [questionType, setQuestionType] = useState('general')
  const [queryDate, setQueryDate] = useState(new Date().toISOString().split('T')[0])
  const [queryTime, setQueryTime] = useState(new Date().toTimeString().slice(0, 5))
  const [latitude, setLatitude] = useState('28.6139')
  const [longitude, setLongitude] = useState('77.2090')
  const [timezone, setTimezone] = useState('Asia/Kolkata')

  // Results state
  const [analysis, setAnalysis] = useState<any>(null)
  const [analysisError, setAnalysisError] = useState<string | null>(null)

  // Question types
  const questionTypes = [
    { value: 'career', label: 'Career & Profession' },
    { value: 'relationship', label: 'Relationship & Marriage' },
    { value: 'health', label: 'Health & Well-being' },
    { value: 'finance', label: 'Finance & Wealth' },
    { value: 'education', label: 'Education & Learning' },
    { value: 'legal', label: 'Legal & Court Matters' },
    { value: 'travel', label: 'Travel & Relocation' },
    { value: 'property', label: 'Property & Assets' },
    { value: 'children', label: 'Children & Family' },
    { value: 'spiritual', label: 'Spiritual & Religious' },
    { value: 'general', label: 'General Question' },
  ]

  // Analyze Prashna mutation
  const analyzeMutation = useMutation({
    mutationFn: async () => {
      setAnalysisError(null)
      const datetime = `${queryDate}T${queryTime}:00`
      const response = await apiClient.analyzePrashna({
        question,
        question_type: questionType,
        datetime,
        latitude: parseFloat(latitude),
        longitude: parseFloat(longitude),
        timezone,
      })
      return response.data
    },
    onSuccess: (data) => {
      setAnalysis(data)
      setAnalysisError(null)
    },
    onError: (error: any) => {
      console.error('Prashna analysis error:', error)
      setAnalysisError(error?.message || 'Failed to analyze question. Please try again.')
    },
  })

  // Save Prashna mutation
  const saveMutation = useMutation({
    mutationFn: async () => {
      if (!analysis) return
      const datetime = `${queryDate}T${queryTime}:00`
      const response = await apiClient.savePrashna({
        question,
        question_type: questionType,
        query_datetime: datetime,
        latitude: parseFloat(latitude),
        longitude: parseFloat(longitude),
        timezone,
        prashna_chart: analysis,
        analysis: analysis,
        notes: '',
      })
      return response.data
    },
    onSuccess: () => {
      alert('Prashna saved successfully!')
      savedPrashnas.refetch()
    },
    onError: (error: any) => {
      console.error('Save Prashna error:', error)
      alert('Failed to save Prashna. Please try again.')
    },
  })

  // Get saved Prashnas
  const savedPrashnas = useQuery({
    queryKey: ['prashnas'],
    queryFn: async () => {
      const response = await apiClient.getPrashnas(20, 0)
      return response.data
    },
  })

  // Delete Prashna mutation
  const deleteMutation = useMutation({
    mutationFn: async (prashnaId: string) => {
      await apiClient.deletePrashna(prashnaId)
    },
    onSuccess: () => {
      savedPrashnas.refetch()
    },
  })

  const handleAnalyze = () => {
    if (!question.trim()) {
      setAnalysisError('Please enter a question')
      return
    }
    analyzeMutation.mutate()
  }

  const handleSave = () => {
    if (!analysis) return
    saveMutation.mutate()
  }

  // Get outcome color
  const getOutcomeColor = (outcome: string) => {
    switch (outcome) {
      case 'favorable':
        return 'bg-green-50 border-green-200 dark:bg-green-900/20 dark:border-green-800'
      case 'unfavorable':
        return 'bg-red-50 border-red-200 dark:bg-red-900/20 dark:border-red-800'
      case 'mixed':
        return 'bg-yellow-50 border-yellow-200 dark:bg-yellow-900/20 dark:border-yellow-800'
      case 'uncertain':
        return 'bg-gray-50 border-gray-200 dark:bg-gray-900/20 dark:border-gray-800'
      default:
        return 'bg-gray-50 border-gray-200'
    }
  }

  const getOutcomeBadgeColor = (outcome: string) => {
    switch (outcome) {
      case 'favorable':
        return 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200'
      case 'unfavorable':
        return 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200'
      case 'mixed':
        return 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200'
      case 'uncertain':
        return 'bg-gray-100 text-gray-800 dark:bg-gray-900 dark:text-gray-200'
      default:
        return 'bg-gray-100 text-gray-800'
    }
  }

  const getConfidenceBadge = (confidence: string) => {
    const colors = {
      high: 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200',
      medium: 'bg-purple-100 text-purple-800 dark:bg-purple-900 dark:text-purple-200',
      low: 'bg-gray-100 text-gray-800 dark:bg-gray-900 dark:text-gray-200',
    }
    return colors[confidence as keyof typeof colors] || colors.medium
  }

  return (
    <div className="container mx-auto p-6 max-w-7xl">
      <div className="mb-8">
        <h1 className="text-3xl font-bold flex items-center gap-3">
          <HelpCircle className="w-8 h-8 text-purple-600" />
          Prashna - Horary Astrology
        </h1>
        <p className="text-muted-foreground mt-2">
          Ask a specific question and receive astrological guidance based on the chart cast for this exact moment
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left Column - Input Form */}
        <div className="lg:col-span-2 space-y-6">
          {/* Question Input */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <HelpCircle className="w-5 h-5" />
                Your Question
              </CardTitle>
              <CardDescription>
                Ask a clear, specific question about a matter concerning you
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <Label htmlFor="question">Question *</Label>
                <Textarea
                  id="question"
                  value={question}
                  onChange={(e) => setQuestion(e.target.value)}
                  placeholder="Will I get the job I interviewed for?"
                  rows={3}
                  className="mt-1"
                />
              </div>

              <div>
                <Label htmlFor="questionType">Question Type</Label>
                <Select value={questionType} onValueChange={setQuestionType}>
                  <SelectTrigger id="questionType" className="mt-1">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    {questionTypes.map((type) => (
                      <SelectItem key={type.value} value={type.value}>
                        {type.label}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
            </CardContent>
          </Card>

          {/* Time & Location */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Calendar className="w-5 h-5" />
                Question Moment & Location
              </CardTitle>
              <CardDescription>
                Enter the time and place when you are asking this question
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <Label htmlFor="date">Date *</Label>
                  <Input
                    id="date"
                    type="date"
                    value={queryDate}
                    onChange={(e) => setQueryDate(e.target.value)}
                    className="mt-1"
                  />
                </div>
                <div>
                  <Label htmlFor="time">Time *</Label>
                  <Input
                    id="time"
                    type="time"
                    value={queryTime}
                    onChange={(e) => setQueryTime(e.target.value)}
                    className="mt-1"
                  />
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <Label htmlFor="latitude">Latitude *</Label>
                  <Input
                    id="latitude"
                    type="number"
                    step="0.0001"
                    value={latitude}
                    onChange={(e) => setLatitude(e.target.value)}
                    placeholder="28.6139"
                    className="mt-1"
                  />
                </div>
                <div>
                  <Label htmlFor="longitude">Longitude *</Label>
                  <Input
                    id="longitude"
                    type="number"
                    step="0.0001"
                    value={longitude}
                    onChange={(e) => setLongitude(e.target.value)}
                    placeholder="77.2090"
                    className="mt-1"
                  />
                </div>
              </div>

              <div>
                <Label htmlFor="timezone">Timezone</Label>
                <Input
                  id="timezone"
                  value={timezone}
                  onChange={(e) => setTimezone(e.target.value)}
                  placeholder="Asia/Kolkata"
                  className="mt-1"
                />
              </div>

              <Button
                onClick={handleAnalyze}
                disabled={analyzeMutation.isPending}
                className="w-full"
                size="lg"
              >
                {analyzeMutation.isPending ? (
                  <>
                    <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                    Analyzing...
                  </>
                ) : (
                  <>
                    <Star className="w-4 h-4 mr-2" />
                    Analyze Question
                  </>
                )}
              </Button>

              {analysisError && (
                <div className="p-4 rounded-lg border border-red-300 bg-red-50 dark:bg-red-900/20">
                  <p className="text-sm text-red-600 dark:text-red-400">{analysisError}</p>
                </div>
              )}
            </CardContent>
          </Card>

          {/* Analysis Results */}
          {analysis && (
            <Card className={getOutcomeColor(analysis.answer?.outcome)}>
              <CardHeader>
                <CardTitle className="flex items-center justify-between">
                  <span>Prashna Analysis</span>
                  <div className="flex gap-2">
                    <span className={`px-3 py-1 rounded-full text-sm font-medium ${getOutcomeBadgeColor(analysis.answer?.outcome)}`}>
                      {analysis.answer?.outcome?.toUpperCase()}
                    </span>
                    <span className={`px-3 py-1 rounded-full text-sm font-medium ${getConfidenceBadge(analysis.answer?.confidence)}`}>
                      {analysis.answer?.confidence} confidence
                    </span>
                  </div>
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-6">
                {/* Summary */}
                <div>
                  <h3 className="font-semibold text-lg mb-2">Answer Summary</h3>
                  <p className="text-base">{analysis.answer?.summary}</p>
                </div>

                {/* Timing */}
                {analysis.answer?.timing && (
                  <div>
                    <h3 className="font-semibold flex items-center gap-2 mb-2">
                      <Clock className="w-4 h-4" />
                      Timing
                    </h3>
                    <p className="text-sm text-muted-foreground">{analysis.answer?.timing}</p>
                  </div>
                )}

                {/* Detailed Interpretation */}
                <div>
                  <h3 className="font-semibold text-lg mb-2">Detailed Interpretation</h3>
                  <pre className="text-sm whitespace-pre-wrap text-muted-foreground font-sans">
                    {analysis.answer?.detailed_interpretation}
                  </pre>
                </div>

                {/* Chart Details */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4 pt-4 border-t">
                  {/* Ascendant */}
                  <div>
                    <h4 className="font-semibold mb-2">Lagna (Ascendant)</h4>
                    <p className="text-sm text-muted-foreground">
                      {analysis.ascendant?.sign} rising ({analysis.ascendant?.degree?.toFixed(2)}°)
                    </p>
                    <p className="text-sm text-muted-foreground">
                      Lord: {analysis.ascendant?.lord} ({analysis.ascendant?.lord_strength})
                    </p>
                  </div>

                  {/* Moon */}
                  <div>
                    <h4 className="font-semibold mb-2">Moon</h4>
                    <p className="text-sm text-muted-foreground">
                      {analysis.moon?.sign} in house {analysis.moon?.house}
                    </p>
                    <p className="text-sm text-muted-foreground">
                      {analysis.moon?.nakshatra} ({analysis.moon?.lunar_phase})
                    </p>
                    <p className="text-sm text-muted-foreground">
                      Strength: {analysis.moon?.strength}
                    </p>
                  </div>
                </div>

                {/* Question Analysis */}
                <div className="pt-4 border-t">
                  <h3 className="font-semibold text-lg mb-3">Question Factors</h3>
                  <div className="space-y-2">
                    <p className="text-sm">
                      <span className="font-medium">Relevant House:</span> House {analysis.question_analysis?.relevant_house}
                    </p>
                    <p className="text-sm">
                      <span className="font-medium">House Lord:</span> {analysis.question_analysis?.house_lord} ({analysis.question_analysis?.house_lord_strength})
                    </p>
                    <p className="text-sm">
                      <span className="font-medium">Karaka Planet:</span> {analysis.question_analysis?.karaka_planet} ({analysis.question_analysis?.karaka_strength})
                    </p>
                  </div>
                </div>

                {/* Supporting/Opposing Factors */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4 pt-4 border-t">
                  <div>
                    <h4 className="font-semibold mb-2 text-green-700 dark:text-green-400">Supporting Factors</h4>
                    <ul className="list-disc list-inside text-sm text-muted-foreground space-y-1">
                      {analysis.question_analysis?.supporting_factors?.map((factor: string, idx: number) => (
                        <li key={idx}>{factor}</li>
                      ))}
                    </ul>
                  </div>
                  <div>
                    <h4 className="font-semibold mb-2 text-red-700 dark:text-red-400">Opposing Factors</h4>
                    <ul className="list-disc list-inside text-sm text-muted-foreground space-y-1">
                      {analysis.question_analysis?.opposing_factors?.map((factor: string, idx: number) => (
                        <li key={idx}>{factor}</li>
                      ))}
                    </ul>
                  </div>
                </div>

                {/* Recommendations */}
                {analysis.answer?.recommendations && analysis.answer.recommendations.length > 0 && (
                  <div className="pt-4 border-t">
                    <h4 className="font-semibold mb-2">Recommendations</h4>
                    <ul className="list-disc list-inside text-sm text-muted-foreground space-y-1">
                      {analysis.answer.recommendations.map((rec: string, idx: number) => (
                        <li key={idx}>{rec}</li>
                      ))}
                    </ul>
                  </div>
                )}

                {/* Precautions */}
                {analysis.answer?.precautions && analysis.answer.precautions.length > 0 && (
                  <div className="pt-4 border-t">
                    <h4 className="font-semibold mb-2">Precautions</h4>
                    <ul className="list-disc list-inside text-sm text-muted-foreground space-y-1">
                      {analysis.answer.precautions.map((prec: string, idx: number) => (
                        <li key={idx}>{prec}</li>
                      ))}
                    </ul>
                  </div>
                )}

                {/* Save Button */}
                <div className="pt-4 border-t">
                  <Button
                    onClick={handleSave}
                    disabled={saveMutation.isPending}
                    variant="outline"
                    className="w-full"
                  >
                    {saveMutation.isPending ? (
                      <>
                        <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                        Saving...
                      </>
                    ) : (
                      <>
                        <Save className="w-4 h-4 mr-2" />
                        Save This Analysis
                      </>
                    )}
                  </Button>
                </div>
              </CardContent>
            </Card>
          )}
        </div>

        {/* Right Column - Saved Prashnas */}
        <div className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Saved Questions</CardTitle>
              <CardDescription>
                Your previous Prashna queries
              </CardDescription>
            </CardHeader>
            <CardContent>
              {savedPrashnas.isLoading ? (
                <div className="flex justify-center py-8">
                  <Loader2 className="w-6 h-6 animate-spin text-muted-foreground" />
                </div>
              ) : savedPrashnas.data?.prashnas?.length === 0 ? (
                <p className="text-sm text-muted-foreground text-center py-8">
                  No saved questions yet
                </p>
              ) : (
                <div className="space-y-3">
                  {savedPrashnas.data?.prashnas?.map((prashna: any) => (
                    <div
                      key={prashna.id}
                      className="p-3 rounded-lg border bg-card hover:bg-accent/50 transition-colors"
                    >
                      <div className="flex justify-between items-start mb-2">
                        <span className="text-xs font-medium text-muted-foreground">
                          {questionTypes.find(t => t.value === prashna.question_type)?.label}
                        </span>
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => deleteMutation.mutate(prashna.id)}
                          className="h-6 w-6 p-0"
                        >
                          <Trash2 className="w-3 h-3" />
                        </Button>
                      </div>
                      <p className="text-sm font-medium line-clamp-2 mb-1">
                        {prashna.question}
                      </p>
                      <p className="text-xs text-muted-foreground">
                        {new Date(prashna.query_datetime).toLocaleDateString()}
                      </p>
                    </div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>

          {/* Info Card */}
          <Card>
            <CardHeader>
              <CardTitle>About Prashna</CardTitle>
            </CardHeader>
            <CardContent className="text-sm text-muted-foreground space-y-3">
              <p>
                Prashna (Horary Astrology) is the art of answering specific questions by analyzing the chart cast for the exact moment the question is asked.
              </p>
              <p>
                The most important factors in Prashna are:
              </p>
              <ul className="list-disc list-inside space-y-1 ml-2">
                <li>Ascendant (represents the querent)</li>
                <li>Moon position and strength</li>
                <li>Relevant house for the question</li>
                <li>Karaka (significator) planet</li>
                <li>Planetary aspects and combinations</li>
              </ul>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  )
}
