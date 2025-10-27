export function LoadingSpinner({ size = 'md' }: { size?: 'sm' | 'md' | 'lg' }) {
  const sizeClasses = {
    sm: 'w-4 h-4 border-2',
    md: 'w-8 h-8 border-4',
    lg: 'w-12 h-12 border-4',
  }

  return (
    <div className={`${sizeClasses[size]} border-purple-600 border-t-transparent rounded-full animate-spin`}></div>
  )
}

export function LoadingPage({ message = 'Loading...' }: { message?: string }) {
  return (
    <div className="min-h-screen flex items-center justify-center">
      <div className="text-center">
        <LoadingSpinner size="lg" />
        <p className="text-gray-600 mt-4">{message}</p>
      </div>
    </div>
  )
}

export function LoadingCard({ message = 'Loading...' }: { message?: string }) {
  return (
    <div className="text-center py-12">
      <LoadingSpinner />
      <p className="text-gray-600 mt-4">{message}</p>
    </div>
  )
}
