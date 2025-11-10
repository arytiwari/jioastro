"use client"

import { useState } from "react"
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { ChevronDown, ChevronUp, CheckCircle, AlertCircle } from "@/components/icons"

interface Yoga {
  name: string
  description: string
  category: string
  strength: string
  impact: string
  importance: string
  life_area: string
  planets_involved?: string[]
  houses_involved?: number[]
}

interface MinorYogasAccordionProps {
  positiveYogas: Yoga[]
  challengeYogas: Yoga[]
  onYogaClick?: (yoga: Yoga) => void
}

export default function MinorYogasAccordion({
  positiveYogas,
  challengeYogas,
  onYogaClick
}: MinorYogasAccordionProps) {
  const [positiveExpanded, setPositiveExpanded] = useState(false)
  const [challengeExpanded, setChallengeExpanded] = useState(false)

  return (
    <div className="space-y-4">
      {/* Minor Positive Yogas */}
      {positiveYogas.length > 0 && (
        <Card className="border-2 border-gray-300 bg-gray-50">
          <CardHeader
            className="cursor-pointer hover:bg-gray-100 transition-colors"
            onClick={() => setPositiveExpanded(!positiveExpanded)}
          >
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <CheckCircle className="w-6 h-6 text-green-600" />
                <div>
                  <CardTitle className="text-xl font-bold text-gray-900">
                    Minor Positive Yogas
                  </CardTitle>
                  <p className="text-sm text-gray-600 mt-1">
                    {positiveYogas.length} supportive yogas providing additional benefits
                  </p>
                </div>
              </div>
              {positiveExpanded ? (
                <ChevronUp className="w-6 h-6 text-gray-600" />
              ) : (
                <ChevronDown className="w-6 h-6 text-gray-600" />
              )}
            </div>
          </CardHeader>

          {positiveExpanded && (
            <CardContent className="pt-4">
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {positiveYogas.map((yoga, index) => (
                  <Card
                    key={index}
                    className="border border-gray-300 bg-white hover:shadow-md transition-shadow cursor-pointer"
                    onClick={() => onYogaClick?.(yoga)}
                  >
                    <CardContent className="p-4 space-y-2">
                      <div className="flex items-start justify-between gap-2">
                        <h4 className="font-semibold text-gray-900 text-sm leading-tight">
                          {yoga.name}
                        </h4>
                        <Badge
                          variant="outline"
                          className={`
                            flex-shrink-0 text-xs
                            ${yoga.strength === 'Strong' ? 'border-blue-500 text-blue-700 bg-blue-50' : ''}
                            ${yoga.strength === 'Medium' ? 'border-yellow-500 text-yellow-700 bg-yellow-50' : ''}
                            ${yoga.strength === 'Weak' ? 'border-gray-500 text-gray-700 bg-gray-50' : ''}
                          `}
                        >
                          {yoga.strength}
                        </Badge>
                      </div>
                      <p className="text-xs text-gray-600 line-clamp-2">
                        {yoga.description}
                      </p>
                      <div className="flex flex-wrap gap-1">
                        <Badge variant="outline" className="text-xs border-gray-300">
                          {yoga.category}
                        </Badge>
                        {yoga.life_area && (
                          <Badge variant="outline" className="text-xs border-gray-300">
                            {yoga.life_area}
                          </Badge>
                        )}
                      </div>
                    </CardContent>
                  </Card>
                ))}
              </div>
            </CardContent>
          )}
        </Card>
      )}

      {/* Minor Challenge Yogas */}
      {challengeYogas.length > 0 && (
        <Card className="border-2 border-yellow-300 bg-yellow-50">
          <CardHeader
            className="cursor-pointer hover:bg-yellow-100 transition-colors"
            onClick={() => setChallengeExpanded(!challengeExpanded)}
          >
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <AlertCircle className="w-6 h-6 text-orange-600" />
                <div>
                  <CardTitle className="text-xl font-bold text-gray-900">
                    Minor Challenges
                  </CardTitle>
                  <p className="text-sm text-gray-600 mt-1">
                    {challengeYogas.length} minor obstacles with manageable effects
                  </p>
                </div>
              </div>
              {challengeExpanded ? (
                <ChevronUp className="w-6 h-6 text-gray-600" />
              ) : (
                <ChevronDown className="w-6 h-6 text-gray-600" />
              )}
            </div>
          </CardHeader>

          {challengeExpanded && (
            <CardContent className="pt-4">
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {challengeYogas.map((yoga, index) => (
                  <Card
                    key={index}
                    className="border border-yellow-300 bg-white hover:shadow-md transition-shadow cursor-pointer"
                    onClick={() => onYogaClick?.(yoga)}
                  >
                    <CardContent className="p-4 space-y-2">
                      <div className="flex items-start justify-between gap-2">
                        <h4 className="font-semibold text-gray-900 text-sm leading-tight">
                          {yoga.name}
                        </h4>
                        <Badge
                          variant="outline"
                          className={`
                            flex-shrink-0 text-xs
                            ${yoga.strength === 'Strong' ? 'border-orange-500 text-orange-700 bg-orange-50' : ''}
                            ${yoga.strength === 'Medium' ? 'border-yellow-500 text-yellow-700 bg-yellow-50' : ''}
                            ${yoga.strength === 'Weak' ? 'border-gray-500 text-gray-700 bg-gray-50' : ''}
                          `}
                        >
                          {yoga.strength}
                        </Badge>
                      </div>
                      <p className="text-xs text-gray-600 line-clamp-2">
                        {yoga.description}
                      </p>
                      <div className="flex flex-wrap gap-1">
                        <Badge variant="outline" className="text-xs border-gray-300">
                          {yoga.category}
                        </Badge>
                        {yoga.life_area && (
                          <Badge variant="outline" className="text-xs border-gray-300">
                            {yoga.life_area}
                          </Badge>
                        )}
                      </div>
                    </CardContent>
                  </Card>
                ))}
              </div>
            </CardContent>
          )}
        </Card>
      )}
    </div>
  )
}
