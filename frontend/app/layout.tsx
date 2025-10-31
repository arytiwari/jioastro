import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import './globals.css'
import { Providers } from './providers'

const inter = Inter({ subsets: ['latin'] })

export const metadata: Metadata = {
  title: 'JioAstro - AI-Powered Vedic Astrology',
  description: 'AI-powered Vedic astrology service with birth chart generation and personalized interpretations by JioAstro',
  keywords: 'jioastro, vedic astrology, birth chart, jyotish, ai astrology, horoscope',
  authors: [{ name: 'JioAstro' }],
  viewport: 'width=device-width, initial-scale=1',
  themeColor: '#0056d6',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body className={inter.className}>
        <Providers>{children}</Providers>
      </body>
    </html>
  )
}
