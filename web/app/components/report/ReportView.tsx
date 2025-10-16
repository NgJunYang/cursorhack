"use client"

import { ReportOut } from '../../types'
import { SeverityBadge } from './SeverityBadge'

export default function ReportView({ report }: { report: ReportOut }) {
  return (
    <div className="space-y-6">
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="rounded border p-3">
          <div className="text-sm text-gray-500">Overall Risk</div>
          <div className="text-3xl font-bold">{report.overall_risk}%</div>
        </div>
        <div className="md:col-span-2 rounded border p-3">
          <div className="text-sm text-gray-500 mb-1">Executive Summary</div>
          <p className="whitespace-pre-wrap leading-relaxed">{report.summary}</p>
        </div>
      </div>

      <div>
        <div className="text-lg font-medium mb-2">Red Flags</div>
        <div className="overflow-x-auto">
          <table className="min-w-full text-sm">
            <thead>
              <tr className="text-left border-b">
                <th className="py-2 pr-4">Title</th>
                <th className="py-2 pr-4">Severity</th>
                <th className="py-2 pr-4">Evidence</th>
              </tr>
            </thead>
            <tbody>
              {report.flags?.map((f, i) => (
                <tr key={i} className="border-b align-top">
                  <td className="py-2 pr-4">
                    <div className="font-medium">{f.title}</div>
                    <div className="text-gray-600 text-xs">Why it matters: {f.why_it_matters}</div>
                    <div className="text-gray-600 text-xs">Recommendation: {f.recommendation}</div>
                  </td>
                  <td className="py-2 pr-4"><SeverityBadge severity={f.severity} /></td>
                  <td className="py-2 pr-4">
                    <ul className="space-y-1">
                      {f.evidence?.map((ev, j) => (
                        <li key={j} className="text-gray-800 text-xs">
                          <span className="text-gray-500">p.{ev.page}</span>: {ev.quote}
                        </li>
                      ))}
                    </ul>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  )
}
