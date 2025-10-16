# 🔴 Live Streaming (SSE) Implementation Guide

## Overview

This document details the Server-Sent Events (SSE) implementation for live streaming analysis in the AI Compliance Copilot.

## What is SSE?

Server-Sent Events (SSE) is a server push technology enabling servers to push real-time updates to clients over HTTP. Unlike WebSockets, SSE:
- Uses standard HTTP (no special protocols)
- Auto-reconnects on connection loss
- Simpler to implement and debug
- Works through most proxies/firewalls
- One-way communication (server → client)

## Architecture

```
Frontend                 Backend                  Groq LLM
   │                        │                        │
   │── POST /analyze_sse ───▶│                        │
   │                        │                        │
   │◀── event: progress ────│                        │
   │    stage: ingest       │                        │
   │                        │                        │
   │◀── event: progress ────│                        │
   │    stage: extract      │                        │
   │                        │                        │
   │◀── event: progress ────│                        │
   │    stage: analyze      │──── API call ─────────▶│
   │                        │                        │
   │                        │◀── JSON response ──────│
   │                        │                        │
   │◀── event: done ────────│                        │
   │    (full report JSON)  │                        │
```

## Backend Implementation (FastAPI)

### SSE Generator Function

```python
async def sse_generator(file_bytes: bytes, filename: str) -> AsyncGenerator[str, None]:
    """Generate SSE events for streaming analysis"""
    try:
        # Stage 1: Ingest
        yield f"event: progress\ndata: {json.dumps({'stage': 'ingest', 'message': 'Processing PDF file...'})}\n\n"
        
        # Stage 2: Extract
        yield f"event: progress\ndata: {json.dumps({'stage': 'extract', 'message': 'Extracting text from PDF...'})}\n\n"
        
        text, page_count = extract_text_from_pdf(file_bytes)
        
        if not text.strip():
            yield f"event: error\ndata: {json.dumps({'error': 'Could not extract text from PDF'})}\n\n"
            return
        
        yield f"event: progress\ndata: {json.dumps({'stage': 'extract', 'message': f'Extracted text from {page_count} pages'})}\n\n"
        
        # Stage 3: Analyze
        yield f"event: progress\ndata: {json.dumps({'stage': 'analyze', 'message': 'Analyzing with Groq LLM...'})}\n\n"
        
        result = analyze_with_groq(text)
        
        # Stage 4: Done
        final_data = {
            "doc_name": filename,
            "page_count": page_count,
            **result
        }
        yield f"event: done\ndata: {json.dumps(final_data)}\n\n"
        
    except Exception as e:
        yield f"event: error\ndata: {json.dumps({'error': str(e)})}\n\n"
```

### SSE Endpoint

```python
@app.post("/analyze_sse")
async def analyze_document_sse(file: UploadFile = File(...)):
    """Streaming analysis endpoint with SSE"""
    if not file.filename.lower().endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are accepted")
    
    file_bytes = await file.read()
    
    if len(file_bytes) > MAX_SIZE_BYTES:
        raise HTTPException(status_code=413, detail=f"File size exceeds {MAX_SIZE_MB}MB limit")
    
    if len(file_bytes) == 0:
        raise HTTPException(status_code=400, detail="Empty file")
    
    return StreamingResponse(
        sse_generator(file_bytes, file.filename),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        }
    )
```

## Frontend Implementation (Next.js/TypeScript)

### SSE Client Handler

```typescript
const handleStreamingUpload = async (file: File, apiUrl: string) => {
  const formData = new FormData();
  formData.append('file', file);

  try {
    const response = await fetch(`${apiUrl}/analyze_sse`, {
      method: 'POST',
      body: formData,
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({ detail: response.statusText }));
      throw new Error(errorData.detail || `HTTP ${response.status}`);
    }

    if (!response.body) {
      throw new Error('No response body');
    }

    const reader = response.body.getReader();
    const decoder = new TextDecoder();
    let buffer = '';

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;

      buffer += decoder.decode(value, { stream: true });
      const lines = buffer.split('\n\n');
      buffer = lines.pop() || '';

      for (const line of lines) {
        if (line.trim() === '') continue;

        const [eventLine, dataLine] = line.split('\n');
        if (!eventLine.startsWith('event:') || !dataLine.startsWith('data:')) continue;

        const event = eventLine.substring(6).trim();
        const data = JSON.parse(dataLine.substring(5).trim());

        if (event === 'progress') {
          setStreamingState({ stage: data.stage, message: data.message });
        } else if (event === 'done') {
          setReport(data);
          setStreamingState({ stage: 'done', message: 'Complete!' });
        } else if (event === 'error') {
          throw new Error(data.error);
        }
      }
    }
  } catch (err: any) {
    console.error('Streaming error:', err);
    setError(getErrorMessage(err));
  }
};
```

### Progress UI Component

```typescript
export default function StreamingProgress({ stage, message }: StreamingProgressProps) {
  const stages = ['ingest', 'extract', 'analyze', 'done'];
  const currentIndex = stages.indexOf(stage);

  return (
    <div className="w-full max-w-2xl mx-auto mt-6 p-6 bg-white dark:bg-gray-800 rounded-lg shadow-lg">
      <h3 className="text-lg font-semibold mb-4 dark:text-white">Analysis Progress</h3>
      
      <div className="space-y-4">
        {stages.slice(0, -1).map((s, idx) => {
          const isActive = idx === currentIndex;
          const isComplete = idx < currentIndex;
          
          return (
            <div key={s} className="flex items-center gap-3">
              <div
                className={`w-8 h-8 rounded-full flex items-center justify-center transition-colors ${
                  isComplete
                    ? 'bg-green-500 text-white'
                    : isActive
                    ? 'bg-blue-500 text-white animate-pulse'
                    : 'bg-gray-300 dark:bg-gray-600 text-gray-500'
                }`}
              >
                {isComplete ? '✓' : idx + 1}
              </div>
              <div className="flex-1">
                <p className={`font-medium ${isActive ? 'text-blue-600 dark:text-blue-400' : 'dark:text-gray-300'}`}>
                  {s.charAt(0).toUpperCase() + s.slice(1)}
                </p>
                {isActive && (
                  <p className="text-sm text-gray-600 dark:text-gray-400">{message}</p>
                )}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
```

## SSE Event Format

### Event Types

#### 1. Progress Event
```
event: progress
data: {"stage": "ingest|extract|analyze", "message": "Status message"}
```

**Example:**
```
event: progress
data: {"stage": "extract", "message": "Extracted text from 5 pages"}
```

#### 2. Done Event
```
event: done
data: {full report JSON with summary, overall_risk, flags, etc.}
```

**Example:**
```
event: done
data: {"doc_name": "report.pdf", "page_count": 5, "summary": "...", "overall_risk": 0.65, "flags": [...]}
```

#### 3. Error Event
```
event: error
data: {"error": "Error message"}
```

**Example:**
```
event: error
data: {"error": "Could not extract text from PDF"}
```

## Analysis Stages

| Stage | Description | Duration (avg) |
|-------|-------------|----------------|
| **ingest** | File validation and reading | < 100ms |
| **extract** | PDF text extraction with pdfplumber | 300-500ms |
| **analyze** | Groq LLM compliance analysis | 2-3s |
| **done** | Final report delivery | Instant |

## Error Handling

### Backend Errors
```python
try:
    # ... processing ...
    yield f"event: done\ndata: {json.dumps(final_data)}\n\n"
except Exception as e:
    yield f"event: error\ndata: {json.dumps({'error': str(e)})}\n\n"
```

### Frontend Error Handling
```typescript
const getErrorMessage = (err: any): string => {
  const message = err.message || String(err);
  
  if (message.includes('413') || message.includes('File size exceeds')) {
    return 'File size exceeds 10MB limit. Please upload a smaller file.';
  }
  if (message.includes('400') || message.includes('Only PDF')) {
    return 'Invalid file format. Only PDF files are accepted.';
  }
  if (message.includes('401') || message.includes('Unauthorized')) {
    return 'Authentication failed. Please check API credentials.';
  }
  if (message.includes('Could not extract')) {
    return 'Unable to extract text from PDF. The file may be corrupted or image-based.';
  }
  
  return `Analysis failed: ${message}`;
};
```

## Streaming Toggle Implementation

### Toggle Switch Component
```typescript
<label className="flex items-center gap-2 cursor-pointer">
  <span className="text-sm dark:text-gray-300">Enable Streaming</span>
  <input
    type="checkbox"
    checked={useStreaming}
    onChange={(e) => onToggleStreaming(e.target.checked)}
    className="w-4 h-4 accent-blue-600"
    disabled={isUploading}
  />
</label>
```

### Conditional Upload Handler
```typescript
const handleFileSelect = async (file: File) => {
  setIsUploading(true);
  setError(null);
  setReport(null);
  setStreamingState(null);

  const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

  if (useStreaming) {
    await handleStreamingUpload(file, apiUrl);  // SSE version
  } else {
    await handleNormalUpload(file, apiUrl);     // Standard version
  }

  setIsUploading(false);
};
```

## Testing SSE

### Manual Testing with curl
```bash
# Test SSE endpoint
curl -N -X POST http://localhost:8000/analyze_sse \
  -H "Accept: text/event-stream" \
  -F "file=@sample.pdf"

# Expected output:
# event: progress
# data: {"stage":"ingest","message":"Processing PDF file..."}
#
# event: progress
# data: {"stage":"extract","message":"Extracting text from PDF..."}
# ...
```

### Browser DevTools Testing
1. Open browser DevTools (F12)
2. Go to Network tab
3. Upload a PDF with streaming enabled
4. Click on `analyze_sse` request
5. Select "EventStream" tab
6. Watch events appear in real-time

### Unit Test Example
```python
import pytest
from httpx import AsyncClient
from app import app

@pytest.mark.asyncio
async def test_sse_endpoint():
    async with AsyncClient(app=app, base_url="http://test") as client:
        with open("test.pdf", "rb") as f:
            response = await client.post(
                "/analyze_sse",
                files={"file": ("test.pdf", f, "application/pdf")}
            )
        
        assert response.status_code == 200
        assert response.headers["content-type"] == "text/event-stream"
```

## Performance Considerations

### Backend
- ✅ **Async generators** - Non-blocking event emission
- ✅ **Early error detection** - Validate before streaming
- ✅ **Chunked encoding** - Transfer-Encoding: chunked
- ✅ **Connection reuse** - Keep-Alive headers

### Frontend
- ✅ **Stream buffering** - Handle partial chunks correctly
- ✅ **Memory management** - Clean up readers on unmount
- ✅ **Error recovery** - Graceful degradation to non-streaming

## Browser Compatibility

| Browser | SSE Support | Notes |
|---------|-------------|-------|
| Chrome 90+ | ✅ Full | EventSource API native |
| Firefox 88+ | ✅ Full | EventSource API native |
| Safari 14+ | ✅ Full | EventSource API native |
| Edge 90+ | ✅ Full | EventSource API native |
| IE 11 | ❌ None | Use polyfill or fallback |

**Fallback Strategy:** Automatic toggle to non-streaming mode if SSE fails.

## Security Considerations

### CORS Configuration
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### SSE-Specific Headers
```python
headers={
    "Cache-Control": "no-cache",      # Prevent proxy caching
    "Connection": "keep-alive",       # Maintain connection
    "X-Accel-Buffering": "no",       # Disable nginx buffering
}
```

## Production Deployment

### Nginx Configuration (if using reverse proxy)
```nginx
location /analyze_sse {
    proxy_pass http://backend:8000;
    proxy_buffering off;              # Critical for SSE
    proxy_cache off;
    proxy_set_header Connection '';
    proxy_http_version 1.1;
    chunked_transfer_encoding on;
}
```

### Vercel/Netlify
- SSE works out-of-the-box
- No special configuration needed
- Automatic chunked encoding

### AWS/CloudFront
- May require disabling response buffering
- Set cache policy to bypass for SSE endpoints

## Debugging Tips

### Backend Debugging
```python
import logging
logging.basicConfig(level=logging.DEBUG)

async def sse_generator(file_bytes: bytes, filename: str):
    logging.debug(f"Starting SSE for {filename}")
    yield f"event: progress\ndata: {json.dumps(...)}\n\n"
    logging.debug("Sent progress event")
```

### Frontend Debugging
```typescript
// Log all SSE events
if (event === 'progress') {
  console.log('SSE Progress:', data);
  setStreamingState({ stage: data.stage, message: data.message });
}
```

### Common Issues

| Issue | Cause | Solution |
|-------|-------|----------|
| Events not arriving | Proxy buffering | Add `X-Accel-Buffering: no` header |
| Partial events | Buffer overflow | Increase buffer size or flush more often |
| Connection timeout | Long analysis | Send heartbeat events every 30s |
| CORS errors | Origin mismatch | Configure CORS properly |

## Comparison: Streaming vs Non-Streaming

### User Experience
| Aspect | Streaming | Non-Streaming |
|--------|-----------|---------------|
| Progress visibility | ✅ Real-time stages | ❌ Generic loader |
| Error granularity | ✅ Stage-specific | ❌ Generic error |
| Perceived speed | ✅ Faster (shows progress) | ❌ Slower (black box) |
| Network efficiency | ⚠️ Long connection | ✅ Single request |

### Technical
| Aspect | Streaming | Non-Streaming |
|--------|-----------|---------------|
| Implementation | Complex | Simple |
| Compatibility | Most browsers | All browsers |
| Debugging | More difficult | Easier |
| Scalability | Requires stateful servers | Easier to scale |

## Best Practices

1. ✅ **Always provide fallback** - Non-streaming mode for compatibility
2. ✅ **Validate before streaming** - Check file early to avoid wasted connections
3. ✅ **Use event types** - `progress`, `done`, `error` for clarity
4. ✅ **Include stage info** - Help users understand what's happening
5. ✅ **Handle disconnects** - Clean up resources properly
6. ✅ **Limit connection time** - Timeout long-running streams
7. ✅ **Buffer management** - Handle partial chunks correctly
8. ✅ **Error messages** - Clear, actionable error descriptions

## Future Enhancements

- [ ] Heartbeat events for connection monitoring
- [ ] Resume capability for interrupted streams
- [ ] Progress percentage (0-100%)
- [ ] ETA estimation based on file size
- [ ] Multi-stage parallelization (extract + analyze simultaneously)
- [ ] Client-side caching of stream data

---

**Summary:** This SSE implementation provides real-time, transparent feedback to users during long-running LLM analysis tasks, significantly improving perceived performance and user experience while maintaining a fallback option for maximum compatibility.
