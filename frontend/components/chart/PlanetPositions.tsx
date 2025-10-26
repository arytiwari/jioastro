'use client'

import React from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'

interface Planet {
  sign: string
  position: number
  house: number
  retrograde?: boolean
}

interface PlanetPositionsProps {
  planets: Record<string, Planet>
}

export function PlanetPositions({ planets }: PlanetPositionsProps) {
  const planetOrder = ['Sun', 'Moon', 'Mars', 'Mercury', 'Jupiter', 'Venus', 'Saturn', 'Rahu', 'Ketu']

  return (
    <Card>
      <CardHeader>
        <CardTitle>Planetary Positions</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b">
                <th className="text-left py-2 px-2">Planet</th>
                <th className="text-left py-2 px-2">Sign</th>
                <th className="text-left py-2 px-2">Position</th>
                <th className="text-left py-2 px-2">House</th>
                <th className="text-left py-2 px-2">Status</th>
              </tr>
            </thead>
            <tbody>
              {planetOrder.map((planetName) => {
                const planet = planets[planetName]
                if (!planet) return null

                return (
                  <tr key={planetName} className="border-b hover:bg-gray-50">
                    <td className="py-2 px-2 font-semibold">{planetName}</td>
                    <td className="py-2 px-2">{planet.sign}</td>
                    <td className="py-2 px-2">{planet.position.toFixed(2)}°</td>
                    <td className="py-2 px-2">{planet.house}</td>
                    <td className="py-2 px-2">
                      {planet.retrograde ? (
                        <span className="text-red-600 font-semibold">R</span>
                      ) : (
                        <span className="text-green-600">D</span>
                      )}
                    </td>
                  </tr>
                )
              })}
            </tbody>
          </table>
        </div>
        <div className="mt-4 text-xs text-gray-500">
          <p>R = Retrograde | D = Direct</p>
        </div>
      </CardContent>
    </Card>
  )
}
