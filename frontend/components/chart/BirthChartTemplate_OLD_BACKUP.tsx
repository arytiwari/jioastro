'use client'

export interface Planet {
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

export interface ChartData {
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

export interface BirthChartProps {
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

const PLANET_ABBREV: Record<string, string> = {
  Sun: 'Su',
  Moon: 'Mo',
  Mars: 'Ma',
  Mercury: 'Me',
  Jupiter: 'Ju',
  Venus: 'Ve',
  Saturn: 'Sa',
  Rahu: 'Ra',
  Ketu: 'Ke'
}

const ZODIAC_SIGNS = [
  { name: 'Aries', abbr: 'ARI' },      // 0
  { name: 'Taurus', abbr: 'TAU' },     // 1
  { name: 'Gemini', abbr: 'GEM' },     // 2
  { name: 'Cancer', abbr: 'CAN' },     // 3
  { name: 'Leo', abbr: 'LEO' },        // 4
  { name: 'Virgo', abbr: 'VIR' },      // 5
  { name: 'Libra', abbr: 'LIB' },      // 6
  { name: 'Scorpio', abbr: 'SCO' },    // 7
  { name: 'Sagittarius', abbr: 'SAG' },// 8
  { name: 'Capricorn', abbr: 'CAP' },  // 9
  { name: 'Aquarius', abbr: 'AQU' },   // 10
  { name: 'Pisces', abbr: 'PIS' }      // 11
]

type LayoutAnchor = {
  label: [number, number]
  sign: [number, number]
  planets: [number, number]
  anchor?: 'start' | 'middle' | 'end'
}

const HOUSE_LAYOUT: Record<number, LayoutAnchor> = {
  1: { label: [0.5, 0.08], sign: [0.5, 0.15], planets: [0.5, 0.22] },
  2: { label: [0.78, 0.22], sign: [0.78, 0.29], planets: [0.78, 0.36] },
  3: { label: [0.92, 0.5], sign: [0.88, 0.57], planets: [0.85, 0.64], anchor: 'end' },
  4: { label: [0.78, 0.78], sign: [0.78, 0.85], planets: [0.78, 0.92], anchor: 'end' },
  5: { label: [0.5, 0.92], sign: [0.5, 0.96], planets: [0.5, 0.88] },
  6: { label: [0.22, 0.78], sign: [0.22, 0.85], planets: [0.22, 0.92], anchor: 'start' },
  7: { label: [0.08, 0.5], sign: [0.12, 0.57], planets: [0.15, 0.64], anchor: 'start' },
  8: { label: [0.22, 0.22], sign: [0.22, 0.29], planets: [0.22, 0.36], anchor: 'start' },
  9: { label: [0.35, 0.35], sign: [0.35, 0.42], planets: [0.35, 0.49] },
  10: { label: [0.65, 0.35], sign: [0.65, 0.42], planets: [0.65, 0.49] },
  11: { label: [0.65, 0.65], sign: [0.65, 0.72], planets: [0.65, 0.79] },
  12: { label: [0.35, 0.65], sign: [0.35, 0.72], planets: [0.35, 0.79] }
}

const STROKE_COLOR = '#b1792d'
const STROKE_WIDTH = 6
const INNER_STROKE_WIDTH = 4
const TEXT_COLOR = '#654321'
const SUBTEXT_COLOR = '#8a5f2a'
const RETROGRADE_COLOR = '#a63a2a'

export function BirthChartTemplate({ chartData, width = 600, height = 600, chartType = 'D1' }: BirthChartProps) {
  if (!chartData || !chartData.houses || !chartData.planets || !chartData.ascendant) {
    return (
      <div className="flex items-center justify-center p-8 text-gray-500">
        <p>Chart data incomplete</p>
      </div>
    )
  }

  const chartSize = Math.min(width, height) * 0.82
  const offsetX = (width - chartSize) / 2
  const offsetY = (height - chartSize) / 2
  const centerX = offsetX + chartSize / 2
  const centerY = offsetY + chartSize / 2

  const corners = {
    topLeft: { x: offsetX, y: offsetY },
    topRight: { x: offsetX + chartSize, y: offsetY },
    bottomLeft: { x: offsetX, y: offsetY + chartSize },
    bottomRight: { x: offsetX + chartSize, y: offsetY + chartSize }
  }

  const midpoints = {
    top: { x: centerX, y: offsetY },
    right: { x: offsetX + chartSize, y: centerY },
    bottom: { x: centerX, y: offsetY + chartSize },
    left: { x: offsetX, y: centerY }
  }

  const lagnaSignNum = chartData.ascendant.sign_num
  const signInHouse = (houseNum: number) => {
    const idx = (lagnaSignNum + (houseNum - 1)) % 12
    return ZODIAC_SIGNS[idx]
  }

  const houseMap = new Map<number, ChartData['houses'][number]>()
  chartData.houses.forEach((house) => {
    houseMap.set(house.house_num, house)
  })

  const planetsByHouse: Record<number, Array<{ name: string; symbol: string; retrograde: boolean }>> = {}
  Object.entries(chartData.planets).forEach(([name, data]) => {
    if (!planetsByHouse[data.house]) {
      planetsByHouse[data.house] = []
    }
    planetsByHouse[data.house].push({
      name,
      symbol: PLANET_SYMBOLS[name] || name.charAt(0),
      retrograde: data.retrograde ?? false
    })
  })

  const lineSpacing = chartSize * 0.048

  return (
    <div className="flex flex-col items-center gap-4 p-4" aria-label={`North Indian ${chartType} birth chart`}>
      <svg width={width} height={height} role="img" shapeRendering="geometricPrecision">
        <rect
          x={offsetX}
          y={offsetY}
          width={chartSize}
          height={chartSize}
          fill="#ffffff"
          stroke={STROKE_COLOR}
          strokeWidth={STROKE_WIDTH}
          strokeLinejoin="miter"
        />

        <line
          x1={corners.topLeft.x}
          y1={corners.topLeft.y}
          x2={corners.bottomRight.x}
          y2={corners.bottomRight.y}
          stroke={STROKE_COLOR}
          strokeWidth={INNER_STROKE_WIDTH}
          strokeLinecap="square"
        />
        <line
          x1={corners.topRight.x}
          y1={corners.topRight.y}
          x2={corners.bottomLeft.x}
          y2={corners.bottomLeft.y}
          stroke={STROKE_COLOR}
          strokeWidth={INNER_STROKE_WIDTH}
          strokeLinecap="square"
        />

        <line
          x1={midpoints.top.x}
          y1={midpoints.top.y}
          x2={midpoints.right.x}
          y2={midpoints.right.y}
          stroke={STROKE_COLOR}
          strokeWidth={INNER_STROKE_WIDTH}
          strokeLinecap="square"
        />
        <line
          x1={midpoints.right.x}
          y1={midpoints.right.y}
          x2={midpoints.bottom.x}
          y2={midpoints.bottom.y}
          stroke={STROKE_COLOR}
          strokeWidth={INNER_STROKE_WIDTH}
          strokeLinecap="square"
        />
        <line
          x1={midpoints.bottom.x}
          y1={midpoints.bottom.y}
          x2={midpoints.left.x}
          y2={midpoints.left.y}
          stroke={STROKE_COLOR}
          strokeWidth={INNER_STROKE_WIDTH}
          strokeLinecap="square"
        />
        <line
          x1={midpoints.left.x}
          y1={midpoints.left.y}
          x2={midpoints.top.x}
          y2={midpoints.top.y}
          stroke={STROKE_COLOR}
          strokeWidth={INNER_STROKE_WIDTH}
          strokeLinecap="square"
        />

        {[...Array(12)].map((_, idx) => {
          const houseNum = idx + 1
          const layout = HOUSE_LAYOUT[houseNum]
          const anchor = layout.anchor ?? 'middle'
          const house = houseMap.get(houseNum)
          const sign = house ? house.sign.substring(0, 3).toUpperCase() : signInHouse(houseNum).abbr
          const signX = offsetX + chartSize * layout.sign[0]
          const signY = offsetY + chartSize * layout.sign[1]
          const labelX = offsetX + chartSize * layout.label[0]
          const labelY = offsetY + chartSize * layout.label[1]
          const planetStartX = offsetX + chartSize * layout.planets[0]
          const planetStartY = offsetY + chartSize * layout.planets[1]
          const planets = planetsByHouse[houseNum] ?? []

          return (
            <g key={houseNum}>
              <text
                x={labelX}
                y={labelY}
                textAnchor={anchor}
                fontSize={chartSize * 0.065}
                fontWeight="700"
                fill={TEXT_COLOR}
              >
                {houseNum}
              </text>

              <text
                x={signX}
                y={signY}
                textAnchor={anchor}
                fontSize={chartSize * 0.05}
                fontWeight="600"
                fill={SUBTEXT_COLOR}
              >
                {sign}
              </text>

              {planets.map((planet, planetIdx) => (
                <g key={`${houseNum}-${planet.name}-${planetIdx}`}>
                  <text
                    x={planetStartX}
                    y={planetStartY + planetIdx * lineSpacing}
                    textAnchor={anchor}
                    fontSize={chartSize * 0.048}
                    fontWeight="700"
                    fill={planet.retrograde ? RETROGRADE_COLOR : TEXT_COLOR}
                    style={{ fontFamily: 'system-ui, -apple-system, sans-serif' }}
                  >
                    {planet.symbol} {PLANET_ABBREV[planet.name] || planet.name.substring(0, 2)}
                    {planet.retrograde ? 'ʀ' : ''}
                  </text>
                </g>
              ))}
            </g>
          )
        })}
      </svg>

      <div className="text-sm text-neutral-600 text-center">
        Ascendant: <span className="font-semibold text-neutral-800">{chartData.ascendant.sign.toUpperCase()}</span>
      </div>

      {/* Planet Legend */}
      <div className="mt-4 p-4 bg-gray-50 rounded-lg border border-gray-200 w-full max-w-2xl">
        <p className="text-center font-bold text-sm mb-3 text-gray-800">Planet Key</p>
        <div className="grid grid-cols-3 gap-2 text-xs">
          {Object.entries(PLANET_SYMBOLS).map(([name, symbol]) => (
            <div key={name} className="flex items-center gap-2">
              <span className="text-lg font-bold">{symbol}</span>
              <span className="font-semibold">{PLANET_ABBREV[name]}</span>
              <span className="text-gray-600">= {name}</span>
            </div>
          ))}
        </div>
        <p className="mt-3 text-xs text-gray-600 text-center">
          <span className="font-semibold text-red-600">ʀ</span> = Retrograde planet
        </p>
      </div>
    </div>
  )
}
