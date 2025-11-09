import React from 'react'
import Image from 'next/image'

interface LogoProps {
  size?: number
  className?: string
  variant?: 'default' | 'white' | 'dark'
}

export function Logo({ size = 40, className = '' }: LogoProps) {
  return (
    <Image
      src="/logo.png"
      alt="JioAstro Logo"
      width={size}
      height={size}
      className={className}
      style={{ height: 'auto' }}  // Maintain aspect ratio if width is modified by CSS
      priority
    />
  )
}

export function LogoMark({ size = 32, className = '' }: { size?: number; className?: string }) {
  return (
    <div
      className={`inline-flex items-center justify-center rounded-lg bg-gradient-to-br from-jio-500 to-jio-700 ${className}`}
      style={{ width: size, height: size }}
    >
      <span className="text-white font-bold" style={{ fontSize: size * 0.6 }}>
        J
      </span>
    </div>
  )
}

export function LogoWithText({
  size = 40,
  className = '',
  textClassName = '',
  showTagline = false
}: {
  size?: number
  className?: string
  textClassName?: string
  showTagline?: boolean
}) {
  return (
    <div className={`flex items-center gap-3 ${className}`}>
      <Logo size={size} />
      <div className="flex flex-col">
        <span className={`font-bold text-gray-900 ${textClassName}`} style={{ fontSize: size * 0.45 }}>
          JioAstro
        </span>
        {showTagline && (
          <span className="text-xs text-gray-600" style={{ fontSize: size * 0.25 }}>
            Cosmic Insights
          </span>
        )}
      </div>
    </div>
  )
}
