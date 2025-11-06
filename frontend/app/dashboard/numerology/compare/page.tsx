'use client'

import { useState } from 'react'
import { useMutation } from '@/lib/query'
import Link from 'next/link'
import { apiClient } from '@/lib/api'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { NumerologyCard } from '@/components/numerology/NumerologyCard'
import { ArrowLeft, Plus, X, Sparkles, TrendingUp, Award } from '@/components/icons'

interface ComparisonResult {
  name: string
  western?: {
    core_numbers: {
      life_path: { number: number; is_master: boolean; meaning?: string }
      expression: { number: number; is_master: boolean; meaning?: string }
      soul_urge: { number: number; is_master: boolean; meaning?: string }
      personality: { number: number; is_master: boolean; meaning?: string }
    }
  }
  vedic?: {
    psychic_number: { number: number; planet: string; meaning?: string }
    destiny_number: { number: number; planet: string; meaning?: string }
    name_number?: { number: number; meaning?: string }
  }
}

export default function NameComparisonPage() {
  const [birthDate, setBirthDate] = useState('')
  const [system, setSystem] = useState<'western' | 'vedic' | 'chaldean'>('western')
  const [names, setNames] = useState<string[]>(['', ''])
  const [comparisonResults, setComparisonResults] = useState<ComparisonResult[] | null>(null)

  const compareMutation = useMutation({
    mutationFn: async (data: { names: string[]; birth_date: string; system: string }) => {
      const response = await apiClient.compareNames(data)
      return response.data
    },
    onSuccess: (data) => {
      setComparisonResults(data.comparisons)
    },
    onError: (error: any) => {
      alert(error?.message || 'Failed to compare names')
    },
  })

  const addNameField = () => {
    if (names.length < 5) {
      setNames([...names, ''])
    }
  }

  const removeNameField = (index: number) => {
    if (names.length > 2) {
      setNames(names.filter((_, i) => i !== index))
    }
  }

  const updateName = (index: number, value: string) => {
    const updated = [...names]
    updated[index] = value
    setNames(updated)
  }

  const handleCompare = () => {
    const validNames = names.filter((n) => n.trim() !== '')
    if (validNames.length < 2) {
      alert('Please enter at least 2 names to compare')
      return
    }
    if (!birthDate) {
      alert('Please enter your birth date')
      return
    }
    compareMutation.mutate({
      names: validNames,
      birth_date: birthDate,
      system,
    })
  }

  const getBestName = (): string | null => {
    if (!comparisonResults || comparisonResults.length === 0) return null

    // Simple scoring: count master numbers and high-value numbers
    const scores = comparisonResults.map((result) => {
      let score = 0
      if (result.western) {
        const { life_path, expression, soul_urge, personality } = result.western.core_numbers
        if (life_path.is_master) score += 3
        if (expression.is_master) score += 2
        if (soul_urge.is_master) score += 2
        if (personality.is_master) score += 1

        // Favor numbers 1, 3, 5, 8, 9 (leadership, creativity, change, power, completion)
        const favorableNumbers = [1, 3, 5, 8, 9, 11, 22, 33]
        if (favorableNumbers.includes(life_path.number)) score += 2
        if (favorableNumbers.includes(expression.number)) score += 1
      }
      if (result.vedic) {
        // Favor certain planetary combinations
        const strongPlanets = ['Sun', 'Jupiter', 'Venus']
        if (strongPlanets.includes(result.vedic.psychic_number.planet)) score += 1
        if (strongPlanets.includes(result.vedic.destiny_number.planet)) score += 1
      }
      return score
    })

    const maxScore = Math.max(...scores)
    const bestIndex = scores.indexOf(maxScore)
    return comparisonResults[bestIndex].name
  }

  const bestName = getBestName()

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          <Link href="/dashboard/numerology">
            <Button variant="default" size="sm">
              <ArrowLeft className="w-4 h-4 mr-2" />
              Back
            </Button>
          </Link>
          <div>
            <h1 className="text-3xl font-bold text-gray-900 flex items-center gap-2">
              <TrendingUp className="w-8 h-8 text-purple-600" />
              Name Comparison Tool
            </h1>
            <p className="text-gray-600 mt-1">Compare different name spellings to find the best energy</p>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left: Input Form */}
        <div className="lg:col-span-1">
          <Card>
            <CardHeader>
              <CardTitle>Compare Names</CardTitle>
              <CardDescription>Enter 2-5 name variations to compare</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <Label htmlFor="birthDate">Birth Date</Label>
                <Input
                  id="birthDate"
                  type="date"
                  value={birthDate}
                  onChange={(e) => setBirthDate(e.target.value)}
                />
              </div>

              <div>
                <Label htmlFor="system">Numerology System</Label>
                <select
                  id="system"
                  className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background file:border-0 file:bg-transparent file:text-sm file:font-medium placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
                  value={system}
                  onChange={(e) => setSystem(e.target.value as 'western' | 'vedic' | 'chaldean')}
                >
                  <option value="western">Western (Pythagorean)</option>
                  <option value="vedic">Vedic (Chaldean)</option>
                </select>
              </div>

              <div className="space-y-2">
                <Label>Name Variations</Label>
                {names.map((name, index) => (
                  <div key={index} className="flex gap-2">
                    <Input
                      type="text"
                      placeholder={`Name ${index + 1}`}
                      value={name}
                      onChange={(e) => updateName(index, e.target.value)}
                    />
                    {names.length > 2 && (
                      <Button
                        variant="default"
                        size="sm"
                        onClick={() => removeNameField(index)}
                      >
                        <X className="w-4 h-4" />
                      </Button>
                    )}
                  </div>
                ))}
                {names.length < 5 && (
                  <Button variant="default" size="sm" onClick={addNameField} className="w-full">
                    <Plus className="w-4 h-4 mr-2" />
                    Add Name
                  </Button>
                )}
              </div>

              <Button
                onClick={handleCompare}
                disabled={compareMutation.isPending}
                className="w-full"
              >
                {compareMutation.isPending ? (
                  <>
                    <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin mr-2"></div>
                    Comparing...
                  </>
                ) : (
                  <>
                    <Sparkles className="w-4 h-4 mr-2" />
                    Compare Names
                  </>
                )}
              </Button>
            </CardContent>
          </Card>
        </div>

        {/* Right: Comparison Results */}
        <div className="lg:col-span-2">
          {!comparisonResults ? (
            <Card>
              <CardContent className="text-center py-12">
                <TrendingUp className="w-16 h-16 text-gray-300 mx-auto mb-4" />
                <h3 className="text-lg font-semibold mb-2">Compare Name Variations</h3>
                <p className="text-gray-600 mb-4">
                  Enter multiple spellings or variations of your name to see which has the best
                  numerological energy
                </p>
                <div className="text-sm text-gray-500">
                  <p>• Side-by-side number comparison</p>
                  <p>• Recommended best name</p>
                  <p>• Master number indicators</p>
                </div>
              </CardContent>
            </Card>
          ) : (
            <div className="space-y-6">
              {/* Best Name Recommendation */}
              {bestName && (
                <Card className="border-2 border-purple-500 bg-purple-50">
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2 text-purple-700">
                      <Award className="w-5 h-5" />
                      Recommended Name
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="text-2xl font-bold text-purple-900">{bestName}</div>
                    <p className="text-sm text-purple-700 mt-2">
                      Based on master numbers and favorable planetary influences
                    </p>
                  </CardContent>
                </Card>
              )}

              {/* Comparison Grid */}
              <div className="space-y-6">
                {comparisonResults.map((result, index) => (
                  <Card key={index} className={result.name === bestName ? 'border-2 border-purple-300' : ''}>
                    <CardHeader>
                      <CardTitle className="flex items-center justify-between">
                        <span>{result.name}</span>
                        {result.name === bestName && (
                          <span className="text-sm bg-purple-100 text-purple-700 px-3 py-1 rounded font-semibold">
                            Best Match
                          </span>
                        )}
                      </CardTitle>
                    </CardHeader>
                    <CardContent>
                      {result.western && (
                        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                          <div className="text-center">
                            <div className="text-xs text-gray-600 uppercase mb-1">Life Path</div>
                            <div className="flex items-center justify-center">
                              <div
                                className={`w-12 h-12 rounded-full flex items-center justify-center text-lg font-bold ${
                                  result.western.core_numbers.life_path.is_master
                                    ? 'bg-yellow-100 text-yellow-700'
                                    : 'bg-purple-100 text-purple-700'
                                }`}
                              >
                                {result.western.core_numbers.life_path.number}
                              </div>
                            </div>
                          </div>
                          <div className="text-center">
                            <div className="text-xs text-gray-600 uppercase mb-1">Expression</div>
                            <div className="flex items-center justify-center">
                              <div
                                className={`w-12 h-12 rounded-full flex items-center justify-center text-lg font-bold ${
                                  result.western.core_numbers.expression.is_master
                                    ? 'bg-yellow-100 text-yellow-700'
                                    : 'bg-purple-100 text-purple-700'
                                }`}
                              >
                                {result.western.core_numbers.expression.number}
                              </div>
                            </div>
                          </div>
                          <div className="text-center">
                            <div className="text-xs text-gray-600 uppercase mb-1">Soul Urge</div>
                            <div className="flex items-center justify-center">
                              <div
                                className={`w-12 h-12 rounded-full flex items-center justify-center text-lg font-bold ${
                                  result.western.core_numbers.soul_urge.is_master
                                    ? 'bg-yellow-100 text-yellow-700'
                                    : 'bg-purple-100 text-purple-700'
                                }`}
                              >
                                {result.western.core_numbers.soul_urge.number}
                              </div>
                            </div>
                          </div>
                          <div className="text-center">
                            <div className="text-xs text-gray-600 uppercase mb-1">Personality</div>
                            <div className="flex items-center justify-center">
                              <div
                                className={`w-12 h-12 rounded-full flex items-center justify-center text-lg font-bold ${
                                  result.western.core_numbers.personality.is_master
                                    ? 'bg-yellow-100 text-yellow-700'
                                    : 'bg-purple-100 text-purple-700'
                                }`}
                              >
                                {result.western.core_numbers.personality.number}
                              </div>
                            </div>
                          </div>
                        </div>
                      )}

                      {result.vedic && (
                        <div className="grid grid-cols-2 gap-4 mt-4">
                          <div>
                            <div className="text-xs text-gray-600 uppercase mb-1">Psychic ({result.vedic.psychic_number.planet})</div>
                            <div className="flex items-center gap-2">
                              <div className="w-10 h-10 rounded-full flex items-center justify-center text-lg font-bold bg-blue-100 text-blue-700">
                                {result.vedic.psychic_number.number}
                              </div>
                              <div className="text-xs text-gray-600">{result.vedic.psychic_number.meaning}</div>
                            </div>
                          </div>
                          <div>
                            <div className="text-xs text-gray-600 uppercase mb-1">Destiny ({result.vedic.destiny_number.planet})</div>
                            <div className="flex items-center gap-2">
                              <div className="w-10 h-10 rounded-full flex items-center justify-center text-lg font-bold bg-green-100 text-green-700">
                                {result.vedic.destiny_number.number}
                              </div>
                              <div className="text-xs text-gray-600">{result.vedic.destiny_number.meaning}</div>
                            </div>
                          </div>
                        </div>
                      )}
                    </CardContent>
                  </Card>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
