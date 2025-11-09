'use client'

import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card'

interface PlanetData {
  sign: string
  degree: number
  house: number
  retrograde: boolean
  exalted?: boolean
  debilitated?: boolean
  own_sign?: boolean
  combust?: boolean
  vargottama?: boolean
  combustion_distance?: number
  nakshatra?: {
    name: string
    pada: number
  }
}

interface PlanetaryPositionsTableProps {
  planets: Record<string, PlanetData>
  title?: string
  description?: string
  showHouse?: boolean
}

export function PlanetaryPositionsTable({
  planets,
  title = "Planetary Positions",
  description = "Detailed positions of all planets in the chart",
  showHouse = true
}: PlanetaryPositionsTableProps) {
  // Order planets in traditional sequence
  const planetOrder = ['Sun', 'Moon', 'Mars', 'Mercury', 'Jupiter', 'Venus', 'Saturn', 'Rahu', 'Ketu']
  const orderedPlanets = planetOrder.filter(p => planets[p])

  return (
    <Card>
      <CardHeader>
        <CardTitle>{title}</CardTitle>
        {description && <CardDescription>{description}</CardDescription>}
      </CardHeader>
      <CardContent>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b">
                <th className="text-left py-3 px-3 font-semibold">Planet</th>
                <th className="text-left py-3 px-3 font-semibold">Sign</th>
                <th className="text-left py-3 px-3 font-semibold">Degree</th>
                <th className="text-left py-3 px-3 font-semibold">Nakshatra</th>
                {showHouse && (
                  <th className="text-left py-3 px-3 font-semibold">House</th>
                )}
                <th className="text-left py-3 px-3 font-semibold">Status</th>
              </tr>
            </thead>
            <tbody>
              {orderedPlanets.map((planetName) => {
                const planet = planets[planetName]
                return (
                  <tr key={planetName} className="border-b hover:bg-gray-50">
                    <td className="py-3 px-3 font-medium">{planetName}</td>
                    <td className="py-3 px-3">{planet.sign}</td>
                    <td className="py-3 px-3">{planet.degree.toFixed(2)}°</td>
                    <td className="py-3 px-3">
                      {planet.nakshatra ? (
                        <span className="text-xs bg-purple-100 text-purple-800 px-2 py-1 rounded">
                          {planet.nakshatra.name}
                          {planet.nakshatra.pada && ` (${planet.nakshatra.pada})`}
                        </span>
                      ) : (
                        <span className="text-gray-400">-</span>
                      )}
                    </td>
                    {showHouse && (
                      <td className="py-3 px-3">{planet.house}</td>
                    )}
                    <td className="py-3 px-3">
                      <div className="flex flex-wrap gap-1">
                        {planet.exalted && (
                          <span className="text-xs bg-green-100 text-green-800 px-2 py-1 rounded font-semibold" title="Planet in exaltation sign">
                            Exalted
                          </span>
                        )}
                        {planet.debilitated && (
                          <span className="text-xs bg-red-100 text-red-800 px-2 py-1 rounded font-semibold" title="Planet in debilitation sign">
                            Debilitated
                          </span>
                        )}
                        {planet.own_sign && (
                          <span className="text-xs bg-blue-100 text-blue-800 px-2 py-1 rounded" title="Planet in its own sign">
                            Own Sign
                          </span>
                        )}
                        {planet.vargottama && (
                          <span className="text-xs bg-purple-100 text-purple-800 px-2 py-1 rounded" title="Same sign in D1 and D9 (powerful position)">
                            Vargottama
                          </span>
                        )}
                        {planet.retrograde && (
                          <span className="text-xs bg-orange-100 text-orange-800 px-2 py-1 rounded" title="Planet moving backward">
                            Retrograde
                          </span>
                        )}
                        {planet.combust && (
                          <span className="text-xs bg-yellow-100 text-yellow-800 px-2 py-1 rounded" title={`Too close to Sun${planet.combustion_distance ? ` (${planet.combustion_distance}°)` : ''}`}>
                            Combust {planet.combustion_distance && `(${planet.combustion_distance}°)`}
                          </span>
                        )}
                        {!planet.exalted && !planet.debilitated && !planet.own_sign && !planet.vargottama && !planet.retrograde && !planet.combust && (
                          <span className="text-xs text-gray-400">-</span>
                        )}
                      </div>
                    </td>
                  </tr>
                )
              })}
            </tbody>
          </table>
        </div>
      </CardContent>
    </Card>
  )
}
