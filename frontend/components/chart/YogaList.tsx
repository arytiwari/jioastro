'use client'

import React from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Star } from 'lucide-react'

interface Yoga {
  name: string
  description: string
  strength?: string
}

interface YogaListProps {
  yogas: Yoga[]
}

const strengthColors: Record<string, string> = {
  Strong: 'text-green-600 bg-green-50',
  Medium: 'text-yellow-600 bg-yellow-50',
  Weak: 'text-gray-600 bg-gray-50',
  Varies: 'text-blue-600 bg-blue-50'
}

export function YogaList({ yogas }: YogaListProps) {
  if (!yogas || yogas.length === 0) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Yogas (Astrological Combinations)</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-gray-500 text-sm">No specific yogas detected in this chart.</p>
        </CardContent>
      </Card>
    )
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Star className="w-5 h-5 text-purple-600" />
          Yogas (Astrological Combinations)
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          {yogas.map((yoga, index) => (
            <div
              key={index}
              className="p-4 border rounded-lg hover:shadow-md transition-shadow"
            >
              <div className="flex items-start justify-between mb-2">
                <h4 className="font-semibold text-lg text-purple-700">
                  {yoga.name}
                </h4>
                {yoga.strength && (
                  <span
                    className={`text-xs px-2 py-1 rounded-full ${
                      strengthColors[yoga.strength] || strengthColors.Varies
                    }`}
                  >
                    {yoga.strength}
                  </span>
                )}
              </div>
              <p className="text-sm text-gray-700">{yoga.description}</p>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  )
}
