# Compliance Copilot (Groq Edition)

Minimal, fast AI compliance analyzer for financial/legal PDFs. Backend (FastAPI) uses Groq Llama 3 for ultra-low latency; frontend is Next.js 14 + Tailwind. Includes SSE live streaming and Supabase history.

## Features
- PDF upload (10 MB limit)
- Text extraction (PyMuPDF → pdfplumber fallback)
- Groq Llama3-70B analysis
- Robust JSON validation and fallback
- Evidence quotes clipped ≤ 600 chars
- SSE endpoint for live stages: `ingest`, `extract`, `analyze`, `done`
- Supabase report history
- Markdown export
- Dark/light mode toggle

## Stack
- Backend: FastAPI, Groq SDK, PyMuPDF, pdfplumber, Supabase
- Frontend: Next.js 14, Tailwind CSS

## Setup

### 1) Backend
Create `.env` from template:

```bash
cp .env.example .env
# Fill GROQ_API_KEY, SUPABASE_URL, SUPABASE_KEY
```

Install deps and run:

```bash
python3 -m pip install -r requirements.txt
uvicorn app:app --reload --port 8000
```

Endpoints:
- POST `/analyze` (multipart/form-data: file=PDF, query: user_id)
- POST `/analyze_sse` (SSE stream)
- GET `/reports?user_id=anonymous&limit=20`

### 2) Frontend
Create env:

```bash
cd web
cp .env.example .env
npm install
npm run dev
```

Open `http://localhost:3000`.

Set `NEXT_PUBLIC_BACKEND_URL` in `web/.env` if backend URL differs.

## Usage
1. Upload a PDF and toggle Streaming (SSE) on/off.
2. Watch live progress. On completion, view the summary, risk score, and red flags.
3. Download Markdown report or view recent reports (from Supabase).

## JSON Contract
Response JSON:
```json
{
  "summary": "...",
  "overall_risk": 42.0,
  "flags": [
    {
      "title": "...",
      "severity": 3,
      "why_it_matters": "...",
      "recommendation": "...",
      "evidence": [ { "page": 2, "quote": "... <=600 chars" } ]
    }
  ]
}
```
Defaults: `overall_risk = mean(severity)/5*100` if missing; quotes clipped ≤ 600 chars.

## SSE
`POST /analyze_sse` returns `text/event-stream` frames like:
- `event: ingest` data: `{ filename, size_mb }`
- `event: extract` data: `{ pages, chars, chunks }`
- `event: analyze` data: `{ status: "started" }`
- `event: done` data: the full report JSON
- `event: error` data: `{ message }`

Frontend parses SSE with a streaming reader and updates a progress panel.

## Supabase
Schema:
```sql
create table reports (
  id bigint generated always as identity primary key,
  user_id text not null,
  doc_name text,
  summary text,
  overall_risk double precision,
  flags jsonb,
  ts bigint
);
```
Set `SUPABASE_URL`, `SUPABASE_KEY` in backend `.env`. The app best-effort inserts and lists per `user_id`.

## Testing
Run backend tests:
```bash
python3 -m pytest -q
```

## Notes
- 413 on oversize; 400 on bad/empty PDFs; 401 if upstream auth is missing.
- Average LLM response target: < 3s for 5-page PDF (use Groq’s high-throughput infra).
- Footer includes “Powered by Groq”.
