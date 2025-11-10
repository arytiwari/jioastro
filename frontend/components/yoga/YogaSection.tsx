"use client"

import { ReactNode } from "react"

interface YogaSectionProps {
  title: string
  description?: string
  icon?: ReactNode
  children: ReactNode
  className?: string
}

export default function YogaSection({
  title,
  description,
  icon,
  children,
  className = ""
}: YogaSectionProps) {
  return (
    <section className={`space-y-6 ${className}`}>
      {/* Section Header */}
      <div className="space-y-2">
        <div className="flex items-center gap-3">
          {icon && (
            <div className="flex-shrink-0">
              {icon}
            </div>
          )}
          <h2 className="text-3xl font-bold text-gray-900">
            {title}
          </h2>
        </div>
        {description && (
          <p className="text-gray-600 text-lg max-w-3xl">
            {description}
          </p>
        )}
      </div>

      {/* Section Content */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {children}
      </div>
    </section>
  )
}
