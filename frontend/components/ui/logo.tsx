import React from 'react'

interface LogoProps {
  size?: number
  className?: string
  variant?: 'default' | 'white' | 'dark'
}

export function Logo({ size = 40, className = '', variant = 'default' }: LogoProps) {
  const colors = {
    default: {
      primary: '#0056d6',
      secondary: '#1a75ff',
      accent: '#fbbf24',
    },
    white: {
      primary: '#ffffff',
      secondary: '#f3f4f6',
      accent: '#fbbf24',
    },
    dark: {
      primary: '#1f2937',
      secondary: '#374151',
      accent: '#0056d6',
    },
  }

  const color = colors[variant]

  return (
    <svg
      width={size}
      height={size}
      viewBox="0 0 100 100"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
      className={className}
    >
      {/* Outer circle - cosmic ring */}
      <circle
        cx="50"
        cy="50"
        r="45"
        stroke={color.primary}
        strokeWidth="3"
        fill="none"
        opacity="0.2"
      />

      {/* Inner glow circle */}
      <circle
        cx="50"
        cy="50"
        r="38"
        fill={color.primary}
        opacity="0.1"
      />

      {/* Main "J" letter - stylized */}
      <path
        d="M 45 25 L 55 25 L 55 55 Q 55 65 45 65 Q 35 65 35 55 L 42 55 Q 42 58 45 58 Q 48 58 48 55 L 48 32 L 45 32 Z"
        fill={color.primary}
      />

      {/* Top star accent */}
      <path
        d="M 70 20 L 72 25 L 77 25 L 73 28 L 75 33 L 70 30 L 65 33 L 67 28 L 63 25 L 68 25 Z"
        fill={color.accent}
      />

      {/* Right star accent - smaller */}
      <path
        d="M 78 45 L 79 48 L 82 48 L 80 50 L 81 53 L 78 51 L 75 53 L 76 50 L 74 48 L 77 48 Z"
        fill={color.accent}
        opacity="0.8"
      />

      {/* Bottom right dot constellation */}
      <circle cx="65" cy="70" r="2" fill={color.secondary} opacity="0.6" />
      <circle cx="70" cy="75" r="1.5" fill={color.secondary} opacity="0.5" />
      <circle cx="72" cy="68" r="1.5" fill={color.secondary} opacity="0.5" />

      {/* Connection lines - subtle */}
      <line x1="65" y1="70" x2="70" y2="75" stroke={color.secondary} strokeWidth="0.5" opacity="0.3" />
      <line x1="70" y1="75" x2="72" y2="68" stroke={color.secondary} strokeWidth="0.5" opacity="0.3" />

      {/* Orbital paths - decorative arcs */}
      <path
        d="M 30 35 Q 25 50 30 65"
        stroke={color.primary}
        strokeWidth="1.5"
        fill="none"
        opacity="0.15"
        strokeDasharray="3 3"
      />
    </svg>
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
