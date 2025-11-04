'use client'

import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card'

interface PlanetData {
  sign: string
  degree: number
  house: number
  retrograde: boolean
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
                      {planet.retrograde && (
                        <span className="text-xs bg-red-100 text-red-800 px-2 py-1 rounded">
                          Retrograde
                        </span>
                      )}
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
