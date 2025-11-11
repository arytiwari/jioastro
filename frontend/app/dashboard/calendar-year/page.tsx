'use client'

import { useState } from 'react'
import { useQuery, useMutation } from '@/lib/query'
import { apiClient } from '@/lib/api'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Skeleton } from '@/components/ui/skeleton'
import { Calendar, Sun, Moon, Sparkles, AlertCircle, TrendingUp, TrendingDown, Star } from '@/components/icons'

export default function CalendarYearPage() {
  const currentYear = new Date().getFullYear()
  const [selectedProfileId, setSelectedProfileId] = useState<string>('')
  const [selectedYear, setSelectedYear] = useState<number>(currentYear)
  const [predictions, setPredictions] = useState<any>(null)
  const [isGenerating, setIsGenerating] = useState(false)

  // Fetch profiles
  const { data: profiles, isLoading: profilesLoading } = useQuery({
    queryKey: ['profiles'],
    queryFn: async () => {
      const response = await apiClient.getProfiles()
      return response.data
    },
  })

  // Set primary profile as default
  useState(() => {
    if (profiles && profiles.length > 0 && !selectedProfileId) {
      const primaryProfile = profiles.find((p: any) => p.is_primary) || profiles[0]
      setSelectedProfileId(primaryProfile.id)
    }
  })

  const handleGenerate = async () => {
    if (!selectedProfileId) {
      alert('Please select a profile first')
      return
    }

    setIsGenerating(true)
    try {
      const response = await apiClient.generateCalendarYear({
        profile_id: selectedProfileId,
        target_year: selectedYear,
      })
      setPredictions(response.data)
    } catch (error: any) {
      alert(error?.message || 'Failed to generate calendar year predictions')
    } finally {
      setIsGenerating(false)
    }
  }

  const getQualityColor = (quality: string) => {
    switch (quality.toLowerCase()) {
      case 'excellent':
        return 'bg-green-100 text-green-800 border-green-300'
      case 'very good':
        return 'bg-blue-100 text-blue-800 border-blue-300'
      case 'moderate':
        return 'bg-yellow-100 text-yellow-800 border-yellow-300'
      case 'challenging':
        return 'bg-orange-100 text-orange-800 border-orange-300'
      case 'difficult':
        return 'bg-red-100 text-red-800 border-red-300'
      default:
        return 'bg-gray-100 text-gray-800 border-gray-300'
    }
  }

  const getMonthColor = (quality: string) => {
    switch (quality.toLowerCase()) {
      case 'excellent':
        return 'border-l-4 border-green-500'
      case 'very good':
        return 'border-l-4 border-blue-500'
      case 'moderate':
        return 'border-l-4 border-yellow-500'
      case 'challenging':
        return 'border-l-4 border-orange-500'
      case 'difficult':
        return 'border-l-4 border-red-500'
      default:
        return 'border-l-4 border-gray-500'
    }
  }

  if (profilesLoading) {
    return (
      <div className="space-y-6">
        <Skeleton className="h-9 w-64 mb-2" />
        <Skeleton className="h-5 w-96" />
        <Card>
          <CardHeader>
            <Skeleton className="h-6 w-32" />
          </CardHeader>
          <CardContent>
            <Skeleton className="h-32 w-full" />
          </CardContent>
        </Card>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-gray-900 flex items-center gap-2">
          <Calendar className="w-8 h-8 text-jio-600" />
          Calendar Year Predictions
        </h1>
        <p className="text-gray-600 mt-2">
          Transit-based predictions for the calendar year (January 1 - December 31)
        </p>
        <div className="mt-3 p-3 bg-blue-50 border border-blue-200 rounded-lg flex items-start gap-2">
          <AlertCircle className="w-5 h-5 text-blue-600 mt-0.5 flex-shrink-0" />
          <div className="text-sm text-blue-800">
            <strong>Note:</strong> Calendar Year predictions run from Jan 1 to Dec 31. For birthday-to-birthday annual predictions, use{' '}
            <a href="/dashboard/varshaphal" className="underline hover:text-blue-900">
              Varshaphal (Solar Return)
            </a>.
          </div>
        </div>
      </div>

      {/* Generate Form */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Sparkles className="w-5 h-5" />
            Generate Year Predictions
          </CardTitle>
          <CardDescription>
            Select a birth profile and year to generate transit-based predictions
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {/* Profile Selection */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Select Profile
              </label>
              <select
                value={selectedProfileId}
                onChange={(e) => setSelectedProfileId(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-jio-500"
              >
                <option value="">Choose a profile...</option>
                {profiles?.map((profile: any) => (
                  <option key={profile.id} value={profile.id}>
                    {profile.name} {profile.is_primary && '(Primary)'}
                  </option>
                ))}
              </select>
            </div>

            {/* Year Selection */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Select Year
              </label>
              <select
                value={selectedYear}
                onChange={(e) => setSelectedYear(parseInt(e.target.value))}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-jio-500"
              >
                {Array.from({ length: 5 }, (_, i) => currentYear - 1 + i).map((year) => (
                  <option key={year} value={year}>
                    {year}
                  </option>
                ))}
              </select>
            </div>
          </div>

          <Button
            onClick={handleGenerate}
            disabled={!selectedProfileId || isGenerating}
            className="w-full md:w-auto"
          >
            {isGenerating ? (
              <>
                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2" />
                Generating...
              </>
            ) : (
              <>
                <Sparkles className="w-4 h-4 mr-2" />
                Generate Predictions
              </>
            )}
          </Button>
        </CardContent>
      </Card>

      {/* Predictions Display */}
      {predictions && (
        <div className="space-y-6">
          {/* Year Overview */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Star className="w-5 h-5 text-yellow-600" />
                Year {selectedYear} Overview
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <div className={`inline-block px-3 py-1 rounded-full text-sm font-medium ${getQualityColor(predictions.year_overview.overall_quality)}`}>
                  Overall Quality: {predictions.year_overview.overall_quality}
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {/* Opportunities */}
                <div>
                  <h4 className="font-semibold text-gray-900 mb-2 flex items-center gap-2">
                    <TrendingUp className="w-4 h-4 text-green-600" />
                    Key Opportunities
                  </h4>
                  <ul className="space-y-1">
                    {predictions.year_overview.key_opportunities.map((opp: string, idx: number) => (
                      <li key={idx} className="text-sm text-gray-700 flex items-start gap-2">
                        <span className="text-green-600">•</span>
                        {opp}
                      </li>
                    ))}
                  </ul>
                </div>

                {/* Challenges */}
                <div>
                  <h4 className="font-semibold text-gray-900 mb-2 flex items-center gap-2">
                    <TrendingDown className="w-4 h-4 text-orange-600" />
                    Main Challenges
                  </h4>
                  <ul className="space-y-1">
                    {predictions.year_overview.main_challenges.map((chal: string, idx: number) => (
                      <li key={idx} className="text-sm text-gray-700 flex items-start gap-2">
                        <span className="text-orange-600">•</span>
                        {chal}
                      </li>
                    ))}
                  </ul>
                </div>
              </div>

              {/* Important Themes */}
              <div>
                <h4 className="font-semibold text-gray-900 mb-2">Important Themes</h4>
                <div className="flex flex-wrap gap-2">
                  {predictions.year_overview.important_themes.map((theme: string, idx: number) => (
                    <span key={idx} className="px-3 py-1 bg-purple-100 text-purple-800 rounded-full text-sm">
                      {theme}
                    </span>
                  ))}
                </div>
              </div>

              {/* Remedies */}
              {predictions.year_overview.recommended_remedies.length > 0 && (
                <div>
                  <h4 className="font-semibold text-gray-900 mb-2">Recommended Remedies</h4>
                  <ul className="space-y-1">
                    {predictions.year_overview.recommended_remedies.map((remedy: string, idx: number) => (
                      <li key={idx} className="text-sm text-gray-700 flex items-start gap-2">
                        <span className="text-jio-600">✓</span>
                        {remedy}
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </CardContent>
          </Card>

          {/* Best and Worst Months */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Best Months */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2 text-green-700">
                  <TrendingUp className="w-5 h-5" />
                  Best Months
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                {predictions.best_months.map((month: any, idx: number) => (
                  <div key={idx} className="p-3 bg-green-50 border border-green-200 rounded-lg">
                    <div className="font-semibold text-green-900">{month.month}</div>
                    <div className="text-sm text-green-700 mt-1">{month.reason}</div>
                    <div className="text-sm text-gray-700 mt-2 italic">{month.advice}</div>
                  </div>
                ))}
              </CardContent>
            </Card>

            {/* Worst Months */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2 text-orange-700">
                  <TrendingDown className="w-5 h-5" />
                  Challenging Months
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                {predictions.worst_months.map((month: any, idx: number) => (
                  <div key={idx} className="p-3 bg-orange-50 border border-orange-200 rounded-lg">
                    <div className="font-semibold text-orange-900">{month.month}</div>
                    <div className="text-sm text-orange-700 mt-1">{month.reason}</div>
                    <div className="text-sm text-gray-700 mt-2 italic">{month.advice}</div>
                  </div>
                ))}
              </CardContent>
            </Card>
          </div>

          {/* Monthly Predictions */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Calendar className="w-5 h-5" />
                Monthly Predictions
              </CardTitle>
              <CardDescription>
                Detailed month-by-month analysis for {selectedYear}
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {predictions.monthly_predictions.map((month: any, idx: number) => (
                  <div key={idx} className={`p-4 bg-white border rounded-lg ${getMonthColor(month.quality)}`}>
                    <div className="flex items-center justify-between mb-2">
                      <h4 className="font-semibold text-gray-900">{month.month}</h4>
                      <span className={`px-2 py-0.5 rounded text-xs font-medium ${getQualityColor(month.quality)}`}>
                        {month.quality}
                      </span>
                    </div>

                    <div className="text-sm text-gray-600 mb-2">
                      Sun in {month.sun_sign}
                    </div>

                    <div className="space-y-2 text-sm">
                      <div>
                        <div className="font-medium text-gray-700">Key Themes:</div>
                        <ul className="ml-4 text-gray-600">
                          {month.key_themes.slice(0, 2).map((theme: string, i: number) => (
                            <li key={i} className="list-disc">{theme}</li>
                          ))}
                        </ul>
                      </div>

                      <div className="pt-2 border-t border-gray-200 italic text-gray-700">
                        {month.advice}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>

          {/* Major Transits */}
          {predictions.major_transits.length > 0 && (
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Sun className="w-5 h-5 text-orange-600" />
                  Major Planetary Transits
                </CardTitle>
                <CardDescription>
                  Significant planetary movements during {selectedYear}
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  {predictions.major_transits.map((transit: any, idx: number) => (
                    <div key={idx} className="p-4 bg-gray-50 border border-gray-200 rounded-lg">
                      <div className="flex items-start justify-between mb-2">
                        <div>
                          <span className="font-semibold text-gray-900">{transit.planet}</span>
                          <span className="text-sm text-gray-600 ml-2">→ {transit.to_sign}</span>
                        </div>
                        <span className={`px-2 py-0.5 rounded text-xs font-medium ${
                          transit.significance === 'High' ? 'bg-red-100 text-red-800' :
                          transit.significance === 'Medium' ? 'bg-yellow-100 text-yellow-800' :
                          'bg-gray-100 text-gray-800'
                        }`}>
                          {transit.significance}
                        </span>
                      </div>
                      <div className="text-sm text-gray-600 mb-1">{transit.date}</div>
                      <div className="text-sm text-gray-700">{transit.effect}</div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          )}

          {/* Eclipses */}
          {predictions.eclipses.length > 0 && (
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Moon className="w-5 h-5 text-purple-600" />
                  Eclipse Predictions
                </CardTitle>
                <CardDescription>
                  Solar and Lunar eclipses in {selectedYear}
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  {predictions.eclipses.map((eclipse: any, idx: number) => (
                    <div key={idx} className="p-4 bg-purple-50 border border-purple-200 rounded-lg">
                      <div className="flex items-start justify-between mb-2">
                        <div>
                          <span className="font-semibold text-purple-900">{eclipse.type} Eclipse</span>
                          <span className="text-sm text-purple-700 ml-2">({eclipse.eclipse_type})</span>
                        </div>
                        <span className="text-sm text-gray-600">{eclipse.date}</span>
                      </div>
                      <div className="text-sm text-purple-700 mb-2">{eclipse.effect}</div>
                      <div className="mt-2 pt-2 border-t border-purple-200">
                        <div className="font-medium text-sm text-purple-900 mb-1">Recommendations:</div>
                        <ul className="space-y-1">
                          {eclipse.recommendations.map((rec: string, i: number) => (
                            <li key={i} className="text-sm text-gray-700 flex items-start gap-2">
                              <span className="text-purple-600">•</span>
                              {rec}
                            </li>
                          ))}
                        </ul>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          )}
        </div>
      )}

      {/* Empty State */}
      {!predictions && !isGenerating && (
        <Card>
          <CardContent className="py-12 text-center">
            <Calendar className="w-16 h-16 text-gray-400 mx-auto mb-4" />
            <p className="text-gray-600">
              Select a profile and year to generate calendar year predictions
            </p>
          </CardContent>
        </Card>
      )}
    </div>
  )
}
