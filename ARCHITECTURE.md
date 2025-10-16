# 🏗️ Architecture Overview

## System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                         Frontend (Next.js 14)                │
│  ┌──────────────┐  ┌──────────────┐  ┌─────────────────┐   │
│  │ Upload Zone  │  │  Streaming   │  │  Report View    │   │
│  │  + Toggle    │  │  Progress    │  │  + Markdown     │   │
│  └──────────────┘  └──────────────┘  └─────────────────┘   │
│         │                   │                    │           │
│         └───────────────────┴────────────────────┘           │
│                             │                                │
│                      SSE / HTTP POST                         │
└─────────────────────────────┼───────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    Backend (FastAPI)                         │
│  ┌────────────────┐  ┌─────────────────┐  ┌──────────────┐ │
│  │  /analyze      │  │  /analyze_sse   │  │  /reports    │ │
│  │  (standard)    │  │  (streaming)    │  │  (history)   │ │
│  └────────────────┘  └─────────────────┘  └──────────────┘ │
│           │                    │                   │         │
│           ▼                    ▼                   │         │
│  ┌─────────────────────────────────────────────┐  │         │
│  │         PDF Processing (pdfplumber)         │  │         │
│  └─────────────────────────────────────────────┘  │         │
│                        │                           │         │
│                        ▼                           │         │
│  ┌─────────────────────────────────────────────┐  │         │
│  │      Groq LLM (llama3-70b-8192)            │  │         │
│  │      - Compliance Analysis                  │  │         │
│  │      - JSON Response Generation             │  │         │
│  └─────────────────────────────────────────────┘  │         │
│                        │                           │         │
│                        ▼                           ▼         │
│  ┌──────────────────────────────────────────────────────┐   │
│  │              Supabase PostgreSQL                      │   │
│  │              - Reports Storage                        │   │
│  │              - History Tracking                       │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

## Data Flow

### Non-Streaming Analysis (`/analyze`)

```
1. User uploads PDF → Frontend
2. Frontend → POST /analyze (multipart/form-data)
3. Backend validates file (size, type)
4. pdfplumber extracts text + page numbers
5. Text → Groq LLM with compliance prompt
6. Groq returns JSON analysis
7. Validate & truncate evidence (≤600 chars)
8. Save to Supabase
9. Return JSON response → Frontend
10. Frontend displays report
```

### Streaming Analysis (`/analyze_sse`)

```
1. User uploads PDF → Frontend
2. Frontend → POST /analyze_sse (multipart/form-data)
3. Backend validates file (size, type)
4. Backend sends SSE: event=progress, stage=ingest
5. pdfplumber extracts text
6. Backend sends SSE: event=progress, stage=extract
7. Text → Groq LLM
8. Backend sends SSE: event=progress, stage=analyze
9. Groq returns analysis
10. Validate & save to Supabase
11. Backend sends SSE: event=done, data={full report}
12. Frontend parses SSE stream
13. Frontend updates progress UI in real-time
14. Frontend displays final report
```

## Technology Choices

### Backend: FastAPI
**Why?**
- Async/await for high concurrency
- Built-in SSE support via `StreamingResponse`
- Fast JSON validation with Pydantic
- OpenAPI docs auto-generation

**Alternatives considered:**
- Flask (no async, harder SSE)
- Django (too heavyweight)

### LLM: Groq (Llama 3 70B)
**Why?**
- Ultra-fast inference (< 3s for compliance analysis)
- Cost-effective compared to OpenAI
- Llama 3 has strong reasoning for legal/financial text
- Simple Python SDK

**Alternatives considered:**
- OpenAI GPT-4 (slower, 8-10s)
- Anthropic Claude (good but slower)
- Local models (too slow, GPU required)

### Database: Supabase
**Why?**
- PostgreSQL (JSONB support for flags)
- Instant REST API
- Real-time subscriptions (future feature)
- Free tier sufficient for hackathon

**Alternatives considered:**
- MongoDB (schemaless, but no JSONB queries)
- SQLite (no cloud, not scalable)

### Frontend: Next.js 14 + TypeScript
**Why?**
- App Router for modern patterns
- TypeScript for type safety
- Tailwind CSS for rapid UI dev
- Server/Client components flexibility

**Alternatives considered:**
- React SPA (no SSR, worse SEO)
- Vue (less ecosystem)

### PDF Processing: pdfplumber
**Why?**
- Accurate text extraction
- Table detection (future use)
- Page-level text access
- Better than PyPDF2 for complex layouts

**Alternatives considered:**
- PyPDF2 (less accurate)
- PyMuPDF (harder to use)

## Key Design Decisions

### Server-Sent Events (SSE)
**Choice:** Use SSE for streaming instead of WebSockets

**Reasoning:**
- Simpler protocol (HTTP-based)
- No need for bidirectional communication
- Better browser compatibility
- Automatic reconnection in modern browsers
- Works through most proxies/firewalls

**Implementation:**
```python
async def sse_generator(file_bytes: bytes) -> AsyncGenerator:
    yield f"event: progress\ndata: {json.dumps(...)}\n\n"
    # ... processing ...
    yield f"event: done\ndata: {json.dumps(report)}\n\n"
```

### Evidence Truncation
**Choice:** Limit evidence quotes to 600 characters

**Reasoning:**
- Prevents payload bloat
- Keeps UI readable
- Still provides sufficient context
- Reduces LLM token usage

**Implementation:**
```python
def truncate_evidence(evidence_list):
    for ev in evidence_list:
        if len(ev['quote']) > 600:
            ev['quote'] = ev['quote'][:600] + "..."
    return evidence_list
```

### JSON Retry Logic
**Choice:** Automatic retry if LLM returns invalid JSON

**Reasoning:**
- LLMs sometimes return markdown-wrapped JSON
- Prevents analysis failures
- Improves reliability
- Degrades gracefully

**Implementation:**
```python
try:
    result = json.loads(content)
except json.JSONDecodeError:
    # Retry with stricter prompt
    response = groq_client.chat.completions.create(
        messages=[..., {"role": "user", "content": "Return ONLY valid JSON"}]
    )
    result = json.loads(response.choices[0].message.content)
```

### Dual Endpoints
**Choice:** Provide both `/analyze` and `/analyze_sse`

**Reasoning:**
- SSE not universally supported (corporate proxies)
- Some users prefer simple request/response
- A/B testing streaming vs non-streaming UX
- Graceful degradation

## Security Considerations

### Current Implementation (Hackathon)
- ✅ File size validation (10MB limit)
- ✅ File type validation (.pdf only)
- ✅ CORS configuration
- ✅ Environment variable separation
- ⚠️ No authentication (demo only)
- ⚠️ No rate limiting

### Production Additions Needed
- [ ] User authentication (Supabase Auth)
- [ ] Row-level security in database
- [ ] API key rotation
- [ ] Rate limiting (per user/IP)
- [ ] Input sanitization for filenames
- [ ] Virus scanning for uploads
- [ ] Audit logging
- [ ] HTTPS enforcement

## Performance Optimizations

### Backend
- **Async processing**: FastAPI handles 100+ concurrent requests
- **Streaming chunks**: SSE sends data as soon as available
- **Connection pooling**: Supabase client reuses connections
- **Text chunking**: Send first 8000 chars to LLM (balance speed/accuracy)

### Frontend
- **Code splitting**: Next.js auto-splits routes
- **Lazy loading**: Components load on demand
- **Debouncing**: Prevents duplicate uploads
- **Optimistic UI**: Shows progress immediately

### Database
- **Indexes**: On `ts` and `user_id` columns
- **JSONB**: Efficient querying of nested flags
- **Limited queries**: Only fetch top 10 recent reports

## Error Handling Strategy

### HTTP Status Codes
- `200`: Success
- `400`: Bad request (invalid file, empty PDF)
- `401`: Unauthorized (invalid API key)
- `413`: Payload too large (> 10MB)
- `500`: Internal server error

### Frontend Error Display
```typescript
const getErrorMessage = (err: any): string => {
  if (err.includes('413')) return 'File too large (max 10MB)';
  if (err.includes('400')) return 'Invalid PDF file';
  if (err.includes('401')) return 'API authentication failed';
  return `Analysis failed: ${err.message}`;
}
```

### SSE Error Events
```
event: error
data: {"error": "Could not extract text from PDF"}
```

## Scalability Path

### Current Limits (Free Tier)
- Groq: 30 requests/minute
- Supabase: 500MB DB, 2GB bandwidth/month
- Next.js: Unlimited (Vercel free tier)

### Scale to 1000 users/day
- [ ] Groq Pro: 60 requests/minute
- [ ] Supabase Pro: 8GB DB, 50GB bandwidth
- [ ] Redis for caching
- [ ] CDN for static assets

### Scale to 10,000+ users/day
- [ ] Load balancer (Nginx)
- [ ] Horizontal scaling (Kubernetes)
- [ ] Dedicated Groq deployment
- [ ] Database read replicas
- [ ] Message queue (RabbitMQ/SQS)

## Testing Strategy

### Unit Tests (`test_app.py`)
- Evidence truncation logic
- JSON schema validation
- Risk score calculation

### Integration Tests (TODO)
- End-to-end PDF upload
- SSE stream parsing
- Supabase CRUD operations

### Manual Testing Checklist
- [ ] Upload valid PDF → Success
- [ ] Upload > 10MB PDF → 413 error
- [ ] Upload .docx file → 400 error
- [ ] Upload empty PDF → 400 error
- [ ] Streaming toggle works
- [ ] Dark mode toggle works
- [ ] Markdown download works
- [ ] Recent reports loads

## Future Enhancements

### Short-term (1 week)
- [ ] User authentication
- [ ] Document history per user
- [ ] Email report delivery
- [ ] Support DOCX, TXT formats

### Medium-term (1 month)
- [ ] Real-time collaboration
- [ ] Custom compliance rules
- [ ] Batch processing
- [ ] Advanced search/filtering

### Long-term (3 months)
- [ ] Multi-language support
- [ ] Voice narration (ElevenLabs)
- [ ] Compare with GPT-4 (benchmark)
- [ ] Chrome extension
- [ ] Mobile app (React Native)

## Deployment Guide

### Backend → Railway
```bash
# railway.toml
[build]
builder = "NIXPACKS"

[deploy]
startCommand = "uvicorn app:app --host 0.0.0.0 --port $PORT"

[env]
GROQ_API_KEY = "$GROQ_API_KEY"
SUPABASE_URL = "$SUPABASE_URL"
SUPABASE_KEY = "$SUPABASE_KEY"
```

### Frontend → Vercel
```bash
# vercel.json
{
  "buildCommand": "npm run build",
  "outputDirectory": ".next",
  "env": {
    "NEXT_PUBLIC_API_URL": "@api_url"
  }
}
```

---

**Built for Cursor Hackathon 2024** | Powered by Groq
