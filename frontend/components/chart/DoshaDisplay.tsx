/**
 * DoshaDisplay Component
 * Displays all detected doshas with severity levels, effects, and remedies
 */

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Alert, AlertDescription } from '@/components/ui/alert'

interface DoshaDetails {
  [key: string]: any
}

interface Dosha {
  name: string
  present: boolean
  severity: 'high' | 'medium' | 'low' | 'none'
  description?: string
  details?: DoshaDetails
  effects?: string
  remedies?: string[]
}

interface DoshaDisplayProps {
  doshas: Dosha[]
}

/**
 * Get background and border color classes based on severity
 */
function getSeverityColor(severity: string): string {
  const colors: Record<string, string> = {
    high: 'border-red-300 bg-red-50',
    medium: 'border-yellow-300 bg-yellow-50',
    low: 'border-blue-300 bg-blue-50',
    none: 'border-gray-300 bg-gray-50'
  }
  return colors[severity] || colors.none
}

/**
 * Get icon based on severity level
 */
function getSeverityIcon(severity: string): string {
  const icons: Record<string, string> = {
    high: '🔴',
    medium: '🟡',
    low: '🔵',
    none: '⚪'
  }
  return icons[severity] || icons.none
}

/**
 * Get badge variant based on severity
 */
function getSeverityBadge(severity: string): 'default' | 'secondary' | 'destructive' | 'outline' {
  const variants: Record<string, 'default' | 'secondary' | 'destructive' | 'outline'> = {
    high: 'destructive',
    medium: 'default',
    low: 'secondary',
    none: 'outline'
  }
  return variants[severity] || 'outline'
}

/**
 * Format dosha details object for display
 */
function formatDoshaDetails(details: DoshaDetails | undefined): string {
  if (!details) return ''

  try {
    return JSON.stringify(details, null, 2)
  } catch {
    return String(details)
  }
}

export function DoshaDisplay({ doshas }: DoshaDisplayProps) {
  // Filter to only show present doshas
  const presentDoshas = doshas.filter((d) => d.present)
  const noDoshas = presentDoshas.length === 0

  return (
    <div className="space-y-6">
      {noDoshas ? (
        // No doshas present - show positive message
        <Card className="bg-green-50 border-green-200">
          <CardHeader>
            <CardTitle className="text-green-800 flex items-center gap-2">
              ✅ No Major Doshas Detected
            </CardTitle>
            <CardDescription className="text-green-700">
              Your chart is relatively free from major afflictions. This is considered auspicious and indicates
              a more harmonious life path.
            </CardDescription>
          </CardHeader>
          <CardContent>
            <p className="text-sm text-green-600">
              While minor challenges may still exist, the absence of major doshas suggests good overall balance
              in your astrological chart.
            </p>
          </CardContent>
        </Card>
      ) : (
        // Doshas present - show each dosha card
        <>
          <Alert>
            <AlertDescription>
              Found {presentDoshas.length} dosha{presentDoshas.length > 1 ? 's' : ''} in your chart.
              Doshas are astrological afflictions that can be remedied through specific practices.
            </AlertDescription>
          </Alert>

          <div className="grid gap-6">
            {presentDoshas.map((dosha) => (
              <Card
                key={dosha.name}
                className={`${getSeverityColor(dosha.severity)} transition-all hover:shadow-lg`}
              >
                <CardHeader>
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <CardTitle className="flex items-center gap-2 text-xl">
                        {getSeverityIcon(dosha.severity)}
                        {dosha.name}
                      </CardTitle>
                      {dosha.description && (
                        <CardDescription className="mt-2 text-base">
                          {dosha.description}
                        </CardDescription>
                      )}
                    </div>
                    <Badge variant={getSeverityBadge(dosha.severity)} className="ml-4">
                      {dosha.severity.toUpperCase()}
                    </Badge>
                  </div>
                </CardHeader>

                <CardContent className="space-y-4">
                  {/* Effects Section */}
                  {dosha.effects && (
                    <div className="p-4 rounded-lg bg-white/50">
                      <h4 className="font-semibold mb-2 flex items-center gap-2">
                        ⚠️ Effects:
                      </h4>
                      {typeof dosha.effects === 'string' ? (
                        <p className="text-sm text-gray-700 leading-relaxed">
                          {dosha.effects}
                        </p>
                      ) : typeof dosha.effects === 'object' && dosha.effects !== null ? (
                        <div className="space-y-2">
                          {Object.entries(dosha.effects).map(([category, effectsList]) => (
                            <div key={category} className="text-sm">
                              <p className="font-medium text-gray-800 capitalize mb-1">
                                {category.replace(/_/g, ' ')}:
                              </p>
                              {Array.isArray(effectsList) ? (
                                <ul className="list-disc list-inside pl-2 space-y-1">
                                  {effectsList.map((effect: string, idx: number) => (
                                    <li key={idx} className="text-gray-700">{effect}</li>
                                  ))}
                                </ul>
                              ) : (
                                <p className="text-gray-700 pl-2">{String(effectsList)}</p>
                              )}
                            </div>
                          ))}
                        </div>
                      ) : (
                        <p className="text-sm text-gray-700 leading-relaxed">
                          {String(dosha.effects)}
                        </p>
                      )}
                    </div>
                  )}

                  {/* Details Section */}
                  {dosha.details && Object.keys(dosha.details).length > 0 && (
                    <div className="p-4 rounded-lg bg-white/50">
                      <h4 className="font-semibold mb-2 flex items-center gap-2">
                        📋 Details:
                      </h4>
                      <div className="bg-gray-50 p-3 rounded border border-gray-200">
                        <pre className="text-xs font-mono text-gray-700 whitespace-pre-wrap overflow-x-auto">
                          {formatDoshaDetails(dosha.details)}
                        </pre>
                      </div>
                    </div>
                  )}

                  {/* Remedies Section */}
                  {dosha.remedies && dosha.remedies.length > 0 && (
                    <div className="p-4 rounded-lg bg-gradient-to-br from-purple-50 to-blue-50 border border-purple-200">
                      <h4 className="font-semibold mb-3 flex items-center gap-2 text-purple-900">
                        🔮 Remedies & Solutions:
                      </h4>
                      <ul className="space-y-2">
                        {dosha.remedies.map((remedy, idx) => (
                          <li
                            key={idx}
                            className="flex items-start gap-2 text-sm text-gray-800"
                          >
                            <span className="text-purple-600 font-bold text-base mt-0.5">•</span>
                            <span className="flex-1 leading-relaxed">{remedy}</span>
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}
                </CardContent>
              </Card>
            ))}
          </div>

          {/* Footer Note */}
          <Card className="bg-blue-50 border-blue-200">
            <CardContent className="py-4">
              <p className="text-sm text-blue-800">
                <strong>Note:</strong> Doshas are part of Vedic astrology and represent challenging planetary
                configurations. The severity and effects can be mitigated through the suggested remedies.
                Consult with a qualified astrologer for personalized guidance.
              </p>
            </CardContent>
          </Card>
        </>
      )}
    </div>
  )
}

export default DoshaDisplay
