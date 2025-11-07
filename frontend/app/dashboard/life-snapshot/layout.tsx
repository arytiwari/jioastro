'use client'

import Link from 'next/link'
import { Logo } from '@/components/ui/logo'
import { Button } from '@/components/ui/button'
import { Home } from '@/components/icons'

export default function LifeSnapshotLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <div className="min-h-screen bg-gray-50">
      {/* Minimal header - no auth checks */}
      <header className="bg-white border-b sticky top-0 z-40">
        <div className="container mx-auto px-4">
          <div className="flex items-center justify-between h-16">
            {/* Logo */}
            <Link href="/dashboard" className="flex items-center space-x-2 hover:opacity-80 transition-opacity">
              <Logo size={36} />
              <span className="font-bold text-xl hidden sm:inline text-jio-700">JioAstro</span>
            </Link>

            {/* Back to Dashboard */}
            <Link href="/dashboard">
              <Button variant="ghost" className="flex items-center gap-2">
                <Home className="w-4 h-4" />
                Dashboard
              </Button>
            </Link>
          </div>
        </div>
      </header>

      {/* Main Content - no layout wrapper, no auth check */}
      <main>
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
