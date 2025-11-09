'use client'

import React, { useEffect, useState } from 'react'
import { useRouter, usePathname } from 'next/navigation'
import Link from 'next/link'
import { getCurrentUser, signOut, getValidSession } from '@/lib/supabase'
import { apiClient } from '@/lib/api'
import { Home, User, MessageSquare, History, LogOut, Menu, X, BookOpen, Sparkles, Gem, Sun, Award, Clock, ChevronDown, BarChart3, Wrench, Database, TrendingUp, Activity, Heart, Zap, Eye, Shield, Calendar, HelpCircle, Users, Hand, Star, Compass, Timeline, Flame } from '@/components/icons'
import { Button } from '@/components/ui/button'
import { Logo } from '@/components/ui/logo'
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu'

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode
}) {
  const router = useRouter()
  const pathname = usePathname()
  const [loading, setLoading] = useState(true)
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false)
  const [isAuthenticated, setIsAuthenticated] = useState(false)
  const hasCheckedAuthRef = React.useRef(false)

  useEffect(() => {
    const checkAuth = async () => {
      // If already authenticated and we've checked before, don't re-check
      if (isAuthenticated && hasCheckedAuthRef.current) {
        console.log('✅ Dashboard Layout: Already authenticated, skipping check')
        return
      }

      console.log('🔍 Dashboard Layout: Checking authentication...')
      console.log('📍 Dashboard Layout: Current pathname:', pathname)
      console.log('📍 Dashboard Layout: Pathname type:', typeof pathname)
      console.log('📍 Dashboard Layout: Pathname length:', pathname?.length)

      // Public routes that don't require authentication (Magical 12 features)
      const publicRoutes = ['/dashboard/instant-onboarding', '/dashboard/life-snapshot', '/dashboard/evidence-mode']

      // More defensive route checking - normalize pathname
      const normalizedPath = pathname?.toLowerCase().replace(/\/+$/, '') || ''
      console.log('📍 Dashboard Layout: Normalized path:', normalizedPath)
      console.log('📍 Dashboard Layout: Normalized path length:', normalizedPath.length)
      console.log('📍 Dashboard Layout: Normalized path charCodes:', normalizedPath.split('').map(c => c.charCodeAt(0)).join(','))

      // Check if current path matches a public route
      // Only exact matches or proper sub-paths should match
      const isPublicRoute = publicRoutes.some(route => {
        const normalizedRoute = route.toLowerCase()
        // Exact match or current path is a sub-path of the public route
        const currentStartsWithPublic = normalizedPath === normalizedRoute ||
                                       normalizedPath.startsWith(normalizedRoute + '/')
        const match = currentStartsWithPublic
        console.log(`  Checking ${route}:`)
        console.log(`    Normalized route: ${normalizedRoute}`)
        console.log(`    Exact match: ${normalizedPath === normalizedRoute}`)
        console.log(`    Subpath match: ${normalizedPath.startsWith(normalizedRoute + '/')}`)
        console.log(`    Match: ${match}`)
        return match
      })

      console.log('🔓 Dashboard Layout: Is public route?', isPublicRoute)

      if (isPublicRoute) {
        console.log('✅ Dashboard Layout: Public route detected, skipping auth check')
        setLoading(false)
        return
      }

      console.log('🔒 Dashboard Layout: Protected route, checking session...')

      // First, get a valid session (auto-refreshes if expired)
      const session = await getValidSession()
      console.log('📦 Dashboard Layout: Got session:', session ? 'valid' : 'null')

      if (!session) {
        console.warn('⚠️ Dashboard Layout: No valid session, redirecting to login from dashboard layout')
        console.log('📞 Dashboard Layout redirect stack:', new Error().stack)
        router.push('/auth/login')
        return
      }

      // Then verify the user
      const user = await getCurrentUser()
      console.log('👤 Dashboard Layout: Got user:', user)

      if (!user) {
        console.warn('⚠️ Dashboard Layout: No user found, redirecting to login from dashboard layout')
        console.log('📞 Dashboard Layout redirect stack:', new Error().stack)
        router.push('/auth/login')
        return
      }

      console.log('✅ Dashboard Layout: User authenticated, loading token...')
      await apiClient.loadToken()
      console.log('✅ Dashboard Layout: Token loaded, rendering dashboard')
      setIsAuthenticated(true)
      hasCheckedAuthRef.current = true
      setLoading(false)
    }

    checkAuth()
  }, [pathname, router, isAuthenticated])

  const handleSignOut = async () => {
    await signOut()
    apiClient.clearToken()
    setIsAuthenticated(false)
    hasCheckedAuthRef.current = false
    router.push('/')
  }

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="w-8 h-8 border-4 border-jio-600 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
          <p className="text-gray-600">Loading...</p>
        </div>
      </div>
    )
  }

  // Reorganized menu structure for better scalability
  const astrologyMenu = [
    { name: 'AI Readings', href: '/dashboard/readings', icon: Sparkles, badge: 'NEW' },
    { name: 'Birth Charts', href: '/dashboard/chart', icon: BarChart3 },
    { name: 'Varshaphal (Annual)', href: '/dashboard/varshaphal', icon: Calendar, badge: 'NEW' },
    { name: 'Jaimini System', href: '/dashboard/jaimini', icon: Award, badge: 'NEW' },
    { name: 'Lal Kitab', href: '/dashboard/lal-kitab', icon: BookOpen, badge: 'NEW' },
    { name: 'Ashtakavarga', href: '/dashboard/ashtakavarga', icon: Activity, badge: 'NEW' },
    { name: 'Yoga Analysis', href: '/dashboard/yogas', icon: Award },
    { name: 'Strength (Shadbala)', href: '/dashboard/strength', icon: TrendingUp },
    { name: 'Current Transits', href: '/dashboard/transits', icon: Sun },
  ]

  const numerologyMenu = [
    { name: 'Calculator', href: '/dashboard/numerology', icon: TrendingUp },
    { name: 'Compare Names', href: '/dashboard/numerology/compare', icon: Activity },
  ]

  const toolsMenu = [
    { name: 'Ask Question', href: '/dashboard/ask', icon: MessageSquare },
    { name: 'Tarot Reading', href: '/dashboard/tarot', icon: Star, badge: 'NEW' },
    { name: 'Feng Shui', href: '/dashboard/feng-shui', icon: Compass, badge: 'NEW' },
    { name: 'Palmistry', href: '/dashboard/palmistry', icon: Hand, badge: 'NEW' },
    { name: 'Prashna (Horary)', href: '/dashboard/prashna', icon: HelpCircle, badge: 'NEW' },
    { name: 'Chart Comparison', href: '/dashboard/chart-comparison', icon: Users, badge: 'NEW' },
    { name: 'Muhurta (Auspicious Times)', href: '/dashboard/muhurta', icon: Clock },
    { name: 'Compatibility Matching', href: '/dashboard/compatibility', icon: Heart },
    { name: 'Birth Time Rectification', href: '/dashboard/rectification', icon: Clock },
    { name: 'Remedies', href: '/dashboard/remedies', icon: Gem },
  ]

  const dataMenu = [
    { name: 'My Profiles', href: '/dashboard/profiles', icon: User },
    { name: 'Query History', href: '/dashboard/history', icon: History },
  ]

  const moreMenu = [
    { name: 'Instant Onboarding', href: '/dashboard/instant-onboarding', icon: Zap, badge: 'NEW' },
    { name: 'Life Snapshot', href: '/dashboard/life-snapshot', icon: Eye, badge: 'NEW' },
    { name: 'Evidence Mode', href: '/dashboard/evidence-mode', icon: Shield, badge: 'NEW' },
    { name: 'Life Threads', href: '/dashboard/life-threads', icon: Timeline, badge: 'NEW' },
    { name: 'Remedy Planner', href: '/dashboard/remedy-planner', icon: Flame, badge: 'NEW' },
    { name: 'Daily Panchang', href: '/dashboard/panchang', icon: Calendar, badge: 'NEW' },
    { name: 'Advanced Systems', href: '/dashboard/advanced', icon: Activity },
    { name: 'Knowledge Base', href: '/dashboard/knowledge', icon: BookOpen },
  ]

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white border-b sticky top-0 z-40">
        <div className="container mx-auto px-4">
          <div className="flex items-center justify-between h-16">
            {/* Logo */}
            <Link href="/dashboard" className="flex items-center space-x-2 hover:opacity-80 transition-opacity">
              <Logo size={36} />
              <span className="font-bold text-xl hidden sm:inline text-jio-700">JioAstro</span>
            </Link>

            {/* Desktop Navigation */}
            <nav className="hidden lg:flex items-center space-x-1">
              {/* Dashboard */}
              <Link href="/dashboard">
                <Button variant="ghost" className="flex items-center gap-1.5">
                  <Home className="w-4 h-4" />
                  <span className="text-sm">Home</span>
                </Button>
              </Link>

              {/* Astrology Dropdown */}
              <DropdownMenu>
                <DropdownMenuTrigger asChild>
                  <Button variant="ghost" className="flex items-center gap-1">
                    <BarChart3 className="w-4 h-4" />
                    <span className="text-sm">Astrology</span>
                    <ChevronDown className="w-3 h-3 opacity-50" />
                  </Button>
                </DropdownMenuTrigger>
                <DropdownMenuContent align="start" className="w-56">
                  {astrologyMenu.map((item) => (
                    <DropdownMenuItem key={item.name} asChild>
                      <Link href={item.href} className="flex items-center gap-2 cursor-pointer">
                        <item.icon className="w-4 h-4" />
                        <span>{item.name}</span>
                        {item.badge && (
                          <span className="ml-auto inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium bg-purple-100 text-purple-800">
                            {item.badge}
                          </span>
                        )}
                      </Link>
                    </DropdownMenuItem>
                  ))}
                </DropdownMenuContent>
              </DropdownMenu>

              {/* Numerology Dropdown */}
              <DropdownMenu>
                <DropdownMenuTrigger asChild>
                  <Button variant="ghost" className="flex items-center gap-1">
                    <TrendingUp className="w-4 h-4" />
                    <span className="text-sm">Numerology</span>
                    <ChevronDown className="w-3 h-3 opacity-50" />
                  </Button>
                </DropdownMenuTrigger>
                <DropdownMenuContent align="start" className="w-48">
                  {numerologyMenu.map((item) => (
                    <DropdownMenuItem key={item.name} asChild>
                      <Link href={item.href} className="flex items-center gap-2 cursor-pointer">
                        <item.icon className="w-4 h-4" />
                        <span>{item.name}</span>
                      </Link>
                    </DropdownMenuItem>
                  ))}
                </DropdownMenuContent>
              </DropdownMenu>

              {/* Tools Dropdown */}
              <DropdownMenu>
                <DropdownMenuTrigger asChild>
                  <Button variant="ghost" className="flex items-center gap-1">
                    <Wrench className="w-4 h-4" />
                    <span className="text-sm">Tools</span>
                    <ChevronDown className="w-3 h-3 opacity-50" />
                  </Button>
                </DropdownMenuTrigger>
                <DropdownMenuContent align="start" className="w-56">
                  {toolsMenu.map((item) => (
                    <DropdownMenuItem key={item.name} asChild>
                      <Link href={item.href} className="flex items-center gap-2 cursor-pointer">
                        <item.icon className="w-4 h-4" />
                        <span>{item.name}</span>
                      </Link>
                    </DropdownMenuItem>
                  ))}
                </DropdownMenuContent>
              </DropdownMenu>

              {/* My Data Dropdown */}
              <DropdownMenu>
                <DropdownMenuTrigger asChild>
                  <Button variant="ghost" className="flex items-center gap-1">
                    <Database className="w-4 h-4" />
                    <span className="text-sm">My Data</span>
                    <ChevronDown className="w-3 h-3 opacity-50" />
                  </Button>
                </DropdownMenuTrigger>
                <DropdownMenuContent align="start" className="w-48">
                  {dataMenu.map((item) => (
                    <DropdownMenuItem key={item.name} asChild>
                      <Link href={item.href} className="flex items-center gap-2 cursor-pointer">
                        <item.icon className="w-4 h-4" />
                        <span>{item.name}</span>
                      </Link>
                    </DropdownMenuItem>
                  ))}
                </DropdownMenuContent>
              </DropdownMenu>

              {/* More Dropdown */}
              <DropdownMenu>
                <DropdownMenuTrigger asChild>
                  <Button variant="ghost" className="flex items-center gap-1">
                    <Sparkles className="w-4 h-4" />
                    <span className="text-sm">More</span>
                    <ChevronDown className="w-3 h-3 opacity-50" />
                  </Button>
                </DropdownMenuTrigger>
                <DropdownMenuContent align="start" className="w-52">
                  {moreMenu.map((item) => (
                    <DropdownMenuItem key={item.name} asChild>
                      <Link href={item.href} className="flex items-center gap-2 cursor-pointer">
                        <item.icon className="w-4 h-4" />
                        <span>{item.name}</span>
                        {item.badge && (
                          <span className="ml-auto inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium bg-purple-100 text-purple-800">
                            {item.badge}
                          </span>
                        )}
                      </Link>
                    </DropdownMenuItem>
                  ))}
                </DropdownMenuContent>
              </DropdownMenu>
            </nav>

            {/* Right side */}
            <div className="flex items-center gap-2">
              <Button
                variant="ghost"
                size="icon"
                onClick={handleSignOut}
                className="hidden md:flex"
              >
                <LogOut className="w-4 h-4" />
              </Button>

              {/* Mobile menu button */}
              <Button
                variant="ghost"
                size="icon"
                className="lg:hidden"
                onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
              >
                {mobileMenuOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
              </Button>
            </div>
          </div>
        </div>

        {/* Mobile Navigation */}
        {mobileMenuOpen && (
          <div className="lg:hidden border-t bg-white">
            <nav className="container mx-auto px-4 py-4 space-y-2 max-h-[calc(100vh-4rem)] overflow-y-auto">
              {/* Home */}
              <Link href="/dashboard" onClick={() => setMobileMenuOpen(false)}>
                <Button variant="ghost" className="w-full justify-start flex items-center gap-2">
                  <Home className="w-4 h-4" />
                  Home
                </Button>
              </Link>

              {/* Astrology Section */}
              <div className="border-t pt-2">
                <div className="flex items-center gap-2 px-2 py-1.5 text-sm font-semibold text-gray-700">
                  <BarChart3 className="w-4 h-4" />
                  Astrology
                </div>
                {astrologyMenu.map((item) => (
                  <Link
                    key={item.name}
                    href={item.href}
                    onClick={() => setMobileMenuOpen(false)}
                  >
                    <Button variant="ghost" className="w-full justify-start flex items-center gap-2 pl-6">
                      <item.icon className="w-4 h-4" />
                      <span className="text-sm">{item.name}</span>
                      {item.badge && (
                        <span className="ml-auto inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium bg-purple-100 text-purple-800">
                          {item.badge}
                        </span>
                      )}
                    </Button>
                  </Link>
                ))}
              </div>

              {/* Numerology Section */}
              <div className="border-t pt-2">
                <div className="flex items-center gap-2 px-2 py-1.5 text-sm font-semibold text-gray-700">
                  <TrendingUp className="w-4 h-4" />
                  Numerology
                </div>
                {numerologyMenu.map((item) => (
                  <Link
                    key={item.name}
                    href={item.href}
                    onClick={() => setMobileMenuOpen(false)}
                  >
                    <Button variant="ghost" className="w-full justify-start flex items-center gap-2 pl-6">
                      <item.icon className="w-4 h-4" />
                      <span className="text-sm">{item.name}</span>
                    </Button>
                  </Link>
                ))}
              </div>

              {/* Tools Section */}
              <div className="border-t pt-2">
                <div className="flex items-center gap-2 px-2 py-1.5 text-sm font-semibold text-gray-700">
                  <Wrench className="w-4 h-4" />
                  Tools
                </div>
                {toolsMenu.map((item) => (
                  <Link
                    key={item.name}
                    href={item.href}
                    onClick={() => setMobileMenuOpen(false)}
                  >
                    <Button variant="ghost" className="w-full justify-start flex items-center gap-2 pl-6">
                      <item.icon className="w-4 h-4" />
                      <span className="text-sm">{item.name}</span>
                      {item.badge && (
                        <span className="ml-auto inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium bg-purple-100 text-purple-800">
                          {item.badge}
                        </span>
                      )}
                    </Button>
                  </Link>
                ))}
              </div>

              {/* My Data Section */}
              <div className="border-t pt-2">
                <div className="flex items-center gap-2 px-2 py-1.5 text-sm font-semibold text-gray-700">
                  <Database className="w-4 h-4" />
                  My Data
                </div>
                {dataMenu.map((item) => (
                  <Link
                    key={item.name}
                    href={item.href}
                    onClick={() => setMobileMenuOpen(false)}
                  >
                    <Button variant="ghost" className="w-full justify-start flex items-center gap-2 pl-6">
                      <item.icon className="w-4 h-4" />
                      <span className="text-sm">{item.name}</span>
                    </Button>
                  </Link>
                ))}
              </div>

              {/* More Section */}
              <div className="border-t pt-2">
                <div className="flex items-center gap-2 px-2 py-1.5 text-sm font-semibold text-gray-700">
                  <Sparkles className="w-4 h-4" />
                  More Features
                </div>
                {moreMenu.map((item) => (
                  <Link
                    key={item.name}
                    href={item.href}
                    onClick={() => setMobileMenuOpen(false)}
                  >
                    <Button variant="ghost" className="w-full justify-start flex items-center gap-2 pl-6">
                      <item.icon className="w-4 h-4" />
                      <span className="text-sm">{item.name}</span>
                      {item.badge && (
                        <span className="ml-auto inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium bg-purple-100 text-purple-800">
                          {item.badge}
                        </span>
                      )}
                    </Button>
                  </Link>
                ))}
              </div>

              {/* Sign Out */}
              <div className="border-t pt-2">
                <Button
                  variant="ghost"
                  className="w-full justify-start flex items-center gap-2"
                  onClick={handleSignOut}
                >
                  <LogOut className="w-4 h-4" />
                  Sign Out
                </Button>
              </div>
            </nav>
          </div>
        )}
      </header>

      {/* Main Content */}
      <main className="container mx-auto px-4 py-8">
        {children}
      </main>

      {/* Footer */}
      <footer className="border-t bg-white mt-20">
        <div className="container mx-auto px-4 py-6 text-center text-sm text-gray-600">
          <p>&copy; 2025 JioAstro. Built with ancient wisdom and modern technology.</p>
        </div>
      </footer>
    </div>
  )
}
