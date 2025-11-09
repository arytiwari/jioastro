"use client"

import * as React from "react"
import { X } from "lucide-react"

interface DialogProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  children: React.ReactNode
}

export function Dialog({ open, onOpenChange, children }: DialogProps) {
  React.useEffect(() => {
    if (open) {
      document.body.style.overflow = 'hidden'
    } else {
      document.body.style.overflow = 'unset'
    }
    return () => {
      document.body.style.overflow = 'unset'
    }
  }, [open])

  if (!open) return null

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center">
      {/* Backdrop */}
      <div
        className="absolute inset-0 bg-black/50 backdrop-blur-sm"
        onClick={() => onOpenChange(false)}
      />

      {/* Dialog content */}
      <div className="relative z-50 w-full max-w-3xl max-h-[90vh] overflow-hidden">
        {children}
      </div>
    </div>
  )
}

interface DialogContentProps {
  children: React.ReactNode
  className?: string
}

export function DialogContent({ children, className = "" }: DialogContentProps) {
  return (
    <div className={`bg-white rounded-lg shadow-xl overflow-y-auto max-h-[90vh] ${className}`}>
      {children}
    </div>
  )
}

interface DialogHeaderProps {
  children: React.ReactNode
  onClose?: () => void
}

export function DialogHeader({ children, onClose }: DialogHeaderProps) {
  return (
    <div className="sticky top-0 bg-white border-b border-gray-200 px-6 py-4 flex items-center justify-between z-10">
      <div className="flex-1">{children}</div>
      {onClose && (
        <button
          onClick={onClose}
          className="ml-4 p-1 hover:bg-gray-100 rounded-full transition-colors"
        >
          <X className="w-5 h-5 text-gray-500" />
        </button>
      )}
    </div>
  )
}

interface DialogTitleProps {
  children: React.ReactNode
  className?: string
}

export function DialogTitle({ children, className = "" }: DialogTitleProps) {
  return (
    <h2 className={`text-2xl font-bold text-gray-900 ${className}`}>
      {children}
    </h2>
  )
}

interface DialogDescriptionProps {
  children: React.ReactNode
  className?: string
}

export function DialogDescription({ children, className = "" }: DialogDescriptionProps) {
  return (
    <p className={`text-sm text-gray-600 mt-1 ${className}`}>
      {children}
    </p>
  )
}

interface DialogBodyProps {
  children: React.ReactNode
  className?: string
}

export function DialogBody({ children, className = "" }: DialogBodyProps) {
  return (
    <div className={`px-6 py-4 ${className}`}>
      {children}
    </div>
  )
}

interface DialogFooterProps {
  children: React.ReactNode
  className?: string
}

export function DialogFooter({ children, className = "" }: DialogFooterProps) {
  return (
    <div className={`sticky bottom-0 bg-gray-50 border-t border-gray-200 px-6 py-4 flex items-center justify-end gap-3 ${className}`}>
      {children}
    </div>
  )
}
