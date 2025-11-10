'use client'

import React, { useState } from 'react'
import { Star, AlertTriangle, ChevronDown, ChevronUp, CheckCircle, AlertCircle, Info } from 'lucide-react'

interface Yoga {
  name: string
  description: string
  strength?: string
  impact?: string
  importance?: string
  life_area?: string
  category?: string
}

interface YogaDisplayProps {
  yogas: Yoga[]
}

const STRENGTH_COLORS: Record<string, { bg: string; text: string; border: string }> = {
  'Very Strong': { bg: 'bg-green-50', text: 'text-green-800', border: 'border-green-500' },
  Strong: { bg: 'bg-green-50', text: 'text-green-800', border: 'border-green-300' },
  Medium: { bg: 'bg-yellow-50', text: 'text-yellow-800', border: 'border-yellow-300' },
  Weak: { bg: 'bg-orange-50', text: 'text-orange-800', border: 'border-orange-300' },
  Varies: { bg: 'bg-gray-50', text: 'text-gray-800', border: 'border-gray-300' }
}

export function YogaDisplay({ yogas }: YogaDisplayProps) {
  const [minorExpanded, setMinorExpanded] = useState(false)

  if (!yogas || yogas.length === 0) {
    return (
      <div className="flex items-center justify-center p-8 text-gray-500">
        <p>No yogas detected in chart</p>
      </div>
    )
  }

  // Categorize yogas
  const majorPositive = yogas.filter(y => y.importance === 'major' && y.impact === 'positive')
  const majorChallenge = yogas.filter(y => y.importance === 'major' && (y.impact === 'negative' || y.impact === 'mixed'))
  const moderate = yogas.filter(y => y.importance === 'moderate')
  const minorYogas = yogas.filter(y => y.importance === 'minor' || !y.importance)

  const renderMajorPositiveYoga = (yoga: Yoga, index: number) => {
    const strength = yoga.strength || 'Varies'
    const strengthColors = STRENGTH_COLORS[strength] || STRENGTH_COLORS.Varies

    return (
      <div
        key={index}
        className="p-4 rounded-lg border-2 border-emerald-400 bg-gradient-to-br from-emerald-50 via-green-50 to-yellow-50 shadow-md"
      >
        <div className="flex items-start gap-3">
          <div className="w-10 h-10 rounded-full bg-gradient-to-br from-emerald-400 to-yellow-400 flex items-center justify-center flex-shrink-0">
            <Star className="w-6 h-6 text-white fill-white" />
          </div>
          <div className="flex-1">
            <div className="flex items-center justify-between gap-2 flex-wrap mb-1">
              <span className="px-2 py-0.5 text-xs font-bold rounded-full bg-emerald-600 text-white">
                MAJOR POSITIVE
              </span>
              <span className={`px-2 py-0.5 text-xs font-bold rounded-full ${strengthColors.text} ${strengthColors.bg} border ${strengthColors.border}`}>
                {strength}
              </span>
            </div>
            <h4 className="font-bold text-lg text-gray-900 mb-1">{yoga.name}</h4>
            {yoga.life_area && (
              <span className="text-xs text-emerald-700 font-semibold">{yoga.life_area}</span>
            )}
            <p className="text-sm text-gray-700 mt-2 leading-relaxed">{yoga.description}</p>
          </div>
        </div>
      </div>
    )
  }

  const renderMajorChallengeYoga = (yoga: Yoga, index: number) => {
    const strength = yoga.strength || 'Varies'
    const strengthColors = STRENGTH_COLORS[strength] || STRENGTH_COLORS.Varies
    const isMixed = yoga.impact === 'mixed'

    return (
      <div
        key={index}
        className={`p-4 rounded-lg border-2 shadow-md ${
          isMixed
            ? 'border-purple-400 bg-gradient-to-br from-purple-50 to-indigo-50'
            : 'border-orange-400 bg-gradient-to-br from-orange-50 to-red-50'
        }`}
      >
        <div className="flex items-start gap-3">
          <div className={`w-10 h-10 rounded-full flex items-center justify-center flex-shrink-0 ${
            isMixed
              ? 'bg-gradient-to-br from-purple-400 to-indigo-400'
              : 'bg-gradient-to-br from-orange-400 to-red-400'
          }`}>
            {isMixed ? (
              <Info className="w-6 h-6 text-white" />
            ) : (
              <AlertTriangle className="w-6 h-6 text-white" />
            )}
          </div>
          <div className="flex-1">
            <div className="flex items-center justify-between gap-2 flex-wrap mb-1">
              <span className={`px-2 py-0.5 text-xs font-bold rounded-full text-white ${
                isMixed ? 'bg-purple-600' : 'bg-orange-600'
              }`}>
                MAJOR {isMixed ? 'MIXED' : 'CHALLENGE'}
              </span>
              <span className={`px-2 py-0.5 text-xs font-bold rounded-full ${strengthColors.text} ${strengthColors.bg} border ${strengthColors.border}`}>
                {strength}
              </span>
            </div>
            <h4 className="font-bold text-lg text-gray-900 mb-1">{yoga.name}</h4>
            {yoga.life_area && (
              <span className={`text-xs font-semibold ${isMixed ? 'text-purple-700' : 'text-orange-700'}`}>
                {yoga.life_area}
              </span>
            )}
            <p className="text-sm text-gray-700 mt-2 leading-relaxed">{yoga.description}</p>
          </div>
        </div>
      </div>
    )
  }

  const renderModerateYoga = (yoga: Yoga, index: number) => {
    const strength = yoga.strength || 'Varies'
    const colors = STRENGTH_COLORS[strength] || STRENGTH_COLORS.Varies

    return (
      <div
        key={index}
        className={`p-4 rounded-lg border-2 ${colors.bg} ${colors.border} transition-all hover:shadow-md`}
      >
        <div className="flex items-start gap-3">
          <div className="text-2xl flex-shrink-0">📊</div>
          <div className="flex-1">
            <div className="flex items-center justify-between gap-2 flex-wrap">
              <h4 className="font-bold text-lg text-gray-900">{yoga.name}</h4>
              <span className={`px-3 py-1 text-xs font-bold rounded-full ${colors.text} ${colors.bg} border ${colors.border}`}>
                {strength}
              </span>
            </div>
            <p className="text-sm text-gray-700 mt-2 leading-relaxed">{yoga.description}</p>
          </div>
        </div>
      </div>
    )
  }

  const renderMinorYoga = (yoga: Yoga, index: number) => {
    const strength = yoga.strength || 'Varies'
    const colors = STRENGTH_COLORS[strength] || STRENGTH_COLORS.Varies

    return (
      <div
        key={index}
        className={`p-3 rounded-lg border ${colors.border} bg-white hover:shadow-sm transition-shadow`}
      >
        <div className="flex items-start gap-2">
          <div className="text-lg flex-shrink-0">✨</div>
          <div className="flex-1 min-w-0">
            <div className="flex items-center justify-between gap-2 flex-wrap mb-1">
              <h5 className="font-semibold text-sm text-gray-900">{yoga.name}</h5>
              <span className={`px-2 py-0.5 text-xs font-medium rounded-full ${colors.text} ${colors.bg}`}>
                {strength}
              </span>
            </div>
            <p className="text-xs text-gray-600 leading-relaxed">{yoga.description}</p>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="w-full space-y-6 p-6 bg-white rounded-lg shadow-md">
      <div className="border-b pb-3">
        <h3 className="text-xl font-bold text-gray-900">Planetary Yogas</h3>
        <p className="text-sm text-gray-600 mt-1">
          {yogas.length} special combinations detected in your birth chart
        </p>
      </div>

      {/* Major Positive Yogas */}
      {majorPositive.length > 0 && (
        <div className="space-y-3">
          <h4 className="text-lg font-bold text-emerald-700 flex items-center gap-2">
            <Star className="w-5 h-5 fill-emerald-500" />
            Major Positive Yogas ({majorPositive.length})
          </h4>
          <div className="space-y-3">
            {majorPositive.map(renderMajorPositiveYoga)}
          </div>
        </div>
      )}

      {/* Major Challenge Yogas */}
      {majorChallenge.length > 0 && (
        <div className="space-y-3">
          <h4 className="text-lg font-bold text-orange-700 flex items-center gap-2">
            <AlertTriangle className="w-5 h-5" />
            Major Challenges ({majorChallenge.length})
          </h4>
          <div className="space-y-3">
            {majorChallenge.map(renderMajorChallengeYoga)}
          </div>
        </div>
      )}

      {/* Moderate Yogas */}
      {moderate.length > 0 && (
        <div className="space-y-3">
          <h4 className="text-lg font-bold text-blue-700">
            Standard Yogas ({moderate.length})
          </h4>
          <div className="space-y-3">
            {moderate.map(renderModerateYoga)}
          </div>
        </div>
      )}

      {/* Minor Yogas - Collapsible */}
      {minorYogas.length > 0 && (
        <div className="space-y-3">
          <button
            onClick={() => setMinorExpanded(!minorExpanded)}
            className="w-full flex items-center justify-between p-3 bg-gray-50 hover:bg-gray-100 rounded-lg border border-gray-300 transition-colors"
          >
            <div className="flex items-center gap-2">
              <CheckCircle className="w-5 h-5 text-gray-600" />
              <h4 className="text-base font-bold text-gray-700">
                Minor Yogas & Subtle Influences ({minorYogas.length})
              </h4>
            </div>
            {minorExpanded ? (
              <ChevronUp className="w-5 h-5 text-gray-600" />
            ) : (
              <ChevronDown className="w-5 h-5 text-gray-600" />
            )}
          </button>

          {minorExpanded && (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3 pt-2">
              {minorYogas.map(renderMinorYoga)}
            </div>
          )}
        </div>
      )}

      {/* Legend */}
      <div className="mt-6 pt-4 border-t">
        <p className="text-xs font-semibold text-gray-700 mb-2">Strength Indicators:</p>
        <div className="flex flex-wrap gap-2">
          {Object.entries(STRENGTH_COLORS).map(([strength, colors]) => (
            <div
              key={strength}
              className={`px-2 py-1 text-xs rounded-md ${colors.bg} ${colors.text} ${colors.border} border`}
            >
              {strength}
            </div>
          ))}
        </div>
      </div>

      <div className="text-xs text-gray-500 italic text-center mt-4">
        Yogas are special planetary combinations that influence various aspects of life. Consult
        with an astrologer for detailed interpretation.
      </div>
    </div>
  )
}
