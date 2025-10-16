"use client"

import { useEffect, useState } from 'react'
import { ReportOut } from '../types'

const BACKEND = process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8000'
const DEFAULT_USER = process.env.NEXT_PUBLIC_USER_ID || 'anonymous'

type Item = {
  id: number
  doc_name: string
  overall_risk: number
  summary: string
  flags: any
  ts: number
}

export default function RecentReports() {
  const [items, setItems] = useState<Item[]>([])

  useEffect(() => {
    const url = `${BACKEND}/reports?user_id=${encodeURIComponent(DEFAULT_USER)}&limit=10`
    fetch(url).then(r => r.json()).then(j => setItems(j?.reports || [])).catch(() => setItems([]))
  }, [])

  if (!items.length) return null

  return (
    <section className="rounded-lg border p-4">
      <h2 className="text-lg font-semibold mb-3">Recent Reports</h2>
      <div className="space-y-2">
        {items.map((it) => (
          <div key={it.id} className="flex items-start justify-between gap-4 text-sm">
            <div>
              <div className="font-medium">{it.doc_name || 'document.pdf'}</div>
              <div className="text-gray-600 max-w-3xl">{it.summary}</div>
            </div>
            <div className="text-right">
              <div className="text-xs text-gray-500">{new Date(it.ts).toLocaleString()}</div>
              <div className="font-semibold">{it.overall_risk}%</div>
            </div>
          </div>
        ))}
      </div>
    </section>
  )
}
