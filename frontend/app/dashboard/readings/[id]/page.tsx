'use client'

import { useState, useEffect } from 'react'
import { useParams, useRouter } from 'next/navigation'
import { apiClient } from '@/lib/api'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import {
  Sparkles, BookOpen, Calendar, CheckCircle, AlertTriangle,
  Briefcase, Heart, Activity, TrendingUp, GraduationCap, Award,
  ArrowLeft, RefreshCw, Info
} from '@/components/icons'

const DOMAIN_ICONS: Record<string, any> = {
  career: Briefcase,
  wealth: TrendingUp,
  relationships: Heart,
  health: Activity,
  education: GraduationCap,
  spirituality: BookOpen,
}

const CONFIDENCE_COLORS: Record<string, string> = {
  very_high: 'bg-green-500',
  high: 'bg-blue-500',
  medium: 'bg-yellow-500',
  low: 'bg-orange-500',
  very_low: 'bg-red-500',
}

const CONFIDENCE_LABELS: Record<string, string> = {
  very_high: 'Very High',
  high: 'High',
  medium: 'Medium',
  low: 'Low',
  very_low: 'Very Low',
}

interface Reading {
  session_id: string
  interpretation: string
  domain_analyses?: Record<string, any>
  predictions?: any[]
  verification: {
    quality_score: number
    citation_accuracy: number
    contradictions_found: number
    confidence_level: string
  }
  rule_citations: any[]
  metadata: {
    tokens_used: number
    cost_usd: number
    cached: boolean
    generation_time_seconds?: number
  }
  created_at: string
}

export default function ReadingDetailsPage() {
  const params = useParams()
  const router = useRouter()
  const sessionId = params?.id as string

  const [reading, setReading] = useState<Reading | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [activeTab, setActiveTab] = useState('interpretation')
  const [regenerating, setRegenerating] = useState(false)

  useEffect(() => {
    if (!sessionId) return

    const loadReading = async () => {
      try {
        const response = await apiClient.getReading(sessionId)
        setReading(response.data)
      } catch (err: any) {
        console.error('Failed to load reading:', err)
        setError(err.message || 'Failed to load reading')
      } finally {
        setLoading(false)
      }
    }

    loadReading()
  }, [sessionId])

  const handleRegenerate = async () => {
    if (!reading) return

    setRegenerating(true)
    try {
      // The backend will ignore cache if we regenerate
      // We'd need to add a force_regenerate parameter to the API
      // For now, just reload the page
      window.location.reload()
    } catch (err: any) {
      console.error('Failed to regenerate:', err)
      alert('Failed to regenerate reading. Please try again.')
    } finally {
      setRegenerating(false)
    }
  }

  if (loading) {
    return (
      <div className="text-center py-12">
        <div className="w-8 h-8 border-4 border-jio-600 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
        <p className="text-gray-600">Loading reading...</p>
      </div>
    )
  }

  if (error || !reading) {
    return (
      <Card>
        <CardContent className="text-center py-12">
          <AlertTriangle className="w-12 h-12 text-red-500 mx-auto mb-4" />
          <h3 className="text-lg font-semibold mb-2">Failed to Load Reading</h3>
          <p className="text-gray-600 mb-6">{error || 'Reading not found'}</p>
          <Button onClick={() => router.push('/dashboard/readings')}>
            <ArrowLeft className="w-4 h-4 mr-2" />
            Back to Readings
          </Button>
        </CardContent>
      </Card>
    )
  }

  const domainAnalyses = reading.domain_analyses || {}
  const predictions = reading.predictions || []
  const verification = reading.verification
  const citations = reading.rule_citations || []

  return (
    <div className="max-w-6xl mx-auto space-y-6">
      {/* Header */}
      <div className="flex items-start justify-between">
        <div className="flex-1">
          <Button
            variant="ghost"
            onClick={() => router.push('/dashboard/readings')}
            className="mb-3 -ml-3"
          >
            <ArrowLeft className="w-4 h-4 mr-2" />
            Back to Readings
          </Button>
          <h1 className="text-3xl font-bold text-gray-900">Comprehensive Reading</h1>
          <p className="text-gray-600 mt-1">
            Generated on {new Date(reading.created_at).toLocaleString()}
          </p>
        </div>
        <Button
          onClick={handleRegenerate}
          variant="outline"
          disabled={regenerating}
        >
          {regenerating ? (
            <>
              <div className="w-4 h-4 border-2 border-gray-600 border-t-transparent rounded-full animate-spin mr-2"></div>
              Regenerating...
            </>
          ) : (
            <>
              <RefreshCw className="w-4 h-4 mr-2" />
              Regenerate
            </>
          )}
        </Button>
      </div>

      {/* Quality Indicators */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center gap-3">
              <div className={`w-10 h-10 rounded-full ${CONFIDENCE_COLORS[verification.confidence_level]} bg-opacity-20 flex items-center justify-center`}>
                <Award className={`w-5 h-5 ${CONFIDENCE_COLORS[verification.confidence_level].replace('bg-', 'text-')}`} />
              </div>
              <div>
                <p className="text-xs text-gray-600">Confidence</p>
                <p className="font-semibold">{CONFIDENCE_LABELS[verification.confidence_level]}</p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-full bg-green-100 flex items-center justify-center">
                <CheckCircle className="w-5 h-5 text-green-600" />
              </div>
              <div>
                <p className="text-xs text-gray-600">Quality Score</p>
                <p className="font-semibold">{verification.quality_score.toFixed(1)}/10</p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-full bg-blue-100 flex items-center justify-center">
                <BookOpen className="w-5 h-5 text-blue-600" />
              </div>
              <div>
                <p className="text-xs text-gray-600">Citations</p>
                <p className="font-semibold">{citations.length} rules</p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-full bg-purple-100 flex items-center justify-center">
                <Sparkles className="w-5 h-5 text-purple-600" />
              </div>
              <div>
                <p className="text-xs text-gray-600">Tokens</p>
                <p className="font-semibold">{reading.metadata.tokens_used.toLocaleString()}</p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Main Content Tabs */}
      <Card>
        <CardContent className="pt-6">
          <Tabs value={activeTab} onValueChange={setActiveTab}>
            <TabsList className="grid w-full grid-cols-4">
              <TabsTrigger value="interpretation">Interpretation</TabsTrigger>
              <TabsTrigger value="domains">
                Domains ({Object.keys(domainAnalyses).length})
              </TabsTrigger>
              {predictions.length > 0 && (
                <TabsTrigger value="predictions">
                  Predictions ({predictions.length})
                </TabsTrigger>
              )}
              <TabsTrigger value="citations">
                Citations ({citations.length})
              </TabsTrigger>
            </TabsList>

            {/* Interpretation Tab */}
            <TabsContent value="interpretation" className="space-y-4 mt-6">
              <div className="prose prose-sm max-w-none">
                <div className="whitespace-pre-wrap text-gray-700 leading-relaxed">
                  {reading.interpretation}
                </div>
              </div>
            </TabsContent>

            {/* Domain Analyses Tab */}
            <TabsContent value="domains" className="space-y-4 mt-6">
              {Object.keys(domainAnalyses).length === 0 ? (
                <p className="text-center text-gray-500 py-8">No domain-specific analyses available</p>
              ) : (
                <div className="space-y-4">
                  {Object.entries(domainAnalyses).map(([domain, analysis]: [string, any]) => {
                    const Icon = DOMAIN_ICONS[domain] || BookOpen
                    return (
                      <Card key={domain} className="border-l-4 border-jio-500">
                        <CardHeader>
                          <CardTitle className="flex items-center gap-2 capitalize">
                            <Icon className="w-5 h-5 text-jio-600" />
                            {domain}
                          </CardTitle>
                        </CardHeader>
                        <CardContent>
                          <div className="prose prose-sm max-w-none">
                            <div className="whitespace-pre-wrap text-gray-700 leading-relaxed">
                              {typeof analysis === 'string' ? analysis : analysis.interpretation || JSON.stringify(analysis, null, 2)}
                            </div>
                          </div>
                        </CardContent>
                      </Card>
                    )
                  })}
                </div>
              )}
            </TabsContent>

            {/* Predictions Tab */}
            {predictions.length > 0 && (
              <TabsContent value="predictions" className="space-y-4 mt-6">
                <div className="space-y-3">
                  {predictions.map((prediction: any, index: number) => (
                    <Card key={index} className="border-l-4 border-purple-500">
                      <CardContent className="pt-6">
                        <div className="flex items-start gap-4">
                          <div className="w-12 h-12 rounded-full bg-purple-100 flex items-center justify-center flex-shrink-0">
                            <Calendar className="w-6 h-6 text-purple-600" />
                          </div>
                          <div className="flex-1">
                            <div className="flex items-start justify-between mb-2">
                              <div>
                                <p className="font-semibold text-gray-900">{prediction.event_type || 'Prediction'}</p>
                                <p className="text-sm text-gray-600">
                                  {prediction.time_period || prediction.date_range || 'Upcoming period'}
                                </p>
                              </div>
                              {prediction.confidence && (
                                <span className={`px-2 py-1 text-xs font-medium rounded ${
                                  CONFIDENCE_COLORS[prediction.confidence]?.replace('bg-', 'bg-') + ' bg-opacity-20'
                                }`}>
                                  {CONFIDENCE_LABELS[prediction.confidence]}
                                </span>
                              )}
                            </div>
                            <p className="text-gray-700 leading-relaxed">
                              {prediction.description || prediction.interpretation}
                            </p>
                            {prediction.dasha_info && (
                              <p className="text-xs text-gray-500 mt-2">
                                Dasha: {prediction.dasha_info}
                              </p>
                            )}
                          </div>
                        </div>
                      </CardContent>
                    </Card>
                  ))}
                </div>
              </TabsContent>
            )}

            {/* Citations Tab */}
            <TabsContent value="citations" className="space-y-4 mt-6">
              {citations.length === 0 ? (
                <p className="text-center text-gray-500 py-8">No rule citations available</p>
              ) : (
                <div className="space-y-3">
                  {citations.map((citation: any, index: number) => (
                    <Card key={index} className="border-l-4 border-blue-500">
                      <CardContent className="pt-6">
                        <div className="flex items-start gap-3">
                          <div className="w-8 h-8 rounded-full bg-blue-100 flex items-center justify-center flex-shrink-0">
                            <BookOpen className="w-4 h-4 text-blue-600" />
                          </div>
                          <div className="flex-1">
                            <div className="flex items-start justify-between mb-2">
                              <div>
                                <p className="text-sm font-mono text-gray-600">Rule #{citation.rule_id || index + 1}</p>
                                {citation.bphs_anchor && (
                                  <p className="text-xs text-gray-500">BPHS: {citation.bphs_anchor}</p>
                                )}
                              </div>
                              {citation.weight !== undefined && (
                                <span className="text-xs font-medium px-2 py-1 bg-gray-100 rounded">
                                  Weight: {(citation.weight * 100).toFixed(0)}%
                                </span>
                              )}
                            </div>
                            {citation.condition && (
                              <p className="text-sm text-gray-700 mb-1">
                                <span className="font-semibold">Condition:</span> {citation.condition}
                              </p>
                            )}
                            {citation.effect && (
                              <p className="text-sm text-gray-700">
                                <span className="font-semibold">Effect:</span> {citation.effect}
                              </p>
                            )}
                            {citation.commentary && (
                              <p className="text-xs text-gray-600 mt-2 italic">
                                {citation.commentary}
                              </p>
                            )}
                          </div>
                        </div>
                      </CardContent>
                    </Card>
                  ))}
                </div>
              )}
            </TabsContent>
          </Tabs>
        </CardContent>
      </Card>

      {/* Metadata */}
      <Card className="bg-gray-50">
        <CardHeader>
          <CardTitle className="text-sm flex items-center gap-2">
            <Info className="w-4 h-4" />
            Generation Metadata
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
            <div>
              <p className="text-gray-600">Tokens Used</p>
              <p className="font-semibold">{reading.metadata.tokens_used.toLocaleString()}</p>
            </div>
            <div>
              <p className="text-gray-600">Cost</p>
              <p className="font-semibold">${reading.metadata.cost_usd.toFixed(4)}</p>
            </div>
            <div>
              <p className="text-gray-600">Cached</p>
              <p className="font-semibold">{reading.metadata.cached ? 'Yes' : 'No'}</p>
            </div>
            {reading.metadata.generation_time_seconds && (
              <div>
                <p className="text-gray-600">Generation Time</p>
                <p className="font-semibold">{reading.metadata.generation_time_seconds.toFixed(1)}s</p>
              </div>
            )}
          </div>
          {verification.contradictions_found > 0 && (
            <div className="mt-4 p-3 bg-yellow-50 border border-yellow-200 rounded-lg">
              <p className="text-sm text-yellow-800">
                <AlertTriangle className="w-4 h-4 inline mr-1" />
                {verification.contradictions_found} potential contradiction{verification.contradictions_found !== 1 ? 's' : ''} detected in analysis
              </p>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  )
}
