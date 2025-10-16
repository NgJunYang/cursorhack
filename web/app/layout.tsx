import './globals.css'
import type { Metadata } from 'next'

export const metadata: Metadata = {
  title: 'AI Compliance Copilot (Groq Edition)',
  description: 'Upload a PDF to get a structured compliance report.',
}

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body className="min-h-screen">
        <div className="container py-6">
          <header className="mb-6 flex items-center justify-between">
            <h1 className="text-2xl font-semibold">AI Compliance Copilot</h1>
            <div className="flex items-center gap-3">
              <ThemeToggle />
              <a className="text-sm text-blue-600 hover:underline" href="https://groq.com" target="_blank" rel="noreferrer">Powered by Groq</a>
            </div>
          </header>
          {children}
          <footer className="mt-12 text-sm text-gray-500">
            <p>
              Built with Next.js, FastAPI, and Supabase. <a className="text-blue-600 hover:underline" href="https://groq.com" target="_blank" rel="noreferrer">Groq</a>
            </p>
          </footer>
        </div>
      </body>
    </html>
  )
}

function ThemeToggle() {
  if (typeof window === 'undefined') return null
  const isDark = typeof document !== 'undefined' && document.documentElement.classList.contains('dark')
  const label = isDark ? 'Light' : 'Dark'
  const onClick = () => {
    const root = document.documentElement
    if (root.classList.contains('dark')) root.classList.remove('dark')
    else root.classList.add('dark')
  }
  return (
    <button className="px-2 py-1 rounded border text-xs" onClick={onClick}>{label} mode</button>
  )
}
