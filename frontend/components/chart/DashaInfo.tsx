'use client'

import React from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Clock } from 'lucide-react'

interface Dasha {
  current_dasha: string
  period_years: number
  note?: string
}

interface DashaInfoProps {
  dasha: Dasha
}

const dashaColors: Record<string, string> = {
  Sun: 'bg-orange-100 text-orange-700',
  Moon: 'bg-blue-100 text-blue-700',
  Mars: 'bg-red-100 text-red-700',
  Mercury: 'bg-green-100 text-green-700',
  Jupiter: 'bg-yellow-100 text-yellow-700',
  Venus: 'bg-pink-100 text-pink-700',
  Saturn: 'bg-gray-100 text-gray-700',
  Rahu: 'bg-jio-100 text-jio-700',
  Ketu: 'bg-indigo-100 text-indigo-700',
}

export function DashaInfo({ dasha }: DashaInfoProps) {
  const colorClass = dashaColors[dasha.current_dasha] || 'bg-gray-100 text-gray-700'

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
            <span className={`px-4 py-2 rounded-lg font-bold text-lg ${colorClass}`}>
              {dasha.current_dasha}
            </span>
          </div>

          <div className="flex items-center justify-between">
            <span className="text-sm text-gray-600">Total Period:</span>
            <span className="font-semibold">{dasha.period_years} years</span>
          </div>

          {dasha.note && (
            <div className="mt-4 p-3 bg-blue-50 rounded-lg">
              <p className="text-xs text-gray-600">{dasha.note}</p>
            </div>
          )}

          <div className="mt-4 p-3 bg-jio-50 rounded-lg">
            <p className="text-xs text-gray-700">
              <strong>Vimshottari Dasha</strong> is a 120-year cycle of planetary periods.
              Each planet governs your life for a specific number of years, influencing
              events and experiences during that time.
            </p>
          </div>
        </div>
      </CardContent>
    </Card>
  )
}
