'use client'

import React, { useEffect, useRef, useState } from 'react'
import { transformChartData, validateChartData } from '@/lib/chartDataTransformer'

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
  language?: 'english' | 'hindi' | 'sanskrit'
  showDegrees?: boolean
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

export function NorthIndianChart({
  chartData,
  width = 600,
  height = 600,
  language = 'english',
  showDegrees = false
}: NorthIndianChartProps) {
  const containerRef = useRef<HTMLDivElement>(null)
  const [chartInstance, setChartInstance] = useState<any>(null)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    // Validate chart data
    if (!validateChartData(chartData)) {
      setError('Invalid chart data format')
      return
    }

    // Dynamically import the master chart generator
    const loadChart = async () => {
      try {
        // Import the master version
        const NorthIndianChartMaster = (await import('@/lib/NorthIndianChartMaster')).default

        // Transform backend data to master format
        const masterData = transformChartData(chartData)

        // Create chart instance with configuration
        const instance = new NorthIndianChartMaster({
          width,
          height,
          language,
          showDegrees,
          showPlanetNames: false,  // Show planet IDs (Su, Mo, etc.) not full names
          showHouseNumbers: true,
          showSigns: true,
          showAscendantMarker: true,
          responsive: true,
          colors: {
            background: '#fefcf8',
            gradient1: '#ffffff',
            gradient2: '#f0f3bf',
            lines: '#b1792d',
            houseNumbers: '#008080',
            signs: '#444444',  // Darker for better readability
            ascendant: '#7c3aed',
            planets: {
              Su: '#FF8C00', // Dark orange (Sun)
              Mo: '#4169E1', // Royal blue (Moon)
              Ma: '#DC143C', // Crimson (Mars)
              Me: '#228B22', // Forest green (Mercury)
              Ju: '#FFD700', // Gold (Jupiter)
              Ve: '#FF1493', // Deep pink (Venus)
              Sa: '#191970', // Midnight blue (Saturn)
              Ra: '#8B4513', // Saddle brown (Rahu)
              Ke: '#A0522D', // Sienna (Ketu)
            }
          },
          fonts: {
            houseNumber: '14px Arial',
            sign: '11px Arial',  // Slightly larger for sign names
            planet: '12px Arial',  // Larger for planets
            ascendant: 'bold 12px Arial'
          }
        })

        setChartInstance(instance)

        // Render chart to container
        if (containerRef.current) {
          instance.render(containerRef.current, masterData)
        }

        setError(null)
      } catch (err) {
        console.error('Error loading North Indian Chart:', err)
        setError('Failed to load chart generator')
      }
    }

    loadChart()
  }, [chartData, width, height, language, showDegrees])

  if (!chartData || !chartData.houses || !chartData.planets || !chartData.ascendant) {
    return (
      <div className="flex items-center justify-center p-8 text-gray-500">
        <p>Chart data incomplete</p>
      </div>
    )
  }

  if (error) {
    return (
      <div className="flex items-center justify-center p-8 text-red-600">
        <p>{error}</p>
      </div>
    )
  }

  return (
    <div className="flex flex-col items-center p-4">
      {/* Chart container for master version */}
      <div ref={containerRef} className="w-full max-w-2xl" />

      {/* Legend */}
      <div className="mt-8 p-4 bg-gray-50 rounded-lg border border-gray-200 w-full max-w-md">
        <p className="text-center font-bold text-lg mb-3 text-gray-800">North Indian Chart (Vedic)</p>
        <div className="text-xs text-gray-600 space-y-1">
          <p><span className="font-semibold text-purple-700">H1</span> - House 1 (Ascendant/Lagna) - CENTER diamond</p>
          <p><span className="font-semibold">H2-H12</span> - Other houses in triangular sections around H1</p>
          <p><span className="font-semibold">Diamond layout</span> - Traditional North Indian style</p>
          <p className="mt-2"><span className="font-semibold text-red-600">R</span> = Retrograde planet</p>
          <p className="text-xs text-gray-500 mt-3 italic">
            H1 (Ascendant) is always in the center. Signs rotate based on Ascendant sign.
          </p>
        </div>
      </div>
    </div>
  )
}
