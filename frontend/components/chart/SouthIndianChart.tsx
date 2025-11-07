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

interface SouthIndianChartProps {
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
  { name: 'Aries', abbr: 'AR', glyph: '♈' },
  { name: 'Taurus', abbr: 'TA', glyph: '♉' },
  { name: 'Gemini', abbr: 'GE', glyph: '♊' },
  { name: 'Cancer', abbr: 'CN', glyph: '♋' },
  { name: 'Leo', abbr: 'LE', glyph: '♌' },
  { name: 'Virgo', abbr: 'VI', glyph: '♍' },
  { name: 'Libra', abbr: 'LI', glyph: '♎' },
  { name: 'Scorpio', abbr: 'SC', glyph: '♏' },
  { name: 'Sagittarius', abbr: 'SG', glyph: '♐' },
  { name: 'Capricorn', abbr: 'CP', glyph: '♑' },
  { name: 'Aquarius', abbr: 'AQ', glyph: '♒' },
  { name: 'Pisces', abbr: 'PI', glyph: '♓' }
]

// South Indian chart has houses in FIXED positions (clockwise from top-center-right)
// Signs rotate based on where the ascendant sign is placed
// Traditional 4x4 grid layout:
//    [11] [12] [1]  [2]
//    [10] [ CENTER ] [3]
//    [9]  [ CENTER ] [4]
//    [8]  [7]  [6]  [5]
const HOUSE_POSITIONS: Record<number, { row: number; col: number; label: string }> = {
  1: { row: 0, col: 2, label: '1' },   // Top row, 3rd column
  2: { row: 0, col: 3, label: '2' },   // Top row, 4th column
  3: { row: 1, col: 3, label: '3' },   // 2nd row, 4th column
  4: { row: 2, col: 3, label: '4' },   // 3rd row, 4th column
  5: { row: 3, col: 3, label: '5' },   // Bottom row, 4th column
  6: { row: 3, col: 2, label: '6' },   // Bottom row, 3rd column
  7: { row: 3, col: 1, label: '7' },   // Bottom row, 2nd column
  8: { row: 3, col: 0, label: '8' },   // Bottom row, 1st column
  9: { row: 2, col: 0, label: '9' },   // 3rd row, 1st column
  10: { row: 1, col: 0, label: '10' }, // 2nd row, 1st column
  11: { row: 0, col: 0, label: '11' }, // Top row, 1st column
  12: { row: 0, col: 1, label: '12' }  // Top row, 2nd column
}

export function SouthIndianChart({ chartData, width = 600, height = 600 }: SouthIndianChartProps) {
  if (!chartData || !chartData.houses || !chartData.planets || !chartData.ascendant) {
    return (
      <div className="flex items-center justify-center p-8 text-gray-500">
        <p>Chart data incomplete</p>
      </div>
    )
  }

  // In South Indian chart, signs are in fixed positions (clockwise from bottom-left)
  // We need to map which sign is in which position based on ascendant
  const lagnaSignNum = chartData.ascendant.sign_num

  // Create sign-to-position mapping
  const signPositions: Record<number, number> = {}
  for (let i = 0; i < 12; i++) {
    const signNum = (lagnaSignNum + i) % 12
    signPositions[signNum] = i + 1  // Position 1-12
  }

  // Group planets by their sign
  const planetsBySign: Record<number, Array<{name: string, symbol: string, retrograde: boolean}>> = {}
  Object.entries(chartData.planets).forEach(([name, data]) => {
    const signNum = data.sign_num
    if (!planetsBySign[signNum]) {
      planetsBySign[signNum] = []
    }
    planetsBySign[signNum].push({
      name,
      symbol: PLANET_SYMBOLS[name] || name[0],
      retrograde: data.retrograde || false
    })
  })

  const boxSize = Math.min(width, height) * 0.9
  const centerX = width / 2
  const centerY = height / 2
  const left = centerX - boxSize / 2
  const top = centerY - boxSize / 2

  // 4x4 grid: each cell is boxSize/4
  const cellSize = boxSize / 4

  return (
    <div className="flex flex-col items-center p-4">
      <svg width={width} height={height + 80} viewBox={`0 0 ${width} ${height + 80}`}>
        {/* Main outer border */}
        <rect
          x={left}
          y={top}
          width={boxSize}
          height={boxSize}
          fill="#fef3e2"
          stroke="#c17817"
          strokeWidth="3"
          rx="8"
        />

        {/* Draw 4x4 grid lines */}
        {/* Vertical lines */}
        {[1, 2, 3].map((i) => (
          <line
            key={`v${i}`}
            x1={left + i * cellSize}
            y1={top}
            x2={left + i * cellSize}
            y2={top + boxSize}
            stroke="#c17817"
            strokeWidth="2"
          />
        ))}

        {/* Horizontal lines */}
        {[1, 2, 3].map((i) => (
          <line
            key={`h${i}`}
            x1={left}
            y1={top + i * cellSize}
            x2={left + boxSize}
            y2={top + i * cellSize}
            stroke="#c17817"
            strokeWidth="2"
          />
        ))}

        {/* Center rectangle highlight (optional subtle fill) */}
        <rect
          x={left + cellSize}
          y={top + cellSize}
          width={cellSize * 2}
          height={cellSize * 2}
          fill="#fff9e6"
          stroke="none"
        />

        {/* Render all 12 zodiac signs in their fixed positions */}
        {ZODIAC_SIGNS.map((zodiacSign, zodiacIdx) => {
          const position = signPositions[zodiacIdx]
          if (!position || !HOUSE_POSITIONS[position]) return null

          const { row, col } = HOUSE_POSITIONS[position]
          const cellX = left + col * cellSize
          const cellY = top + row * cellSize
          const centerCellX = cellX + cellSize / 2
          const centerCellY = cellY + cellSize / 2

          // Get planets in this sign
          const planetsInSign = planetsBySign[zodiacIdx] || []

          // Calculate which house this sign represents
          const houseNum = position
          const isAscendant = houseNum === 1
          const isKendra = [1, 4, 7, 10].includes(houseNum)
          const isTrikona = [5, 9].includes(houseNum)
          const houseColor = isAscendant ? '#7c3aed' : (isKendra ? '#d97706' : (isTrikona ? '#2563eb' : '#1f2937'))

          return (
            <g key={zodiacIdx}>
              {/* House number (small, in corner) */}
              <text
                x={centerCellX}
                y={centerCellY - 32}
                textAnchor="middle"
                fontSize="12"
                fontWeight="700"
                fill={houseColor}
                style={{ fontFamily: 'system-ui, -apple-system, sans-serif' }}
              >
                H{houseNum}
              </text>

              {/* Sign symbol and abbreviation */}
              <text
                x={centerCellX}
                y={centerCellY - 12}
                textAnchor="middle"
                fontSize="15"
                fontWeight="600"
                fill="#374151"
                style={{ fontFamily: 'system-ui, -apple-system, sans-serif' }}
              >
                {zodiacSign.glyph} {zodiacSign.abbr}
              </text>

              {/* Planets in this sign */}
              {planetsInSign.map((planet, idx) => (
                <text
                  key={idx}
                  x={centerCellX}
                  y={centerCellY + 8 + (idx * 18)}
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

        {/* Ascendant label at bottom */}
        <rect
          x={centerX - 70}
          y={top + boxSize + 15}
          width={140}
          height={32}
          fill="#7c3aed"
          stroke="#5b21b6"
          strokeWidth="2"
          rx="8"
        />
        <text
          x={centerX}
          y={top + boxSize + 35}
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
      <div className="mt-12 p-4 bg-gray-50 rounded-lg border border-gray-200 w-full max-w-md">
        <p className="text-center font-bold text-lg mb-3 text-gray-800">South Indian Chart (Vedic)</p>
        <div className="text-xs text-gray-600 space-y-1">
          <p><span className="font-semibold text-jio-700">H1</span> - House 1 (Ascendant/Lagna) - Always top-center-right</p>
          <p><span className="font-semibold text-amber-700">Kendra</span> (H1,H4,H7,H10) - Angular houses (power)</p>
          <p><span className="font-semibold text-blue-700">Trikona</span> (H5,H9) - Trinal houses (dharma)</p>
          <p className="mt-2"><span className="font-semibold text-red-600">ʀ</span> = Retrograde planet</p>
          <p className="text-xs text-gray-500 mt-3 italic">
            Houses in FIXED positions (clockwise from H1). Signs rotate based on Ascendant sign.
          </p>
        </div>
      </div>
    </div>
  )
}
