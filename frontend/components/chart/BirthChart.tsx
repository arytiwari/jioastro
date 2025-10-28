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

  // Traditional North Indian Vedic Chart Layout
  // Based on exact template: Square with two diagonal lines creating 12 sections
  // House 1 (Lagna/Ascendant) is at TOP
  const getHousePolygon = (houseNum: number) => {
    const half = size / 2

    // Square corners and center
    const top = centerY - half
    const bottom = centerY + half
    const left = centerX - half
    const right = centerX + half

    // North Indian Chart - 12 Houses
    // Two diagonals from corner to corner create the 12 sections
    const positions: Record<number, string> = {
      // House 1 - TOP triangle (Ascendant - ALWAYS here)
      1: `${left},${top} ${centerX},${centerY} ${right},${top}`,

      // House 2 - Upper RIGHT section (between top corner and right corner)
      2: `${right},${top} ${centerX},${centerY} ${right},${centerY}`,

      // House 3 - RIGHT triangle
      3: `${right},${centerY} ${centerX},${centerY} ${right},${bottom}`,

      // House 4 - Lower RIGHT section (between right corner and bottom corner)
      4: `${right},${bottom} ${centerX},${centerY} ${centerX},${bottom}`,

      // House 5 - BOTTOM triangle
      5: `${centerX},${bottom} ${centerX},${centerY} ${left},${bottom}`,

      // House 6 - Lower LEFT section (between bottom corner and left corner)
      6: `${left},${bottom} ${centerX},${centerY} ${left},${centerY}`,

      // House 7 - LEFT triangle
      7: `${left},${centerY} ${centerX},${centerY} ${left},${top}`,

      // House 8 - Upper LEFT section (between left corner and top corner)
      8: `${left},${top} ${centerX},${centerY} ${centerX},${top}`,

      // House 9 - Center UPPER-LEFT quadrant
      9: `${left + half/2},${top + half/2} ${centerX},${top + half/2} ${centerX},${centerY} ${left + half/2},${centerY}`,

      // House 10 - Center UPPER-RIGHT quadrant
      10: `${centerX},${top + half/2} ${right - half/2},${top + half/2} ${right - half/2},${centerY} ${centerX},${centerY}`,

      // House 11 - Center LOWER-RIGHT quadrant
      11: `${centerX},${centerY} ${right - half/2},${centerY} ${right - half/2},${bottom - half/2} ${centerX},${bottom - half/2}`,

      // House 12 - Center LOWER-LEFT quadrant
      12: `${left + half/2},${centerY} ${centerX},${centerY} ${centerX},${bottom - half/2} ${left + half/2},${bottom - half/2}`
    }

    return positions[houseNum] || ''
  }

  // Get text position for house number and planets
  // Positions match the new polygon layout
  const getTextPosition = (houseNum: number) => {
    const half = size / 2
    const quarter = size / 4
    const eighth = size / 8

    const positions: Record<number, { x: number; y: number }> = {
      1: { x: centerX, y: centerY - quarter },                        // House 1 - Top triangle
      2: { x: centerX + quarter, y: centerY - quarter },              // House 2 - Upper right
      3: { x: centerX + quarter, y: centerY },                        // House 3 - Right triangle
      4: { x: centerX + quarter, y: centerY + quarter },              // House 4 - Lower right
      5: { x: centerX, y: centerY + quarter },                        // House 5 - Bottom triangle
      6: { x: centerX - quarter, y: centerY + quarter },              // House 6 - Lower left
      7: { x: centerX - quarter, y: centerY },                        // House 7 - Left triangle
      8: { x: centerX - quarter, y: centerY - quarter },              // House 8 - Upper left
      9: { x: centerX - eighth, y: centerY - eighth },                // House 9 - Center upper-left
      10: { x: centerX + eighth, y: centerY - eighth },               // House 10 - Center upper-right
      11: { x: centerX + eighth, y: centerY + eighth },               // House 11 - Center lower-right
      12: { x: centerX - eighth, y: centerY + eighth }                // House 12 - Center lower-left
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
        {[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12].map((houseNum) => {
          const house = chartData.houses.find(h => h.house_num === houseNum)
          if (!house) return null

          const pos = getTextPosition(houseNum)
          const isAscendant = houseNum === 1
          const isKendra = [1, 4, 7, 10].includes(houseNum)
          const isTrikona = [5, 9].includes(houseNum)

          return (
            <g key={houseNum}>
              {/* House number */}
              <text
                x={pos.x}
                y={pos.y}
                textAnchor="middle"
                fontSize="16"
                fontWeight="bold"
                fill={isAscendant ? '#7c3aed' : (isKendra ? '#d97706' : (isTrikona ? '#2563eb' : '#475569'))}
                style={{ fontFamily: 'system-ui, -apple-system, sans-serif' }}
              >
                {houseNum}
              </text>
              {/* Sign abbreviation */}
              <text
                x={pos.x}
                y={pos.y + 16}
                textAnchor="middle"
                fontSize="11"
                fontWeight="600"
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
                const yOffset = 32 + (row * 18)

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
