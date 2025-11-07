/**
 * TransitsDisplay Component
 * Displays current planetary transits and Sade Sati status
 */

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert'

interface PlanetTransit {
  sign: string
  degree: number
  house_from_moon: number
  house_from_lagna: number
  effects: string
  is_significant?: boolean
}

interface TransitsData {
  reference_date: string
  transits: {
    Jupiter?: PlanetTransit
    Saturn?: PlanetTransit
    Rahu?: PlanetTransit
    Ketu?: PlanetTransit
  }
  significant_transits?: string[]
}

interface SadeSatiData {
  in_sade_sati: boolean
  phase?: string
  severity?: 'high' | 'medium' | 'low' | 'none'
  saturn_current_sign?: string
  saturn_house_from_moon?: number
  natal_moon_sign?: string
  effects?: string
  remedies?: string[]
  years_until_next?: number
}

interface TransitsDisplayProps {
  transits: TransitsData
  sadeSati: SadeSatiData
}

/**
 * Get planet icon
 */
function getPlanetIcon(planet: string): string {
  const icons: Record<string, string> = {
    Jupiter: '♃',
    Saturn: '♄',
    Rahu: '☊',
    Ketu: '☋',
  }
  return icons[planet] || '🪐'
}

/**
 * Get severity color for Sade Sati
 */
function getSadeSatiColor(severity: string): string {
  const colors: Record<string, string> = {
    high: 'border-red-500 bg-red-50',
    medium: 'border-yellow-500 bg-yellow-50',
    low: 'border-blue-500 bg-blue-50',
    none: 'border-gray-300 bg-gray-50'
  }
  return colors[severity] || colors.medium
}

/**
 * Format date for display
 */
function formatDate(dateString: string): string {
  try {
    const date = new Date(dateString)
    return date.toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    })
  } catch {
    return dateString
  }
}

export function TransitsDisplay({ transits, sadeSati }: TransitsDisplayProps) {
  const planetOrder = ['Jupiter', 'Saturn', 'Rahu', 'Ketu']
  const transitEntries = planetOrder
    .map((planet) => ({
      planet,
      data: transits.transits[planet as keyof typeof transits.transits]
    }))
    .filter((entry) => entry.data !== undefined)

  return (
    <div className="space-y-6">
      {/* Sade Sati Status Card */}
      {sadeSati.in_sade_sati ? (
        <Card className={`${getSadeSatiColor(sadeSati.severity || 'medium')} border-2`}>
          <CardHeader>
            <div className="flex items-start justify-between">
              <div className="flex-1">
                <CardTitle className="flex items-center gap-2 text-xl">
                  ⚠️ Sade Sati Currently Active
                </CardTitle>
                <CardDescription className="mt-2 text-base">
                  {sadeSati.phase && `${sadeSati.phase}`}
                  {sadeSati.saturn_house_from_moon &&
                    ` - Saturn in ${sadeSati.saturn_house_from_moon}th house from Moon`}
                </CardDescription>
              </div>
              {sadeSati.severity && (
                <Badge
                  variant={sadeSati.severity === 'high' ? 'destructive' : 'default'}
                  className="ml-4"
                >
                  {sadeSati.severity.toUpperCase()}
                </Badge>
              )}
            </div>
          </CardHeader>

          <CardContent className="space-y-4">
            {/* Sade Sati Details */}
            <div className="grid md:grid-cols-2 gap-4 p-4 bg-white/60 rounded-lg">
              <div>
                <p className="text-sm font-semibold text-gray-600">Current Phase:</p>
                <p className="text-base text-gray-900">{sadeSati.phase || 'Unknown'}</p>
              </div>
              <div>
                <p className="text-sm font-semibold text-gray-600">Severity:</p>
                <p className="text-base text-gray-900 capitalize">{sadeSati.severity || 'medium'}</p>
              </div>
              <div>
                <p className="text-sm font-semibold text-gray-600">Saturn Currently In:</p>
                <p className="text-base text-gray-900">{sadeSati.saturn_current_sign || 'N/A'}</p>
              </div>
              <div>
                <p className="text-sm font-semibold text-gray-600">Your Moon Sign:</p>
                <p className="text-base text-gray-900">{sadeSati.natal_moon_sign || 'N/A'}</p>
              </div>
            </div>

            {/* Effects */}
            {sadeSati.effects && (
              <div className="p-4 bg-white/60 rounded-lg">
                <h4 className="font-semibold mb-2 flex items-center gap-2">
                  📊 Effects:
                </h4>
                <p className="text-sm text-gray-700 leading-relaxed">
                  {sadeSati.effects}
                </p>
              </div>
            )}

            {/* Remedies */}
            {sadeSati.remedies && sadeSati.remedies.length > 0 && (
              <div className="p-4 bg-gradient-to-br from-purple-50 to-blue-50 rounded-lg border border-purple-200">
                <h4 className="font-semibold mb-3 flex items-center gap-2 text-purple-900">
                  🙏 Remedies for Sade Sati:
                </h4>
                <ul className="space-y-2">
                  {sadeSati.remedies.map((remedy, idx) => (
                    <li key={idx} className="text-sm flex items-start gap-2 text-gray-800">
                      <span className="text-purple-600 font-bold text-base mt-0.5">•</span>
                      <span className="flex-1 leading-relaxed">{remedy}</span>
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </CardContent>
        </Card>
      ) : (
        <Card className="bg-green-50 border-green-200">
          <CardHeader>
            <CardTitle className="text-green-800 flex items-center gap-2">
              ✅ Not Currently in Sade Sati
            </CardTitle>
            <CardDescription className="text-green-700">
              {sadeSati.years_until_next
                ? `Sade Sati will begin in approximately ${sadeSati.years_until_next} years`
                : 'You are not experiencing the 7.5-year Saturn transit period'}
            </CardDescription>
          </CardHeader>
        </Card>
      )}

      {/* Current Transits */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            🪐 Current Planetary Transits
          </CardTitle>
          <CardDescription>
            Positions as of {formatDate(transits.reference_date)}
          </CardDescription>
        </CardHeader>

        <CardContent className="space-y-4">
          {transitEntries.length > 0 ? (
            <div className="grid md:grid-cols-2 gap-4">
              {transitEntries.map(({ planet, data }) => (
                <Card
                  key={planet}
                  className={`border-2 transition-all hover:shadow-md ${
                    data?.is_significant ? 'border-jio-500 bg-jio-50' : 'border-gray-200'
                  }`}
                >
                  <CardHeader className="pb-3">
                    <CardTitle className="text-lg flex items-center gap-2">
                      <span className="text-2xl">{getPlanetIcon(planet)}</span>
                      {planet}
                      {data?.is_significant && (
                        <Badge variant="default" className="ml-auto">
                          Significant
                        </Badge>
                      )}
                    </CardTitle>
                  </CardHeader>

                  <CardContent className="space-y-3">
                    <div className="grid grid-cols-2 gap-2 text-sm">
                      <div className="space-y-1">
                        <p className="font-semibold text-gray-600">Sign:</p>
                        <p className="text-gray-900">
                          {data?.sign} ({data?.degree.toFixed(2)}°)
                        </p>
                      </div>

                      <div className="space-y-1">
                        <p className="font-semibold text-gray-600">From Moon:</p>
                        <p className="text-gray-900">{data?.house_from_moon}th house</p>
                      </div>

                      <div className="space-y-1 col-span-2">
                        <p className="font-semibold text-gray-600">From Ascendant:</p>
                        <p className="text-gray-900">{data?.house_from_lagna}th house</p>
                      </div>
                    </div>

                    {data?.effects && (
                      <div className="pt-3 border-t">
                        <p className="text-xs text-gray-600 font-semibold mb-1">Effects:</p>
                        <p className="text-sm text-gray-700 leading-relaxed">{data.effects}</p>
                      </div>
                    )}
                  </CardContent>
                </Card>
              ))}
            </div>
          ) : (
            <p className="text-gray-500 text-center py-4">No transit data available</p>
          )}

          {/* Significant Transits Highlight */}
          {transits.significant_transits && transits.significant_transits.length > 0 && (
            <Alert className="bg-blue-50 border-blue-200">
              <AlertTitle className="flex items-center gap-2">
                🌟 Significant Current Transits
              </AlertTitle>
              <AlertDescription>
                <ul className="mt-2 space-y-1">
                  {transits.significant_transits.map((transit, idx) => (
                    <li key={idx} className="text-sm flex items-start gap-2">
                      <span className="text-blue-600 font-bold">•</span>
                      <span>{transit}</span>
                    </li>
                  ))}
                </ul>
              </AlertDescription>
            </Alert>
          )}
        </CardContent>
      </Card>

      {/* Information Footer */}
      <Card className="bg-gray-50 border-gray-200">
        <CardContent className="py-4">
          <p className="text-sm text-gray-700 leading-relaxed">
            <strong>About Transits:</strong> Planetary transits (Gochar) represent the current movement of
            planets through the zodiac. They interact with your birth chart positions to create temporary
            influences. Slower planets like Jupiter and Saturn have longer-lasting effects, while Rahu and
            Ketu indicate karmic lessons and transformation periods.
          </p>
        </CardContent>
      </Card>
    </div>
  )
}

export default TransitsDisplay
