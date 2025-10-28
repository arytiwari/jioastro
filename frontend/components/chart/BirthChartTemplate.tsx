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
  chartType?: string
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
  { name: 'Aries', abbr: 'ARI', glyph: '♈' },      // 0
  { name: 'Taurus', abbr: 'TAU', glyph: '♉' },     // 1
  { name: 'Gemini', abbr: 'GEM', glyph: '♊' },     // 2
  { name: 'Cancer', abbr: 'CAN', glyph: '♋' },     // 3
  { name: 'Leo', abbr: 'LEO', glyph: '♌' },        // 4
  { name: 'Virgo', abbr: 'VIR', glyph: '♍' },      // 5
  { name: 'Libra', abbr: 'LIB', glyph: '♎' },      // 6
  { name: 'Scorpio', abbr: 'SCO', glyph: '♏' },    // 7
  { name: 'Sagittarius', abbr: 'SAG', glyph: '♐' },// 8
  { name: 'Capricorn', abbr: 'CAP', glyph: '♑' },  // 9
  { name: 'Aquarius', abbr: 'AQU', glyph: '♒' },   // 10
  { name: 'Pisces', abbr: 'PIS', glyph: '♓' }      // 11
]

// House anchor positions (as percentages of canvas size)
// Matching the HTML template exactly
const HOUSE_ANCHORS: Record<number, [number, number]> = {
  1: [0.50, 0.18],  // top mid
  2: [0.78, 0.24],  // top-right corner
  3: [0.86, 0.50],  // right mid
  4: [0.78, 0.78],  // bottom-right corner
  5: [0.50, 0.84],  // bottom mid
  6: [0.22, 0.78],  // bottom-left corner
  7: [0.14, 0.50],  // left mid
  8: [0.22, 0.24],  // top-left corner
  9: [0.36, 0.28],  // upper-left inner
  10: [0.64, 0.28], // upper-right inner
  11: [0.64, 0.72], // lower-right inner
  12: [0.36, 0.72]  // lower-left inner
}

export function BirthChartTemplate({ chartData, width = 600, height = 600, chartType = 'D1' }: BirthChartProps) {
  if (!chartData || !chartData.houses || !chartData.planets || !chartData.ascendant) {
    return (
      <div className="flex items-center justify-center p-8 text-gray-500">
        <p>Chart data incomplete</p>
      </div>
    )
  }

  // Get ascendant sign number (0-indexed for array)
  const lagnaSignNum = chartData.ascendant.sign_num

  // Calculate sign in each house (anti-clockwise from ascendant)
  const signInHouse = (houseNum: number): typeof ZODIAC_SIGNS[0] => {
    const idx = (lagnaSignNum + (houseNum - 1)) % 12
    return ZODIAC_SIGNS[idx]
  }

  // Group planets by house
  const planetsByHouse: Record<number, Array<{name: string, symbol: string, retrograde: boolean}>> = {}
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

  const boxSize = Math.min(width, height) * 0.9
  const half = boxSize / 2
  const centerX = width / 2
  const centerY = height / 2
  const left = centerX - half
  const top = centerY - half
  const right = centerX + half
  const bottom = centerY + half

  return (
    <div className="flex flex-col items-center p-4">
      <svg width={width} height={height}>
        {/* Background square with rounded corners */}
        <rect
          x={left}
          y={top}
          width={boxSize}
          height={boxSize}
          fill="#fef9e7"
          stroke="#d68910"
          strokeWidth="4"
          rx="15"
        />

        {/* Diagonal lines forming X */}
        <line x1={left} y1={top} x2={right} y2={bottom} stroke="#d68910" strokeWidth="2.5" />
        <line x1={right} y1={top} x2={left} y2={bottom} stroke="#d68910" strokeWidth="2.5" />

        {/* Horizontal and vertical center lines */}
        <line x1={left} y1={centerY} x2={right} y2={centerY} stroke="#d68910" strokeWidth="2.5" />
        <line x1={centerX} y1={top} x2={centerX} y2={bottom} stroke="#d68910" strokeWidth="2.5" />

        {/* Render all 12 houses with their labels */}
        {[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12].map((houseNum) => {
          const [fx, fy] = HOUSE_ANCHORS[houseNum]
          const x = left + (boxSize * fx)
          const y = top + (boxSize * fy)

          const sign = signInHouse(houseNum)
          const planets = planetsByHouse[houseNum] || []

          // Determine colors
          const isAscendant = houseNum === 1
          const isKendra = [1, 4, 7, 10].includes(houseNum)
          const isTrikona = [5, 9].includes(houseNum)
          const houseColor = isAscendant ? '#7c3aed' : (isKendra ? '#d97706' : (isTrikona ? '#2563eb' : '#1f2937'))

          let yOffset = 0

          return (
            <g key={houseNum}>
              {/* House number - large and bold */}
              <text
                x={x}
                y={y + yOffset}
                textAnchor="middle"
                fontSize="22"
                fontWeight="bold"
                fill={houseColor}
                style={{ fontFamily: 'system-ui, -apple-system, sans-serif' }}
              >
                {houseNum}
              </text>

              {/* Sign glyph and abbreviation */}
              <text
                x={x}
                y={y + yOffset + 24}
                textAnchor="middle"
                fontSize="16"
                fontWeight="600"
                fill="#374151"
                style={{ fontFamily: 'system-ui, -apple-system, sans-serif' }}
              >
                {sign.glyph} {sign.abbr}
              </text>

              {/* Planets in this house */}
              {planets.map((planet, idx) => (
                <text
                  key={idx}
                  x={x}
                  y={y + yOffset + 46 + (idx * 20)}
                  textAnchor="middle"
                  fontSize="15"
                  fontWeight="600"
                  fill={planet.retrograde ? '#dc2626' : '#be123c'}
                  style={{ fontFamily: 'system-ui, -apple-system, sans-serif' }}
                >
                  {planet.symbol}{planet.retrograde ? 'ʀ' : ''}
                </text>
              ))}
            </g>
          )
        })}

        {/* Ascendant label at top */}
        <rect
          x={centerX - 70}
          y={top - 40}
          width={140}
          height={32}
          fill="#7c3aed"
          stroke="#5b21b6"
          strokeWidth="2"
          rx="8"
        />
        <text
          x={centerX}
          y={top - 16}
          textAnchor="middle"
          fontSize="15"
          fontWeight="bold"
          fill="#ffffff"
          style={{ fontFamily: 'system-ui, -apple-system, sans-serif' }}
        >
          ASC: {chartData.ascendant.sign.toUpperCase()}
        </text>
      </svg>

      {/* Legend */}
      <div className="mt-6 p-4 bg-gray-50 rounded-lg border border-gray-200 w-full max-w-md">
        <p className="text-center font-bold text-lg mb-3 text-gray-800">North Indian Chart (Vedic)</p>
        <div className="text-xs text-gray-600 space-y-1">
          <p><span className="font-semibold text-purple-700">House 1</span> (Top) - Ascendant/Lagna</p>
          <p><span className="font-semibold text-amber-700">Kendra</span> (1,4,7,10) - Angular houses</p>
          <p><span className="font-semibold text-blue-700">Trikona</span> (5,9) - Trinal houses</p>
          <p className="mt-2"><span className="font-semibold text-red-600">ʀ</span> = Retrograde</p>
          <p className="text-xs text-gray-500 mt-3 italic">
            Signs proceed anti-clockwise from Ascendant
          </p>
        </div>
      </div>
    </div>
  )
}
