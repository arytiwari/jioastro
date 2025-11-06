import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Star, AlertTriangle, Sparkles } from '@/components/icons'
import { cn } from '@/lib/utils'

interface NumerologyCardProps {
  title: string
  number: number
  description?: string
  isMaster?: boolean
  karmicDebt?: number | null
  meaning?: string | {
    title?: string
    description?: string
    keywords?: string[]
    traits?: string
    challenges?: string
    purpose?: string
    career?: string
    relationships?: string
    personality?: string
    favorable_dates?: number[]
    favorable_colors?: string[]
    favorable_gems?: string[]
    favorable_days?: string[]
    element?: string
    characteristics?: string
  }
  favorableAttributes?: string[]
  className?: string
}

export function NumerologyCard({
  title,
  number,
  description,
  isMaster = false,
  karmicDebt = null,
  meaning,
  favorableAttributes,
  className,
}: NumerologyCardProps) {
  return (
    <Card className={cn('hover:shadow-md transition-shadow', className)}>
      <CardHeader>
        <div className="flex items-start justify-between">
          <CardTitle className="text-lg">{title}</CardTitle>
          <div className="flex gap-1">
            {isMaster && (
              <span className="flex items-center gap-1 text-xs bg-yellow-100 text-yellow-700 px-2 py-1 rounded font-semibold">
                <Star className="w-3 h-3" />
                Master
              </span>
            )}
            {karmicDebt && (
              <span className="flex items-center gap-1 text-xs bg-red-100 text-red-700 px-2 py-1 rounded font-semibold">
                <AlertTriangle className="w-3 h-3" />
                Karmic {karmicDebt}
              </span>
            )}
          </div>
        </div>
        {description && <CardDescription>{description}</CardDescription>}
      </CardHeader>
      <CardContent>
        <div className="flex items-center gap-4 mb-4">
          <div
            className={cn(
              'flex items-center justify-center w-16 h-16 rounded-full text-2xl font-bold',
              isMaster
                ? 'bg-yellow-100 text-yellow-700'
                : karmicDebt
                ? 'bg-red-100 text-red-700'
                : 'bg-purple-100 text-purple-700'
            )}
          >
            {number}
          </div>
          {meaning && (
            <div className="flex-1 space-y-1">
              {typeof meaning === 'string' ? (
                <p className="text-sm text-gray-700 font-medium">{meaning}</p>
              ) : (
                <>
                  {meaning.title && (
                    <p className="text-sm font-semibold text-gray-800">{meaning.title}</p>
                  )}
                  {meaning.description && (
                    <p className="text-sm text-gray-700">{meaning.description}</p>
                  )}
                  {meaning.personality && (
                    <p className="text-sm text-gray-700">{meaning.personality}</p>
                  )}
                  {meaning.characteristics && (
                    <p className="text-sm text-gray-700">{meaning.characteristics}</p>
                  )}
                </>
              )}
            </div>
          )}
        </div>

        {/* Additional meaning details for object type */}
        {meaning && typeof meaning === 'object' && (
          <div className="space-y-3 mb-4">
            {meaning.traits && (
              <div className="text-xs">
                <span className="font-semibold text-gray-700">Traits: </span>
                <span className="text-gray-600">{meaning.traits}</span>
              </div>
            )}
            {meaning.challenges && (
              <div className="text-xs">
                <span className="font-semibold text-gray-700">Challenges: </span>
                <span className="text-gray-600">{meaning.challenges}</span>
              </div>
            )}
            {meaning.purpose && (
              <div className="text-xs">
                <span className="font-semibold text-gray-700">Life Purpose: </span>
                <span className="text-gray-600">{meaning.purpose}</span>
              </div>
            )}
            {meaning.career && (
              <div className="text-xs">
                <span className="font-semibold text-gray-700">Career Paths: </span>
                <span className="text-gray-600">{meaning.career}</span>
              </div>
            )}
            {meaning.relationships && (
              <div className="text-xs">
                <span className="font-semibold text-gray-700">Relationships: </span>
                <span className="text-gray-600">{meaning.relationships}</span>
              </div>
            )}
            {meaning.element && (
              <div className="text-xs">
                <span className="font-semibold text-gray-700">Element: </span>
                <span className="text-gray-600">{meaning.element}</span>
              </div>
            )}
          </div>
        )}

        {/* Vedic favorable attributes */}
        {meaning && typeof meaning === 'object' && (
          <>
            {meaning.favorable_colors && meaning.favorable_colors.length > 0 && (
              <div className="space-y-2 mb-3">
                <div className="text-xs font-semibold text-gray-600 uppercase">Favorable Colors</div>
                <div className="flex flex-wrap gap-2">
                  {meaning.favorable_colors.map((color, idx) => (
                    <span key={idx} className="text-xs bg-blue-100 text-blue-700 px-2 py-1 rounded">
                      {color}
                    </span>
                  ))}
                </div>
              </div>
            )}
            {meaning.favorable_gems && meaning.favorable_gems.length > 0 && (
              <div className="space-y-2 mb-3">
                <div className="text-xs font-semibold text-gray-600 uppercase">Favorable Gems</div>
                <div className="flex flex-wrap gap-2">
                  {meaning.favorable_gems.map((gem, idx) => (
                    <span key={idx} className="text-xs bg-purple-100 text-purple-700 px-2 py-1 rounded">
                      {gem}
                    </span>
                  ))}
                </div>
              </div>
            )}
            {meaning.favorable_days && meaning.favorable_days.length > 0 && (
              <div className="space-y-2 mb-3">
                <div className="text-xs font-semibold text-gray-600 uppercase">Favorable Days</div>
                <div className="flex flex-wrap gap-2">
                  {meaning.favorable_days.map((day, idx) => (
                    <span key={idx} className="text-xs bg-green-100 text-green-700 px-2 py-1 rounded">
                      {day}
                    </span>
                  ))}
                </div>
              </div>
            )}
            {meaning.favorable_dates && meaning.favorable_dates.length > 0 && (
              <div className="space-y-2 mb-3">
                <div className="text-xs font-semibold text-gray-600 uppercase">Favorable Dates</div>
                <div className="flex flex-wrap gap-2">
                  {meaning.favorable_dates.map((date, idx) => (
                    <span key={idx} className="text-xs bg-indigo-100 text-indigo-700 px-2 py-1 rounded">
                      {date}
                    </span>
                  ))}
                </div>
              </div>
            )}
          </>
        )}

        {favorableAttributes && favorableAttributes.length > 0 && (
          <div className="space-y-2">
            <div className="flex items-center gap-1 text-xs font-semibold text-gray-600 uppercase">
              <Sparkles className="w-3 h-3" />
              Key Qualities
            </div>
            <div className="flex flex-wrap gap-2">
              {favorableAttributes.map((attr, idx) => (
                <span
                  key={idx}
                  className="text-xs bg-gray-100 text-gray-700 px-2 py-1 rounded"
                >
                  {attr}
                </span>
              ))}
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  )
}
