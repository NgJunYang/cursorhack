import { ReportOut } from '../types'

export function generateMarkdown(report: ReportOut, docName: string) {
  const lines: string[] = []
  lines.push(`# Compliance Report: ${docName}`)
  lines.push('')
  lines.push(`**Overall Risk:** ${report.overall_risk}%`)
  lines.push('')
  lines.push('## Executive Summary')
  lines.push(report.summary || 'No summary provided.')
  lines.push('')
  lines.push('## Red Flags')
  if (!report.flags?.length) {
    lines.push('No red flags identified.')
  } else {
    for (const f of report.flags) {
      lines.push(`### ${f.title}`)
      lines.push(`- Severity: ${f.severity}`)
      lines.push(`- Why it matters: ${f.why_it_matters}`)
      lines.push(`- Recommendation: ${f.recommendation}`)
      if (f.evidence?.length) {
        lines.push('- Evidence:')
        for (const ev of f.evidence) {
          const quote = (ev.quote || '').slice(0, 600)
          lines.push(`  - p.${ev.page}: "${quote.replace(/\"/g, '"')}"`)
        }
      }
      lines.push('')
    }
  }
  return lines.join('\n')
}

export function downloadMarkdown(report: ReportOut, docName: string) {
  const md = generateMarkdown(report, docName)
  const blob = new Blob([md], { type: 'text/markdown;charset=utf-8' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `${docName.replace(/[^a-z0-9-_\.]/gi, '_')}.md`
  document.body.appendChild(a)
  a.click()
  a.remove()
  URL.revokeObjectURL(url)
}
