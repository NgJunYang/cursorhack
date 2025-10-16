export interface EvidenceItem { page: number; quote: string }
export interface FlagItem {
  title: string
  severity: number
  why_it_matters: string
  recommendation: string
  evidence: EvidenceItem[]
}
export interface ReportOut {
  summary: string
  overall_risk: number
  flags: FlagItem[]
}

export type AnalyzeEventName = 'ingest' | 'extract' | 'analyze' | 'done' | 'error'
export interface AnalyzeEvent<T = unknown> { event: AnalyzeEventName; data: T }
