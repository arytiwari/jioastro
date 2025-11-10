"use client"

import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { AlertTriangle, Info } from "@/components/icons"

interface ChallengeYogaCardProps {
  yoga: {
    name: string
    description: string
    category: string
    strength: string
    impact: string
    importance: string
    life_area: string
    planets_involved?: string[]
    houses_involved?: number[]
    benefic_nature?: string
  }
  onClick?: () => void
}

export default function ChallengeYogaCard({ yoga, onClick }: ChallengeYogaCardProps) {
  const isMixed = yoga.impact === "mixed"

  return (
    <Card
      className={`
        border-2 shadow-md transition-all duration-300 hover:shadow-lg cursor-pointer
        ${isMixed
          ? 'border-purple-500 bg-gradient-to-br from-purple-50 to-indigo-50'
          : 'border-orange-500 bg-gradient-to-br from-orange-50 to-red-50'
        }
      `}
      onClick={onClick}
    >
      <CardHeader className="pb-3">
        <div className="flex items-start gap-4">
          {/* Icon */}
          <div className={`
            w-14 h-14 rounded-full flex items-center justify-center flex-shrink-0
            ${isMixed
              ? 'bg-gradient-to-br from-purple-400 to-indigo-400'
              : 'bg-gradient-to-br from-orange-400 to-red-400'
            }
          `}>
            {isMixed ? (
              <Info className="w-8 h-8 text-white" />
            ) : (
              <AlertTriangle className="w-8 h-8 text-white" />
            )}
          </div>

          {/* Title & Badges */}
          <div className="flex-1 min-w-0">
            <div className="flex flex-wrap gap-2 mb-2">
              <Badge className={`
                text-white font-semibold
                ${isMixed ? 'bg-purple-600 hover:bg-purple-700' : 'bg-orange-600 hover:bg-orange-700'}
              `}>
                MAJOR {isMixed ? 'MIXED' : 'CHALLENGE'}
              </Badge>
              <Badge variant="outline" className="border-gray-400">
                {yoga.life_area}
              </Badge>
            </div>
            <CardTitle className="text-2xl font-bold text-gray-900">
              {yoga.name}
            </CardTitle>
          </div>
        </div>
      </CardHeader>

      <CardContent className="space-y-3">
        {/* Description */}
        <p className="text-gray-700 leading-relaxed">
          {yoga.description}
        </p>

        {/* Info Box for Mixed Yogas */}
        {isMixed && (
          <div className="bg-purple-100 border border-purple-300 rounded-lg p-3">
            <div className="flex items-start gap-2">
              <Info className="w-5 h-5 text-purple-700 flex-shrink-0 mt-0.5" />
              <p className="text-sm text-purple-900">
                This yoga presents both challenges and opportunities for transformation.
                Proper understanding and remedial measures can help maximize benefits.
              </p>
            </div>
          </div>
        )}

        {/* Remedial Focus for Negative Yogas */}
        {!isMixed && (
          <div className="bg-amber-100 border border-amber-300 rounded-lg p-3">
            <div className="flex items-start gap-2">
              <AlertTriangle className="w-5 h-5 text-amber-700 flex-shrink-0 mt-0.5" />
              <p className="text-sm text-amber-900">
                Remedial measures are recommended. Click for detailed solutions including
                mantras, gemstones, and lifestyle adjustments.
              </p>
            </div>
          </div>
        )}

        {/* Metadata Grid */}
        <div className="grid grid-cols-2 gap-3 pt-2">
          <div className="space-y-1">
            <div className="text-xs font-semibold text-gray-500 uppercase tracking-wide">
              Category
            </div>
            <div className="text-sm font-medium text-gray-900">
              {yoga.category}
            </div>
          </div>

          <div className="space-y-1">
            <div className="text-xs font-semibold text-gray-500 uppercase tracking-wide">
              Strength
            </div>
            <div className="text-sm font-medium text-gray-900">
              <Badge
                variant="outline"
                className={`
                  ${yoga.strength === 'Very Strong' ? 'border-red-600 text-red-700 bg-red-50' : ''}
                  ${yoga.strength === 'Strong' ? 'border-orange-600 text-orange-700 bg-orange-50' : ''}
                  ${yoga.strength === 'Medium' ? 'border-yellow-600 text-yellow-700 bg-yellow-50' : ''}
                `}
              >
                {yoga.strength}
              </Badge>
            </div>
          </div>
        </div>

        {/* Planets & Houses */}
        {(yoga.planets_involved || yoga.houses_involved) && (
          <div className="grid grid-cols-2 gap-3 pt-2 border-t border-gray-200">
            {yoga.planets_involved && (
              <div className="space-y-1">
                <div className="text-xs font-semibold text-gray-500 uppercase tracking-wide">
                  Planets
                </div>
                <div className="text-sm text-gray-700">
                  {yoga.planets_involved.join(", ")}
                </div>
              </div>
            )}

            {yoga.houses_involved && (
              <div className="space-y-1">
                <div className="text-xs font-semibold text-gray-500 uppercase tracking-wide">
                  Houses
                </div>
                <div className="text-sm text-gray-700">
                  {yoga.houses_involved.join(", ")}
                </div>
              </div>
            )}
          </div>
        )}

        {/* Click hint */}
        <div className="pt-2 text-center">
          <span className="text-xs text-gray-500 italic">
            Click for remedies, timing, and transformation guidance
          </span>
        </div>
      </CardContent>
    </Card>
  )
}
