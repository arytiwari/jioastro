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
  chartType?: string // D1 or D9 for debugging/key
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

export function BirthChart({ chartData, width = 500, height = 500, chartType = 'Unknown' }: BirthChartProps) {
  // Validate chart data - ensure all required fields exist
  if (!chartData) {
    console.error(`BirthChart (${chartType}): chartData is null or undefined`)
    return (
      <div className="flex items-center justify-center p-8 text-gray-500">
        <p>No chart data available</p>
      </div>
    )
  }

  // Debug log to see what we're receiving
  console.log(`BirthChart (${chartType}) received data:`, {
    chart_type: chartData.chart_type || chartType,
    ascendant: chartData.ascendant,
    planet_count: Object.keys(chartData.planets || {}).length,
    house_count: (chartData.houses || []).length,
    planets_sample: Object.entries(chartData.planets || {}).slice(0, 2)
  })

  if (!chartData.houses || !Array.isArray(chartData.houses) || chartData.houses.length === 0) {
    console.error('BirthChart: houses field is missing or invalid:', chartData.houses)
    return (
      <div className="flex flex-col items-center justify-center p-8 text-gray-500 space-y-2">
        <p className="font-semibold">Chart data incomplete</p>
        <p className="text-sm">Missing house information</p>
        <p className="text-xs mt-2">Please recalculate this chart</p>
      </div>
    )
  }

  if (!chartData.planets || typeof chartData.planets !== 'object') {
    return (
      <div className="flex flex-col items-center justify-center p-8 text-gray-500 space-y-2">
        <p className="font-semibold">Chart data incomplete</p>
        <p className="text-sm">Missing planet information</p>
      </div>
    )
  }

  if (!chartData.ascendant) {
    return (
      <div className="flex flex-col items-center justify-center p-8 text-gray-500 space-y-2">
        <p className="font-semibold">Chart data incomplete</p>
        <p className="text-sm">Missing ascendant information</p>
      </div>
    )
  }

  // North Indian chart is a square divided into 12 houses in diamond pattern
  const centerX = width / 2
  const centerY = height / 2
  const size = Math.min(width, height) * 0.85

  // Group planets by house with full details
  const planetsByHouse: Record<number, Array<{
    name: string
    symbol: string
    sign: string
    retrograde: boolean
  }>> = {}

  Object.entries(chartData.planets).forEach(([planetName, planetData]) => {
    const house = planetData.house
    if (!planetsByHouse[house]) {
      planetsByHouse[house] = []
    }
    const symbol = PLANET_SYMBOLS[planetName] || planetName.charAt(0)
    planetsByHouse[house].push({
      name: planetName,
      symbol: symbol,
      sign: planetData.sign,
      retrograde: planetData.retrograde || false
    })
  })

  // Get house background color (alternating for clarity)
  const getHouseFill = (houseNum: number) => {
    // Kendra houses (1, 4, 7, 10) - Angular houses (most important)
    if ([1, 4, 7, 10].includes(houseNum)) {
      return '#fef3c7' // Light amber
    }
    // Trikona houses (5, 9) - Trinal houses (very auspicious)
    if ([5, 9].includes(houseNum)) {
      return '#dbeafe' // Light blue
    }
    // Other houses
    return '#f3f4f6' // Light gray
  }

  // North Indian chart house positions (diamond layout)
  // Traditional Vedic North Indian chart - FIXED house positions
  // House 1 (Ascendant/Lagna) always at TOP
  const getHousePolygon = (houseNum: number) => {
    const half = size / 2
    const quarter = size / 4

    // Standard North Indian diamond chart
    // The chart is a square rotated 45 degrees, divided into 12 sections
    const positions: Record<number, string> = {
      // House 1 - Top center (Ascendant - always here)
      1: `${centerX - quarter},${centerY - quarter} ${centerX},${centerY - half} ${centerX + quarter},${centerY - quarter}`,

      // House 2 - Top right
      2: `${centerX},${centerY - half} ${centerX + half},${centerY} ${centerX + quarter},${centerY - quarter}`,

      // House 3 - Right side upper
      3: `${centerX + quarter},${centerY - quarter} ${centerX + half},${centerY} ${centerX + quarter},${centerY}`,

      // House 4 - Right side lower
      4: `${centerX + quarter},${centerY} ${centerX + half},${centerY} ${centerX + quarter},${centerY + quarter}`,

      // House 5 - Bottom right
      5: `${centerX + quarter},${centerY + quarter} ${centerX + half},${centerY} ${centerX},${centerY + half}`,

      // House 6 - Bottom center
      6: `${centerX + quarter},${centerY + quarter} ${centerX},${centerY + half} ${centerX - quarter},${centerY + quarter}`,

      // House 7 - Bottom left
      7: `${centerX},${centerY + half} ${centerX - half},${centerY} ${centerX - quarter},${centerY + quarter}`,

      // House 8 - Left side lower
      8: `${centerX - quarter},${centerY + quarter} ${centerX - half},${centerY} ${centerX - quarter},${centerY}`,

      // House 9 - Left side upper
      9: `${centerX - quarter},${centerY} ${centerX - half},${centerY} ${centerX - quarter},${centerY - quarter}`,

      // House 10 - Top left
      10: `${centerX - quarter},${centerY - quarter} ${centerX - half},${centerY} ${centerX},${centerY - half}`,

      // House 11 - Center lower right
      11: `${centerX},${centerY} ${centerX + quarter},${centerY} ${centerX + quarter},${centerY + quarter} ${centerX},${centerY + quarter}`,

      // House 12 - Center lower left
      12: `${centerX - quarter},${centerY} ${centerX},${centerY} ${centerX},${centerY + quarter} ${centerX - quarter},${centerY + quarter}`
    }

    return positions[houseNum] || ''
  }

  // Get text position for house number and planets
  const getTextPosition = (houseNum: number) => {
    const half = size / 2
    const quarter = size / 4
    const eighth = size / 8

    const positions: Record<number, { x: number; y: number }> = {
      1: { x: centerX, y: centerY - half + quarter / 2 },           // Top center
      2: { x: centerX + quarter + eighth, y: centerY - quarter },   // Top right
      3: { x: centerX + quarter + eighth, y: centerY - eighth },    // Right upper
      4: { x: centerX + quarter + eighth, y: centerY + eighth },    // Right lower
      5: { x: centerX + quarter, y: centerY + quarter + eighth },   // Bottom right
      6: { x: centerX, y: centerY + half - quarter / 2 },           // Bottom center
      7: { x: centerX - quarter, y: centerY + quarter + eighth },   // Bottom left
      8: { x: centerX - quarter - eighth, y: centerY + eighth },    // Left lower
      9: { x: centerX - quarter - eighth, y: centerY - eighth },    // Left upper
      10: { x: centerX - quarter - eighth, y: centerY - quarter },  // Top left
      11: { x: centerX + eighth, y: centerY + eighth },             // Center lower right
      12: { x: centerX - eighth, y: centerY + eighth }              // Center lower left
    }

    return positions[houseNum] || { x: centerX, y: centerY }
  }

  return (
    <div className="flex flex-col items-center p-4">
      <svg
        width={width}
        height={height}
        className="shadow-lg rounded-lg"
        style={{ background: '#ffffff' }}
      >
        {/* Outer border */}
        <rect
          x="2"
          y="2"
          width={width - 4}
          height={height - 4}
          fill="none"
          stroke="#1e293b"
          strokeWidth="3"
          rx="8"
        />

        {/* Draw house divisions with backgrounds */}
        {[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12].map((houseNum) => (
          <g key={houseNum}>
            <polygon
              points={getHousePolygon(houseNum)}
              fill={getHouseFill(houseNum)}
              stroke="#1e293b"
              strokeWidth="2"
              strokeLinejoin="round"
            />
          </g>
        ))}

        {/* Add house numbers and signs */}
        {chartData.houses.map((house) => {
          const pos = getTextPosition(house.house_num)
          const isAscendant = house.house_num === 1
          const isKendra = [1, 4, 7, 10].includes(house.house_num)
          const isTrikona = [5, 9].includes(house.house_num)

          return (
            <g key={house.house_num}>
              {/* House number */}
              <text
                x={pos.x}
                y={pos.y}
                textAnchor="middle"
                fontSize="14"
                fontWeight="bold"
                fill={isAscendant ? '#7c3aed' : (isKendra ? '#d97706' : (isTrikona ? '#2563eb' : '#475569'))}
                style={{ fontFamily: 'system-ui, -apple-system, sans-serif' }}
              >
                {house.house_num}
              </text>
              {/* Sign abbreviation */}
              <text
                x={pos.x}
                y={pos.y + 14}
                textAnchor="middle"
                fontSize="10"
                fontWeight="500"
                fill="#64748b"
                style={{ fontFamily: 'system-ui, -apple-system, sans-serif' }}
              >
                {house.sign.substring(0, 3).toUpperCase()}
              </text>
            </g>
          )
        })}

        {/* Add planets */}
        {Object.entries(planetsByHouse).map(([houseNum, planets]) => {
          const pos = getTextPosition(parseInt(houseNum))
          const maxPlanetsPerRow = 3 // Limit planets per row to prevent overcrowding

          return (
            <g key={houseNum}>
              {planets.map((planet, idx) => {
                // Calculate position based on number of planets
                const row = Math.floor(idx / maxPlanetsPerRow)
                const col = idx % maxPlanetsPerRow
                const xOffset = (col - Math.floor(Math.min(planets.length - row * maxPlanetsPerRow, maxPlanetsPerRow) / 2)) * 25
                const yOffset = 28 + (row * 18)

                return (
                  <g key={idx}>
                    {/* Planet symbol */}
                    <text
                      x={pos.x + xOffset}
                      y={pos.y + yOffset}
                      textAnchor="middle"
                      fontSize="15"
                      fontWeight="600"
                      fill={planet.retrograde ? '#dc2626' : '#be123c'}
                      style={{ fontFamily: 'system-ui, -apple-system, sans-serif' }}
                    >
                      {planet.symbol}
                      {planet.retrograde && (
                        <tspan fontSize="9" baselineShift="super">R</tspan>
                      )}
                    </text>
                    {/* Planet sign (small text below symbol) */}
                    <text
                      x={pos.x + xOffset}
                      y={pos.y + yOffset + 9}
                      textAnchor="middle"
                      fontSize="7"
                      fontWeight="500"
                      fill="#64748b"
                      style={{ fontFamily: 'system-ui, -apple-system, sans-serif' }}
                    >
                      {planet.sign.substring(0, 3)}
                    </text>
                  </g>
                )
              })}
            </g>
          )
        })}

        {/* Add ascendant marker at top */}
        <rect
          x={centerX - 60}
          y={10}
          width="120"
          height="25"
          fill="#7c3aed"
          stroke="#5b21b6"
          strokeWidth="2"
          rx="4"
        />
        <text
          x={centerX}
          y={28}
          textAnchor="middle"
          fontSize="13"
          fontWeight="bold"
          fill="#ffffff"
          style={{ fontFamily: 'system-ui, -apple-system, sans-serif' }}
        >
          ASC: {chartData.ascendant.sign.toUpperCase()}
        </text>
      </svg>

      {/* Enhanced Legend */}
      <div className="mt-6 p-4 bg-gray-50 rounded-lg border border-gray-200 w-full max-w-md">
        <p className="text-center font-bold text-lg mb-3 text-gray-800">North Indian Chart (Vedic)</p>

        <div className="grid grid-cols-2 gap-3 text-xs mb-3">
          <div className="flex items-center gap-2">
            <div className="w-6 h-6 bg-amber-100 border-2 border-gray-800 rounded"></div>
            <span className="text-gray-700">Kendra (1,4,7,10)</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-6 h-6 bg-blue-100 border-2 border-gray-800 rounded"></div>
            <span className="text-gray-700">Trikona (5,9)</span>
          </div>
        </div>

        <div className="border-t border-gray-300 pt-3 mb-3">
          <p className="font-semibold text-sm text-gray-700 mb-2">Planet Symbols:</p>
          <div className="grid grid-cols-3 gap-2 text-xs">
            {Object.entries(PLANET_SYMBOLS).map(([name, symbol]) => (
              <div key={name} className="flex items-center gap-1">
                <span className="text-lg text-rose-700">{symbol}</span>
                <span className="text-gray-600">{name}</span>
              </div>
            ))}
          </div>
        </div>

        <div className="border-t border-gray-300 pt-2 text-xs text-gray-600 space-y-1">
          <p><span className="font-semibold">ASC</span> = Ascendant (Lagna) - Rising sign</p>
          <p><span className="font-semibold text-red-600">R</span> = Retrograde motion</p>
          <p><span className="font-semibold">Kendra</span> = Angular houses (strength & action)</p>
          <p><span className="font-semibold">Trikona</span> = Trinal houses (fortune & dharma)</p>
        </div>
      </div>
    </div>
  )
}
