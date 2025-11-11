'use client'

import { useEffect, useState } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { apiClient } from '@/lib/api'
import {
  Loader2,
  CheckCircle2,
  AlertCircle,
  Book,
  ArrowLeft,
  Clock,
  Sparkles,
  Target,
  TrendingUp,
} from 'lucide-react'
import Link from 'next/link'

interface MissingYoga {
  name: string
  bphs_ref: string
  category: string
  priority: string
  implementation_effort: string
  reason: string
}

interface CategoryCoverage {
  total: number
  implemented: number
  missing: number
  coverage: number
  status: string
}

interface BphsReport {
  summary: {
    total_bphs_yogas: number
    implemented: number
    missing: number
    coverage_percentage: number
    world_class_threshold: number
    status: string
  }
  category_coverage: Record<string, CategoryCoverage>
  missing_yogas: MissingYoga[]
  roadmap: {
    phase_5: {
      timeline: string
      yogas_to_implement: number
      target_coverage: string
    }
  }
}

export default function BphsReportPage() {
  const [report, setReport] = useState<BphsReport | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    loadReport()
  }, [])

  const loadReport = async () => {
    try {
      setLoading(true)
      setError(null)
      const response = await apiClient.getYogaBphsReport()
      // Backend returns { success, report, message }, extract the report
      setReport(response.data.report || response.data)
    } catch (err: any) {
      console.error('Failed to load BPHS report:', err)
      setError(err.message || 'Failed to load report')
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return (
      <div className="container max-w-7xl mx-auto px-4 py-8">
        <div className="flex items-center justify-center min-h-[400px]">
          <div className="text-center">
            <Loader2 className="h-8 w-8 animate-spin text-primary mx-auto mb-4" />
            <p className="text-gray-600">Loading BPHS coverage report...</p>
          </div>
        </div>
      </div>
    )
  }

  if (error || !report || !report.summary) {
    return (
      <div className="container max-w-7xl mx-auto px-4 py-8">
        <Card className="border-red-200 bg-red-50">
          <CardContent className="py-8">
            <div className="flex flex-col items-center justify-center text-center">
              <AlertCircle className="h-12 w-12 text-red-600 mb-4" />
              <h3 className="text-lg font-semibold text-red-900 mb-2">Failed to load report</h3>
              <p className="text-red-700 mb-4">{error || 'Invalid report data'}</p>
              <Button variant="outline" onClick={loadReport}>
                Try Again
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>
    )
  }

  const priorityColors: Record<string, string> = {
    High: 'bg-red-100 text-red-800 border-red-300',
    Medium: 'bg-yellow-100 text-yellow-800 border-yellow-300',
    Low: 'bg-blue-100 text-blue-800 border-blue-300',
  }

  const effortColors: Record<string, string> = {
    High: 'bg-purple-100 text-purple-800 border-purple-300',
    Medium: 'bg-orange-100 text-orange-800 border-orange-300',
    Low: 'bg-green-100 text-green-800 border-green-300',
  }

  return (
    <div className="container max-w-7xl mx-auto px-4 py-8">
      {/* Header */}
      <div className="mb-8">
        <Link href="/dashboard/yogas">
          <Button variant="ghost" size="sm" className="mb-4">
            <ArrowLeft className="h-4 w-4 mr-2" />
            Back to Yogas
          </Button>
        </Link>
        <div className="flex items-start justify-between flex-wrap gap-4">
          <div>
            <h1 className="text-3xl font-bold text-gray-900 mb-2">BPHS Coverage Report</h1>
            <p className="text-gray-600">
              Comprehensive analysis of Brihat Parashara Hora Shastra yoga implementation
            </p>
          </div>
          <Badge
            variant="outline"
            className={
              report.summary.coverage_percentage >= report.summary.world_class_threshold
                ? 'bg-emerald-50 text-emerald-700 border-emerald-300 text-lg px-4 py-2'
                : 'bg-blue-50 text-blue-700 border-blue-300 text-lg px-4 py-2'
            }
          >
            <CheckCircle2 className="h-5 w-5 mr-2" />
            {report.summary.status}
          </Badge>
        </div>
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
        <Card className="border-purple-200 bg-gradient-to-br from-purple-50 to-purple-100">
          <CardHeader className="pb-3">
            <CardDescription className="text-xs">Total BPHS Yogas</CardDescription>
            <CardTitle className="text-3xl font-bold text-purple-700">
              {report.summary.total_bphs_yogas}
            </CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-xs text-purple-600">Classical yogas from BPHS</p>
          </CardContent>
        </Card>

        <Card className="border-emerald-200 bg-gradient-to-br from-emerald-50 to-emerald-100">
          <CardHeader className="pb-3">
            <CardDescription className="text-xs">Implemented</CardDescription>
            <CardTitle className="text-3xl font-bold text-emerald-700">
              {report.summary.implemented}
            </CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-xs text-emerald-600">
              {report.summary.coverage_percentage}% coverage
            </p>
          </CardContent>
        </Card>

        <Card className="border-amber-200 bg-gradient-to-br from-amber-50 to-amber-100">
          <CardHeader className="pb-3">
            <CardDescription className="text-xs">Missing</CardDescription>
            <CardTitle className="text-3xl font-bold text-amber-700">
              {report.summary.missing}
            </CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-xs text-amber-600">
              {((report.summary.missing / report.summary.total_bphs_yogas) * 100).toFixed(1)}% remaining
            </p>
          </CardContent>
        </Card>

        <Card className="border-blue-200 bg-gradient-to-br from-blue-50 to-blue-100">
          <CardHeader className="pb-3">
            <CardDescription className="text-xs">Target Phase 5</CardDescription>
            <CardTitle className="text-3xl font-bold text-blue-700">
              {report.roadmap.phase_5.target_coverage}
            </CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-xs text-blue-600">{report.roadmap.phase_5.timeline}</p>
          </CardContent>
        </Card>
      </div>

      {/* Category Coverage */}
      <Card className="mb-8">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Target className="h-5 w-5 text-purple-600" />
            Category-wise Coverage
          </CardTitle>
          <CardDescription>Implementation status by BPHS category</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {Object.entries(report.category_coverage).map(([category, coverage]) => (
              <div key={category} className="space-y-2">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-3 flex-1">
                    <h3 className="font-medium text-gray-900">{category}</h3>
                    <Badge
                      variant="outline"
                      className={
                        coverage.status === 'Excellent'
                          ? 'bg-emerald-50 text-emerald-700 border-emerald-300'
                          : coverage.status === 'Good'
                          ? 'bg-blue-50 text-blue-700 border-blue-300'
                          : 'bg-amber-50 text-amber-700 border-amber-300'
                      }
                    >
                      {coverage.status}
                    </Badge>
                  </div>
                  <div className="text-right">
                    <span className="font-bold text-lg text-purple-700">
                      {coverage.coverage.toFixed(1)}%
                    </span>
                    <p className="text-xs text-gray-500">
                      {coverage.implemented}/{coverage.total} implemented
                    </p>
                  </div>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2 overflow-hidden">
                  <div
                    className={`h-full rounded-full transition-all ${
                      coverage.coverage >= 90
                        ? 'bg-gradient-to-r from-emerald-500 to-emerald-600'
                        : coverage.coverage >= 75
                        ? 'bg-gradient-to-r from-blue-500 to-blue-600'
                        : 'bg-gradient-to-r from-amber-500 to-amber-600'
                    }`}
                    style={{ width: `${coverage.coverage}%` }}
                  />
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Missing Yogas */}
      <Card className="mb-8">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Sparkles className="h-5 w-5 text-amber-600" />
            Missing Yogas ({report.missing_yogas.length})
          </CardTitle>
          <CardDescription>Yogas yet to be implemented with priority and effort estimates</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {report.missing_yogas.map((yoga, index) => (
              <Card key={index} className="border-amber-200 bg-amber-50/50">
                <CardContent className="pt-6">
                  <div className="space-y-3">
                    <div className="flex items-start justify-between gap-4">
                      <div className="flex-1">
                        <h3 className="font-semibold text-gray-900 mb-1">{yoga.name}</h3>
                        <div className="flex items-center gap-2 flex-wrap mb-2">
                          <Badge variant="outline" className="bg-white text-gray-700 border-gray-300">
                            <Book className="h-3 w-3 mr-1" />
                            {yoga.bphs_ref}
                          </Badge>
                          <Badge variant="outline" className="bg-white text-purple-700 border-purple-300">
                            {yoga.category}
                          </Badge>
                        </div>
                        <p className="text-sm text-gray-600">{yoga.reason}</p>
                      </div>
                      <div className="flex flex-col gap-2 shrink-0">
                        <Badge variant="outline" className={priorityColors[yoga.priority]}>
                          <Target className="h-3 w-3 mr-1" />
                          {yoga.priority} Priority
                        </Badge>
                        <Badge variant="outline" className={effortColors[yoga.implementation_effort]}>
                          <Clock className="h-3 w-3 mr-1" />
                          {yoga.implementation_effort} Effort
                        </Badge>
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Roadmap */}
      <Card className="border-blue-200 bg-gradient-to-br from-blue-50 to-indigo-50">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <TrendingUp className="h-5 w-5 text-blue-600" />
            Phase 5 Roadmap
          </CardTitle>
          <CardDescription>Plan to achieve {report.roadmap.phase_5.target_coverage} coverage</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="bg-white rounded-lg p-4 border border-blue-200">
              <div className="text-sm text-gray-600 mb-2">Timeline</div>
              <div className="text-2xl font-bold text-blue-700">
                {report.roadmap.phase_5.timeline}
              </div>
            </div>
            <div className="bg-white rounded-lg p-4 border border-blue-200">
              <div className="text-sm text-gray-600 mb-2">Yogas to Implement</div>
              <div className="text-2xl font-bold text-blue-700">
                {report.roadmap.phase_5.yogas_to_implement}
              </div>
            </div>
            <div className="bg-white rounded-lg p-4 border border-blue-200">
              <div className="text-sm text-gray-600 mb-2">Target Coverage</div>
              <div className="text-2xl font-bold text-blue-700">
                {report.roadmap.phase_5.target_coverage}
              </div>
            </div>
          </div>

          <div className="mt-6 p-4 bg-white rounded-lg border border-blue-200">
            <h3 className="font-semibold text-gray-900 mb-3">Implementation Approach</h3>
            <ul className="space-y-2 text-sm text-gray-700">
              <li className="flex items-start gap-2">
                <CheckCircle2 className="h-4 w-4 text-blue-600 mt-0.5 shrink-0" />
                <span>
                  <strong>Week 1-2:</strong> Jaimini integration (Arudha Pada, Arudha Relations)
                </span>
              </li>
              <li className="flex items-start gap-2">
                <CheckCircle2 className="h-4 w-4 text-blue-600 mt-0.5 shrink-0" />
                <span>
                  <strong>Week 3-4:</strong> D9 yoga detection (Kendra/Trikona from Navamsa)
                </span>
              </li>
              <li className="flex items-start gap-2">
                <CheckCircle2 className="h-4 w-4 text-blue-600 mt-0.5 shrink-0" />
                <span>
                  <strong>Week 5-6:</strong> Advanced features (Birth Moment Factor, Vargottama Moon, AK factors)
                </span>
              </li>
            </ul>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
