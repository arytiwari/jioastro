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

export function BirthChartNew({ chartData, width = 600, height = 600, chartType = 'D1' }: BirthChartProps) {
  // Validate chart data
  if (!chartData || !chartData.houses || !chartData.planets || !chartData.ascendant) {
    return (
      <div className="flex items-center justify-center p-8 text-gray-500">
        <p>Chart data incomplete</p>
      </div>
    )
  }

  const centerX = width / 2
  const centerY = height / 2
  const boxSize = Math.min(width, height) * 0.8

  // Square corners
  const half = boxSize / 2
  const top = centerY - half
  const bottom = centerY + half
  const left = centerX - half
  const right = centerX + half

  // Group planets by house
  const planetsByHouse: Record<number, Array<{name: string, symbol: string, sign: string, retrograde: boolean}>> = {}
  Object.entries(chartData.planets).forEach(([name, data]) => {
    if (!planetsByHouse[data.house]) {
      planetsByHouse[data.house] = []
    }
    planetsByHouse[data.house].push({
      name,
      symbol: PLANET_SYMBOLS[name] || name[0],
      sign: data.sign,
      retrograde: data.retrograde || false
    })
  })

  // Get house data for any house number
  const getHouseData = (houseNum: number) => {
    return chartData.houses.find(h => h.house_num === houseNum) || {
      house_num: houseNum,
      sign: '?',
      sign_num: 0
    }
  }

  return (
    <div className="flex flex-col items-center p-4">
      <svg width={width} height={height} className="border-0">
        {/* Outer rounded rectangle */}
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

        {/* Diagonal line 1: top-left to bottom-right */}
        <line
          x1={left}
          y1={top}
          x2={right}
          y2={bottom}
          stroke="#d68910"
          strokeWidth="2"
        />

        {/* Diagonal line 2: top-right to bottom-left */}
        <line
          x1={right}
          y1={top}
          x2={left}
          y2={bottom}
          stroke="#d68910"
          strokeWidth="2"
        />

        {/* Horizontal line through center */}
        <line
          x1={left}
          y1={centerY}
          x2={right}
          y2={centerY}
          stroke="#d68910"
          strokeWidth="2"
        />

        {/* Vertical line through center */}
        <line
          x1={centerX}
          y1={top}
          x2={centerX}
          y2={bottom}
          stroke="#d68910"
          strokeWidth="2"
        />

        {/* House 1 - TOP */}
        <text x={centerX} y={top + 30} textAnchor="middle" fontSize="20" fontWeight="bold" fill="#7c3aed">1</text>
        <text x={centerX} y={top + 50} textAnchor="middle" fontSize="12" fontWeight="600" fill="#666">
          {getHouseData(1).sign.substring(0, 3).toUpperCase()}
        </text>

        {/* House 2 - TOP RIGHT */}
        <text x={centerX + half/2} y={top + half/2 - 10} textAnchor="middle" fontSize="18" fontWeight="bold" fill="#475569">2</text>
        <text x={centerX + half/2} y={top + half/2 + 10} textAnchor="middle" fontSize="11" fontWeight="600" fill="#666">
          {getHouseData(2).sign.substring(0, 3).toUpperCase()}
        </text>

        {/* House 3 - RIGHT */}
        <text x={right - 40} y={centerY} textAnchor="middle" fontSize="18" fontWeight="bold" fill="#dc2626">3</text>
        <text x={right - 40} y={centerY + 20} textAnchor="middle" fontSize="11" fontWeight="600" fill="#666">
          {getHouseData(3).sign.substring(0, 3).toUpperCase()}
        </text>

        {/* House 4 - BOTTOM RIGHT */}
        <text x={centerX + half/2} y={centerY + half/2 + 10} textAnchor="middle" fontSize="18" fontWeight="bold" fill="#d97706">4</text>
        <text x={centerX + half/2} y={centerY + half/2 + 30} textAnchor="middle" fontSize="11" fontWeight="600" fill="#666">
          {getHouseData(4).sign.substring(0, 3).toUpperCase()}
        </text>

        {/* House 5 - BOTTOM */}
        <text x={centerX} y={bottom - 30} textAnchor="middle" fontSize="18" fontWeight="bold" fill="#475569">5</text>
        <text x={centerX} y={bottom - 10} textAnchor="middle" fontSize="11" fontWeight="600" fill="#666">
          {getHouseData(5).sign.substring(0, 3).toUpperCase()}
        </text>

        {/* House 6 - BOTTOM LEFT */}
        <text x={centerX - half/2} y={centerY + half/2 + 10} textAnchor="middle" fontSize="18" fontWeight="bold" fill="#475569">6</text>
        <text x={centerX - half/2} y={centerY + half/2 + 30} textAnchor="middle" fontSize="11" fontWeight="600" fill="#666">
          {getHouseData(6).sign.substring(0, 3).toUpperCase()}
        </text>

        {/* House 7 - LEFT */}
        <text x={left + 40} y={centerY} textAnchor="middle" fontSize="18" fontWeight="bold" fill="#d97706">7</text>
        <text x={left + 40} y={centerY + 20} textAnchor="middle" fontSize="11" fontWeight="600" fill="#666">
          {getHouseData(7).sign.substring(0, 3).toUpperCase()}
        </text>

        {/* House 8 - TOP LEFT */}
        <text x={centerX - half/2} y={top + half/2 - 10} textAnchor="middle" fontSize="18" fontWeight="bold" fill="#475569">8</text>
        <text x={centerX - half/2} y={top + half/2 + 10} textAnchor="middle" fontSize="11" fontWeight="600" fill="#666">
          {getHouseData(8).sign.substring(0, 3).toUpperCase()}
        </text>

        {/* House 9 - CENTER TOP LEFT */}
        <text x={centerX - half/4} y={centerY - half/4 + 5} textAnchor="middle" fontSize="18" fontWeight="bold" fill="#2563eb">9</text>
        <text x={centerX - half/4} y={centerY - half/4 + 25} textAnchor="middle" fontSize="11" fontWeight="600" fill="#666">
          {getHouseData(9).sign.substring(0, 3).toUpperCase()}
        </text>

        {/* House 10 - CENTER TOP RIGHT */}
        <text x={centerX + half/4} y={centerY - half/4 + 5} textAnchor="middle" fontSize="18" fontWeight="bold" fill="#d97706">10</text>
        <text x={centerX + half/4} y={centerY - half/4 + 25} textAnchor="middle" fontSize="11" fontWeight="600" fill="#666">
          {getHouseData(10).sign.substring(0, 3).toUpperCase()}
        </text>

        {/* House 11 - CENTER BOTTOM RIGHT */}
        <text x={centerX + half/4} y={centerY + half/4 + 5} textAnchor="middle" fontSize="18" fontWeight="bold" fill="#475569">11</text>
        <text x={centerX + half/4} y={centerY + half/4 + 25} textAnchor="middle" fontSize="11" fontWeight="600" fill="#666">
          {getHouseData(11).sign.substring(0, 3).toUpperCase()}
        </text>

        {/* House 12 - CENTER BOTTOM LEFT */}
        <text x={centerX - half/4} y={centerY + half/4 + 5} textAnchor="middle" fontSize="18" fontWeight="bold" fill="#475569">12</text>
        <text x={centerX - half/4} y={centerY + half/4 + 25} textAnchor="middle" fontSize="11" fontWeight="600" fill="#666">
          {getHouseData(12).sign.substring(0, 3).toUpperCase()}
        </text>

        {/* Planets - simplified positioning */}
        {Object.entries(planetsByHouse).map(([houseNum, planets]) => {
          const house = parseInt(houseNum)
          let x = centerX, y = centerY

          // Position planets based on house
          if (house === 1) { x = centerX; y = top + 70 }
          else if (house === 2) { x = centerX + half/2; y = top + half/2 + 30 }
          else if (house === 3) { x = right - 40; y = centerY + 40 }
          else if (house === 4) { x = centerX + half/2; y = centerY + half/2 + 50 }
          else if (house === 5) { x = centerX; y = bottom - 50 }
          else if (house === 6) { x = centerX - half/2; y = centerY + half/2 + 50 }
          else if (house === 7) { x = left + 40; y = centerY + 40 }
          else if (house === 8) { x = centerX - half/2; y = top + half/2 + 30 }
          else if (house === 9) { x = centerX - half/4; y = centerY - half/4 + 45 }
          else if (house === 10) { x = centerX + half/4; y = centerY - half/4 + 45 }
          else if (house === 11) { x = centerX + half/4; y = centerY + half/4 + 45 }
          else if (house === 12) { x = centerX - half/4; y = centerY + half/4 + 45 }

          return (
            <g key={houseNum}>
              {planets.map((planet, idx) => (
                <text
                  key={idx}
                  x={x}
                  y={y + (idx * 20)}
                  textAnchor="middle"
                  fontSize="16"
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

        {/* Ascendant label */}
        <rect
          x={centerX - 70}
          y={top - 35}
          width={140}
          height={30}
          fill="#7c3aed"
          stroke="#5b21b6"
          strokeWidth="2"
          rx="6"
        />
        <text
          x={centerX}
          y={top - 13}
          textAnchor="middle"
          fontSize="14"
          fontWeight="bold"
          fill="#ffffff"
        >
          ASC: {chartData.ascendant.sign.toUpperCase()}
        </text>
      </svg>

      {/* Legend */}
      <div className="mt-6 p-4 bg-gray-50 rounded-lg border border-gray-200 w-full max-w-md">
        <p className="text-center font-bold text-lg mb-3 text-gray-800">North Indian Chart (Vedic)</p>
        <div className="text-xs text-gray-600 space-y-1">
          <p><span className="font-semibold">House 1</span> (Top) - Ascendant/Lagna (Self, Personality)</p>
          <p><span className="font-semibold">Kendra Houses</span> (1,4,7,10) - Angular (Strength)</p>
          <p><span className="font-semibold">Trikona Houses</span> (5,9) - Trinal (Fortune)</p>
          <p className="mt-2"><span className="font-semibold text-red-600">ʀ</span> = Retrograde motion</p>
        </div>
      </div>
    </div>
  )
}
