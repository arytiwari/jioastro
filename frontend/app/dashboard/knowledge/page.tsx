'use client'

import { KnowledgeBase } from '@/components/vedic/KnowledgeBase'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { BookOpen } from 'lucide-react'

export default function KnowledgeBasePage() {
  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <div className="flex items-center gap-3 mb-2">
          <BookOpen className="w-8 h-8 text-jio-600" />
          <h1 className="text-3xl font-bold text-gray-900">Vedic Astrology Knowledge Base</h1>
        </div>
        <p className="text-gray-600">
          Learn about the fundamental concepts of Vedic astrology
        </p>
      </div>

      {/* Introduction Card */}
      <Card className="bg-gradient-to-r from-jio-50 to-blue-50 border-jio-200">
        <CardHeader>
          <CardTitle className="text-jio-900">Welcome to Vedic Wisdom</CardTitle>
          <CardDescription className="text-jio-700">
            Explore the ancient science of Jyotish (Vedic Astrology)
          </CardDescription>
        </CardHeader>
        <CardContent>
          <p className="text-sm text-gray-700 leading-relaxed">
            Vedic astrology, also known as Jyotish (the science of light), is an ancient system
            of astrology that originated in India over 5,000 years ago. It provides insights into
            your personality, relationships, career, health, and spiritual path based on the precise
            positions of planets at your birth.
          </p>
          <p className="text-sm text-gray-700 leading-relaxed mt-3">
            Use this knowledge base to understand the meaning of planets, houses, yogas, nakshatras,
            and dashas in your birth chart. Each concept is explained in clear, accessible language.
          </p>
        </CardContent>
      </Card>

      {/* Knowledge Base Component */}
      <KnowledgeBase />

      {/* Additional Resources */}
      <Card>
        <CardHeader>
          <CardTitle>How to Use Your Chart</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4 text-sm text-gray-700">
            <div>
              <h4 className="font-semibold text-gray-900 mb-1">1. Start with the Basics</h4>
              <p>
                Learn about the 9 planets (Grahas) and their significations. Each planet represents
                different aspects of life and personality.
              </p>
            </div>
            <div>
              <h4 className="font-semibold text-gray-900 mb-1">2. Understand the Houses</h4>
              <p>
                The 12 houses (Bhavas) represent different life areas from self to spirituality.
                Planets placed in different houses influence those life areas.
              </p>
            </div>
            <div>
              <h4 className="font-semibold text-gray-900 mb-1">3. Look for Yogas</h4>
              <p>
                Yogas are special planetary combinations that create specific results in life.
                They can indicate talents, challenges, or opportunities.
              </p>
            </div>
            <div>
              <h4 className="font-semibold text-gray-900 mb-1">4. Check Your Dasha</h4>
              <p>
                Your current Dasha (planetary period) shows which planet's energy is most active
                in your life right now and influences current life events.
              </p>
            </div>
            <div>
              <h4 className="font-semibold text-gray-900 mb-1">5. Explore Nakshatras</h4>
              <p>
                Nakshatras (lunar mansions) add deeper nuance to planetary positions and reveal
                subtle psychological patterns.
              </p>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Attribution */}
      <Card className="border-jio-200 bg-jio-50">
        <CardContent className="py-4">
          <p className="text-xs text-gray-600 text-center">
            Based on classical Vedic astrology texts and principles. Calculations powered by{' '}
            <a href="https://vedastro.org" target="_blank" rel="noopener noreferrer" className="font-semibold text-jio-700 hover:underline">
              VedAstro
            </a>
            {' '}(MIT License)
          </p>
        </CardContent>
      </Card>
    </div>
  )
}
