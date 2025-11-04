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

// South Indian chart has houses in fixed positions
// Signs rotate based on where the ascendant sign is placed
const HOUSE_POSITIONS: Record<number, { x: number; y: number; label: string }> = {
  1: { x: 0.25, y: 0.75, label: '1' },   // Bottom-left
  2: { x: 0.25, y: 0.50, label: '2' },   // Mid-left
  3: { x: 0.25, y: 0.25, label: '3' },   // Top-left
  4: { x: 0.50, y: 0.25, label: '4' },   // Top-mid
  5: { x: 0.75, y: 0.25, label: '5' },   // Top-right
  6: { x: 0.75, y: 0.50, label: '6' },   // Mid-right
  7: { x: 0.75, y: 0.75, label: '7' },   // Bottom-right
  8: { x: 0.50, y: 0.75, label: '8' },   // Bottom-mid
  9: { x: 0.37, y: 0.625, label: '9' },  // Inner bottom-left
  10: { x: 0.37, y: 0.375, label: '10' }, // Inner top-left
  11: { x: 0.63, y: 0.375, label: '11' }, // Inner top-right
  12: { x: 0.63, y: 0.625, label: '12' }  // Inner bottom-right
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
        {/* Background square */}
        <rect
          x={left}
          y={top}
          width={boxSize}
          height={boxSize}
          fill="#fef3e2"
          stroke="#c17817"
          strokeWidth="4"
          rx="12"
        />

        {/* Diagonal cross lines (X) */}
        <line x1={left} y1={top} x2={right} y2={bottom} stroke="#c17817" strokeWidth="2.5" />
        <line x1={right} y1={top} x2={left} y2={bottom} stroke="#c17817" strokeWidth="2.5" />

        {/* Vertical and horizontal lines */}
        <line x1={left} y1={centerY} x2={right} y2={centerY} stroke="#c17817" strokeWidth="2.5" />
        <line x1={centerX} y1={top} x2={centerX} y2={bottom} stroke="#c17817" strokeWidth="2.5" />

        {/* Render all 12 zodiac signs in their fixed positions */}
        {ZODIAC_SIGNS.map((zodiacSign, zodiacIdx) => {
          const position = signPositions[zodiacIdx]
          if (!position || !HOUSE_POSITIONS[position]) return null

          const { x: fx, y: fy } = HOUSE_POSITIONS[position]
          const x = left + (boxSize * fx)
          const y = top + (boxSize * fy)

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
                x={x}
                y={y - 42}
                textAnchor="middle"
                fontSize="13"
                fontWeight="700"
                fill={houseColor}
                style={{ fontFamily: 'system-ui, -apple-system, sans-serif' }}
              >
                H{houseNum}
              </text>

              {/* Sign symbol and abbreviation */}
              <text
                x={x}
                y={y - 20}
                textAnchor="middle"
                fontSize="17"
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
                  x={x}
                  y={y + 4 + (idx * 20)}
                  textAnchor="middle"
                  fontSize="16"
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
          y={bottom + 15}
          width={140}
          height={32}
          fill="#7c3aed"
          stroke="#5b21b6"
          strokeWidth="2"
          rx="8"
        />
        <text
          x={centerX}
          y={bottom + 35}
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
        <p className="text-center font-bold text-lg mb-3 text-gray-800">South Indian Chart (Vedic)</p>
        <div className="text-xs text-gray-600 space-y-1">
          <p><span className="font-semibold text-jio-700">H1</span> - House 1 (Ascendant/Lagna)</p>
          <p><span className="font-semibold text-amber-700">Kendra</span> (H1,H4,H7,H10) - Angular houses</p>
          <p><span className="font-semibold text-blue-700">Trikona</span> (H5,H9) - Trinal houses</p>
          <p className="mt-2"><span className="font-semibold text-red-600">ʀ</span> = Retrograde planet</p>
          <p className="text-xs text-gray-500 mt-3 italic">
            Zodiac signs in fixed positions, houses rotate with Ascendant
          </p>
        </div>
      </div>
    </div>
  )
}
