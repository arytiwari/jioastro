'use client'

import React from 'react'

interface Yoga {
  name: string
  description: string
  strength?: string
}

interface YogaDisplayProps {
  yogas: Yoga[]
}

const STRENGTH_COLORS: Record<string, { bg: string; text: string; border: string }> = {
  Strong: { bg: 'bg-green-50', text: 'text-green-800', border: 'border-green-300' },
  Medium: { bg: 'bg-yellow-50', text: 'text-yellow-800', border: 'border-yellow-300' },
  Weak: { bg: 'bg-orange-50', text: 'text-orange-800', border: 'border-orange-300' },
  Varies: { bg: 'bg-gray-50', text: 'text-gray-800', border: 'border-gray-300' }
}

const YOGA_ICONS: Record<string, string> = {
  'Raj Yoga': '👑',
  'Dhana Yoga': '💰',
  'Gaja Kesari Yoga': '🐘',
  'Budhaditya Yoga': '🧠',
  'Chandra-Mangala Yoga': '🌙',
  'Pancha Mahapurusha Yoga': '⭐',
  'Neecha Bhanga Raj Yoga': '📈'
}

export function YogaDisplay({ yogas }: YogaDisplayProps) {
  if (!yogas || yogas.length === 0) {
    return (
      <div className="flex items-center justify-center p-8 text-gray-500">
        <p>No yogas detected in chart</p>
      </div>
    )
  }

  return (
    <div className="w-full space-y-4 p-6 bg-white rounded-lg shadow-md">
      <div className="border-b pb-3">
        <h3 className="text-xl font-bold text-gray-900">Planetary Yogas</h3>
        <p className="text-sm text-gray-600 mt-1">
          Special combinations detected in your birth chart
        </p>
      </div>

      <div className="space-y-3">
        {yogas.map((yoga, index) => {
          const strength = yoga.strength || 'Varies'
          const colors = STRENGTH_COLORS[strength] || STRENGTH_COLORS.Varies
          const icon = YOGA_ICONS[yoga.name] || '✨'

          return (
            <div
              key={index}
              className={`p-4 rounded-lg border-2 ${colors.bg} ${colors.border} transition-all hover:shadow-md`}
            >
              <div className="flex items-start gap-3">
                {/* Icon */}
                <div className="text-3xl flex-shrink-0">{icon}</div>

                {/* Content */}
                <div className="flex-1">
                  <div className="flex items-center justify-between gap-2 flex-wrap">
                    <h4 className="font-bold text-lg text-gray-900">{yoga.name}</h4>
                    <span
                      className={`px-3 py-1 text-xs font-bold rounded-full ${colors.text} ${colors.bg} border ${colors.border}`}
                    >
                      {strength}
                    </span>
                  </div>
                  <p className="text-sm text-gray-700 mt-2 leading-relaxed">{yoga.description}</p>
                </div>
              </div>
            </div>
          )
        })}
      </div>

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
