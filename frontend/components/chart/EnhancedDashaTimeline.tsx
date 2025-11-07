/**
 * Enhanced Dasha Timeline with Interpretations
 * Displays Mahadasha and Antardasha periods with detailed interpretations,
 * planetary relationships, and personalized guidance
 */

'use client'

import React, { useState } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { Sparkles, TrendingUp, AlertCircle, Calendar } from '@/components/icons'

interface Interpretation {
  general?: string
  positive?: string[]
  challenges?: string[]
  remedies?: string[]
  summary?: string
  effect?: string
  relationship?: string
  advice?: string
  focus_areas?: string[]
}

interface Mahadasha {
  planet: string
  start_date: string
  end_date: string
  years: number
  months: number
  brief_interpretation?: string
  key_themes?: string[]
  interpretation?: Interpretation
  summary?: string
  life_themes?: string[]
}

interface Antardasha {
  planet: string
  start_date: string
  end_date: string
  years: number
  months: number
  days: number
  interpretation?: Interpretation
  summary?: string
}

interface CurrentMahadasha extends Mahadasha {
  remaining_years: number
}

interface CurrentAntardasha extends Antardasha {}

interface DashaData {
  current_mahadasha: CurrentMahadasha
  current_antardasha?: CurrentAntardasha
  mahadashas: Mahadasha[]
  antardashas: Antardasha[]
  interpretations_included?: boolean
}

interface EnhancedDashaTimelineProps {
  dashaData: DashaData
}

const PLANET_COLORS: Record<string, string> = {
  Sun: '#f59e0b',
  Moon: '#e0e7ff',
  Mars: '#dc2626',
  Mercury: '#22c55e',
  Jupiter: '#eab308',
  Venus: '#ec4899',
  Saturn: '#6366f1',
  Rahu: '#8b5cf6',
  Ketu: '#78350f'
}

const PLANET_SYMBOLS: Record<string, string> = {
  Sun: '☉',
  Moon: '☽',
  Mars: '♂',
  Mercury: '☿',
  Jupiter: '♃',
  Venus: '♀',
  Saturn: '♄',
  Rahu: '☊',
  Ketu: '☋'
}

const EFFECT_BADGES: Record<string, { color: string; icon: JSX.Element }> = {
  very_favorable: { color: 'bg-green-500 text-white', icon: <Sparkles className="w-3 h-3" /> },
  favorable: { color: 'bg-blue-500 text-white', icon: <TrendingUp className="w-3 h-3" /> },
  neutral: { color: 'bg-gray-500 text-white', icon: <AlertCircle className="w-3 h-3" /> },
  challenging: { color: 'bg-orange-500 text-white', icon: <AlertCircle className="w-3 h-3" /> }
}

export function EnhancedDashaTimeline({ dashaData }: EnhancedDashaTimelineProps) {
  const [activeTab, setActiveTab] = useState<'current' | 'timeline' | 'antardashas'>('current')

  if (!dashaData || !dashaData.mahadashas) {
    return (
      <Card>
        <CardContent className="py-8 text-center text-gray-500">
          Dasha data not available
        </CardContent>
      </Card>
    )
  }

  const currentMaha = dashaData.current_mahadasha
  const currentAntar = dashaData.current_antardasha
  const hasInterpretations = dashaData.interpretations_included

  const formatDate = (dateStr: string) => {
    const date = new Date(dateStr)
    return date.toLocaleDateString('en-US', { year: 'numeric', month: 'short' })
  }

  const isCurrentPeriod = (startDate: string, endDate: string) => {
    const current = new Date().toISOString().split('T')[0]
    return current >= startDate && current <= endDate
  }

  return (
    <div className="space-y-6">
      {/* Header Card */}
      <Card className="border-2 border-jio-300 bg-gradient-to-r from-jio-50 to-purple-50">
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-2xl">
            <Sparkles className="w-6 h-6 text-jio-600" />
            Vimshottari Dasha Periods
          </CardTitle>
          <CardDescription>
            Your current life phase and planetary periods based on Vedic astrology
          </CardDescription>
        </CardHeader>
      </Card>

      {/* Tabs */}
      <Tabs value={activeTab} onValueChange={(v) => setActiveTab(v as any)}>
        <TabsList className="grid w-full grid-cols-3">
          <TabsTrigger value="current">Current Period</TabsTrigger>
          <TabsTrigger value="timeline">Full Timeline</TabsTrigger>
          <TabsTrigger value="antardashas">Sub-Periods</TabsTrigger>
        </TabsList>

        {/* Current Period Tab */}
        <TabsContent value="current" className="space-y-4">
          {/* Current Mahadasha */}
          <Card className="border-2 border-jio-400">
            <CardHeader
              className="pb-4"
              style={{ backgroundColor: PLANET_COLORS[currentMaha.planet] + '20' }}
            >
              <div className="flex items-center justify-between">
                <CardTitle className="flex items-center gap-2">
                  <span
                    className="w-12 h-12 rounded-full flex items-center justify-center text-2xl"
                    style={{ backgroundColor: PLANET_COLORS[currentMaha.planet] }}
                  >
                    {PLANET_SYMBOLS[currentMaha.planet]}
                  </span>
                  Current Mahadasha: {currentMaha.planet}
                </CardTitle>
                <Badge variant="default" className="bg-jio-600">
                  ACTIVE NOW
                </Badge>
              </div>
              <CardDescription className="mt-2">
                <Calendar className="w-4 h-4 inline mr-1" />
                {formatDate(currentMaha.start_date)} → {formatDate(currentMaha.end_date)}
              </CardDescription>
            </CardHeader>
            {hasInterpretations && (
              <CardContent className="space-y-4">
                {/* Summary */}
                {currentMaha.summary && (
                  <Alert>
                    <AlertDescription className="text-base">
                      {currentMaha.summary}
                    </AlertDescription>
                  </Alert>
                )}

                {/* Life Themes */}
                {currentMaha.life_themes && currentMaha.life_themes.length > 0 && (
                  <div>
                    <h4 className="font-semibold text-sm text-gray-700 mb-2">
                      🎯 Key Life Themes:
                    </h4>
                    <div className="flex flex-wrap gap-2">
                      {currentMaha.life_themes.map((theme, idx) => (
                        <Badge key={idx} variant="outline">
                          {theme.charAt(0).toUpperCase() + theme.slice(1)}
                        </Badge>
                      ))}
                    </div>
                  </div>
                )}

                {/* Positive Influences */}
                {currentMaha.interpretation?.positive && (
                  <div>
                    <h4 className="font-semibold text-sm text-green-700 mb-2">
                      ✨ Positive Influences:
                    </h4>
                    <ul className="list-disc list-inside space-y-1 text-sm text-gray-700">
                      {currentMaha.interpretation.positive.slice(0, 3).map((item, idx) => (
                        <li key={idx}>{item}</li>
                      ))}
                    </ul>
                  </div>
                )}

                {/* Challenges */}
                {currentMaha.interpretation?.challenges && (
                  <div>
                    <h4 className="font-semibold text-sm text-orange-700 mb-2">
                      ⚠️ Potential Challenges:
                    </h4>
                    <ul className="list-disc list-inside space-y-1 text-sm text-gray-700">
                      {currentMaha.interpretation.challenges.slice(0, 3).map((item, idx) => (
                        <li key={idx}>{item}</li>
                      ))}
                    </ul>
                  </div>
                )}

                {/* Remedies */}
                {currentMaha.interpretation?.remedies && (
                  <div className="bg-purple-50 p-4 rounded-lg border border-purple-200">
                    <h4 className="font-semibold text-sm text-purple-700 mb-2">
                      🛡️ Recommended Remedies:
                    </h4>
                    <ul className="list-disc list-inside space-y-1 text-sm text-gray-700">
                      {currentMaha.interpretation.remedies.slice(0, 2).map((item, idx) => (
                        <li key={idx}>{item}</li>
                      ))}
                    </ul>
                  </div>
                )}
              </CardContent>
            )}
          </Card>

          {/* Current Antardasha */}
          {currentAntar && (
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <span
                    className="w-10 h-10 rounded-full flex items-center justify-center text-xl"
                    style={{ backgroundColor: PLANET_COLORS[currentAntar.planet] }}
                  >
                    {PLANET_SYMBOLS[currentAntar.planet]}
                  </span>
                  Current Antardasha: {currentAntar.planet}
                </CardTitle>
                <CardDescription>
                  {formatDate(currentAntar.start_date)} → {formatDate(currentAntar.end_date)}
                </CardDescription>
              </CardHeader>
              {currentAntar.interpretation && (
                <CardContent className="space-y-3">
                  <Alert>
                    <AlertDescription>{currentAntar.interpretation.summary}</AlertDescription>
                  </Alert>

                  <div className="grid grid-cols-2 gap-3 text-sm">
                    <div>
                      <span className="font-semibold text-gray-600">Effect:</span>
                      <div className="mt-1">
                        <Badge
                          className={
                            EFFECT_BADGES[currentAntar.interpretation.effect || 'neutral']?.color
                          }
                        >
                          {currentAntar.interpretation.effect?.toUpperCase() || 'N/A'}
                        </Badge>
                      </div>
                    </div>
                    <div>
                      <span className="font-semibold text-gray-600">Relationship:</span>
                      <div className="mt-1">
                        <Badge variant="outline">
                          {currentAntar.interpretation.relationship?.toUpperCase() || 'N/A'}
                        </Badge>
                      </div>
                    </div>
                  </div>

                  {currentAntar.interpretation.advice && (
                    <div className="bg-blue-50 p-3 rounded-lg border border-blue-200">
                      <p className="text-sm text-gray-700">
                        <span className="font-semibold">💡 Advice: </span>
                        {currentAntar.interpretation.advice}
                      </p>
                    </div>
                  )}
                </CardContent>
              )}
            </Card>
          )}
        </TabsContent>

        {/* Timeline Tab */}
        <TabsContent value="timeline" className="space-y-3">
          {dashaData.mahadashas.map((maha, index) => {
            const isCurrent = isCurrentPeriod(maha.start_date, maha.end_date)

            return (
              <Card
                key={index}
                className={
                  isCurrent ? 'border-2 border-jio-500 shadow-md' : 'border border-gray-200'
                }
              >
                <CardHeader className="pb-3">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <span
                        className="w-10 h-10 rounded-full flex items-center justify-center text-xl"
                        style={{ backgroundColor: PLANET_COLORS[maha.planet] }}
                      >
                        {PLANET_SYMBOLS[maha.planet]}
                      </span>
                      <div>
                        <CardTitle className="text-base">{maha.planet}</CardTitle>
                        <CardDescription className="text-xs">
                          {formatDate(maha.start_date)} → {formatDate(maha.end_date)}
                        </CardDescription>
                      </div>
                    </div>
                    {isCurrent && (
                      <Badge className="bg-jio-600">CURRENT</Badge>
                    )}
                  </div>
                </CardHeader>
                {maha.brief_interpretation && (
                  <CardContent className="pt-0">
                    <p className="text-sm text-gray-700">{maha.brief_interpretation}</p>
                    {maha.key_themes && maha.key_themes.length > 0 && (
                      <div className="flex flex-wrap gap-1 mt-2">
                        {maha.key_themes.map((theme, idx) => (
                          <Badge key={idx} variant="outline" className="text-xs">
                            {theme}
                          </Badge>
                        ))}
                      </div>
                    )}
                  </CardContent>
                )}
              </Card>
            )
          })}
        </TabsContent>

        {/* Antardashas Tab */}
        <TabsContent value="antardashas" className="space-y-3">
          <p className="text-sm text-gray-600 mb-4">
            Sub-periods within current {currentMaha.planet} Mahadasha
          </p>
          {dashaData.antardashas.map((antar, index) => {
            const isCurrent = isCurrentPeriod(antar.start_date, antar.end_date)
            const interp = antar.interpretation

            return (
              <Card
                key={index}
                className={
                  isCurrent ? 'border-2 border-jio-400 bg-jio-50' : 'border border-gray-200'
                }
              >
                <CardHeader className="pb-2">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <span
                        className="w-8 h-8 rounded-full flex items-center justify-center text-lg"
                        style={{ backgroundColor: PLANET_COLORS[antar.planet] }}
                      >
                        {PLANET_SYMBOLS[antar.planet]}
                      </span>
                      <div>
                        <CardTitle className="text-sm">{antar.planet}</CardTitle>
                        <CardDescription className="text-xs">
                          {formatDate(antar.start_date)} → {formatDate(antar.end_date)}
                        </CardDescription>
                      </div>
                    </div>
                    {isCurrent && (
                      <Badge className="bg-jio-600 text-xs">ACTIVE</Badge>
                    )}
                  </div>
                </CardHeader>
                {interp && (
                  <CardContent className="pt-2 space-y-2">
                    <p className="text-xs text-gray-700">{interp.summary}</p>
                    <div className="flex gap-2">
                      {interp.effect && (
                        <Badge
                          className={EFFECT_BADGES[interp.effect]?.color || 'bg-gray-500'}
                        >
                          {interp.effect}
                        </Badge>
                      )}
                      {interp.relationship && (
                        <Badge variant="outline" className="text-xs">
                          {interp.relationship}
                        </Badge>
                      )}
                    </div>
                  </CardContent>
                )}
              </Card>
            )
          })}
        </TabsContent>
      </Tabs>
    </div>
  )
}
