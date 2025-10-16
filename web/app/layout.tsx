import type { Metadata } from 'next'
import './globals.css'

export const metadata: Metadata = {
  title: 'AI Compliance Copilot',
  description: 'Powered by Groq - Ultra-fast compliance analysis',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  )
}
