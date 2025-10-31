import { NextResponse } from 'next/server'
import type { NextRequest } from 'next/server'

// Simple middleware to redirect from root /dashboard to /dashboard/dashboard
export function middleware(request: NextRequest) {
  // This middleware runs on all routes matching the config below
  return NextResponse.next()
}

// Configure which routes this middleware runs on
export const config = {
  matcher: [
    /*
     * Match all request paths except:
     * - _next/static (static files)
     * - _next/image (image optimization files)
     * - favicon.ico (favicon file)
     * - public folder
     */
    '/((?!_next/static|_next/image|favicon.ico|public).*)',
  ],
}
