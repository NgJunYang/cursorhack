"use client"

import clsx from 'clsx'

export function SeverityBadge({ severity }: { severity: number }) {
  const color = severity >= 4 ? 'bg-red-100 text-red-800 border-red-300' : severity === 3 ? 'bg-yellow-100 text-yellow-800 border-yellow-300' : 'bg-green-100 text-green-800 border-green-300'
  return (
    <span className={clsx('inline-flex items-center px-2 py-0.5 rounded text-xs border', color)}>
      {severity}
    </span>
  )
}
