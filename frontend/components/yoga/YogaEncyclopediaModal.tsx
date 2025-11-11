'use client'

import { useState } from 'react'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Badge } from '@/components/ui/badge'
import { Card, CardContent } from '@/components/ui/card'
import { apiClient } from '@/lib/api'
import {
  Search,
  Loader2,
  AlertCircle,
  Book,
  Sparkles,
  Calendar,
  Target,
  XCircle,
} from 'lucide-react'

interface YogaInfo {
  description: string
  category: string
  bphs_category: string
  bphs_section: string
  bphs_ref: string
  effects: string
  activation_age: string
  life_areas: string[]
  cancellation_conditions: string[]
}

interface YogaEncyclopediaModalProps {
  trigger?: React.ReactNode
}

export function YogaEncyclopediaModal({ trigger }: YogaEncyclopediaModalProps) {
  const [open, setOpen] = useState(false)
  const [searchTerm, setSearchTerm] = useState('')
  const [yogaInfo, setYogaInfo] = useState<YogaInfo | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [searched, setSearched] = useState(false)

  const handleSearch = async (yogaNameOverride?: string) => {
    const yogaToSearch = yogaNameOverride || searchTerm
    if (!yogaToSearch.trim()) {
      setError('Please enter a yoga name')
      return
    }

    try {
      setLoading(true)
      setError(null)
      setSearched(true)
      const response = await apiClient.lookupYoga(yogaToSearch.trim())
      setYogaInfo(response.data.yoga_info)
    } catch (err: any) {
      console.error('Failed to lookup yoga:', err)
      if (err.status === 404) {
        setError(`Yoga "${yogaToSearch}" not found. Try searching for: Gajakesari Yoga, Ruchaka Yoga, Raj Yoga, Dhana Yoga, etc.`)
      } else {
        setError(err.message || 'Failed to search for yoga')
      }
      setYogaInfo(null)
    } finally {
      setLoading(false)
    }
  }

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      handleSearch()
    }
  }

  const resetSearch = () => {
    setSearchTerm('')
    setYogaInfo(null)
    setError(null)
    setSearched(false)
  }

  const popularYogas = [
    'Gajakesari Yoga',
    'Ruchaka Yoga',
    'Hamsa Yoga',
    'Bhadra Yoga',
    'Malavya Yoga',
    'Sasa Yoga',
    'Raj Yoga',
    'Dhana Yoga',
    'Dhana from Moon Yoga',
    'Neecha Bhanga Raj Yoga',
    'Kala Sarpa Yoga',
    'Kedāra Yoga',
    'Vīṇā Yoga',
  ]

  const categoryColors: Record<string, string> = {
    'Major Positive Yogas': 'bg-emerald-100 text-emerald-800 border-emerald-300',
    'Standard Yogas': 'bg-blue-100 text-blue-800 border-blue-300',
    'Major Challenges': 'bg-red-100 text-red-800 border-red-300',
    'Minor Yogas & Subtle Influences': 'bg-purple-100 text-purple-800 border-purple-300',
    'Non-BPHS (Practical)': 'bg-gray-100 text-gray-800 border-gray-300',
  }

  return (
    <>
      {/* Trigger button */}
      <div onClick={() => setOpen(true)}>
        {trigger || (
          <Button variant="outline">
            <Search className="h-4 w-4 mr-2" />
            Yoga Encyclopedia
          </Button>
        )}
      </div>

      {/* Dialog */}
      <Dialog open={open} onOpenChange={setOpen}>
        <DialogContent className="max-w-3xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2 text-xl">
            <Book className="h-5 w-5 text-purple-600" />
            Yoga Encyclopedia
          </DialogTitle>
          <DialogDescription>
            Search for detailed information about any classical or practical yoga
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-6">
          {/* Search Box */}
          <div className="space-y-3">
            <div className="flex gap-2">
              <div className="relative flex-1">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
                <Input
                  placeholder="Enter yoga name (e.g., Gajakesari Yoga, Ruchaka Yoga)"
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  onKeyPress={handleKeyPress}
                  className="pl-10"
                  disabled={loading}
                />
              </div>
              <Button onClick={handleSearch} disabled={loading || !searchTerm.trim()}>
                {loading ? (
                  <Loader2 className="h-4 w-4 animate-spin" />
                ) : (
                  <>
                    <Search className="h-4 w-4 mr-2" />
                    Search
                  </>
                )}
              </Button>
              {searched && (
                <Button variant="outline" onClick={resetSearch}>
                  <XCircle className="h-4 w-4" />
                </Button>
              )}
            </div>

            {/* Popular Yogas */}
            {!searched && (
              <div>
                <p className="text-sm text-gray-600 mb-2">Popular yogas:</p>
                <div className="flex flex-wrap gap-2">
                  {popularYogas.map((yoga) => (
                    <Badge
                      key={yoga}
                      variant="outline"
                      className="cursor-pointer hover:bg-purple-50 hover:border-purple-300"
                      onClick={() => {
                        setSearchTerm(yoga)
                        handleSearch(yoga)
                      }}
                    >
                      {yoga}
                    </Badge>
                  ))}
                </div>
              </div>
            )}
          </div>

          {/* Error State */}
          {error && (
            <Card className="border-red-200 bg-red-50">
              <CardContent className="pt-6">
                <div className="flex items-start gap-3">
                  <AlertCircle className="h-5 w-5 text-red-600 mt-0.5 shrink-0" />
                  <div>
                    <p className="font-medium text-red-900">Search failed</p>
                    <p className="text-sm text-red-700 mt-1">{error}</p>
                  </div>
                </div>
              </CardContent>
            </Card>
          )}

          {/* Yoga Information */}
          {yogaInfo && (
            <div className="space-y-4">
              {/* Header */}
              <Card className="border-purple-200 bg-gradient-to-r from-purple-50 to-indigo-50">
                <CardContent className="pt-6">
                  <div className="space-y-3">
                    <div>
                      <h2 className="text-2xl font-bold text-gray-900 mb-2">{searchTerm}</h2>
                      <div className="flex flex-wrap gap-2">
                        <Badge
                          variant="outline"
                          className={categoryColors[yogaInfo.bphs_category] || 'bg-gray-100 text-gray-800'}
                        >
                          {yogaInfo.bphs_category}
                        </Badge>
                        <Badge variant="outline" className="bg-white text-purple-700 border-purple-300">
                          <Book className="h-3 w-3 mr-1" />
                          {yogaInfo.bphs_ref}
                        </Badge>
                        <Badge variant="outline" className="bg-white text-gray-700 border-gray-300">
                          {yogaInfo.bphs_section}
                        </Badge>
                      </div>
                    </div>
                    <p className="text-gray-700 leading-relaxed">{yogaInfo.description}</p>
                  </div>
                </CardContent>
              </Card>

              {/* Effects */}
              <Card>
                <CardContent className="pt-6">
                  <h3 className="font-semibold text-gray-900 mb-3 flex items-center gap-2">
                    <Sparkles className="h-4 w-4 text-amber-600" />
                    Effects & Benefits
                  </h3>
                  <p className="text-gray-700 leading-relaxed">{yogaInfo.effects}</p>
                </CardContent>
              </Card>

              {/* Activation Age */}
              <Card>
                <CardContent className="pt-6">
                  <h3 className="font-semibold text-gray-900 mb-3 flex items-center gap-2">
                    <Calendar className="h-4 w-4 text-blue-600" />
                    Activation Period
                  </h3>
                  <p className="text-gray-700">
                    Typically activates during: <strong>{yogaInfo.activation_age}</strong>
                  </p>
                </CardContent>
              </Card>

              {/* Life Areas */}
              <Card>
                <CardContent className="pt-6">
                  <h3 className="font-semibold text-gray-900 mb-3 flex items-center gap-2">
                    <Target className="h-4 w-4 text-purple-600" />
                    Life Areas Affected
                  </h3>
                  <div className="flex flex-wrap gap-2">
                    {yogaInfo.life_areas.map((area, index) => (
                      <Badge key={index} variant="secondary" className="bg-purple-100 text-purple-800">
                        {area}
                      </Badge>
                    ))}
                  </div>
                </CardContent>
              </Card>

              {/* Cancellation Conditions */}
              <Card className="border-amber-200 bg-amber-50">
                <CardContent className="pt-6">
                  <h3 className="font-semibold text-gray-900 mb-3 flex items-center gap-2">
                    <AlertCircle className="h-4 w-4 text-amber-600" />
                    Cancellation Conditions (Bhanga)
                  </h3>
                  <p className="text-sm text-gray-600 mb-3">
                    The yoga may be cancelled or weakened if:
                  </p>
                  <ul className="space-y-2">
                    {yogaInfo.cancellation_conditions.map((condition, index) => (
                      <li key={index} className="flex items-start gap-2 text-sm text-gray-700">
                        <span className="text-amber-600 mt-1">•</span>
                        <span>{condition}</span>
                      </li>
                    ))}
                  </ul>
                </CardContent>
              </Card>

              {/* Category Note */}
              <Card className="border-gray-200 bg-gray-50">
                <CardContent className="pt-6">
                  <p className="text-xs text-gray-600">
                    <strong>Category:</strong> {yogaInfo.category} •{' '}
                    <strong>Classification:</strong> {yogaInfo.bphs_category}
                    {yogaInfo.bphs_category === 'Non-BPHS (Practical)' && (
                      <span className="ml-1">(Modern analysis, not from classical BPHS text)</span>
                    )}
                  </p>
                </CardContent>
              </Card>
            </div>
          )}

          {/* Empty State */}
          {!yogaInfo && !error && !loading && searched && (
            <div className="text-center py-8">
              <Search className="h-12 w-12 text-gray-300 mx-auto mb-4" />
              <p className="text-gray-600">No results found. Try a different yoga name.</p>
            </div>
          )}
        </div>
      </DialogContent>
    </Dialog>
    </>
  )
}
