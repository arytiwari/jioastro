"use client"

import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Star, Sparkles } from "@/components/icons"

interface MajorYogaCardProps {
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

export default function MajorYogaCard({ yoga, onClick }: MajorYogaCardProps) {
  const isPositive = yoga.impact === "positive"

  return (
    <Card
      className={`
        border-2 shadow-lg transition-all duration-300 hover:shadow-xl cursor-pointer
        ${isPositive
          ? 'border-emerald-500 bg-gradient-to-br from-emerald-50 via-amber-50 to-yellow-50'
          : 'border-purple-500 bg-gradient-to-br from-purple-50 via-pink-50 to-rose-50'
        }
      `}
      onClick={onClick}
    >
      <CardHeader className="pb-3">
        <div className="flex items-start gap-4">
          {/* Icon */}
          <div className={`
            w-14 h-14 rounded-full flex items-center justify-center flex-shrink-0
            ${isPositive
              ? 'bg-gradient-to-br from-emerald-400 to-amber-400'
              : 'bg-gradient-to-br from-purple-400 to-pink-400'
            }
          `}>
            {isPositive ? (
              <Star className="w-8 h-8 text-white fill-white" />
            ) : (
              <Sparkles className="w-8 h-8 text-white" />
            )}
          </div>

          {/* Title & Badges */}
          <div className="flex-1 min-w-0">
            <div className="flex flex-wrap gap-2 mb-2">
              <Badge className={`
                text-white font-semibold
                ${isPositive ? 'bg-emerald-600 hover:bg-emerald-700' : 'bg-purple-600 hover:bg-purple-700'}
              `}>
                MAJOR {isPositive ? 'POSITIVE' : 'MIXED'}
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
                  ${yoga.strength === 'Very Strong' ? 'border-green-600 text-green-700 bg-green-50' : ''}
                  ${yoga.strength === 'Strong' ? 'border-blue-600 text-blue-700 bg-blue-50' : ''}
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
            Click for detailed timing, examples & remedies
          </span>
        </div>
      </CardContent>
    </Card>
  )
}
