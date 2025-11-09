'use client'

import { useQuery } from '@/lib/query'
import { useParams, useRouter } from 'next/navigation'
import { apiClient } from '@/lib/api'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Skeleton } from '@/components/ui/skeleton'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import {
  Calendar,
  Sun,
  Moon,
  Star,
  Award,
  TrendingUp,
  TrendingDown,
  Gem,
  ArrowLeft,
  AlertCircle,
  CheckCircle,
  Clock,
} from '@/components/icons'

export default function VarshapalDetailPage() {
  const params = useParams()
  const router = useRouter()
  const varshaphalId = params.id as string

  const { data: varshaphal, isLoading, error } = useQuery({
    queryKey: ['varshaphal', varshaphalId],
    queryFn: async () => {
      try {
        console.log('Fetching varshaphal:', varshaphalId)
        const response = await apiClient.getVarshaphal(varshaphalId)
        console.log('Got varshaphal response:', response)
        return response.data
      } catch (err) {
        console.error('Error fetching varshaphal:', err)
        throw err
      }
    },
  })

  if (isLoading) {
    return (
      <div className="space-y-6">
        <Skeleton className="h-8 w-64" />
        <Skeleton className="h-96" />
      </div>
    )
  }

  if (error || !varshaphal) {
    return (
      <div className="space-y-6">
        <Card>
          <CardContent className="text-center py-12">
            <AlertCircle className="w-12 h-12 text-red-400 mx-auto mb-4" />
            <h3 className="text-lg font-semibold mb-2">Varshaphal Not Found</h3>
            <p className="text-gray-600 mb-6">
              {error?.message || 'The requested Varshaphal could not be found'}
            </p>
            <Button onClick={() => router.push('/dashboard/varshaphal')}>
              <ArrowLeft className="w-4 h-4 mr-2" />
              Back to Varshaphals
            </Button>
          </CardContent>
        </Card>
      </div>
    )
  }

  const getQualityColor = (quality: string) => {
    switch (quality.toLowerCase()) {
      case 'excellent':
        return 'text-green-600 bg-green-100'
      case 'mixed':
        return 'text-yellow-600 bg-yellow-100'
      case 'challenging':
        return 'text-red-600 bg-red-100'
      default:
        return 'text-gray-600 bg-gray-100'
    }
  }

  const getYogaTypeColor = (type: string) => {
    switch (type.toLowerCase()) {
      case 'auspicious':
        return 'text-green-600 bg-green-50 border-green-200'
      case 'challenging':
        return 'text-red-600 bg-red-50 border-red-200'
      case 'mixed':
        return 'text-yellow-600 bg-yellow-50 border-yellow-200'
      default:
        return 'text-gray-600 bg-gray-50 border-gray-200'
    }
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-start justify-between">
        <div>
          <Button
            variant="ghost"
            onClick={() => router.push('/dashboard/varshaphal')}
            className="mb-4"
          >
            <ArrowLeft className="w-4 h-4 mr-2" />
            Back to Varshaphals
          </Button>
          <h1 className="text-3xl font-bold text-gray-900 flex items-center gap-2">
            <Sun className="w-8 h-8 text-jio-600" />
            Varshaphal {varshaphal.target_year}
          </h1>
          <p className="text-gray-600 mt-2">
            Solar Return Chart • Generated on{' '}
            {new Date(varshaphal.generated_at).toLocaleDateString()}
          </p>
        </div>
        <span
          className={`px-4 py-2 rounded-full text-sm font-semibold ${getQualityColor(
            varshaphal.annual_interpretation.overall_quality
          )}`}
        >
          {varshaphal.annual_interpretation.overall_quality} Year
        </span>
      </div>

      {/* Year Summary */}
      <Card>
        <CardHeader>
          <CardTitle>Year Overview</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-gray-700 leading-relaxed">
            {varshaphal.annual_interpretation.year_summary}
          </p>
        </CardContent>
      </Card>

      <Tabs defaultValue="predictions" className="w-full">
        <TabsList className="grid w-full grid-cols-5">
          <TabsTrigger value="predictions">Predictions</TabsTrigger>
          <TabsTrigger value="yogas">Yogas</TabsTrigger>
          <TabsTrigger value="dasha">Dasha Periods</TabsTrigger>
          <TabsTrigger value="sahams">Sahams</TabsTrigger>
          <TabsTrigger value="remedies">Remedies</TabsTrigger>
        </TabsList>

        {/* Monthly Predictions */}
        <TabsContent value="predictions" className="space-y-6">
          {/* Best & Worst Periods */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <Card className="border-green-200 bg-green-50">
              <CardHeader>
                <CardTitle className="flex items-center gap-2 text-green-700">
                  <TrendingUp className="w-5 h-5" />
                  Best Periods
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                {varshaphal.annual_interpretation.best_periods.map((period: any, idx: number) => (
                  <div key={idx} className="bg-white p-4 rounded-lg border border-green-200">
                    <div className="font-semibold text-gray-900 mb-1">{period.period}</div>
                    <div className="text-sm text-gray-700 mb-2">{period.reason}</div>
                    <div className="text-xs text-green-700 font-medium">
                      Utilize for: {period.utilize_for}
                    </div>
                  </div>
                ))}
              </CardContent>
            </Card>

            <Card className="border-orange-200 bg-orange-50">
              <CardHeader>
                <CardTitle className="flex items-center gap-2 text-orange-700">
                  <TrendingDown className="w-5 h-5" />
                  Challenging Periods
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                {varshaphal.annual_interpretation.worst_periods.map((period: any, idx: number) => (
                  <div key={idx} className="bg-white p-4 rounded-lg border border-orange-200">
                    <div className="font-semibold text-gray-900 mb-1">{period.period}</div>
                    <div className="text-sm text-gray-700 mb-2">{period.reason}</div>
                    <div className="text-xs text-orange-700 font-medium">
                      Precautions: {period.precautions}
                    </div>
                  </div>
                ))}
              </CardContent>
            </Card>
          </div>

          {/* Monthly Timeline */}
          <Card>
            <CardHeader>
              <CardTitle>Month-by-Month Predictions</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {varshaphal.annual_interpretation.monthly_predictions.map(
                  (month: any, idx: number) => (
                    <div key={idx} className="border-l-4 border-jio-500 pl-4 py-2">
                      <div className="flex items-start justify-between mb-2">
                        <div className="font-semibold text-gray-900">{month.period}</div>
                        <div className="text-sm text-jio-600 font-medium">{month.ruling_planet}</div>
                      </div>
                      <div className="text-sm text-gray-700 mb-2">
                        <strong>Theme:</strong> {month.theme}
                      </div>
                      <div className="text-sm text-gray-600 mb-2">
                        <strong>Focus Areas:</strong> {month.focus_areas.join(', ')}
                      </div>
                      <div className="text-sm text-gray-600 italic">{month.advice}</div>
                    </div>
                  )
                )}
              </div>
            </CardContent>
          </Card>

          {/* Key Opportunities & Challenges */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <CheckCircle className="w-5 h-5 text-green-600" />
                  Key Opportunities
                </CardTitle>
              </CardHeader>
              <CardContent>
                <ul className="space-y-2">
                  {varshaphal.annual_interpretation.key_opportunities.map(
                    (opportunity: string, idx: number) => (
                      <li key={idx} className="flex items-start gap-2">
                        <Star className="w-4 h-4 text-yellow-500 flex-shrink-0 mt-0.5" />
                        <span className="text-sm text-gray-700">{opportunity}</span>
                      </li>
                    )
                  )}
                </ul>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <AlertCircle className="w-5 h-5 text-orange-600" />
                  Key Challenges
                </CardTitle>
              </CardHeader>
              <CardContent>
                <ul className="space-y-2">
                  {varshaphal.annual_interpretation.key_challenges.map(
                    (challenge: string, idx: number) => (
                      <li key={idx} className="flex items-start gap-2">
                        <AlertCircle className="w-4 h-4 text-orange-500 flex-shrink-0 mt-0.5" />
                        <span className="text-sm text-gray-700">{challenge}</span>
                      </li>
                    )
                  )}
                </ul>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        {/* Varshaphal Yogas */}
        <TabsContent value="yogas" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Detected Yogas</CardTitle>
              <CardDescription>
                {varshaphal.solar_return_chart.yogas.length} special annual yogas found in your solar
                return chart
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {varshaphal.solar_return_chart.yogas.map((yoga: any, idx: number) => (
                  <div
                    key={idx}
                    className={`p-4 rounded-lg border ${getYogaTypeColor(yoga.type)}`}
                  >
                    <div className="flex items-start justify-between mb-2">
                      <div className="font-semibold text-lg">{yoga.name}</div>
                      <div className="flex gap-2">
                        <span className="px-2 py-1 rounded text-xs font-medium bg-white border">
                          {yoga.type}
                        </span>
                        <span className="px-2 py-1 rounded text-xs font-medium bg-white border">
                          {yoga.strength}
                        </span>
                      </div>
                    </div>
                    <div className="text-sm mb-2">{yoga.description}</div>
                    <div className="text-sm font-medium mb-1">
                      Planets: {yoga.planets_involved.join(', ')}
                    </div>
                    <div className="text-sm italic">{yoga.effects}</div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Patyayini Dasha */}
        <TabsContent value="dasha" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Patyayini Dasha Periods</CardTitle>
              <CardDescription>
                Annual planetary periods based on strength in the solar return chart
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {varshaphal.patyayini_dasha.map((period: any, idx: number) => (
                  <div key={idx} className="border-l-4 border-jio-500 pl-4 py-3">
                    <div className="flex items-start justify-between mb-2">
                      <div className="font-semibold text-lg flex items-center gap-2">
                        <Moon className="w-5 h-5 text-jio-600" />
                        {period.planet}
                      </div>
                      <div className="text-sm text-gray-600">
                        {period.duration_months.toFixed(1)} months
                      </div>
                    </div>
                    <div className="text-sm text-gray-600 mb-2">
                      <Clock className="w-4 h-4 inline mr-1" />
                      {new Date(period.start_date).toLocaleDateString()} -{' '}
                      {new Date(period.end_date).toLocaleDateString()}
                    </div>
                    <div className="text-sm text-gray-700">{period.effects}</div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Sahams */}
        <TabsContent value="sahams" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Important Sahams (Sensitive Points)</CardTitle>
              <CardDescription>
                Key sensitive points in your annual chart revealing specific life areas
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {varshaphal.annual_interpretation.important_sahams.map((saham: any, idx: number) => (
                  <div key={idx} className="border rounded-lg p-4">
                    <div className="font-semibold text-gray-900 mb-1">{saham.name}</div>
                    <div className="text-sm text-jio-600 mb-2">{saham.position}</div>
                    <div className="text-sm text-gray-700">{saham.meaning}</div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Remedies */}
        <TabsContent value="remedies" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Gem className="w-5 h-5 text-purple-600" />
                Recommended Remedies
              </CardTitle>
              <CardDescription>Personalized remedies for the year ahead</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {varshaphal.annual_interpretation.recommended_remedies.map(
                  (remedy: any, idx: number) => (
                    <div key={idx} className="border-l-4 border-purple-500 pl-4 py-3">
                      <div className="font-semibold text-gray-900 mb-1">{remedy.category}</div>
                      <div className="text-sm text-gray-700 mb-2">{remedy.remedy}</div>
                      <div className="text-xs text-gray-600">Frequency: {remedy.frequency}</div>
                    </div>
                  )
                )}
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>

      {/* Chart Details */}
      <Card>
        <CardHeader>
          <CardTitle>Solar Return Chart Details</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div>
              <div className="text-sm text-gray-600 mb-1">Solar Return Time</div>
              <div className="font-semibold">
                {new Date(varshaphal.solar_return_chart.solar_return_time).toLocaleString()}
              </div>
            </div>
            <div>
              <div className="text-sm text-gray-600 mb-1">Varsha Lagna (Annual Ascendant)</div>
              <div className="font-semibold">
                {varshaphal.solar_return_chart.varsha_lagna.sign} •{' '}
                {varshaphal.solar_return_chart.varsha_lagna.degree_in_sign.toFixed(2)}°
              </div>
            </div>
            <div>
              <div className="text-sm text-gray-600 mb-1">Muntha</div>
              <div className="font-semibold">
                {varshaphal.solar_return_chart.muntha.sign} • Age{' '}
                {varshaphal.solar_return_chart.muntha.age}
              </div>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
