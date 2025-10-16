"use client"

import { useCallback, useMemo, useState } from 'react'
import { ReportOut } from '../types'
import { parseSSE } from '../lib/sse'
import { downloadMarkdown } from '../utils/export'
import clsx from 'clsx'
import ReportView from './report/ReportView'

const BACKEND = process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8000'
const DEFAULT_USER = process.env.NEXT_PUBLIC_USER_ID || 'anonymous'

export default function UploadPanel() {
  const [file, setFile] = useState<File | null>(null)
  const [streaming, setStreaming] = useState(true)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [progress, setProgress] = useState<any[]>([])
  const [report, setReport] = useState<ReportOut | null>(null)

  const onFile = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    const f = e.target.files?.[0] || null
    setFile(f)
    setReport(null)
    setError(null)
    setProgress([])
  }, [])

  const handleSubmit = useCallback(async () => {
    if (!file) return
    setLoading(true)
    setError(null)
    setReport(null)
    setProgress([])
    try {
      const form = new FormData()
      form.append('file', file)
      const endpoint = streaming ? 'analyze_sse' : 'analyze'
      const url = `${BACKEND}/${endpoint}?user_id=${encodeURIComponent(DEFAULT_USER)}`
      if (streaming) {
        const res = await fetch(url, { method: 'POST', body: form })
        if (!res.ok && res.headers.get('content-type')?.includes('application/json')) {
          const j = await res.json().catch(() => null)
          throw new Error(j?.detail || `HTTP ${res.status}`)
        }
        if (!res.body) throw new Error('No response body')
        for await (const { event, data } of parseSSE(res.body)) {
          if (event === 'error') {
            const msg = safeParseData(data)?.message || 'Streaming error'
            setProgress((p) => [...p, { event, data: safeParseData(data) }])
            throw new Error(msg)
          }
          if (event === 'done') {
            const payload = safeParseData(data)
            setReport(payload as ReportOut)
            setProgress((p) => [...p, { event, data: payload }])
          } else {
            setProgress((p) => [...p, { event, data: safeParseData(data) }])
          }
        }
      } else {
        const res = await fetch(url, { method: 'POST', body: form })
        if (!res.ok) {
          if (res.status === 413) throw new Error('File too large (max 10MB).')
          if (res.status === 400) {
            const j = await res.json().catch(() => null)
            throw new Error(j?.detail || 'Bad request')
          }
          if (res.status === 401) throw new Error('Unauthorized (check API key).')
          throw new Error(`HTTP ${res.status}`)
        }
        const payload = await res.json()
        setReport(payload as ReportOut)
      }
    } catch (e: any) {
      setError(e?.message || 'Unknown error')
    } finally {
      setLoading(false)
    }
  }, [file, streaming])

  const canAnalyze = useMemo(() => !!file && !loading, [file, loading])

  return (
    <section className="space-y-4">
      <div className="rounded-lg border p-4">
        <div className="flex items-center gap-4">
          <input type="file" accept="application/pdf" onChange={onFile} />
          <label className="flex items-center gap-2 text-sm">
            <input type="checkbox" checked={streaming} onChange={e => setStreaming(e.target.checked)} />
            Streaming (SSE)
          </label>
          <button
            onClick={handleSubmit}
            disabled={!canAnalyze}
            className={clsx('px-3 py-1.5 rounded bg-blue-600 text-white text-sm', (!canAnalyze) && 'opacity-50 cursor-not-allowed')}
          >
            Analyze
          </button>
        </div>
        {error && <p className="mt-3 text-sm text-red-600">{error}</p>}
        {loading && <ProgressPanel progress={progress} />}
      </div>

      {report && (
        <div className="rounded-lg border p-4">
          <div className="flex items-center justify-between">
            <h2 className="text-xl font-semibold">Report</h2>
            <button className="px-3 py-1.5 rounded bg-gray-800 text-white text-sm" onClick={() => downloadMarkdown(report, file?.name || 'report')}>Download Markdown</button>
          </div>
          <ReportView report={report} />
        </div>
      )}
    </section>
  )
}

function safeParseData(data: any) {
  try { return typeof data === 'string' ? JSON.parse(data) : data } catch { return {} }
}

function ProgressPanel({ progress }: { progress: any[] }) {
  return (
    <div className="mt-4 space-y-2 text-sm">
      {progress.map((p, idx) => (
        <div key={idx} className="flex items-start gap-2">
          <span className="inline-flex w-16 shrink-0 select-none text-gray-500">{p.event}</span>
          <pre className="text-xs whitespace-pre-wrap leading-snug overflow-x-auto">{JSON.stringify(p.data, null, 2)}</pre>
        </div>
      ))}
    </div>
  )
}
