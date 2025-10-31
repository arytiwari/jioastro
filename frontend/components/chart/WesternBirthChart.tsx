'use client'

import React, { useEffect, useRef } from 'react'

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

interface WesternBirthChartProps {
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
  { name: 'Aries', glyph: '♈' },
  { name: 'Taurus', glyph: '♉' },
  { name: 'Gemini', glyph: '♊' },
  { name: 'Cancer', glyph: '♋' },
  { name: 'Leo', glyph: '♌' },
  { name: 'Virgo', glyph: '♍' },
  { name: 'Libra', glyph: '♎' },
  { name: 'Scorpio', glyph: '♏' },
  { name: 'Sagittarius', glyph: '♐' },
  { name: 'Capricorn', glyph: '♑' },
  { name: 'Aquarius', glyph: '♒' },
  { name: 'Pisces', glyph: '♓' }
]

export function WesternBirthChart({ chartData, width = 720, height = 720 }: WesternBirthChartProps) {
  const canvasRef = useRef<HTMLCanvasElement>(null)

  useEffect(() => {
    if (!chartData || !chartData.houses || !chartData.planets || !chartData.ascendant) {
      return
    }

    const canvas = canvasRef.current
    if (!canvas) return

    const ctx = canvas.getContext('2d')
    if (!ctx) return

    const size = canvas.width
    const center = size / 2

    // Helper function to convert degrees to radians (0° = East, going counter-clockwise)
    const toRad = (deg: number) => (deg - 90) * (Math.PI / 180)

    // Calculate ascendant degree (traditionally at 9 o'clock position = 180°)
    const ascendantDegree = 180

    // Draw a ring
    function drawRing(radius: number, thickness: number, fillStyle: string) {
      ctx.save()
      ctx.beginPath()
      ctx.arc(center, center, radius, 0, Math.PI * 2)
      ctx.strokeStyle = 'transparent'
      ctx.lineWidth = 1
      ctx.fillStyle = fillStyle
      ctx.fill()
      ctx.restore()

      if (thickness > 0) {
        ctx.save()
        ctx.beginPath()
        ctx.arc(center, center, radius, 0, Math.PI * 2)
        ctx.lineWidth = thickness
        ctx.strokeStyle = '#3f2c1c'
        ctx.stroke()
        ctx.restore()
      }
    }

    // Draw house division lines (12 equal segments)
    function drawHouseLines() {
      ctx.save()
      ctx.lineWidth = 2.4
      ctx.strokeStyle = 'rgba(63, 44, 28, 0.6)'
      for (let i = 0; i < 12; i++) {
        const angle = (Math.PI * 2 * i) / 12
        const x = center + Math.cos(angle) * 360
        const y = center + Math.sin(angle) * 360
        ctx.beginPath()
        ctx.moveTo(center, center)
        ctx.lineTo(x, y)
        ctx.stroke()
      }
      ctx.restore()
    }

    // Draw zodiac slices with alternating colors
    function drawZodiacSlices() {
      // Calculate starting angle based on ascendant
      const ascSignNum = chartData.ascendant.sign_num
      const startAngle = toRad(ascendantDegree) - (ascSignNum * Math.PI / 6)

      for (let i = 0; i < 12; i++) {
        const start = startAngle + (Math.PI * 2 * i) / 12
        const end = startAngle + (Math.PI * 2 * (i + 1)) / 12
        ctx.beginPath()
        ctx.moveTo(center, center)
        ctx.arc(center, center, 390, start, end)
        ctx.closePath()
        ctx.fillStyle = i % 2 === 0 ? 'rgba(255, 255, 255, 0.72)' : 'rgba(248, 229, 198, 0.76)'
        ctx.fill()
      }
    }

    // Draw house numbers
    function drawHouseNumbers() {
      ctx.save()
      ctx.fillStyle = 'rgba(63, 44, 28, 0.85)'
      ctx.font = '600 22px "Inter", "Helvetica Neue", Arial, sans-serif'
      ctx.textAlign = 'center'
      ctx.textBaseline = 'middle'

      for (let i = 0; i < 12; i++) {
        // Start from ascendant (house 1 at 180°) and go counter-clockwise
        const angle = toRad(ascendantDegree) - (i * Math.PI / 6)
        const x = center + Math.cos(angle) * 235
        const y = center + Math.sin(angle) * 235
        ctx.fillText(String(i + 1), x, y)
      }
      ctx.restore()
    }

    // Draw zodiac glyphs
    function drawZodiacGlyphs() {
      ctx.save()
      ctx.fillStyle = 'rgba(42, 26, 17, 0.85)'
      ctx.font = '700 44px "Noto Sans Symbols 2", "Segoe UI Symbol", sans-serif'
      ctx.textAlign = 'center'
      ctx.textBaseline = 'middle'

      const ascSignNum = chartData.ascendant.sign_num
      const startAngle = toRad(ascendantDegree) - (ascSignNum * Math.PI / 6)

      ZODIAC_SIGNS.forEach((sign, index) => {
        const angle = startAngle + ((index + 0.5) * Math.PI * 2) / 12
        const x = center + Math.cos(angle) * 325
        const y = center + Math.sin(angle) * 325
        ctx.fillText(sign.glyph, x, y)
      })
      ctx.restore()
    }

    // Draw planets
    function drawPlanets() {
      ctx.save()
      ctx.font = '600 28px "Noto Sans Symbols 2", "Segoe UI Symbol", sans-serif'
      ctx.textAlign = 'center'
      ctx.textBaseline = 'middle'

      Object.entries(chartData.planets).forEach(([name, planetData]) => {
        // Calculate planet's absolute degree position
        // Each sign is 30 degrees, position is within that sign
        const absoluteDegree = (planetData.sign_num * 30) + planetData.position

        // Adjust for ascendant being at 180° (9 o'clock)
        const adjustedDegree = ascendantDegree - (chartData.ascendant.sign_num * 30) + absoluteDegree
        const angle = toRad(adjustedDegree)

        const r = 180
        const x = center + Math.cos(angle) * r
        const y = center + Math.sin(angle) * r

        // Draw planet circle background
        ctx.beginPath()
        ctx.arc(x, y, 22, 0, Math.PI * 2)
        ctx.fillStyle = 'rgba(255, 255, 255, 0.92)'
        ctx.fill()
        ctx.lineWidth = 2
        ctx.strokeStyle = planetData.retrograde ? 'rgba(220, 38, 38, 0.6)' : 'rgba(63, 44, 28, 0.4)'
        ctx.stroke()

        // Draw planet symbol
        ctx.fillStyle = planetData.retrograde ? '#dc2626' : '#2a1a11'
        const symbol = PLANET_SYMBOLS[name] || name[0]
        ctx.fillText(symbol, x, y)
      })
      ctx.restore()
    }

    // Draw zodiac sign names around the outer edge
    function drawRadialLabels() {
      ctx.save()
      ctx.fillStyle = 'rgba(63, 44, 28, 0.7)'
      ctx.font = '500 16px "Inter", "Helvetica Neue", Arial, sans-serif'
      ctx.textAlign = 'center'
      ctx.textBaseline = 'middle'

      const ascSignNum = chartData.ascendant.sign_num
      const startAngle = toRad(ascendantDegree) - (ascSignNum * Math.PI / 6)

      ZODIAC_SIGNS.forEach((sign, index) => {
        const angle = startAngle + ((index + 0.5) * Math.PI * 2) / 12
        const x = center + Math.cos(angle) * 420
        const y = center + Math.sin(angle) * 420
        ctx.fillText(sign.name, x, y)
      })
      ctx.restore()
    }

    // Main drawing function
    function drawChart() {
      ctx.clearRect(0, 0, size, size)

      // Draw outer and inner rings
      drawRing(420, 10, 'rgba(255, 255, 255, 0.75)')
      drawRing(300, 8, '#f4e3c5')

      // Draw all elements
      drawZodiacSlices()
      drawHouseLines()
      drawHouseNumbers()
      drawZodiacGlyphs()
      drawPlanets()
      drawRadialLabels()

      // Draw center circle with label
      ctx.save()
      ctx.beginPath()
      ctx.arc(center, center, 110, 0, Math.PI * 2)
      ctx.fillStyle = 'rgba(255, 255, 255, 0.94)'
      ctx.fill()
      ctx.lineWidth = 1.4
      ctx.strokeStyle = 'rgba(63, 44, 28, 0.35)'
      ctx.stroke()

      ctx.fillStyle = 'rgba(42, 26, 17, 0.82)'
      ctx.font = '600 20px "Inter", "Helvetica Neue", Arial, sans-serif'
      ctx.textAlign = 'center'
      ctx.textBaseline = 'middle'
      ctx.fillText('Vedic Birth Chart', center, center - 12)
      ctx.font = '500 16px "Inter", "Helvetica Neue", Arial, sans-serif'
      ctx.fillText(`ASC: ${chartData.ascendant.sign}`, center, center + 12)
      ctx.restore()
    }

    drawChart()
  }, [chartData, width, height])

  if (!chartData || !chartData.houses || !chartData.planets || !chartData.ascendant) {
    return (
      <div className="flex items-center justify-center p-8 text-gray-500">
        <p>Chart data incomplete</p>
      </div>
    )
  }

  return (
    <div className="flex flex-col items-center p-4">
      <canvas
        ref={canvasRef}
        width={900}
        height={900}
        style={{
          width: `${width}px`,
          height: `${height}px`,
          filter: 'drop-shadow(0 22px 55px rgba(0, 0, 0, 0.18))',
          borderRadius: '24px',
          background: 'rgba(255, 255, 255, 0.96)'
        }}
        role="img"
        aria-label="Circular birth chart with zodiac houses"
      />

      {/* Legend */}
      <div className="mt-6 p-4 bg-gray-50 rounded-lg border border-gray-200 w-full max-w-md">
        <p className="text-center font-bold text-lg mb-3 text-gray-800">Western Style Chart (Vedic Data)</p>
        <div className="text-xs text-gray-600 space-y-1">
          <p><span className="font-semibold">House 1</span> (9 o'clock position) - Ascendant/Lagna</p>
          <p><span className="font-semibold">Houses</span> proceed counter-clockwise from Ascendant</p>
          <p><span className="font-semibold">Zodiac signs</span> rotate with Ascendant position</p>
          <p className="mt-2"><span className="font-semibold text-red-600">Red outline</span> = Retrograde planet</p>
          <p className="text-xs text-gray-500 mt-3 italic">
            Circular Western layout displaying Vedic astrological data
          </p>
        </div>
      </div>
    </div>
  )
}
