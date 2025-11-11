"use client"

import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Star, Sparkles, Info } from "@/components/icons"

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
    bphs_category?: string
    bphs_section?: string
    bphs_ref?: string
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

        {/* BPHS Badge */}
        {yoga.bphs_category && (
          <div className="flex items-center space-x-2 pt-3 border-t border-gray-200">
            <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium border ${
              yoga.bphs_category === 'Major Positive Yogas' ? 'bg-emerald-100 text-emerald-800 border-emerald-300' :
              yoga.bphs_category === 'Standard Yogas' ? 'bg-blue-100 text-blue-800 border-blue-300' :
              yoga.bphs_category === 'Major Challenges' ? 'bg-red-100 text-red-800 border-red-300' :
              yoga.bphs_category === 'Minor Yogas & Subtle Influences' ? 'bg-purple-100 text-purple-800 border-purple-300' :
              'bg-gray-100 text-gray-800 border-gray-300'
            }`}>
              <span className="mr-1">
                {yoga.bphs_category === 'Major Positive Yogas' ? '⭐' :
                 yoga.bphs_category === 'Standard Yogas' ? '📖' :
                 yoga.bphs_category === 'Major Challenges' ? '⚠️' :
                 yoga.bphs_category === 'Minor Yogas & Subtle Influences' ? '✨' :
                 '🔧'}
              </span>
              {yoga.bphs_category}
            </span>
            {yoga.bphs_category !== 'Non-BPHS (Practical)' && yoga.bphs_ref && (
              <span className="text-xs text-gray-600 italic">
                {yoga.bphs_ref}
              </span>
            )}
          </div>
        )}

        {/* BPHS Info */}
        {yoga.bphs_section && (
          <div className="mt-2 p-3 bg-blue-50 border border-blue-200 rounded-lg text-sm">
            <div className="flex items-start space-x-2">
              <Info className="h-4 w-4 text-blue-600 mt-0.5 flex-shrink-0" />
              <div>
                <p className="font-semibold text-blue-900">BPHS Classification</p>
                <p className="text-blue-800 mt-1">
                  <strong>Section:</strong> {yoga.bphs_section}
                </p>
                {yoga.bphs_ref && (
                  <p className="text-blue-800 mt-1">
                    <strong>Reference:</strong> {yoga.bphs_ref}
                  </p>
                )}
                {yoga.bphs_category !== 'Non-BPHS (Practical)' && (
                  <p className="text-blue-700 mt-2 text-xs">
                    This is a classical yoga from the Brihat Parashara Hora Shastra (BPHS), the foundational text of Vedic astrology.
                  </p>
                )}
                {yoga.bphs_category === 'Non-BPHS (Practical)' && (
                  <p className="text-blue-700 mt-2 text-xs">
                    This is a practical yoga not explicitly mentioned in BPHS but derived from traditional principles for modern analysis.
                  </p>
                )}
              </div>
            </div>
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
