"use client"

import { useState, useEffect } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Loader2, AlertCircle, AlertTriangle, Eye, EyeOff, Lightbulb } from 'lucide-react'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { getSession } from '@/lib/supabase'
import axios from 'axios'

interface LalKitabAnalysisProps {
  profileId: string
}

interface Debt {
  type: string
  planet: string
  house: number
  reason: string
  severity: string
  manifestation: string
  remedies: string[]
}

interface BlindPlanet {
  planet: string
  house: number
  reason: string
  effects: string[]
  remedies: string[]
}

interface LalKitabData {
  debts: {
    debts: Debt[]
    total_debts: number
    overall_severity: string
  }
  blind_planets: BlindPlanet[]
  priority_remedies: string[]
  general_remedies: string[]
  overall_assessment: string
}

export default function LalKitabAnalysis({ profileId }: LalKitabAnalysisProps) {
  const [data, setData] = useState<LalKitabData | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (profileId) {
      fetchLalKitabData()
    }
  }, [profileId])

  const fetchLalKitabData = async () => {
    try {
      setLoading(true)
      setError(null)

      const session = getSession()
      if (!session) return

      const response = await axios.get(
        `${process.env.NEXT_PUBLIC_API_URL}/enhancements/lal-kitab/analyze/${profileId}`,
        {
          headers: {
            Authorization: `Bearer ${session.access_token}`
          }
        }
      )

      setData(response.data.analysis)
    } catch (err: any) {
      console.error('Error fetching Lal Kitab data:', err)
      setError(err.response?.data?.detail || err.message || 'Failed to load Lal Kitab analysis')
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center py-12">
        <Loader2 className="h-8 w-8 animate-spin text-primary" />
      </div>
    )
  }

  if (error) {
    return (
      <Alert variant="destructive">
        <AlertCircle className="h-4 w-4" />
        <AlertDescription>{error}</AlertDescription>
      </Alert>
    )
  }

  if (!data) return null

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'high': return 'destructive'
      case 'medium': return 'default'
      case 'low': return 'secondary'
      default: return 'secondary'
    }
  }

  return (
    <div className="space-y-6">
      {/* Overall Assessment */}
      <Alert>
        <AlertTriangle className="h-4 w-4" />
        <AlertDescription className="font-medium">{data.overall_assessment}</AlertDescription>
      </Alert>

      {/* Planetary Debts (Rins) */}
      {data.debts && data.debts.debts.length > 0 && (
        <Card>
          <CardHeader>
            <div className="flex items-center justify-between">
              <div>
                <CardTitle>Planetary Debts (Karmic Rins)</CardTitle>
                <CardDescription>Unfulfilled karmic obligations from past lives</CardDescription>
              </div>
              <Badge variant={getSeverityColor(data.debts.overall_severity) as any}>
                {data.debts.overall_severity.toUpperCase()} Severity
              </Badge>
            </div>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {data.debts.debts.map((debt, index) => (
                <div key={index} className="p-4 border rounded-lg space-y-3">
                  <div className="flex items-center justify-between">
                    <div>
                      <div className="font-medium text-lg">{debt.type}</div>
                      <div className="text-sm text-muted-foreground">
                        {debt.planet} in House {debt.house}
                      </div>
                    </div>
                    <Badge variant={getSeverityColor(debt.severity) as any}>
                      {debt.severity}
                    </Badge>
                  </div>

                  <div className="space-y-2">
                    <div className="text-sm">
                      <span className="font-medium">Reason: </span>
                      {debt.reason}
                    </div>
                    <div className="text-sm">
                      <span className="font-medium">Manifestation: </span>
                      {debt.manifestation}
                    </div>
                  </div>

                  <div>
                    <div className="font-medium text-sm mb-2">Remedies:</div>
                    <ul className="space-y-1">
                      {debt.remedies.slice(0, 3).map((remedy, i) => (
                        <li key={i} className="text-sm text-muted-foreground flex items-start gap-2">
                          <span className="text-primary">•</span>
                          {remedy}
                        </li>
                      ))}
                    </ul>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Blind Planets */}
      {data.blind_planets && data.blind_planets.length > 0 && (
        <Card>
          <CardHeader>
            <div className="flex items-center gap-2">
              <EyeOff className="h-5 w-5" />
              <CardTitle>Blind Planets (Andhe Graha)</CardTitle>
            </div>
            <CardDescription>Planets unable to give results due to adverse placement</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {data.blind_planets.map((blind, index) => (
                <div key={index} className="p-4 border rounded-lg space-y-3">
                  <div className="flex items-center justify-between">
                    <div className="font-medium text-lg">{blind.planet}</div>
                    <Badge variant="outline">House {blind.house}</Badge>
                  </div>

                  <div className="text-sm">
                    <span className="font-medium">Reason: </span>
                    {blind.reason}
                  </div>

                  <div>
                    <div className="font-medium text-sm mb-2">Effects:</div>
                    <ul className="space-y-1">
                      {blind.effects.map((effect, i) => (
                        <li key={i} className="text-sm text-muted-foreground flex items-start gap-2">
                          <span className="text-destructive">•</span>
                          {effect}
                        </li>
                      ))}
                    </ul>
                  </div>

                  <div>
                    <div className="font-medium text-sm mb-2">Remedies to "Open Eyes":</div>
                    <ul className="space-y-1">
                      {blind.remedies.slice(0, 3).map((remedy, i) => (
                        <li key={i} className="text-sm text-muted-foreground flex items-start gap-2">
                          <span className="text-primary">•</span>
                          {remedy}
                        </li>
                      ))}
                    </ul>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Priority Remedies */}
      {data.priority_remedies && data.priority_remedies.length > 0 && (
        <Card className="border-primary">
          <CardHeader>
            <div className="flex items-center gap-2">
              <Lightbulb className="h-5 w-5 text-primary" />
              <CardTitle>Priority Remedies</CardTitle>
            </div>
            <CardDescription>Start with these most important remedies</CardDescription>
          </CardHeader>
          <CardContent>
            <ul className="space-y-2">
              {data.priority_remedies.map((remedy, index) => (
                <li key={index} className="flex items-start gap-3 p-3 bg-primary/5 rounded-lg">
                  <span className="flex-shrink-0 w-6 h-6 rounded-full bg-primary text-primary-foreground flex items-center justify-center text-sm font-medium">
                    {index + 1}
                  </span>
                  <span className="text-sm">{remedy}</span>
                </li>
              ))}
            </ul>
          </CardContent>
        </Card>
      )}

      {/* General Remedies */}
      {data.general_remedies && data.general_remedies.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle>General Lal Kitab Remedies</CardTitle>
            <CardDescription>Universal remedies beneficial for everyone</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
              {data.general_remedies.map((remedy, index) => (
                <div key={index} className="flex items-start gap-2 p-3 border rounded-lg">
                  <span className="text-primary">•</span>
                  <span className="text-sm">{remedy}</span>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Information Card */}
      <Card className="bg-muted/50">
        <CardHeader>
          <CardTitle className="text-lg">Understanding Lal Kitab</CardTitle>
        </CardHeader>
        <CardContent className="space-y-2 text-sm">
          <p><strong>Planetary Debts (Rins):</strong> Indicate unfulfilled karmic obligations from past lives that manifest as challenges.</p>
          <p><strong>Blind Planets:</strong> Planets that lose their power due to adverse placement and cannot give promised results.</p>
          <p><strong>Remedies (Totke):</strong> Simple, practical actions that anyone can perform - no expensive rituals required.</p>
          <p><strong>Philosophy:</strong> Focus on practical karma and simple daily actions to improve life circumstances.</p>
        </CardContent>
      </Card>
    </div>
  )
}
