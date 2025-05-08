import './globals.css'
import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import { SearchProvider } from './contexts/SearchContext'

const inter = Inter({ subsets: ['latin'] })

export const metadata: Metadata = {
  title: 'eBay Price Scraper',
  description: 'A tool to scrape and analyze eBay product prices',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body className={inter.className}>
        <SearchProvider>
          {children}
        </SearchProvider>
      </body>
    </html>
  )
} 