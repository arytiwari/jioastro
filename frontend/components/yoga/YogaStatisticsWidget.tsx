'use client'

import { useEffect, useState } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { apiClient } from '@/lib/api'
import { Loader2, BarChart3, CheckCircle2, AlertCircle, Book, Sparkles } from 'lucide-react'
import Link from 'next/link'

interface YogaStatistics {
  total_yogas: number
  bphs_classical_yogas: number
  practical_modern_yogas: number
  bphs_coverage_percentage: number
  bphs_implemented: number
  bphs_total: number
  bphs_missing: number
  category_breakdown: Record<string, number>
  section_coverage: Record<string, { total: number; implemented: number; coverage: number }>
  practical_breakdown: Record<string, number>
  system_capabilities: Record<string, boolean>
}

export function YogaStatisticsWidget() {
  const [statistics, setStatistics] = useState<YogaStatistics | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    loadStatistics()
  }, [])

  const loadStatistics = async () => {
    try {
      setLoading(true)
      setError(null)
      const response = await apiClient.getYogaStatistics()
      setStatistics(response.data.statistics)
    } catch (err: any) {
      console.error('Failed to load yoga statistics:', err)
      setError(err.message || 'Failed to load statistics')
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return (
      <Card>
        <CardContent className="flex items-center justify-center py-8">
          <Loader2 className="h-6 w-6 animate-spin text-primary" />
        </CardContent>
      </Card>
    )
  }

  if (error || !statistics) {
    return (
      <Card className="border-red-200 bg-red-50">
        <CardContent className="py-6">
          <div className="flex items-start gap-3">
            <AlertCircle className="h-5 w-5 text-red-600 mt-0.5" />
            <div>
              <p className="font-medium text-red-900">Failed to load statistics</p>
              <p className="text-sm text-red-700 mt-1">{error}</p>
              <Button
                variant="outline"
                size="sm"
                onClick={loadStatistics}
                className="mt-3"
              >
                Try Again
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>
    )
  }

  const bphsCoverageColor =
    statistics.bphs_coverage_percentage >= 90
      ? 'text-emerald-600'
      : statistics.bphs_coverage_percentage >= 75
      ? 'text-blue-600'
      : 'text-amber-600'

  return (
    <Card className="border-purple-200 bg-gradient-to-br from-purple-50 to-indigo-50">
      <CardHeader>
        <div className="flex items-center justify-between">
          <div>
            <CardTitle className="flex items-center gap-2 text-xl">
              <BarChart3 className="h-5 w-5 text-purple-600" />
              Yoga System Statistics
            </CardTitle>
            <CardDescription className="mt-1">
              Comprehensive coverage and capabilities
            </CardDescription>
          </div>
          <Badge variant="outline" className="bg-white text-purple-700 border-purple-300">
            v2.0
          </Badge>
        </div>
      </CardHeader>
      <CardContent className="space-y-6">
        {/* Total Yogas Overview */}
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
          <div className="bg-white rounded-lg p-4 border border-purple-100 shadow-sm">
            <div className="text-sm text-gray-600 mb-1">Total Yogas</div>
            <div className="text-3xl font-bold text-purple-700">
              {statistics.total_yogas}
            </div>
            <div className="text-xs text-gray-500 mt-1">
              Classical + Modern
            </div>
          </div>

          <div className="bg-white rounded-lg p-4 border border-emerald-100 shadow-sm">
            <div className="text-sm text-gray-600 mb-1">BPHS Classical</div>
            <div className="text-3xl font-bold text-emerald-600">
              {statistics.bphs_classical_yogas}
            </div>
            <div className="text-xs text-gray-500 mt-1">
              Traditional yogas
            </div>
          </div>

          <div className="bg-white rounded-lg p-4 border border-blue-100 shadow-sm">
            <div className="text-sm text-gray-600 mb-1">Practical Modern</div>
            <div className="text-3xl font-bold text-blue-600">
              {statistics.practical_modern_yogas}
            </div>
            <div className="text-xs text-gray-500 mt-1">
              Modern analysis
            </div>
          </div>
        </div>

        {/* BPHS Coverage */}
        <div className="bg-white rounded-lg p-5 border border-purple-200 shadow-sm">
          <div className="flex items-center justify-between mb-3">
            <h3 className="font-semibold text-gray-900 flex items-center gap-2">
              <Book className="h-4 w-4 text-purple-600" />
              BPHS Coverage
            </h3>
            <Badge
              variant="outline"
              className={`${
                statistics.bphs_coverage_percentage >= 90
                  ? 'bg-emerald-50 text-emerald-700 border-emerald-300'
                  : 'bg-blue-50 text-blue-700 border-blue-300'
              }`}
            >
              {statistics.bphs_coverage_percentage >= 90 ? (
                <CheckCircle2 className="h-3 w-3 mr-1" />
              ) : null}
              {statistics.bphs_coverage_percentage >= 92
                ? 'Elite World-Class'
                : statistics.bphs_coverage_percentage >= 90
                ? 'World-Class'
                : 'Excellent'}
            </Badge>
          </div>

          <div className="space-y-2">
            <div className="flex items-center justify-between text-sm">
              <span className="text-gray-600">Implementation Progress</span>
              <span className={`font-bold ${bphsCoverageColor}`}>
                {statistics.bphs_coverage_percentage}%
              </span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-3 overflow-hidden">
              <div
                className={`h-full rounded-full transition-all ${
                  statistics.bphs_coverage_percentage >= 90
                    ? 'bg-gradient-to-r from-emerald-500 to-emerald-600'
                    : 'bg-gradient-to-r from-blue-500 to-blue-600'
                }`}
                style={{ width: `${statistics.bphs_coverage_percentage}%` }}
              />
            </div>
            <div className="flex items-center justify-between text-xs text-gray-500 pt-1">
              <span>
                {statistics.bphs_implemented}/{statistics.bphs_total} implemented
              </span>
              <span>{statistics.bphs_missing} missing</span>
            </div>
          </div>
        </div>

        {/* Category Breakdown */}
        <div className="bg-white rounded-lg p-5 border border-purple-200 shadow-sm">
          <h3 className="font-semibold text-gray-900 mb-3 flex items-center gap-2">
            <Sparkles className="h-4 w-4 text-purple-600" />
            Category Breakdown
          </h3>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
            {Object.entries(statistics.category_breakdown).map(([category, count]) => {
              const categoryIcons: Record<string, string> = {
                'Major Positive Yogas': '⭐',
                'Standard Yogas': '📖',
                'Major Challenges': '⚠️',
                'Minor Yogas & Subtle Influences': '✨',
                'Non-BPHS (Practical)': '🔧',
              }

              const categoryColors: Record<string, string> = {
                'Major Positive Yogas': 'bg-emerald-50 text-emerald-700 border-emerald-200',
                'Standard Yogas': 'bg-blue-50 text-blue-700 border-blue-200',
                'Major Challenges': 'bg-red-50 text-red-700 border-red-200',
                'Minor Yogas & Subtle Influences': 'bg-purple-50 text-purple-700 border-purple-200',
                'Non-BPHS (Practical)': 'bg-gray-50 text-gray-700 border-gray-200',
              }

              return (
                <div
                  key={category}
                  className={`p-3 rounded-lg border ${categoryColors[category] || 'bg-gray-50'}`}
                >
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2 flex-1 min-w-0">
                      <span className="text-base">{categoryIcons[category]}</span>
                      <span className="text-xs font-medium truncate">{category}</span>
                    </div>
                    <Badge variant="secondary" className="ml-2 shrink-0">
                      {count}
                    </Badge>
                  </div>
                </div>
              )
            })}
          </div>
        </div>

        {/* System Capabilities */}
        <div className="bg-gradient-to-r from-purple-50 to-indigo-50 rounded-lg p-4 border border-purple-200">
          <h3 className="font-semibold text-gray-900 mb-3 text-sm">System Capabilities</h3>
          <div className="flex flex-wrap gap-2">
            {Object.entries(statistics.system_capabilities).map(([capability, enabled]) => {
              const capabilityLabels: Record<string, string> = {
                strength_calculation: 'Strength',
                cancellation_detection: 'Cancellation',
                timing_prediction: 'Timing',
                dasha_integration: 'Dasha',
                jaimini_karakas: 'Jaimini',
                divisional_charts_d9: 'D9 Analysis',
                nakshatra_analysis: 'Nakshatra',
                hora_calculations: 'Hora',
              }

              return enabled ? (
                <Badge
                  key={capability}
                  variant="secondary"
                  className="bg-white text-purple-700 border border-purple-200 text-xs"
                >
                  <CheckCircle2 className="h-3 w-3 mr-1" />
                  {capabilityLabels[capability] || capability}
                </Badge>
              ) : null
            })}
          </div>
        </div>

        {/* Action Buttons */}
        <div className="flex flex-col sm:flex-row gap-3 pt-2">
          <Link href="/dashboard/yogas/bphs-report" className="flex-1">
            <Button variant="outline" className="w-full border-purple-300 hover:bg-purple-50">
              <Book className="h-4 w-4 mr-2" />
              View Coverage Report
            </Button>
          </Link>
          <Link href="/dashboard/yogas/search" className="flex-1">
            <Button variant="outline" className="w-full border-purple-300 hover:bg-purple-50">
              <Sparkles className="h-4 w-4 mr-2" />
              Yoga Encyclopedia
            </Button>
          </Link>
        </div>
      </CardContent>
    </Card>
  )
}
