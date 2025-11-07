'use client'

import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import Link from 'next/link'
import { getCurrentUser, signOut } from '@/lib/supabase'
import { apiClient } from '@/lib/api'
import { Home, User, MessageSquare, History, LogOut, Menu, X, BookOpen, Sparkles, Gem, Sun, Award, Clock, ChevronDown, BarChart3, Wrench, Database, TrendingUp } from '@/components/icons'
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
  const [loading, setLoading] = useState(true)
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false)

  useEffect(() => {
    const checkAuth = async () => {
      console.log('🔍 Dashboard: Checking authentication...')

      const user = await getCurrentUser()
      console.log('👤 Dashboard: Got user:', user)

      if (!user) {
        console.warn('⚠️ Dashboard: No user found, redirecting to login')
        router.push('/auth/login')
        return
      }

      console.log('✅ Dashboard: User authenticated, loading token...')
      await apiClient.loadToken()
      console.log('✅ Dashboard: Token loaded, rendering dashboard')
      setLoading(false)
    }

    checkAuth()
  }, [router])

  const handleSignOut = async () => {
    await signOut()
    apiClient.clearToken()
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

  const chartsMenu = [
    { name: 'AI Readings', href: '/dashboard/readings', icon: Sparkles, badge: 'NEW' },
    { name: 'Yoga Analysis', href: '/dashboard/yogas', icon: Award, badge: 'NEW' },
    { name: 'Strength Analysis', href: '/dashboard/strength', icon: Award },
    { name: 'Current Transits', href: '/dashboard/transits', icon: Sun },
  ]

  const toolsMenu = [
    { name: 'Ask Question', href: '/dashboard/ask', icon: MessageSquare },
    { name: 'Birth Time Rectification', href: '/dashboard/rectification', icon: Clock },
    { name: 'Remedies', href: '/dashboard/remedies', icon: Gem },
  ]

  const myDataMenu = [
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

            {/* Desktop Navigation */}
            <nav className="hidden md:flex items-center space-x-1">
              {/* Dashboard */}
              <Link href="/dashboard">
                <Button variant="ghost" className="flex items-center gap-2">
                  <Home className="w-4 h-4" />
                  Dashboard
                </Button>
              </Link>

              {/* Charts Dropdown */}
              <DropdownMenu>
                <DropdownMenuTrigger asChild>
                  <Button variant="ghost" className="flex items-center gap-1">
                    <BarChart3 className="w-4 h-4" />
                    Charts
                    <ChevronDown className="w-3 h-3 opacity-50" />
                  </Button>
                </DropdownMenuTrigger>
                <DropdownMenuContent align="start">
                  {chartsMenu.map((item) => (
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

              {/* Tools Dropdown */}
              <DropdownMenu>
                <DropdownMenuTrigger asChild>
                  <Button variant="ghost" className="flex items-center gap-1">
                    <Wrench className="w-4 h-4" />
                    Tools
                    <ChevronDown className="w-3 h-3 opacity-50" />
                  </Button>
                </DropdownMenuTrigger>
                <DropdownMenuContent align="start">
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
                    My Data
                    <ChevronDown className="w-3 h-3 opacity-50" />
                  </Button>
                </DropdownMenuTrigger>
                <DropdownMenuContent align="start">
                  {myDataMenu.map((item) => (
                    <DropdownMenuItem key={item.name} asChild>
                      <Link href={item.href} className="flex items-center gap-2 cursor-pointer">
                        <item.icon className="w-4 h-4" />
                        <span>{item.name}</span>
                      </Link>
                    </DropdownMenuItem>
                  ))}
                </DropdownMenuContent>
              </DropdownMenu>

              {/* Numerology */}
              <Link href="/dashboard/numerology">
                <Button variant="ghost" className="flex items-center gap-2">
                  <TrendingUp className="w-4 h-4" />
                  Numerology
                </Button>
              </Link>

              {/* Knowledge */}
              <Link href="/dashboard/knowledge">
                <Button variant="ghost" className="flex items-center gap-2">
                  <BookOpen className="w-4 h-4" />
                  Knowledge
                </Button>
              </Link>
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

        {/* Mobile Navigation */}
        {mobileMenuOpen && (
          <div className="md:hidden border-t bg-white">
            <nav className="container mx-auto px-4 py-4 space-y-2">
              {/* Dashboard */}
              <Link href="/dashboard" onClick={() => setMobileMenuOpen(false)}>
                <Button variant="ghost" className="w-full justify-start flex items-center gap-2">
                  <Home className="w-4 h-4" />
                  Dashboard
                </Button>
              </Link>

              {/* Charts Section */}
              <div className="pl-2">
                <div className="flex items-center gap-2 px-2 py-1.5 text-sm font-semibold text-gray-600">
                  <BarChart3 className="w-4 h-4" />
                  Charts
                </div>
                {chartsMenu.map((item) => (
                  <Link
                    key={item.name}
                    href={item.href}
                    onClick={() => setMobileMenuOpen(false)}
                  >
                    <Button variant="ghost" className="w-full justify-start flex items-center gap-2 pl-6">
                      <item.icon className="w-4 h-4" />
                      {item.name}
                      {item.badge && (
                        <span className="ml-auto inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium bg-purple-100 text-purple-800">
                          {item.badge}
                        </span>
                      )}
                    </Button>
                  </Link>
                ))}
              </div>

              {/* Tools Section */}
              <div className="pl-2">
                <div className="flex items-center gap-2 px-2 py-1.5 text-sm font-semibold text-gray-600">
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
                      {item.name}
                    </Button>
                  </Link>
                ))}
              </div>

              {/* My Data Section */}
              <div className="pl-2">
                <div className="flex items-center gap-2 px-2 py-1.5 text-sm font-semibold text-gray-600">
                  <Database className="w-4 h-4" />
                  My Data
                </div>
                {myDataMenu.map((item) => (
                  <Link
                    key={item.name}
                    href={item.href}
                    onClick={() => setMobileMenuOpen(false)}
                  >
                    <Button variant="ghost" className="w-full justify-start flex items-center gap-2 pl-6">
                      <item.icon className="w-4 h-4" />
                      {item.name}
                    </Button>
                  </Link>
                ))}
              </div>

              {/* Numerology */}
              <Link href="/dashboard/numerology" onClick={() => setMobileMenuOpen(false)}>
                <Button variant="ghost" className="w-full justify-start flex items-center gap-2">
                  <TrendingUp className="w-4 h-4" />
                  Numerology
                </Button>
              </Link>

              {/* Knowledge */}
              <Link href="/dashboard/knowledge" onClick={() => setMobileMenuOpen(false)}>
                <Button variant="ghost" className="w-full justify-start flex items-center gap-2">
                  <BookOpen className="w-4 h-4" />
                  Knowledge
                </Button>
              </Link>

              {/* Sign Out */}
              <Button
                variant="ghost"
                className="w-full justify-start flex items-center gap-2"
                onClick={handleSignOut}
              >
                <LogOut className="w-4 h-4" />
                Sign Out
              </Button>
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
