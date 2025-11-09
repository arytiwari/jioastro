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
  DropdownMenuSub,
  DropdownMenuSubContent,
  DropdownMenuSubTrigger,
  DropdownMenuLabel,
  DropdownMenuSeparator,
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
  }, [pathname, router]) // Removed isAuthenticated to prevent infinite loop

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
  // Reorganized menu structure - 4 top-level menus with sub-categories
  const readingsMenu = {
    main: [
      { name: 'AI Readings', href: '/dashboard/readings', icon: Sparkles, badge: 'NEW' },
      { name: 'Birth Charts', href: '/dashboard/chart', icon: BarChart3 },
      { name: 'Ask Question', href: '/dashboard/ask', icon: MessageSquare },
      { name: 'Current Transits', href: '/dashboard/transits', icon: Sun },
    ],
    insights: [
      { name: 'Instant Onboarding', href: '/dashboard/instant-onboarding', icon: Zap, badge: 'NEW' },
      { name: 'Life Snapshot', href: '/dashboard/life-snapshot', icon: Eye, badge: 'NEW' },
      { name: 'Evidence Mode', href: '/dashboard/evidence-mode', icon: Shield, badge: 'NEW' },
    ]
  }

  const systemsMenu = {
    vedic: [
      { name: 'Varshaphal (Annual)', href: '/dashboard/varshaphal', icon: Calendar, badge: 'NEW' },
      { name: 'Jaimini System', href: '/dashboard/jaimini', icon: Award, badge: 'NEW' },
      { name: 'Lal Kitab', href: '/dashboard/lal-kitab', icon: BookOpen, badge: 'NEW' },
      { name: 'Ashtakavarga', href: '/dashboard/ashtakavarga', icon: Activity, badge: 'NEW' },
      { name: 'Yoga Analysis', href: '/dashboard/yogas', icon: Award },
      { name: 'Strength (Shadbala)', href: '/dashboard/strength', icon: TrendingUp },
    ],
    numerology: [
      { name: 'Calculator', href: '/dashboard/numerology', icon: TrendingUp },
      { name: 'Compare Names', href: '/dashboard/numerology/compare', icon: Activity },
    ],
    divination: [
      { name: 'Tarot Reading', href: '/dashboard/tarot', icon: Star, badge: 'NEW' },
      { name: 'Feng Shui', href: '/dashboard/feng-shui', icon: Compass, badge: 'NEW' },
      { name: 'Palmistry', href: '/dashboard/palmistry', icon: Hand, badge: 'NEW' },
      { name: 'Prashna (Horary)', href: '/dashboard/prashna', icon: HelpCircle, badge: 'NEW' },
    ]
  }

  const toolsMenu = {
    planning: [
      { name: 'Life Threads', href: '/dashboard/life-threads', icon: Timeline, badge: 'NEW' },
      { name: 'Remedy Planner', href: '/dashboard/remedy-planner', icon: Flame, badge: 'NEW' },
      { name: 'Daily Panchang', href: '/dashboard/panchang', icon: Calendar, badge: 'NEW' },
      { name: 'Remedies', href: '/dashboard/remedies', icon: Gem },
    ],
    analysis: [
      { name: 'Chart Comparison', href: '/dashboard/chart-comparison', icon: Users, badge: 'NEW' },
      { name: 'Muhurta (Times)', href: '/dashboard/muhurta', icon: Clock },
      { name: 'Compatibility', href: '/dashboard/compatibility', icon: Heart },
      { name: 'Time Rectification', href: '/dashboard/rectification', icon: Clock },
    ],
    resources: [
      { name: 'Knowledge Base', href: '/dashboard/knowledge', icon: BookOpen },
      { name: 'Advanced Systems', href: '/dashboard/advanced', icon: Activity },
    ]
  }

  const accountMenu = [
    { name: 'My Profiles', href: '/dashboard/profiles', icon: User },
    { name: 'Query History', href: '/dashboard/history', icon: History },
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

            {/* Desktop Navigation - Modern 4-Menu Structure */}
            <nav className="hidden md:flex items-center space-x-1">
              {/* Home */}
              <Link href="/dashboard">
                <Button variant="ghost" className="flex items-center gap-1.5 hover:bg-purple-50 hover:text-purple-700 transition-colors">
                  <Home className="w-4 h-4" />
                  <span className="text-sm font-medium">Home</span>
                </Button>
              </Link>

              {/* 1. Readings Menu */}
              <DropdownMenu>
                <DropdownMenuTrigger asChild>
                  <Button variant="ghost" className="flex items-center gap-1.5 hover:bg-purple-50 hover:text-purple-700 transition-colors">
                    <Sparkles className="w-4 h-4" />
                    <span className="text-sm font-medium">Readings</span>
                    <ChevronDown className="w-3 h-3 opacity-50" />
                  </Button>
                </DropdownMenuTrigger>
                <DropdownMenuContent align="start" className="w-64">
                  <DropdownMenuLabel className="text-xs font-semibold text-gray-500 uppercase">Core Readings</DropdownMenuLabel>
                  {readingsMenu.main.map((item) => (
                    <DropdownMenuItem key={item.name} asChild>
                      <Link href={item.href} className="flex items-center gap-2 cursor-pointer py-2">
                        <item.icon className="w-4 h-4 text-purple-600" />
                        <span className="font-medium">{item.name}</span>
                        {item.badge && (
                          <span className="ml-auto inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium bg-purple-100 text-purple-800">
                            {item.badge}
                          </span>
                        )}
                      </Link>
                    </DropdownMenuItem>
                  ))}
                  <DropdownMenuSeparator />
                  <DropdownMenuLabel className="text-xs font-semibold text-gray-500 uppercase">Personal Insights</DropdownMenuLabel>
                  {readingsMenu.insights.map((item) => (
                    <DropdownMenuItem key={item.name} asChild>
                      <Link href={item.href} className="flex items-center gap-2 cursor-pointer py-2">
                        <item.icon className="w-4 h-4 text-purple-600" />
                        <span className="font-medium">{item.name}</span>
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

              {/* 2. Systems Menu */}
              <DropdownMenu>
                <DropdownMenuTrigger asChild>
                  <Button variant="ghost" className="flex items-center gap-1.5 hover:bg-purple-50 hover:text-purple-700 transition-colors">
                    <BarChart3 className="w-4 h-4" />
                    <span className="text-sm font-medium">Systems</span>
                    <ChevronDown className="w-3 h-3 opacity-50" />
                  </Button>
                </DropdownMenuTrigger>
                <DropdownMenuContent align="start" className="w-64">
                  <DropdownMenuLabel className="text-xs font-semibold text-gray-500 uppercase">Vedic Astrology</DropdownMenuLabel>
                  {systemsMenu.vedic.map((item) => (
                    <DropdownMenuItem key={item.name} asChild>
                      <Link href={item.href} className="flex items-center gap-2 cursor-pointer py-2">
                        <item.icon className="w-4 h-4 text-indigo-600" />
                        <span className="font-medium">{item.name}</span>
                        {item.badge && (
                          <span className="ml-auto inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium bg-purple-100 text-purple-800">
                            {item.badge}
                          </span>
                        )}
                      </Link>
                    </DropdownMenuItem>
                  ))}
                  <DropdownMenuSeparator />
                  <DropdownMenuLabel className="text-xs font-semibold text-gray-500 uppercase">Numerology</DropdownMenuLabel>
                  {systemsMenu.numerology.map((item) => (
                    <DropdownMenuItem key={item.name} asChild>
                      <Link href={item.href} className="flex items-center gap-2 cursor-pointer py-2">
                        <item.icon className="w-4 h-4 text-indigo-600" />
                        <span className="font-medium">{item.name}</span>
                      </Link>
                    </DropdownMenuItem>
                  ))}
                  <DropdownMenuSeparator />
                  <DropdownMenuLabel className="text-xs font-semibold text-gray-500 uppercase">Divination Arts</DropdownMenuLabel>
                  {systemsMenu.divination.map((item) => (
                    <DropdownMenuItem key={item.name} asChild>
                      <Link href={item.href} className="flex items-center gap-2 cursor-pointer py-2">
                        <item.icon className="w-4 h-4 text-indigo-600" />
                        <span className="font-medium">{item.name}</span>
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

              {/* 3. Tools Menu */}
              <DropdownMenu>
                <DropdownMenuTrigger asChild>
                  <Button variant="ghost" className="flex items-center gap-1.5 hover:bg-purple-50 hover:text-purple-700 transition-colors">
                    <Wrench className="w-4 h-4" />
                    <span className="text-sm font-medium">Tools</span>
                    <ChevronDown className="w-3 h-3 opacity-50" />
                  </Button>
                </DropdownMenuTrigger>
                <DropdownMenuContent align="start" className="w-64">
                  <DropdownMenuLabel className="text-xs font-semibold text-gray-500 uppercase">Life Planning</DropdownMenuLabel>
                  {toolsMenu.planning.map((item) => (
                    <DropdownMenuItem key={item.name} asChild>
                      <Link href={item.href} className="flex items-center gap-2 cursor-pointer py-2">
                        <item.icon className="w-4 h-4 text-green-600" />
                        <span className="font-medium">{item.name}</span>
                        {item.badge && (
                          <span className="ml-auto inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium bg-purple-100 text-purple-800">
                            {item.badge}
                          </span>
                        )}
                      </Link>
                    </DropdownMenuItem>
                  ))}
                  <DropdownMenuSeparator />
                  <DropdownMenuLabel className="text-xs font-semibold text-gray-500 uppercase">Analysis Tools</DropdownMenuLabel>
                  {toolsMenu.analysis.map((item) => (
                    <DropdownMenuItem key={item.name} asChild>
                      <Link href={item.href} className="flex items-center gap-2 cursor-pointer py-2">
                        <item.icon className="w-4 h-4 text-green-600" />
                        <span className="font-medium">{item.name}</span>
                        {item.badge && (
                          <span className="ml-auto inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium bg-purple-100 text-purple-800">
                            {item.badge}
                          </span>
                        )}
                      </Link>
                    </DropdownMenuItem>
                  ))}
                  <DropdownMenuSeparator />
                  <DropdownMenuLabel className="text-xs font-semibold text-gray-500 uppercase">Resources</DropdownMenuLabel>
                  {toolsMenu.resources.map((item) => (
                    <DropdownMenuItem key={item.name} asChild>
                      <Link href={item.href} className="flex items-center gap-2 cursor-pointer py-2">
                        <item.icon className="w-4 h-4 text-green-600" />
                        <span className="font-medium">{item.name}</span>
                      </Link>
                    </DropdownMenuItem>
                  ))}
                </DropdownMenuContent>
              </DropdownMenu>

              {/* 4. Account Menu */}
              <DropdownMenu>
                <DropdownMenuTrigger asChild>
                  <Button variant="ghost" className="flex items-center gap-1.5 hover:bg-purple-50 hover:text-purple-700 transition-colors">
                    <User className="w-4 h-4" />
                    <span className="text-sm font-medium">Account</span>
                    <ChevronDown className="w-3 h-3 opacity-50" />
                  </Button>
                </DropdownMenuTrigger>
                <DropdownMenuContent align="start" className="w-56">
                  {accountMenu.map((item) => (
                    <DropdownMenuItem key={item.name} asChild>
                      <Link href={item.href} className="flex items-center gap-2 cursor-pointer py-2">
                        <item.icon className="w-4 h-4 text-blue-600" />
                        <span className="font-medium">{item.name}</span>
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
                className="md:hidden"
                onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
              >
                {mobileMenuOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
              </Button>
            </div>
          </div>
        </div>

        {/* Mobile Navigation - Reorganized */}
        {mobileMenuOpen && (
          <div className="md:hidden border-t bg-white shadow-lg">
            <nav className="container mx-auto px-4 py-4 space-y-2 max-h-[calc(100vh-4rem)] overflow-y-auto">
              {/* Home */}
              <Link href="/dashboard" onClick={() => setMobileMenuOpen(false)}>
                <Button variant="ghost" className="w-full justify-start flex items-center gap-2 hover:bg-purple-50">
                  <Home className="w-4 h-4" />
                  <span className="font-medium">Home</span>
                </Button>
              </Link>

              {/* 1. Readings Section */}
              <div className="border-t pt-2">
                <div className="flex items-center gap-2 px-2 py-2 text-sm font-bold text-purple-700 bg-purple-50 rounded-md">
                  <Sparkles className="w-4 h-4" />
                  Readings
                </div>
                <div className="ml-2 mt-1">
                  <div className="text-xs font-semibold text-gray-500 px-2 py-1">CORE READINGS</div>
                  {readingsMenu.main.map((item) => (
                    <Link key={item.name} href={item.href} onClick={() => setMobileMenuOpen(false)}>
                      <Button variant="ghost" className="w-full justify-start flex items-center gap-2 pl-4 py-2">
                        <item.icon className="w-4 h-4 text-purple-600" />
                        <span className="text-sm">{item.name}</span>
                        {item.badge && (
                          <span className="ml-auto inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium bg-purple-100 text-purple-800">
                            {item.badge}
                          </span>
                        )}
                      </Button>
                    </Link>
                  ))}
                  <div className="text-xs font-semibold text-gray-500 px-2 py-1 mt-2">PERSONAL INSIGHTS</div>
                  {readingsMenu.insights.map((item) => (
                    <Link key={item.name} href={item.href} onClick={() => setMobileMenuOpen(false)}>
                      <Button variant="ghost" className="w-full justify-start flex items-center gap-2 pl-4 py-2">
                        <item.icon className="w-4 h-4 text-purple-600" />
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
              </div>

              {/* 2. Systems Section */}
              <div className="border-t pt-2">
                <div className="flex items-center gap-2 px-2 py-2 text-sm font-bold text-indigo-700 bg-indigo-50 rounded-md">
                  <BarChart3 className="w-4 h-4" />
                  Systems
                </div>
                <div className="ml-2 mt-1">
                  <div className="text-xs font-semibold text-gray-500 px-2 py-1">VEDIC ASTROLOGY</div>
                  {systemsMenu.vedic.map((item) => (
                    <Link key={item.name} href={item.href} onClick={() => setMobileMenuOpen(false)}>
                      <Button variant="ghost" className="w-full justify-start flex items-center gap-2 pl-4 py-2">
                        <item.icon className="w-4 h-4 text-indigo-600" />
                        <span className="text-sm">{item.name}</span>
                        {item.badge && (
                          <span className="ml-auto inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium bg-purple-100 text-purple-800">
                            {item.badge}
                          </span>
                        )}
                      </Button>
                    </Link>
                  ))}
                  <div className="text-xs font-semibold text-gray-500 px-2 py-1 mt-2">NUMEROLOGY</div>
                  {systemsMenu.numerology.map((item) => (
                    <Link key={item.name} href={item.href} onClick={() => setMobileMenuOpen(false)}>
                      <Button variant="ghost" className="w-full justify-start flex items-center gap-2 pl-4 py-2">
                        <item.icon className="w-4 h-4 text-indigo-600" />
                        <span className="text-sm">{item.name}</span>
                      </Button>
                    </Link>
                  ))}
                  <div className="text-xs font-semibold text-gray-500 px-2 py-1 mt-2">DIVINATION ARTS</div>
                  {systemsMenu.divination.map((item) => (
                    <Link key={item.name} href={item.href} onClick={() => setMobileMenuOpen(false)}>
                      <Button variant="ghost" className="w-full justify-start flex items-center gap-2 pl-4 py-2">
                        <item.icon className="w-4 h-4 text-indigo-600" />
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
              </div>

              {/* 3. Tools Section */}
              <div className="border-t pt-2">
                <div className="flex items-center gap-2 px-2 py-2 text-sm font-bold text-green-700 bg-green-50 rounded-md">
                  <Wrench className="w-4 h-4" />
                  Tools
                </div>
                <div className="ml-2 mt-1">
                  <div className="text-xs font-semibold text-gray-500 px-2 py-1">LIFE PLANNING</div>
                  {toolsMenu.planning.map((item) => (
                    <Link key={item.name} href={item.href} onClick={() => setMobileMenuOpen(false)}>
                      <Button variant="ghost" className="w-full justify-start flex items-center gap-2 pl-4 py-2">
                        <item.icon className="w-4 h-4 text-green-600" />
                        <span className="text-sm">{item.name}</span>
                        {item.badge && (
                          <span className="ml-auto inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium bg-purple-100 text-purple-800">
                            {item.badge}
                          </span>
                        )}
                      </Button>
                    </Link>
                  ))}
                  <div className="text-xs font-semibold text-gray-500 px-2 py-1 mt-2">ANALYSIS TOOLS</div>
                  {toolsMenu.analysis.map((item) => (
                    <Link key={item.name} href={item.href} onClick={() => setMobileMenuOpen(false)}>
                      <Button variant="ghost" className="w-full justify-start flex items-center gap-2 pl-4 py-2">
                        <item.icon className="w-4 h-4 text-green-600" />
                        <span className="text-sm">{item.name}</span>
                        {item.badge && (
                          <span className="ml-auto inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium bg-purple-100 text-purple-800">
                            {item.badge}
                          </span>
                        )}
                      </Button>
                    </Link>
                  ))}
                  <div className="text-xs font-semibold text-gray-500 px-2 py-1 mt-2">RESOURCES</div>
                  {toolsMenu.resources.map((item) => (
                    <Link key={item.name} href={item.href} onClick={() => setMobileMenuOpen(false)}>
                      <Button variant="ghost" className="w-full justify-start flex items-center gap-2 pl-4 py-2">
                        <item.icon className="w-4 h-4 text-green-600" />
                        <span className="text-sm">{item.name}</span>
                      </Button>
                    </Link>
                  ))}
                </div>
              </div>

              {/* 4. Account Section */}
              <div className="border-t pt-2">
                <div className="flex items-center gap-2 px-2 py-2 text-sm font-bold text-blue-700 bg-blue-50 rounded-md">
                  <User className="w-4 h-4" />
                  Account
                </div>
                <div className="ml-2 mt-1">
                  {accountMenu.map((item) => (
                    <Link key={item.name} href={item.href} onClick={() => setMobileMenuOpen(false)}>
                      <Button variant="ghost" className="w-full justify-start flex items-center gap-2 pl-4 py-2">
                        <item.icon className="w-4 h-4 text-blue-600" />
                        <span className="text-sm">{item.name}</span>
                      </Button>
                    </Link>
                  ))}
                </div>
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
