"use client"

import { useState, useEffect } from 'react'
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
  DialogBody,
  DialogFooter
} from '@/components/ui/dialog'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import {
  Sparkles, Clock, Lightbulb, BookOpen, User, Calendar,
  TrendingUp, Award, Star
} from 'lucide-react'
import { apiClient } from '@/lib/api'

interface Yoga {
  name: string
  description: string
  strength: string
  category: string
}

interface YogaTiming {
  yoga_name: string
  activation_status: string
  current_strength: string
  dasha_activation_periods: Array<{
    planet: string
    start_date: string
    end_date: string
    period_type: string
    intensity: string
  }>
  peak_periods: string[]
  general_activation_age: string
  recommendations: string[]
}

interface YogaDetailsModalProps {
  yoga: Yoga | null
  open: boolean
  onOpenChange: (open: boolean) => void
  profileId?: string
}

// Historical examples data for major yogas
const HISTORICAL_EXAMPLES: Record<string, Array<{ name: string; description: string }>> = {
  "Hamsa Yoga": [
    { name: "Mahatma Gandhi", description: "Jupiter in Kendra gave him moral authority, spiritual wisdom, and influence over masses" },
    { name: "Albert Einstein", description: "Strong Jupiter in Kendra blessed him with profound wisdom and revolutionary insights" }
  ],
  "Sasha Yoga": [
    { name: "Napoleon Bonaparte", description: "Saturn in Kendra gave him discipline, organizational skills, and lasting legacy" },
    { name: "Abraham Lincoln", description: "Strong Saturn made him persevere through hardships to achieve lasting reforms" }
  ],
  "Ruchaka Yoga": [
    { name: "Alexander the Great", description: "Mars in Kendra gave him exceptional courage, military genius, and conquering spirit" },
    { name: "Winston Churchill", description: "Strong Mars blessed him with wartime leadership and indomitable will" }
  ],
  "Bhadra Yoga": [
    { name: "William Shakespeare", description: "Mercury in Kendra blessed him with unparalleled literary genius and communication skills" },
    { name: "Isaac Newton", description: "Strong Mercury gave him analytical brilliance and scientific breakthroughs" }
  ],
  "Malavya Yoga": [
    { name: "Cleopatra", description: "Venus in Kendra gave her beauty, charm, diplomatic skills, and luxurious lifestyle" },
    { name: "Leonardo da Vinci", description: "Strong Venus blessed him with artistic genius and aesthetic sensibility" }
  ],
  "Gaja Kesari Yoga": [
    { name: "Swami Vivekananda", description: "Moon-Jupiter conjunction gave him spiritual wisdom and mass influence" },
    { name: "Dr. APJ Abdul Kalam", description: "Strong Jupiter-Moon combination blessed him with knowledge, humility, and public respect" }
  ],
  "Budhaditya Yoga": [
    { name: "Steve Jobs", description: "Sun-Mercury conjunction gave him innovative thinking and business acumen" },
    { name: "Benjamin Franklin", description: "Strong Mercury-Sun gave him intellectual brilliance and diplomatic success" }
  ],
  "Raj Yoga": [
    { name: "Queen Elizabeth I", description: "Lord of Kendra-Trikona combination gave her long and prosperous reign" },
    { name: "Akbar the Great", description: "Strong Raj Yoga blessed him with imperial power and enlightened rule" }
  ]
}

// Remedies data for different yoga types
const YOGA_REMEDIES: Record<string, string[]> = {
  "Weak": [
    "Strengthen the yoga-forming planets through gemstones (consult an astrologer)",
    "Chant mantras of the yoga-forming planets daily",
    "Perform charity related to the planets involved",
    "Observe fasts on the days ruled by the planets"
  ],
  "Combustion": [
    "Chant Aditya Hridayam (Sun hymn) daily to pacify combustion",
    "Offer water to the Sun every morning",
    "Donate to reduce the malefic effects of combustion",
    "Wear gemstones of the combusted planet (after consultation)"
  ],
  "Debilitated": [
    "Chant Navgraha mantras to balance planetary energies",
    "Perform remedies for the debilitated planet specifically",
    "Strengthen the dispositor (sign lord) of the debilitated planet",
    "Focus on the positive significations of the planet"
  ],
  "General": [
    "Maintain regular spiritual practices (meditation, yoga, prayer)",
    "Practice virtues associated with the yoga (e.g., generosity for Dhana Yoga)",
    "Seek blessings from elders and teachers",
    "Perform good deeds aligned with the yoga's significations",
    "Study and embody the principles represented by the yoga"
  ],
  "Pancha Mahapurusha": [
    "Honor the deity associated with the planet (Mars: Hanuman, Jupiter: Brihaspati, etc.)",
    "Practice the virtues of the planet (Mars: courage, Jupiter: wisdom, etc.)",
    "Wear the gemstone of the planet in the correct finger",
    "Chant the planet's mantra 108 times daily",
    "Observe the planet's vrata (fast) on its day"
  ]
}

// Strength color configuration
const STRENGTH_CONFIG: Record<string, { color: string; badge: string; icon: any }> = {
  'Very Strong': { color: 'text-red-700', badge: 'bg-red-100 text-red-800 border-red-300', icon: TrendingUp },
  'Strong': { color: 'text-orange-700', badge: 'bg-orange-100 text-orange-800 border-orange-300', icon: Award },
  'Medium': { color: 'text-blue-700', badge: 'bg-blue-100 text-blue-800 border-blue-300', icon: Star },
  'Weak': { color: 'text-gray-700', badge: 'bg-gray-100 text-gray-700 border-gray-300', icon: Sparkles },
}

export function YogaDetailsModal({ yoga, open, onOpenChange, profileId }: YogaDetailsModalProps) {
  const [timing, setTiming] = useState<YogaTiming | null>(null)
  const [loadingTiming, setLoadingTiming] = useState(false)
  const [activeTab, setActiveTab] = useState('overview')

  useEffect(() => {
    if (open && yoga && profileId) {
      fetchYogaTiming()
    }
  }, [open, yoga, profileId])

  const fetchYogaTiming = async () => {
    if (!yoga || !profileId) return

    setLoadingTiming(true)
    try {
      // Call API to get yoga timing information
      const response = await apiClient.get(`/enhancements/yoga-timing/${profileId}`, {
        params: { yoga_name: yoga.name }
      })
      setTiming(response.data)
    } catch (error) {
      console.error('Failed to fetch yoga timing:', error)
    } finally {
      setLoadingTiming(false)
    }
  }

  if (!yoga) return null

  const strengthConfig = STRENGTH_CONFIG[yoga.strength] || STRENGTH_CONFIG['Medium']
  const StrengthIcon = strengthConfig.icon
  const examples = HISTORICAL_EXAMPLES[yoga.name] || []
  const remedies = YOGA_REMEDIES[yoga.category] || YOGA_REMEDIES["General"]

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent>
        <DialogHeader onClose={() => onOpenChange(false)}>
          <div>
            <div className="flex items-center gap-2 mb-2">
              <StrengthIcon className={`w-6 h-6 ${strengthConfig.color}`} />
              <DialogTitle>{yoga.name}</DialogTitle>
            </div>
            <div className="flex items-center gap-2">
              <Badge className={`${strengthConfig.badge} border`}>
                {yoga.strength}
              </Badge>
              <Badge variant="outline">{yoga.category}</Badge>
            </div>
          </div>
        </DialogHeader>

        <DialogBody>
          <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
            <TabsList className="grid w-full grid-cols-4 mb-4">
              <TabsTrigger value="overview" className="text-xs sm:text-sm">
                <BookOpen className="w-4 h-4 mr-1" />
                Overview
              </TabsTrigger>
              <TabsTrigger value="examples" className="text-xs sm:text-sm">
                <User className="w-4 h-4 mr-1" />
                Examples
              </TabsTrigger>
              <TabsTrigger value="timing" className="text-xs sm:text-sm">
                <Clock className="w-4 h-4 mr-1" />
                Timing
              </TabsTrigger>
              <TabsTrigger value="remedies" className="text-xs sm:text-sm">
                <Lightbulb className="w-4 h-4 mr-1" />
                Remedies
              </TabsTrigger>
            </TabsList>

            {/* Overview Tab */}
            <TabsContent value="overview" className="space-y-4">
              <Card>
                <CardHeader>
                  <CardTitle className="text-lg">Description</CardTitle>
                </CardHeader>
                <CardContent>
                  <p className="text-gray-700 leading-relaxed">{yoga.description}</p>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle className="text-lg">Key Points</CardTitle>
                </CardHeader>
                <CardContent className="space-y-2">
                  <div className="flex items-start gap-2">
                    <div className="w-1.5 h-1.5 bg-jio-600 rounded-full mt-2" />
                    <p className="text-sm text-gray-700">
                      <strong>Category:</strong> {yoga.category}
                    </p>
                  </div>
                  <div className="flex items-start gap-2">
                    <div className="w-1.5 h-1.5 bg-jio-600 rounded-full mt-2" />
                    <p className="text-sm text-gray-700">
                      <strong>Current Strength:</strong> {yoga.strength}
                    </p>
                  </div>
                  <div className="flex items-start gap-2">
                    <div className="w-1.5 h-1.5 bg-jio-600 rounded-full mt-2" />
                    <p className="text-sm text-gray-700">
                      <strong>Nature:</strong> This yoga influences the {yoga.category.toLowerCase()} aspects of life
                    </p>
                  </div>
                </CardContent>
              </Card>
            </TabsContent>

            {/* Historical Examples Tab */}
            <TabsContent value="examples" className="space-y-4">
              {examples.length > 0 ? (
                <>
                  <p className="text-sm text-gray-600 mb-3">
                    Historical figures who benefited from {yoga.name}:
                  </p>
                  {examples.map((example, idx) => (
                    <Card key={idx}>
                      <CardHeader>
                        <CardTitle className="text-lg flex items-center gap-2">
                          <User className="w-5 h-5 text-jio-600" />
                          {example.name}
                        </CardTitle>
                      </CardHeader>
                      <CardContent>
                        <p className="text-sm text-gray-700">{example.description}</p>
                      </CardContent>
                    </Card>
                  ))}
                </>
              ) : (
                <Card>
                  <CardContent className="py-8 text-center">
                    <User className="w-12 h-12 text-gray-300 mx-auto mb-3" />
                    <p className="text-gray-500">
                      No historical examples available for this yoga yet.
                    </p>
                  </CardContent>
                </Card>
              )}
            </TabsContent>

            {/* Timing Tab */}
            <TabsContent value="timing" className="space-y-4">
              {loadingTiming ? (
                <Card>
                  <CardContent className="py-8 text-center">
                    <div className="w-8 h-8 border-4 border-jio-600 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
                    <p className="text-gray-600">Calculating yoga timing...</p>
                  </CardContent>
                </Card>
              ) : timing ? (
                <>
                  <Card>
                    <CardHeader>
                      <CardTitle className="text-lg">Activation Information</CardTitle>
                    </CardHeader>
                    <CardContent className="space-y-3">
                      <div>
                        <p className="text-sm font-semibold text-gray-900">Status</p>
                        <p className="text-sm text-gray-700">{timing.activation_status}</p>
                      </div>
                      {timing.general_activation_age && (
                        <div>
                          <p className="text-sm font-semibold text-gray-900">General Activation Age</p>
                          <p className="text-sm text-gray-700">{timing.general_activation_age}</p>
                        </div>
                      )}
                    </CardContent>
                  </Card>

                  {timing.dasha_activation_periods && timing.dasha_activation_periods.length > 0 && (
                    <Card>
                      <CardHeader>
                        <CardTitle className="text-lg flex items-center gap-2">
                          <Calendar className="w-5 h-5 text-jio-600" />
                          Dasha Activation Periods
                        </CardTitle>
                      </CardHeader>
                      <CardContent>
                        <div className="space-y-3">
                          {timing.dasha_activation_periods.map((period, idx) => (
                            <div key={idx} className="p-3 bg-jio-50 rounded-lg border border-jio-200">
                              <div className="flex items-center justify-between mb-1">
                                <p className="font-semibold text-gray-900">{period.planet} {period.period_type}</p>
                                <Badge className="bg-jio-100 text-jio-800">
                                  {period.intensity} Intensity
                                </Badge>
                              </div>
                              <p className="text-sm text-gray-600">
                                {period.start_date} to {period.end_date}
                              </p>
                            </div>
                          ))}
                        </div>
                      </CardContent>
                    </Card>
                  )}

                  {timing.recommendations && timing.recommendations.length > 0 && (
                    <Card>
                      <CardHeader>
                        <CardTitle className="text-lg">Recommendations</CardTitle>
                      </CardHeader>
                      <CardContent>
                        <ul className="space-y-2">
                          {timing.recommendations.map((rec, idx) => (
                            <li key={idx} className="flex items-start gap-2 text-sm text-gray-700">
                              <span className="text-green-600 mt-1">✓</span>
                              <span>{rec}</span>
                            </li>
                          ))}
                        </ul>
                      </CardContent>
                    </Card>
                  )}
                </>
              ) : (
                <Card>
                  <CardContent className="py-8 text-center">
                    <Clock className="w-12 h-12 text-gray-300 mx-auto mb-3" />
                    <p className="text-gray-500">
                      Timing information is not available. Ensure you have selected a profile.
                    </p>
                  </CardContent>
                </Card>
              )}
            </TabsContent>

            {/* Remedies Tab */}
            <TabsContent value="remedies" className="space-y-4">
              <Card>
                <CardHeader>
                  <CardTitle className="text-lg flex items-center gap-2">
                    <Lightbulb className="w-5 h-5 text-green-600" />
                    Strengthening Remedies
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <ul className="space-y-2">
                    {remedies.map((remedy, idx) => (
                      <li key={idx} className="flex items-start gap-2 text-sm text-gray-700">
                        <span className="text-green-600 mt-1">✓</span>
                        <span>{remedy}</span>
                      </li>
                    ))}
                  </ul>
                </CardContent>
              </Card>

              <div className="p-4 bg-amber-50 border border-amber-200 rounded-lg">
                <p className="text-xs text-amber-900">
                  <strong>Note:</strong> These are general remedies. For personalized recommendations,
                  consult with a qualified Vedic astrologer who can analyze your complete birth chart.
                </p>
              </div>
            </TabsContent>
          </Tabs>
        </DialogBody>

        <DialogFooter>
          <Button variant="outline" onClick={() => onOpenChange(false)}>
            Close
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}
