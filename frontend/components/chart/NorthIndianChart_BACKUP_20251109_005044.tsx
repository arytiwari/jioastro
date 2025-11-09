'use client'

import React from 'react'

interface Planet {
  sign: string
  sign_num: number
  degree: number
  longitude: number
  house: number
  retrograde?: boolean
  nakshatra?: {
    name: string
    pada: number
  }
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

interface NorthIndianChartProps {
  chartData: ChartData
  width?: number
  height?: number
}

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

const ZODIAC_SIGNS = [
  { name: 'Aries', abbr: 'AR' },
  { name: 'Taurus', abbr: 'TA' },
  { name: 'Gemini', abbr: 'GE' },
  { name: 'Cancer', abbr: 'CN' },
  { name: 'Leo', abbr: 'LE' },
  { name: 'Virgo', abbr: 'VI' },
  { name: 'Libra', abbr: 'LI' },
  { name: 'Scorpio', abbr: 'SC' },
  { name: 'Sagittarius', abbr: 'SG' },
  { name: 'Capricorn', abbr: 'CP' },
  { name: 'Aquarius', abbr: 'AQ' },
  { name: 'Pisces', abbr: 'PI' }
]

// North Indian chart house positions (as per standard North Indian chart layout)
// H1 is in the CENTER diamond, other houses are in triangular sections around it
// Position coordinates: [x, y] as fraction of chart size
const HOUSE_POSITIONS: Record<number, {
  houseNum: { x: number; y: number }
  sign: { x: number; y: number }
  planetsStart: { x: number; y: number }
  textAnchor: 'start' | 'middle' | 'end'
}> = {
  1: {
    // CENTER diamond - Ascendant/Lagna (moved much higher)
    houseNum: { x: 0.50, y: 0.33 },
    sign: { x: 0.50, y: 0.39 },
    planetsStart: { x: 0.50, y: 0.45 },
    textAnchor: 'middle'
  },
  2: {
    // Top-left triangle (moved further up)
    houseNum: { x: 0.25, y: 0.09 },
    sign: { x: 0.25, y: 0.15 },
    planetsStart: { x: 0.25, y: 0.21 },
    textAnchor: 'middle'
  },
  3: {
    // Left triangle (moved further left and up)
    houseNum: { x: 0.06, y: 0.30 },
    sign: { x: 0.06, y: 0.36 },
    planetsStart: { x: 0.06, y: 0.42 },
    textAnchor: 'start'
  },
  4: {
    // Lower-left triangle (moved further up)
    houseNum: { x: 0.25, y: 0.60 },
    sign: { x: 0.25, y: 0.54 },
    planetsStart: { x: 0.25, y: 0.48 },
    textAnchor: 'middle'
  },
  5: {
    // Bottom-left corner triangle (moved left and up)
    houseNum: { x: 0.06, y: 0.82 },
    sign: { x: 0.06, y: 0.76 },
    planetsStart: { x: 0.06, y: 0.70 },
    textAnchor: 'start'
  },
  6: {
    // Bottom left-of-center triangle
    houseNum: { x: 0.30, y: 0.93 },
    sign: { x: 0.30, y: 0.87 },
    planetsStart: { x: 0.30, y: 0.81 },
    textAnchor: 'middle'
  },
  7: {
    // Bottom center triangle (moved up)
    houseNum: { x: 0.50, y: 0.90 },
    sign: { x: 0.50, y: 0.84 },
    planetsStart: { x: 0.50, y: 0.78 },
    textAnchor: 'middle'
  },
  8: {
    // Bottom right-of-center triangle
    houseNum: { x: 0.70, y: 0.93 },
    sign: { x: 0.70, y: 0.87 },
    planetsStart: { x: 0.70, y: 0.81 },
    textAnchor: 'middle'
  },
  9: {
    // Bottom-right corner triangle (moved right and up)
    houseNum: { x: 0.94, y: 0.82 },
    sign: { x: 0.94, y: 0.76 },
    planetsStart: { x: 0.94, y: 0.70 },
    textAnchor: 'end'
  },
  10: {
    // Lower-right triangle (moved further up)
    houseNum: { x: 0.75, y: 0.60 },
    sign: { x: 0.75, y: 0.54 },
    planetsStart: { x: 0.75, y: 0.48 },
    textAnchor: 'middle'
  },
  11: {
    // Right triangle (moved even further up and right)
    houseNum: { x: 0.94, y: 0.26 },
    sign: { x: 0.94, y: 0.32 },
    planetsStart: { x: 0.94, y: 0.38 },
    textAnchor: 'end'
  },
  12: {
    // Top-right triangle (moved much further up)
    houseNum: { x: 0.75, y: 0.06 },
    sign: { x: 0.75, y: 0.12 },
    planetsStart: { x: 0.75, y: 0.18 },
    textAnchor: 'middle'
  }
}

export function NorthIndianChart({ chartData, width = 600, height = 600 }: NorthIndianChartProps) {
  if (!chartData || !chartData.houses || !chartData.planets || !chartData.ascendant) {
    return (
      <div className="flex items-center justify-center p-8 text-gray-500">
        <p>Chart data incomplete</p>
      </div>
    )
  }

  const chartSize = Math.min(width, height) * 0.85
  const offsetX = (width - chartSize) / 2
  const offsetY = (height - chartSize) / 2

  // Calculate corner and midpoint positions
  const corners = {
    topLeft: { x: offsetX, y: offsetY },
    topRight: { x: offsetX + chartSize, y: offsetY },
    bottomLeft: { x: offsetX, y: offsetY + chartSize },
    bottomRight: { x: offsetX + chartSize, y: offsetY + chartSize }
  }

  const midpoints = {
    top: { x: offsetX + chartSize / 2, y: offsetY },
    right: { x: offsetX + chartSize, y: offsetY + chartSize / 2 },
    bottom: { x: offsetX + chartSize / 2, y: offsetY + chartSize },
    left: { x: offsetX, y: offsetY + chartSize / 2 }
  }

  // Group planets by house
  const planetsByHouse: Record<number, Array<{ name: string; symbol: string; retrograde: boolean }>> = {}
  Object.entries(chartData.planets).forEach(([name, data]) => {
    if (!planetsByHouse[data.house]) {
      planetsByHouse[data.house] = []
    }
    planetsByHouse[data.house].push({
      name,
      symbol: PLANET_SYMBOLS[name] || name[0],
      retrograde: data.retrograde || false
    })
  })

  // Get sign for each house based on ascendant
  const getSignForHouse = (houseNum: number): string => {
    const lagnaSignNum = chartData.ascendant.sign_num
    const signNum = (lagnaSignNum + houseNum - 1) % 12
    return ZODIAC_SIGNS[signNum].abbr
  }

  return (
    <div className="flex flex-col items-center p-4">
      <svg width={width} height={height + 80} viewBox={`0 0 ${width} ${height + 80}`}>
        {/* Outer square border */}
        <rect
          x={offsetX}
          y={offsetY}
          width={chartSize}
          height={chartSize}
          fill="#fefcf8"
          stroke="#b1792d"
          strokeWidth="3"
          rx="4"
        />

        {/* Diagonal lines (X pattern) */}
        <line
          x1={corners.topLeft.x}
          y1={corners.topLeft.y}
          x2={corners.bottomRight.x}
          y2={corners.bottomRight.y}
          stroke="#b1792d"
          strokeWidth="2"
        />
        <line
          x1={corners.topRight.x}
          y1={corners.topRight.y}
          x2={corners.bottomLeft.x}
          y2={corners.bottomLeft.y}
          stroke="#b1792d"
          strokeWidth="2"
        />

        {/* Inner diamond (connecting midpoints) */}
        <line
          x1={midpoints.top.x}
          y1={midpoints.top.y}
          x2={midpoints.right.x}
          y2={midpoints.right.y}
          stroke="#b1792d"
          strokeWidth="2"
        />
        <line
          x1={midpoints.right.x}
          y1={midpoints.right.y}
          x2={midpoints.bottom.x}
          y2={midpoints.bottom.y}
          stroke="#b1792d"
          strokeWidth="2"
        />
        <line
          x1={midpoints.bottom.x}
          y1={midpoints.bottom.y}
          x2={midpoints.left.x}
          y2={midpoints.left.y}
          stroke="#b1792d"
          strokeWidth="2"
        />
        <line
          x1={midpoints.left.x}
          y1={midpoints.left.y}
          x2={midpoints.top.x}
          y2={midpoints.top.y}
          stroke="#b1792d"
          strokeWidth="2"
        />

        {/* Render houses with signs and planets */}
        {[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12].map((houseNum) => {
          const pos = HOUSE_POSITIONS[houseNum]
          const houseNumX = offsetX + chartSize * pos.houseNum.x
          const houseNumY = offsetY + chartSize * pos.houseNum.y
          const signX = offsetX + chartSize * pos.sign.x
          const signY = offsetY + chartSize * pos.sign.y
          const planetsX = offsetX + chartSize * pos.planetsStart.x
          const planetsY = offsetY + chartSize * pos.planetsStart.y
          const sign = getSignForHouse(houseNum)
          const planets = planetsByHouse[houseNum] || []
          const isAscendant = houseNum === 1

          return (
            <g key={houseNum}>
              {/* Special label for H1 (center) */}
              {isAscendant && (
                <>
                  <text
                    x={offsetX + chartSize * 0.50}
                    y={offsetY + chartSize * 0.24}
                    textAnchor="middle"
                    fontSize={chartSize * 0.030}
                    fontWeight="600"
                    fill="#666"
                    style={{ fontFamily: 'system-ui, sans-serif' }}
                  >
                    Rising/Lagna
                  </text>
                  <text
                    x={offsetX + chartSize * 0.50}
                    y={offsetY + chartSize * 0.27}
                    textAnchor="middle"
                    fontSize={chartSize * 0.028}
                    fontWeight="600"
                    fill="#666"
                    style={{ fontFamily: 'system-ui, sans-serif' }}
                  >
                    Ascendant
                  </text>
                </>
              )}

              {/* House number */}
              <text
                x={houseNumX}
                y={houseNumY}
                textAnchor={pos.textAnchor}
                fontSize={chartSize * 0.05}
                fontWeight="700"
                fill={isAscendant ? '#7c3aed' : '#654321'}
                style={{ fontFamily: 'system-ui, sans-serif' }}
              >
                H{houseNum}
              </text>

              {/* Zodiac sign */}
              <text
                x={signX}
                y={signY}
                textAnchor={pos.textAnchor}
                fontSize={chartSize * 0.038}
                fontWeight="600"
                fill="#8a5f2a"
                style={{ fontFamily: 'system-ui, sans-serif' }}
              >
                {sign}
              </text>

              {/* Planets in this house */}
              {planets.map((planet, idx) => (
                <text
                  key={`${houseNum}-${planet.name}`}
                  x={planetsX}
                  y={planetsY + idx * chartSize * 0.055}
                  textAnchor={pos.textAnchor}
                  fontSize={chartSize * 0.036}
                  fontWeight="600"
                  fill={planet.retrograde ? '#dc2626' : '#be123c'}
                  style={{ fontFamily: 'system-ui, sans-serif' }}
                >
                  {planet.symbol}{planet.retrograde ? 'ʀ' : ''}
                </text>
              ))}
            </g>
          )
        })}

        {/* Ascendant label at bottom */}
        <rect
          x={width / 2 - 70}
          y={offsetY + chartSize + 20}
          width={140}
          height={32}
          fill="#7c3aed"
          stroke="#5b21b6"
          strokeWidth="2"
          rx="8"
        />
        <text
          x={width / 2}
          y={offsetY + chartSize + 40}
          textAnchor="middle"
          fontSize="15"
          fontWeight="bold"
          fill="#ffffff"
          style={{ fontFamily: 'system-ui, sans-serif' }}
        >
          ASC: {chartData.ascendant.sign.toUpperCase()}
        </text>
      </svg>

      {/* Legend */}
      <div className="mt-8 p-4 bg-gray-50 rounded-lg border border-gray-200 w-full max-w-md">
        <p className="text-center font-bold text-lg mb-3 text-gray-800">North Indian Chart (Vedic)</p>
        <div className="text-xs text-gray-600 space-y-1">
          <p><span className="font-semibold text-purple-700">H1</span> - House 1 (Ascendant/Lagna) - CENTER diamond</p>
          <p><span className="font-semibold">H2-H12</span> - Other houses in triangular sections around H1</p>
          <p><span className="font-semibold">Diamond layout</span> - Traditional North Indian style</p>
          <p className="mt-2"><span className="font-semibold text-red-600">ʀ</span> = Retrograde planet</p>
          <p className="text-xs text-gray-500 mt-3 italic">
            H1 (Ascendant) is always in the center. Signs rotate based on Ascendant sign.
          </p>
        </div>
      </div>
    </div>
  )
}
