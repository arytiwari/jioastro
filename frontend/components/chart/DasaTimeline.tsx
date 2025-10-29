'use client'

import React from 'react'

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

interface DashaData {
  current_mahadasha: string
  mahadasha_years: number
  mahadashas: Mahadasha[]
  antardashas: Antardasha[]
  note?: string
}

interface DasaTimelineProps {
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

export function DasaTimeline({ dashaData }: DasaTimelineProps) {
  if (!dashaData || !dashaData.mahadashas) {
    return (
      <div className="flex items-center justify-center p-8 text-gray-500">
        <p>Dasha data not available</p>
      </div>
    )
  }

  const formatDate = (dateStr: string) => {
    const date = new Date(dateStr)
    return date.toLocaleDateString('en-US', { year: 'numeric', month: 'short', day: 'numeric' })
  }

  const getCurrentDate = () => {
    return new Date().toISOString().split('T')[0]
  }

  const isCurrentPeriod = (startDate: string, endDate: string) => {
    const current = getCurrentDate()
    return current >= startDate && current <= endDate
  }

  return (
    <div className="w-full space-y-6 p-6 bg-white rounded-lg shadow-md">
      {/* Current Mahadasha Highlight */}
      <div className="bg-gradient-to-r from-jio-100 to-blue-100 rounded-lg p-4 border-2 border-jio-300">
        <div className="flex items-center justify-between">
          <div>
            <h3 className="text-lg font-bold text-gray-900">Current Mahadasha</h3>
            <p className="text-2xl font-extrabold text-jio-700 mt-1">
              {PLANET_SYMBOLS[dashaData.current_mahadasha] || ''} {dashaData.current_mahadasha}
            </p>
            <p className="text-sm text-gray-600 mt-1">
              {dashaData.mahadasha_years.toFixed(1)} years remaining
            </p>
          </div>
          <div
            className="w-20 h-20 rounded-full flex items-center justify-center text-4xl"
            style={{ backgroundColor: PLANET_COLORS[dashaData.current_mahadasha] || '#9ca3af' }}
          >
            {PLANET_SYMBOLS[dashaData.current_mahadasha] || '?'}
          </div>
        </div>
      </div>

      {/* Mahadasha Timeline */}
      <div>
        <h4 className="text-lg font-bold text-gray-900 mb-4">Mahadasha Timeline</h4>
        <div className="space-y-3">
          {dashaData.mahadashas.map((maha, index) => {
            const isCurrent = isCurrentPeriod(maha.start_date, maha.end_date)
            const planetColor = PLANET_COLORS[maha.planet] || '#9ca3af'

            return (
              <div
                key={index}
                className={`flex items-center gap-3 p-3 rounded-lg border-2 transition-all ${
                  isCurrent
                    ? 'border-jio-500 bg-jio-50 shadow-md scale-105'
                    : 'border-gray-200 bg-white hover:bg-gray-50'
                }`}
              >
                {/* Planet indicator */}
                <div
                  className="w-12 h-12 rounded-full flex items-center justify-center text-2xl font-bold flex-shrink-0"
                  style={{ backgroundColor: planetColor, color: maha.planet === 'Moon' ? '#000' : '#fff' }}
                >
                  {PLANET_SYMBOLS[maha.planet] || '?'}
                </div>

                {/* Details */}
                <div className="flex-1">
                  <div className="flex items-center justify-between">
                    <span className="font-bold text-gray-900">{maha.planet}</span>
                    {isCurrent && (
                      <span className="px-2 py-1 text-xs font-bold text-white bg-jio-600 rounded-full">
                        CURRENT
                      </span>
                    )}
                  </div>
                  <div className="text-sm text-gray-600 mt-1">
                    {formatDate(maha.start_date)} → {formatDate(maha.end_date)}
                  </div>
                  <div className="text-xs text-gray-500 mt-1">
                    Duration: {maha.years} years ({maha.months} months)
                  </div>
                </div>
              </div>
            )
          })}
        </div>
      </div>

      {/* Antardasha (Sub-periods) */}
      {dashaData.antardashas && dashaData.antardashas.length > 0 && (
        <div>
          <h4 className="text-lg font-bold text-gray-900 mb-4">
            Antardashas in {dashaData.current_mahadasha} Period
          </h4>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
            {dashaData.antardashas.slice(0, 9).map((antar, index) => {
              const isCurrent = isCurrentPeriod(antar.start_date, antar.end_date)
              const planetColor = PLANET_COLORS[antar.planet] || '#9ca3af'

              return (
                <div
                  key={index}
                  className={`flex items-center gap-2 p-2 rounded-md border ${
                    isCurrent
                      ? 'border-jio-400 bg-jio-50 font-semibold'
                      : 'border-gray-200 bg-gray-50'
                  }`}
                >
                  <div
                    className="w-8 h-8 rounded-full flex items-center justify-center text-lg"
                    style={{ backgroundColor: planetColor, color: antar.planet === 'Moon' ? '#000' : '#fff' }}
                  >
                    {PLANET_SYMBOLS[antar.planet]}
                  </div>
                  <div className="text-xs flex-1">
                    <div className="font-medium">{antar.planet}</div>
                    <div className="text-gray-600">
                      {formatDate(antar.start_date)} - {formatDate(antar.end_date)}
                    </div>
                    <div className="text-gray-500">{antar.months}m {antar.days}d</div>
                  </div>
                </div>
              )
            })}
          </div>
        </div>
      )}

      {/* Note */}
      {dashaData.note && (
        <div className="text-xs text-gray-500 italic text-center border-t pt-3">
          {dashaData.note}
        </div>
      )}
    </div>
  )
}
