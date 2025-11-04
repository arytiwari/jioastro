'use client'

import React, { useState } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Clock, ChevronDown, ChevronRight } from '@/components/icons'

interface Mahadasha {
  planet: string
  start_date: string
  end_date: string
  years: number
  months: number
}

interface Antardasha {
  planet: string
  start_date: string
  end_date: string
  years: number
  months: number
  days: number
}

interface CurrentMahadasha {
  planet: string
  start_date: string
  end_date: string
  remaining_years: number
}

interface DashaData {
  current_mahadasha: string | CurrentMahadasha  // Support both old and new formats
  mahadasha_years?: number
  mahadashas: Mahadasha[]
  antardashas: Antardasha[]
  note?: string
  // Backward compatibility
  current_dasha?: string
  period_years?: number
}

interface VimshottariDashaTableProps {
  dasha: DashaData
}

const dashaColors: Record<string, string> = {
  Sun: 'bg-orange-100 text-orange-800 border-orange-300',
  Moon: 'bg-blue-100 text-blue-800 border-blue-300',
  Mars: 'bg-red-100 text-red-800 border-red-300',
  Mercury: 'bg-green-100 text-green-800 border-green-300',
  Jupiter: 'bg-yellow-100 text-yellow-800 border-yellow-300',
  Venus: 'bg-pink-100 text-pink-800 border-pink-300',
  Saturn: 'bg-gray-100 text-gray-800 border-gray-300',
  Rahu: 'bg-jio-100 text-jio-800 border-jio-300',
  Ketu: 'bg-indigo-100 text-indigo-800 border-indigo-300',
}

const formatDate = (dateStr: string) => {
  const date = new Date(dateStr)
  return date.toLocaleDateString('en-US', { year: 'numeric', month: 'short', day: 'numeric' })
}

export function VimshottariDashaTable({ dasha }: VimshottariDashaTableProps) {
  // Extract planet name - support both old and new formats
  const currentMahaPlanet = typeof dasha.current_mahadasha === 'string'
    ? (dasha.current_mahadasha || dasha.current_dasha || 'Unknown')
    : (dasha.current_mahadasha?.planet || 'Unknown')

  const remainingYears = typeof dasha.current_mahadasha === 'string'
    ? (dasha.mahadasha_years || 0)
    : (dasha.current_mahadasha?.remaining_years || 0)

  const [expandedMaha, setExpandedMaha] = useState<string | null>(currentMahaPlanet)

  const currentMaha = currentMahaPlanet
  const mahadashas = dasha.mahadashas || []
  const antardashas = dasha.antardashas || []

  // Handle old format
  const isOldFormat = !dasha.mahadashas

  if (isOldFormat) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Clock className="w-5 h-5 text-jio-600" />
            Current Dasha Period
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <span className="text-sm text-gray-600">Planet:</span>
              <span className={`px-4 py-2 rounded-lg font-bold text-lg ${dashaColors[currentMaha] || 'bg-gray-100'}`}>
                {currentMaha}
              </span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-sm text-gray-600">Total Period:</span>
              <span className="font-semibold">{dasha.period_years || 0} years</span>
            </div>
            {dasha.note && (
              <div className="mt-4 p-3 bg-blue-50 rounded-lg">
                <p className="text-xs text-gray-600">{dasha.note}</p>
              </div>
            )}
          </div>
        </CardContent>
      </Card>
    )
  }

  return (
    <div className="space-y-6">
      {/* Current Mahadasha Highlight */}
      <Card className="border-2 border-jio-500">
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-jio-700">
            <Clock className="w-5 h-5" />
            Current Mahadasha
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex items-center justify-between">
            <div>
              <p className="text-2xl font-bold">{currentMaha}</p>
              <p className="text-sm text-gray-600 mt-1">
                {remainingYears.toFixed(1)} years remaining
              </p>
            </div>
            <div className={`px-6 py-3 rounded-lg text-2xl ${dashaColors[currentMaha]}`}>
              {currentMaha.charAt(0)}
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Mahadasha Table */}
      <Card>
        <CardHeader>
          <CardTitle>Mahadasha Periods</CardTitle>
          <CardDescription>120-year cycle of planetary periods</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-2">
            {mahadashas.map((maha, idx) => {
              const isExpanded = expandedMaha === maha.planet
              const isCurrent = maha.planet === currentMaha && idx === 0
              const colorClass = dashaColors[maha.planet] || 'bg-gray-100'

              return (
                <div key={idx} className={`border rounded-lg ${isCurrent ? 'border-jio-500 border-2' : 'border-gray-200'}`}>
                  <div
                    className={`p-4 cursor-pointer hover:bg-gray-50 transition-colors ${colorClass} border-b`}
                    onClick={() => setExpandedMaha(isExpanded ? null : maha.planet)}
                  >
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-3">
                        {isExpanded ? (
                          <ChevronDown className="w-5 h-5" />
                        ) : (
                          <ChevronRight className="w-5 h-5" />
                        )}
                        <div>
                          <p className="font-bold text-lg">{maha.planet}</p>
                          <p className="text-sm opacity-80">
                            {formatDate(maha.start_date)} - {formatDate(maha.end_date)}
                          </p>
                        </div>
                      </div>
                      <div className="text-right">
                        <p className="font-semibold">{maha.years} years</p>
                        <p className="text-xs opacity-80">{maha.months} months</p>
                      </div>
                    </div>
                  </div>

                  {/* Antardasha Table (shown when expanded and it's current Mahadasha) */}
                  {isExpanded && isCurrent && antardashas.length > 0 && (
                    <div className="p-4 bg-gray-50">
                      <h4 className="font-semibold text-sm text-gray-700 mb-3">
                        Antardasha Periods (Sub-periods)
                      </h4>
                      <div className="space-y-1">
                        {antardashas.map((antara, antaraIdx) => {
                          const antaraColorClass = dashaColors[antara.planet] || 'bg-gray-100'
                          return (
                            <div
                              key={antaraIdx}
                              className={`p-3 rounded-md ${antaraColorClass} border`}
                            >
                              <div className="flex items-center justify-between">
                                <div>
                                  <p className="font-semibold text-sm">{antara.planet}</p>
                                  <p className="text-xs opacity-75">
                                    {formatDate(antara.start_date)} - {formatDate(antara.end_date)}
                                  </p>
                                </div>
                                <div className="text-right text-xs">
                                  <p className="font-medium">{antara.months}m {antara.days % 30}d</p>
                                </div>
                              </div>
                            </div>
                          )
                        })}
                      </div>
                    </div>
                  )}
                </div>
              )
            })}
          </div>
        </CardContent>
      </Card>

      {/* Info Box */}
      <Card className="bg-jio-50">
        <CardContent className="py-4">
          <h3 className="font-semibold mb-2 text-jio-900">About Vimshottari Dasha</h3>
          <p className="text-sm text-gray-700">
            Vimshottari Dasha is a 120-year cycle based on the Moon's nakshatra at birth.
            Each planet governs your life for a specific period, bringing its unique influences.
            The current Mahadasha sets the overall tone, while Antardashas (sub-periods) add nuanced effects.
          </p>
          <ul className="text-xs text-gray-600 list-disc list-inside mt-2 space-y-1">
            <li><strong>Mahadasha:</strong> Main planetary period (7-20 years)</li>
            <li><strong>Antardasha:</strong> Sub-period within Mahadasha (months to years)</li>
            <li><strong>Pratyantar Dasha:</strong> Sub-sub-period (days to months) - Coming soon</li>
          </ul>
        </CardContent>
      </Card>
    </div>
  )
}
