import './globals.css'
import type { Metadata } from 'next'

export const metadata: Metadata = {
  title: 'Nerior CRM',
  description: 'Workspace CRM for the Nerior ecosystem'
}

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="ru" suppressHydrationWarning>
      <body>{children}</body>
    </html>
  )
}
