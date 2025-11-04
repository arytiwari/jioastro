'use client'

import { useEffect } from 'react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { AlertCircle } from '@/components/icons'

export default function Error({
  error,
  reset,
}: {
  error: Error & { digest?: string }
  reset: () => void
}) {
  useEffect(() => {
    console.error('Application error:', error)
  }, [error])

  return (
    <div className="min-h-screen flex items-center justify-center p-4 bg-gray-50">
      <Card className="max-w-md w-full">
        <CardHeader>
          <div className="flex items-center gap-3">
            <AlertCircle className="w-8 h-8 text-red-600" />
            <CardTitle>Something went wrong</CardTitle>
          </div>
        </CardHeader>
        <CardContent className="space-y-4">
          <p className="text-gray-600">
            We encountered an unexpected error. Please try again.
          </p>
          {error.message && (
            <div className="p-3 bg-red-50 rounded-lg">
              <p className="text-sm text-red-800 font-mono">{error.message}</p>
            </div>
          )}
          <div className="flex gap-3">
            <Button onClick={() => reset()} className="flex-1">
              Try Again
            </Button>
            <Button variant="outline" onClick={() => window.location.href = '/dashboard'}>
              Go Home
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
