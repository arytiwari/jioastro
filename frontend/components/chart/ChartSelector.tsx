'use client'

import React, { useState } from 'react'
import { BirthChartTemplate } from './BirthChartTemplate'
import { SouthIndianChart } from './SouthIndianChart'
import { WesternBirthChart } from './WesternBirthChart'

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

interface ChartSelectorProps {
  chartData: ChartData
  defaultChart?: 'north' | 'south' | 'western'
}

type ChartType = 'north' | 'south' | 'western'

export function ChartSelector({ chartData, defaultChart = 'north' }: ChartSelectorProps) {
  const [selectedChart, setSelectedChart] = useState<ChartType>(defaultChart)

  const chartTypes = [
    { id: 'north' as ChartType, name: 'North Indian', description: 'Diamond layout, traditional' },
    { id: 'south' as ChartType, name: 'South Indian', description: 'Square layout, fixed houses' },
    { id: 'western' as ChartType, name: 'Western Style', description: 'Circular wheel layout' }
  ]

  const renderChart = () => {
    switch (selectedChart) {
      case 'north':
        return <BirthChartTemplate chartData={chartData} />
      case 'south':
        return <SouthIndianChart chartData={chartData} />
      case 'western':
        return <WesternBirthChart chartData={chartData} />
      default:
        return <BirthChartTemplate chartData={chartData} />
    }
  }

  return (
    <div className="w-full space-y-4">
      {/* Chart Type Selector */}
      <div className="flex justify-center gap-2 flex-wrap">
        {chartTypes.map((chart) => (
          <button
            key={chart.id}
            onClick={() => setSelectedChart(chart.id)}
            className={`px-4 py-2 rounded-lg border-2 transition-all ${
              selectedChart === chart.id
                ? 'border-jio-600 bg-jio-50 text-jio-900 font-semibold'
                : 'border-gray-300 bg-white text-gray-700 hover:border-jio-400 hover:bg-jio-50'
            }`}
          >
            <div className="text-sm font-medium">{chart.name}</div>
            <div className="text-xs text-gray-500">{chart.description}</div>
          </button>
        ))}
      </div>

      {/* Selected Chart */}
      <div className="flex justify-center">
        {renderChart()}
      </div>
    </div>
  )
}
