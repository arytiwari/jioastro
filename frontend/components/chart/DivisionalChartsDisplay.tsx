/**
 * DivisionalChartsDisplay Component
 * Displays all divisional charts (D2-D60) with detailed analysis
 */

'use client'

import { useState } from 'react'
import { Tabs, TabsList, TabsTrigger, TabsContent } from '@/components/ui/tabs'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { SouthIndianChart } from './SouthIndianChart'
import { PlanetaryPositionsTable } from './PlanetaryPositionsTable'

interface DivisionalChartData {
  chart_type: string
  division: number
  purpose: string
  description?: string
  ascendant: {
    sign: string
    sign_num: number
    degree: number
    house: number
  }
  planets: Record<string, {
    sign: string
    sign_num: number
    degree: number
    house: number
    retrograde?: boolean
    nakshatra?: {
      name: string
      pada: number
    }
  }>
  houses: Array<{
    house_num: number
    sign: string
    sign_num: number
  }>
}

interface DivisionalChartsDisplayProps {
  divisionalCharts: Record<string, DivisionalChartData>
}

/**
 * Chart type configurations with icons and descriptions
 */
const CHART_CONFIGS: Record<string, {
  icon: string
  title: string
  shortDesc: string
  importance: 'high' | 'medium' | 'low'
}> = {
  D2: {
    icon: '💰',
    title: 'Hora (D2)',
    shortDesc: 'Wealth & Prosperity',
    importance: 'high'
  },
  D4: {
    icon: '🏡',
    title: 'Chaturthamsa (D4)',
    shortDesc: 'Property & Assets',
    importance: 'high'
  },
  D7: {
    icon: '👶',
    title: 'Saptamsa (D7)',
    shortDesc: 'Children & Progeny',
    importance: 'high'
  },
  D9: {
    icon: '💑',
    title: 'Navamsa (D9)',
    shortDesc: 'Marriage & Dharma',
    importance: 'high'
  },
  D10: {
    icon: '💼',
    title: 'Dashamsa (D10)',
    shortDesc: 'Career & Profession',
    importance: 'high'
  },
  D12: {
    icon: '👨‍👩‍👧',
    title: 'Dwadashamsa (D12)',
    shortDesc: 'Parents & Ancestry',
    importance: 'medium'
  },
  D16: {
    icon: '🚗',
    title: 'Shodashamsa (D16)',
    shortDesc: 'Vehicles & Comforts',
    importance: 'medium'
  },
  D20: {
    icon: '🙏',
    title: 'Vimshamsa (D20)',
    shortDesc: 'Spiritual Development',
    importance: 'medium'
  },
  D24: {
    icon: '📚',
    title: 'Chaturvimshamsa (D24)',
    shortDesc: 'Education & Learning',
    importance: 'high'
  },
  D27: {
    icon: '💪',
    title: 'Nakshatramsa (D27)',
    shortDesc: 'Strengths & Weaknesses',
    importance: 'low'
  },
  D30: {
    icon: '⚡',
    title: 'Trimshamsa (D30)',
    shortDesc: 'Evils & Misfortunes',
    importance: 'medium'
  },
  D40: {
    icon: '🎯',
    title: 'Khavedamsa (D40)',
    shortDesc: 'Auspicious & Inauspicious',
    importance: 'low'
  },
  D45: {
    icon: '🧬',
    title: 'Akshavedamsa (D45)',
    shortDesc: 'Character & Conduct',
    importance: 'low'
  },
  D60: {
    icon: '♾️',
    title: 'Shashtyamsa (D60)',
    shortDesc: 'Karma & Past Lives',
    importance: 'medium'
  }
}

/**
 * Get importance badge variant
 */
function getImportanceBadge(importance: 'high' | 'medium' | 'low'): {
  variant: 'default' | 'secondary' | 'outline'
  label: string
} {
  const configs = {
    high: { variant: 'default' as const, label: 'High Priority' },
    medium: { variant: 'secondary' as const, label: 'Medium Priority' },
    low: { variant: 'outline' as const, label: 'Advanced' }
  }
  return configs[importance]
}

export function DivisionalChartsDisplay({ divisionalCharts }: DivisionalChartsDisplayProps) {
  const chartTypes = Object.keys(divisionalCharts).sort((a, b) => {
    // Sort by division number (D2, D4, D7, D9, D10, ...)
    const numA = parseInt(a.replace('D', ''))
    const numB = parseInt(b.replace('D', ''))
    return numA - numB
  })

  const [selectedChart, setSelectedChart] = useState(chartTypes[0] || 'D2')

  if (chartTypes.length === 0) {
    return (
      <Card>
        <CardContent className="py-8 text-center text-gray-500">
          No divisional charts available. Please regenerate the chart to get divisional chart data.
        </CardContent>
      </Card>
    )
  }

  const currentChartData = divisionalCharts[selectedChart]
  const config = CHART_CONFIGS[selectedChart] || {
    icon: '📊',
    title: selectedChart,
    shortDesc: 'Divisional Chart',
    importance: 'medium' as const
  }

  return (
    <div className="space-y-6">
      {/* Chart Selection Tabs */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            📊 Divisional Charts (Varga Kundali)
          </CardTitle>
          <CardDescription>
            Divisional charts provide deeper insights into specific life areas.
            Each division magnifies particular aspects of your birth chart.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <Tabs value={selectedChart} onValueChange={setSelectedChart}>
            <TabsList className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-2 h-auto p-2 bg-gray-100">
              {chartTypes.map((chartType) => {
                const cfg = CHART_CONFIGS[chartType] || { icon: '📊', shortDesc: chartType }
                return (
                  <TabsTrigger
                    key={chartType}
                    value={chartType}
                    className="flex flex-col items-center justify-center h-auto py-3 px-2 data-[state=active]:bg-jio-500 data-[state=active]:text-white"
                  >
                    <span className="text-2xl mb-1">{cfg.icon}</span>
                    <span className="text-sm font-bold">{chartType}</span>
                    <span className="text-xs opacity-80 text-center">{cfg.shortDesc}</span>
                  </TabsTrigger>
                )
              })}
            </TabsList>
          </Tabs>
        </CardContent>
      </Card>

      {/* Selected Chart Display */}
      {currentChartData && (
        <>
          {/* Chart Information Card */}
          <Card className="border-2 border-jio-200 bg-jio-50/30">
            <CardHeader>
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <CardTitle className="text-2xl flex items-center gap-2">
                    {config.icon} {config.title}
                  </CardTitle>
                  <CardDescription className="mt-2 text-base">
                    {currentChartData.purpose}
                  </CardDescription>
                </div>
                <Badge {...getImportanceBadge(config.importance)}>
                  {getImportanceBadge(config.importance).label}
                </Badge>
              </div>
            </CardHeader>
            {currentChartData.description && (
              <CardContent>
                <p className="text-sm text-gray-700 leading-relaxed">
                  {currentChartData.description}
                </p>
              </CardContent>
            )}
          </Card>

          {/* Chart Visualization */}
          <Card>
            <CardHeader>
              <CardTitle>Chart Diagram</CardTitle>
              <CardDescription>
                Ascendant: {currentChartData.ascendant.sign} ({currentChartData.ascendant.degree.toFixed(2)}°)
              </CardDescription>
            </CardHeader>
            <CardContent className="flex justify-center p-6">
              <SouthIndianChart
                chartData={{
                  ascendant: currentChartData.ascendant,
                  planets: currentChartData.planets,
                  houses: currentChartData.houses
                }}
                width={400}
                height={400}
              />
            </CardContent>
          </Card>

          {/* Planetary Positions Table */}
          <PlanetaryPositionsTable
            planets={currentChartData.planets}
            title={`Planetary Positions in ${config.title}`}
            description={`Positions of all planets in the ${selectedChart} divisional chart`}
            showHouse={true}
          />

          {/* House Analysis */}
          <Card>
            <CardHeader>
              <CardTitle>House Distribution</CardTitle>
              <CardDescription>
                Zodiac signs in each house of {config.title}
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-3">
                {currentChartData.houses.map((house) => {
                  // Count planets in this house
                  const planetsInHouse = Object.entries(currentChartData.planets).filter(
                    ([_, data]) => data.house === house.house_num
                  )

                  return (
                    <Card
                      key={house.house_num}
                      className={`${
                        planetsInHouse.length > 0
                          ? 'border-2 border-jio-400 bg-jio-50'
                          : 'border-gray-200'
                      }`}
                    >
                      <CardHeader className="pb-2">
                        <CardTitle className="text-sm flex items-center justify-between">
                          <span>House {house.house_num}</span>
                          {planetsInHouse.length > 0 && (
                            <Badge variant="default" className="text-xs">
                              {planetsInHouse.length}
                            </Badge>
                          )}
                        </CardTitle>
                      </CardHeader>
                      <CardContent className="pb-3">
                        <p className="text-xs font-semibold text-gray-700">{house.sign}</p>
                        {planetsInHouse.length > 0 && (
                          <div className="mt-2 space-y-1">
                            {planetsInHouse.map(([planetName, _]) => (
                              <Badge key={planetName} variant="outline" className="text-xs mr-1">
                                {planetName}
                              </Badge>
                            ))}
                          </div>
                        )}
                      </CardContent>
                    </Card>
                  )
                })}
              </div>
            </CardContent>
          </Card>

          {/* Information Footer */}
          <Card className="bg-blue-50 border-blue-200">
            <CardContent className="py-4">
              <p className="text-sm text-blue-800 leading-relaxed">
                <strong>About {config.title}:</strong> The {selectedChart} divisional chart is created by
                dividing each zodiac sign into {currentChartData.division} equal parts. This magnifies specific
                life areas related to {currentChartData.purpose.toLowerCase()}. Analyzing planetary positions
                in divisional charts provides deeper insights beyond the main birth chart (D1).
              </p>
            </CardContent>
          </Card>
        </>
      )}
    </div>
  )
}

export default DivisionalChartsDisplay
