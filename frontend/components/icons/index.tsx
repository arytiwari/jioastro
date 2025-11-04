import * as React from "react"

export type IconProps = React.SVGProps<SVGSVGElement>

function createIcon(paths: React.ReactNode, displayName: string) {
  const Icon = React.forwardRef<SVGSVGElement, IconProps>(function Icon({ className, ...props }, ref) {
    return (
      <svg
        ref={ref}
        xmlns="http://www.w3.org/2000/svg"
        viewBox="0 0 24 24"
        fill="none"
        stroke="currentColor"
        strokeWidth={2}
        strokeLinecap="round"
        strokeLinejoin="round"
        className={className}
        {...props}
      >
        {paths}
      </svg>
    )
  })

  Icon.displayName = displayName
  return Icon
}

export const Activity = createIcon(
  <polyline points="3 12 6 12 8 7 12 19 16 9 18 12 21 12" />,
  "Activity"
)

export const AlertCircle = createIcon(
  <>
    <circle cx="12" cy="12" r="9" />
    <line x1="12" y1="7" x2="12" y2="13" />
    <circle cx="12" cy="17" r="1" fill="currentColor" stroke="none" />
  </>,
  "AlertCircle"
)

export const ArrowLeft = createIcon(
  <>
    <line x1="19" y1="12" x2="5" y2="12" />
    <polyline points="12 5 5 12 12 19" />
  </>,
  "ArrowLeft"
)

export const BookOpen = createIcon(
  <>
    <path d="M12 6c-2.8-1.4-6-1.4-9 0v12c3-1.4 6-1.4 9 0" />
    <path d="M12 6c2.8-1.4 6-1.4 9 0v12c-3-1.4-6-1.4-9 0" />
    <line x1="12" y1="6" x2="12" y2="20" />
  </>,
  "BookOpen"
)

export const Briefcase = createIcon(
  <>
    <rect x="3" y="7" width="18" height="13" rx="2" />
    <path d="M9 7V5a2 2 0 0 1 2-2h2a2 2 0 0 1 2 2v2" />
    <line x1="3" y1="12" x2="21" y2="12" />
    <line x1="10" y1="12" x2="10" y2="15" />
    <line x1="14" y1="12" x2="14" y2="15" />
  </>,
  "Briefcase"
)

export const Calendar = createIcon(
  <>
    <rect x="3" y="4" width="18" height="17" rx="2" />
    <line x1="3" y1="9" x2="21" y2="9" />
    <line x1="8" y1="2" x2="8" y2="6" />
    <line x1="16" y1="2" x2="16" y2="6" />
  </>,
  "Calendar"
)

export const Check = createIcon(<polyline points="5 13 9 17 19 7" />, "Check")

export const ChevronDown = createIcon(<polyline points="6 9 12 15 18 9" />, "ChevronDown")

export const ChevronRight = createIcon(<polyline points="9 6 15 12 9 18" />, "ChevronRight")

export const ChevronUp = createIcon(<polyline points="6 15 12 9 18 15" />, "ChevronUp")

export const Clock = createIcon(
  <>
    <circle cx="12" cy="12" r="9" />
    <polyline points="12 7 12 12 15.5 13.5" />
  </>,
  "Clock"
)

export const Download = createIcon(
  <>
    <line x1="12" y1="3" x2="12" y2="15" />
    <polyline points="7 11 12 16 17 11" />
    <path d="M5 19h14" />
  </>,
  "Download"
)

export const Heart = createIcon(
  <path d="M12 20s-6.5-4.3-8.5-8A4.5 4.5 0 0 1 12 7.5 4.5 4.5 0 0 1 20.5 12c-2 3.7-8.5 8-8.5 8z" />,
  "Heart"
)

export const History = createIcon(
  <>
    <path d="M3 3v6h6" />
    <path d="M12 8a6 6 0 1 1-4.24 1.76L6 9" />
    <polyline points="12 12 12 14 14 15" />
  </>,
  "History"
)

export const Home = createIcon(
  <>
    <path d="M3 11 12 4l9 7" />
    <path d="M5 10v10h14V10" />
    <path d="M9 20v-6h6v6" />
  </>,
  "Home"
)

export const LogOut = createIcon(
  <>
    <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4" />
    <polyline points="16 17 21 12 16 7" />
    <line x1="21" y1="12" x2="9" y2="12" />
  </>,
  "LogOut"
)

export const MapPin = createIcon(
  <>
    <path d="M12 21s-6-6.2-6-11a6 6 0 1 1 12 0c0 4.8-6 11-6 11z" />
    <circle cx="12" cy="10" r="2.5" />
  </>,
  "MapPin"
)

export const Menu = createIcon(
  <>
    <line x1="4" y1="6" x2="20" y2="6" />
    <line x1="4" y1="12" x2="20" y2="12" />
    <line x1="4" y1="18" x2="20" y2="18" />
  </>,
  "Menu"
)

export const MessageSquare = createIcon(
  <>
    <path d="M21 15a2 2 0 0 1-2 2H9l-4 4V5a2 2 0 0 1 2-2h12a2 2 0 0 1 2 2z" />
  </>,
  "MessageSquare"
)

export const Plus = createIcon(
  <>
    <line x1="12" y1="5" x2="12" y2="19" />
    <line x1="5" y1="12" x2="19" y2="12" />
  </>,
  "Plus"
)

export const RefreshCw = createIcon(
  <>
    <polyline points="21 2 21 8 15 8" />
    <path d="M21 8a9 9 0 1 0 2.6 6.4" />
    <polyline points="3 22 3 16 9 16" />
    <path d="M3 16a9 9 0 1 1-2.6-6.4" />
  </>,
  "RefreshCw"
)

export const Sparkles = createIcon(
  <>
    <path d="M12 4l1.2 3.5L17 9l-3.8 1.5L12 14l-1.2-3.5L7 9l3.8-1.5z" />
    <path d="M6 3l0.8 2.2L9 6l-2.2 0.8L6 9 5.2 6.8 3 6l2.2-0.8z" />
    <path d="M18 13l0.6 1.6L20 15l-1.4 0.4L18 17l-0.6-1.6L16 15l1.4-0.4z" />
  </>,
  "Sparkles"
)

export const Star = createIcon(
  <path d="M12 4.5l2.5 5 5.5.8-4 3.8.9 5.4L12 16.9l-4.9 2.6.9-5.4-4-3.8 5.5-.8z" />,
  "Star"
)

export const TrendingUp = createIcon(
  <>
    <polyline points="3 17 9 11 13 15 21 7" />
    <polyline points="21 13 21 7 15 7" />
  </>,
  "TrendingUp"
)

export const User = createIcon(
  <>
    <circle cx="12" cy="8" r="4" />
    <path d="M5 20c1.5-3 4.5-4.5 7-4.5s5.5 1.5 7 4.5" />
  </>,
  "User"
)

export const DownloadCloud = createIcon(
  <>
    <path d="M20 16.6a4.4 4.4 0 0 0-1.3-8.6 6 6 0 0 0-11-.6A4 4 0 0 0 6 16.6" />
    <line x1="12" y1="11" x2="12" y2="19" />
    <polyline points="8 15 12 19 16 15" />
  </>,
  "DownloadCloud"
)

export const Sparkle = Sparkles

export const Book = BookOpen

export const Message = MessageSquare

export const MenuIcon = Menu

export const Close = createIcon(
  <>
    <line x1="5" y1="5" x2="19" y2="19" />
    <line x1="19" y1="5" x2="5" y2="19" />
  </>,
  "X"
)

export const X = Close

export const ChevronLeft = createIcon(<polyline points="15 6 9 12 15 18" />, "ChevronLeft")
