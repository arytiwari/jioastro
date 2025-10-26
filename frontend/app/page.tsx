import Link from 'next/link'
import { Button } from '@/components/ui/button'
import { Sparkles, Star, BookOpen, TrendingUp } from 'lucide-react'

export default function HomePage() {
  return (
    <div className="min-h-screen bg-gradient-to-b from-purple-50 to-white">
      {/* Hero Section */}
      <div className="container mx-auto px-4 py-16">
        <div className="text-center max-w-3xl mx-auto">
          <div className="flex justify-center mb-6">
            <div className="p-4 bg-purple-100 rounded-full">
              <Sparkles className="w-12 h-12 text-purple-600" />
            </div>
          </div>

          <h1 className="text-5xl md:text-6xl font-bold text-gray-900 mb-6">
            Vedic AI Astrology
          </h1>

          <p className="text-xl text-gray-600 mb-8">
            Discover your cosmic blueprint through ancient Vedic wisdom powered by modern AI.
            Get personalized insights from your birth chart.
          </p>

          <div className="flex gap-4 justify-center">
            <Link href="/auth/signup">
              <Button size="lg" className="bg-purple-600 hover:bg-purple-700">
                Get Started Free
              </Button>
            </Link>
            <Link href="/auth/login">
              <Button size="lg" variant="outline">
                Sign In
              </Button>
            </Link>
          </div>
        </div>

        {/* Features */}
        <div className="mt-20 grid md:grid-cols-3 gap-8 max-w-5xl mx-auto">
          <div className="text-center p-6 rounded-lg bg-white shadow-sm">
            <div className="flex justify-center mb-4">
              <Star className="w-10 h-10 text-purple-600" />
            </div>
            <h3 className="text-xl font-semibold mb-2">Birth Charts</h3>
            <p className="text-gray-600">
              Generate accurate Vedic birth charts (D1 & D9) using Swiss Ephemeris calculations
            </p>
          </div>

          <div className="text-center p-6 rounded-lg bg-white shadow-sm">
            <div className="flex justify-center mb-4">
              <BookOpen className="w-10 h-10 text-purple-600" />
            </div>
            <h3 className="text-xl font-semibold mb-2">AI Interpretations</h3>
            <p className="text-gray-600">
              Get personalized insights powered by advanced AI trained in Vedic astrology
            </p>
          </div>

          <div className="text-center p-6 rounded-lg bg-white shadow-sm">
            <div className="flex justify-center mb-4">
              <TrendingUp className="w-10 h-10 text-purple-600" />
            </div>
            <h3 className="text-xl font-semibold mb-2">Yogas & Dashas</h3>
            <p className="text-gray-600">
              Discover powerful planetary combinations and current planetary periods
            </p>
          </div>
        </div>

        {/* How It Works */}
        <div className="mt-20 max-w-4xl mx-auto">
          <h2 className="text-3xl font-bold text-center mb-12">How It Works</h2>

          <div className="space-y-6">
            <div className="flex items-start gap-4">
              <div className="flex-shrink-0 w-8 h-8 rounded-full bg-purple-600 text-white flex items-center justify-center font-bold">
                1
              </div>
              <div>
                <h4 className="font-semibold text-lg mb-1">Create Your Profile</h4>
                <p className="text-gray-600">
                  Enter your birth details - date, time, and location
                </p>
              </div>
            </div>

            <div className="flex items-start gap-4">
              <div className="flex-shrink-0 w-8 h-8 rounded-full bg-purple-600 text-white flex items-center justify-center font-bold">
                2
              </div>
              <div>
                <h4 className="font-semibold text-lg mb-1">View Your Chart</h4>
                <p className="text-gray-600">
                  Explore your birth chart with planetary positions and yogas
                </p>
              </div>
            </div>

            <div className="flex items-start gap-4">
              <div className="flex-shrink-0 w-8 h-8 rounded-full bg-purple-600 text-white flex items-center justify-center font-bold">
                3
              </div>
              <div>
                <h4 className="font-semibold text-lg mb-1">Ask Questions</h4>
                <p className="text-gray-600">
                  Get AI-powered insights about career, relationships, health, and more
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Footer */}
      <footer className="border-t mt-20 py-8">
        <div className="container mx-auto px-4 text-center text-gray-600">
          <p>&copy; 2024 Vedic AI Astrology. Built with ancient wisdom and modern technology.</p>
        </div>
      </footer>
    </div>
  )
}
