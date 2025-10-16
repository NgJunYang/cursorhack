# AI Compliance Copilot (Groq Edition)

> **Ultra-fast compliance analysis powered by Groq's Llama 3 API**

A production-ready AI compliance analysis tool built for the 24-hour Cursor Hackathon. Upload financial or legal PDFs and get instant compliance reports with red-flag findings, severity scores, and actionable recommendations.

## 🚀 Features

- **⚡ Ultra-Fast Analysis**: Powered by Groq's Llama 3 (llama3-70b-8192) - average response time < 3s for 5-page PDFs
- **📊 Live Streaming (SSE)**: Real-time progress updates with Server-Sent Events showing:
  - Ingest stage: Processing PDF file
  - Extract stage: Extracting text from PDF
  - Analyze stage: AI analysis with Groq LLM
  - Done event: Complete report with JSON payload
- **🔍 Compliance Categories**: Detects Cross-Border, AML, Sanctions, PDPA/GDPR violations
- **📈 Risk Scoring**: Severity ratings (1-5) and overall risk percentage
- **📝 Evidence Tracking**: Page-referenced quotes (≤600 chars) from source documents
- **💾 History**: Supabase-backed reports database
- **📥 Export**: Download detailed Markdown reports
- **🎨 Modern UI**: Dark/light mode, responsive design with Tailwind CSS
- **🔄 Fallback Mode**: Toggle between streaming and non-streaming analysis

## 🛠️ Tech Stack

- **Backend**: FastAPI (Python 3.10+)
- **LLM Engine**: Groq API (llama3-70b-8192)
- **Database**: Supabase
- **Frontend**: Next.js 14 + TypeScript + Tailwind CSS
- **PDF Processing**: pdfplumber

## 📋 Prerequisites

- Python 3.10+
- Node.js 18+
- Groq API Key ([Get one here](https://console.groq.com))
- Supabase Account ([Sign up here](https://supabase.com))

## 🔧 Installation

### 1. Clone & Setup

```bash
git clone <repository-url>
cd cursorhack
```

### 2. Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your API keys:
# GROQ_API_KEY=your_groq_api_key
# SUPABASE_URL=your_supabase_url
# SUPABASE_KEY=your_supabase_anon_key
```

### 3. Supabase Database Setup

Create the `reports` table in your Supabase dashboard:

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

-- Optional: Add index for faster queries
create index idx_reports_ts on reports(ts desc);
create index idx_reports_user_id on reports(user_id);
```

### 4. Frontend Setup

```bash
cd ../web

# Install dependencies
npm install

# Configure environment
cp .env.local.example .env.local
# Edit .env.local:
# NEXT_PUBLIC_API_URL=http://localhost:8000
```

## 🚀 Running the Application

### Start Backend (Terminal 1)

```bash
cd backend
source venv/bin/activate
uvicorn app:app --reload --port 8000
```

Backend will run at: http://localhost:8000

### Start Frontend (Terminal 2)

```bash
cd web
npm run dev
```

Frontend will run at: http://localhost:3000

## 📡 API Endpoints

### POST `/analyze`
**Non-streaming analysis endpoint**

- **Request**: `multipart/form-data` with PDF file (max 10MB)
- **Response**: JSON report with summary, overall_risk, and flags
- **Errors**: 
  - 400: Invalid file format or empty file
  - 413: File size exceeds 10MB
  - 500: Analysis failed

**Example:**
```bash
curl -X POST http://localhost:8000/analyze \
  -F "file=@document.pdf"
```

### POST `/analyze_sse`
**Streaming analysis endpoint with Server-Sent Events**

- **Request**: `multipart/form-data` with PDF file (max 10MB)
- **Response**: `text/event-stream` with progress events
- **Event Types**:
  - `progress`: Stage updates (ingest, extract, analyze)
  - `done`: Final report JSON
  - `error`: Error messages

**SSE Event Format:**
```
event: progress
data: {"stage": "ingest", "message": "Processing PDF file..."}

event: progress
data: {"stage": "extract", "message": "Extracting text from PDF..."}

event: progress
data: {"stage": "analyze", "message": "Analyzing with Groq LLM..."}

event: done
data: {"doc_name": "file.pdf", "summary": "...", "overall_risk": 0.75, "flags": [...]}
```

**Frontend Implementation:**
```typescript
const response = await fetch('/analyze_sse', {
  method: 'POST',
  body: formData,
});

const reader = response.body.getReader();
const decoder = new TextDecoder();

while (true) {
  const { done, value } = await reader.read();
  if (done) break;
  
  const text = decoder.decode(value);
  // Parse SSE events
  const lines = text.split('\n\n');
  for (const line of lines) {
    const [eventLine, dataLine] = line.split('\n');
    const event = eventLine.substring(6).trim();
    const data = JSON.parse(dataLine.substring(5).trim());
    
    if (event === 'progress') {
      // Update UI with progress
    } else if (event === 'done') {
      // Display final report
    }
  }
}
```

### GET `/reports`
**Fetch recent reports**

- **Query Params**: `limit` (default: 10)
- **Response**: JSON array of reports

### GET `/health`
**Health check endpoint**

- **Response**: `{"status": "ok", "groq": true, "supabase": true}`

## 🧪 Testing

Run backend tests:

```bash
cd backend
pytest test_app.py -v
```

Tests verify:
- Evidence truncation (≤600 chars)
- JSON schema validation
- Overall risk calculation

## 📊 Response Schema

```typescript
interface Report {
  doc_name: string;
  page_count?: number;
  summary: string;
  overall_risk: number;  // 0.0 - 1.0
  flags: Flag[];
}

interface Flag {
  title: string;           // e.g., "Cross-Border Transaction"
  severity: number;        // 1-5
  why_it_matters: string;
  recommendation: string;
  evidence: Evidence[];
}

interface Evidence {
  page: number;
  quote: string;  // Max 600 characters
}
```

## 🎨 UI Features

### Streaming Progress Panel
Real-time visualization of analysis stages with animated progress indicators.

### Dark/Light Mode Toggle
System preference detection with manual override.

### Color-Coded Severity
- **Green (1-2)**: Low risk
- **Yellow (3)**: Medium risk  
- **Red (4-5)**: High risk

### Responsive Design
Optimized for desktop, tablet, and mobile devices.

## 🔒 Error Handling

The application provides clear error messages for common issues:

- **400 Bad Request**: Invalid file format or empty PDF
- **401 Unauthorized**: Invalid API credentials
- **413 Payload Too Large**: File exceeds 10MB limit
- **500 Internal Server Error**: Analysis or processing failure
- **Streaming Errors**: Connection issues, malformed SSE events

## 📈 Performance

- **Average LLM Response**: < 3s for 5-page PDF
- **Concurrent Requests**: Supported via FastAPI async
- **Evidence Truncation**: Automatic clipping at 600 chars
- **Retry Logic**: Automatic JSON parsing retry on failure

## 🏆 Hackathon Features

Built for Cursor Hackathon with focus on:
- **Speed**: Groq's ultra-fast inference
- **Reliability**: Robust error handling and fallbacks
- **UX**: Live streaming progress and dark mode
- **Production-Ready**: Environment configs, tests, documentation

## 📝 Demo Script

1. Start both backend and frontend servers
2. Open http://localhost:3000
3. Toggle "Enable Streaming" checkbox
4. Drag & drop a financial/legal PDF (< 10MB)
5. Watch live progress through ingest → extract → analyze stages
6. Review compliance report with severity ratings
7. Download Markdown report
8. Check "Recent Reports" for history
9. Toggle dark/light mode

## 🔗 Links

- **Groq**: https://groq.com
- **Supabase**: https://supabase.com
- **Next.js**: https://nextjs.org
- **FastAPI**: https://fastapi.tiangolo.com

## 📄 License

MIT License - Built for Cursor Hackathon 2024

---

**Powered by Groq** | Built with ❤️ in 24 hours
