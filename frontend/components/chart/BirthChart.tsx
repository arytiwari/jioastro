'use client'

import React from 'react'

interface Planet {
  sign: string
  sign_num: number
  position: number
  house: number
  retrograde?: boolean
}

interface ChartData {
  ascendant: {
    sign: string
    sign_num: number
    house: number
  }
  planets: Record<string, Planet>
  houses: Array<{
    house_num: number
    sign: string
    sign_num: number
  }>
}

interface BirthChartProps {
  chartData: ChartData
  width?: number
  height?: number
}

const ZODIAC_SIGNS = [
  'Aries', 'Taurus', 'Gemini', 'Cancer', 'Leo', 'Virgo',
  'Libra', 'Scorpio', 'Sagittarius', 'Capricorn', 'Aquarius', 'Pisces'
]

const PLANET_SYMBOLS: Record<string, string> = {
  Sun: '☉',
  Moon: '☽',
  Mars: '♂',
  Mercury: '☿',
  Jupiter: '♃',
  Venus: '♀',
  Saturn: '♄',
  Rahu: '☊',
  Ketu: '☋'
}

export function BirthChart({ chartData, width = 400, height = 400 }: BirthChartProps) {
  // North Indian chart is a square divided into 12 houses in diamond pattern
  const centerX = width / 2
  const centerY = height / 2
  const size = Math.min(width, height) * 0.9

  // Group planets by house
  const planetsByHouse: Record<number, string[]> = {}

  Object.entries(chartData.planets).forEach(([planetName, planetData]) => {
    const house = planetData.house
    if (!planetsByHouse[house]) {
      planetsByHouse[house] = []
    }
    const symbol = PLANET_SYMBOLS[planetName] || planetName.charAt(0)
    const retrograde = planetData.retrograde ? ' R' : ''
    planetsByHouse[house].push(`${symbol}${retrograde}`)
  })

  // North Indian chart house positions (diamond layout)
  const getHousePolygon = (houseNum: number) => {
    const half = size / 2
    const quarter = size / 4

    // North Indian chart layout
    const positions: Record<number, string> = {
      1: `${centerX},${centerY - half} ${centerX + quarter},${centerY - quarter} ${centerX - quarter},${centerY - quarter}`,
      2: `${centerX + quarter},${centerY - quarter} ${centerX + half},${centerY} ${centerX},${centerY - half}`,
      3: `${centerX + half},${centerY} ${centerX + quarter},${centerY + quarter} ${centerX + quarter},${centerY - quarter}`,
      4: `${centerX + quarter},${centerY + quarter} ${centerX},${centerY + half} ${centerX + half},${centerY}`,
      5: `${centerX},${centerY + half} ${centerX - quarter},${centerY + quarter} ${centerX + quarter},${centerY + quarter}`,
      6: `${centerX - quarter},${centerY + quarter} ${centerX - half},${centerY} ${centerX},${centerY + half}`,
      7: `${centerX - half},${centerY} ${centerX - quarter},${centerY - quarter} ${centerX - quarter},${centerY + quarter}`,
      8: `${centerX - quarter},${centerY - quarter} ${centerX},${centerY - half} ${centerX - half},${centerY}`,
      9: `${centerX - quarter},${centerY - quarter} ${centerX},${centerY} ${centerX + quarter},${centerY - quarter}`,
      10: `${centerX + quarter},${centerY - quarter} ${centerX},${centerY} ${centerX + quarter},${centerY + quarter}`,
      11: `${centerX + quarter},${centerY + quarter} ${centerX},${centerY} ${centerX - quarter},${centerY + quarter}`,
      12: `${centerX - quarter},${centerY + quarter} ${centerX},${centerY} ${centerX - quarter},${centerY - quarter}`
    }

    return positions[houseNum] || ''
  }

  // Get text position for house number and planets
  const getTextPosition = (houseNum: number) => {
    const half = size / 2
    const quarter = size / 4
    const offset = size / 12

    const positions: Record<number, { x: number; y: number }> = {
      1: { x: centerX, y: centerY - half + offset },
      2: { x: centerX + quarter + offset, y: centerY - quarter },
      3: { x: centerX + half - offset, y: centerY },
      4: { x: centerX + quarter + offset, y: centerY + quarter },
      5: { x: centerX, y: centerY + half - offset },
      6: { x: centerX - quarter - offset, y: centerY + quarter },
      7: { x: centerX - half + offset, y: centerY },
      8: { x: centerX - quarter - offset, y: centerY - quarter },
      9: { x: centerX, y: centerY - offset },
      10: { x: centerX + offset, y: centerY },
      11: { x: centerX, y: centerY + offset },
      12: { x: centerX - offset, y: centerY }
    }

    return positions[houseNum] || { x: centerX, y: centerY }
  }

  return (
    <div className="flex flex-col items-center">
      <svg width={width} height={height} className="border border-gray-300 rounded-lg bg-white">
        {/* Draw house divisions */}
        {[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12].map((houseNum) => (
          <g key={houseNum}>
            <polygon
              points={getHousePolygon(houseNum)}
              fill="none"
              stroke="#333"
              strokeWidth="1.5"
            />
          </g>
        ))}

        {/* Add house numbers and signs */}
        {chartData.houses.map((house) => {
          const pos = getTextPosition(house.house_num)
          const isAscendant = house.house_num === 1

          return (
            <g key={house.house_num}>
              <text
                x={pos.x}
                y={pos.y}
                textAnchor="middle"
                fontSize="11"
                fontWeight={isAscendant ? 'bold' : 'normal'}
                fill={isAscendant ? '#7c3aed' : '#666'}
              >
                {house.house_num}
              </text>
              <text
                x={pos.x}
                y={pos.y + 12}
                textAnchor="middle"
                fontSize="9"
                fill="#999"
              >
                {house.sign.substring(0, 3)}
              </text>
            </g>
          )
        })}

        {/* Add planets */}
        {Object.entries(planetsByHouse).map(([houseNum, planets]) => {
          const pos = getTextPosition(parseInt(houseNum))

          return (
            <g key={houseNum}>
              {planets.map((planet, idx) => (
                <text
                  key={idx}
                  x={pos.x}
                  y={pos.y + 24 + (idx * 12)}
                  textAnchor="middle"
                  fontSize="13"
                  fontWeight="600"
                  fill="#e11d48"
                >
                  {planet}
                </text>
              ))}
            </g>
          )
        })}

        {/* Add ascendant marker */}
        <text
          x={centerX}
          y={centerY - size / 2 - 10}
          textAnchor="middle"
          fontSize="12"
          fontWeight="bold"
          fill="#7c3aed"
        >
          ASC: {chartData.ascendant.sign}
        </text>
      </svg>

      {/* Legend */}
      <div className="mt-4 text-sm text-gray-600">
        <p className="text-center font-semibold mb-2">North Indian Chart</p>
        <p className="text-center text-xs">
          ASC = Ascendant (Lagna) | R = Retrograde
        </p>
      </div>
    </div>
  )
}
