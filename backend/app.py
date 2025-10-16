import os
import json
import time
from typing import AsyncGenerator, Optional
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from groq import Groq
import pdfplumber
from io import BytesIO
from supabase import create_client, Client
from pydantic import BaseModel

app = FastAPI(title="AI Compliance Copilot")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuration
MAX_SIZE_MB = 10
MAX_SIZE_BYTES = MAX_SIZE_MB * 1024 * 1024
MAX_EVIDENCE_LENGTH = 600

# Initialize clients
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not GROQ_API_KEY:
    raise ValueError("GROQ_API_KEY environment variable not set")

groq_client = Groq(api_key=GROQ_API_KEY)

supabase: Optional[Client] = None
if SUPABASE_URL and SUPABASE_KEY:
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)


class Evidence(BaseModel):
    page: int
    quote: str


class Flag(BaseModel):
    title: str
    severity: int
    why_it_matters: str
    recommendation: str
    evidence: list[Evidence]


class AnalysisReport(BaseModel):
    summary: str
    overall_risk: float
    flags: list[Flag]


def extract_text_from_pdf(file_bytes: bytes) -> tuple[str, int]:
    """Extract text from PDF using pdfplumber"""
    text_parts = []
    page_count = 0
    
    with pdfplumber.open(BytesIO(file_bytes)) as pdf:
        page_count = len(pdf.pages)
        for page_num, page in enumerate(pdf.pages, 1):
            page_text = page.extract_text() or ""
            if page_text.strip():
                text_parts.append(f"[Page {page_num}]\n{page_text}")
    
    full_text = "\n\n".join(text_parts)
    return full_text, page_count


def truncate_evidence(evidence_list: list[dict]) -> list[dict]:
    """Truncate evidence quotes to MAX_EVIDENCE_LENGTH"""
    for evidence in evidence_list:
        if len(evidence.get("quote", "")) > MAX_EVIDENCE_LENGTH:
            evidence["quote"] = evidence["quote"][:MAX_EVIDENCE_LENGTH] + "..."
    return evidence_list


def analyze_with_groq(text: str) -> dict:
    """Analyze document with Groq LLM"""
    prompt = f"""You are a compliance expert. Analyze this financial/legal document for compliance risks.

Document:
{text[:8000]}

Return a JSON response with:
{{
  "summary": "executive summary (2-3 sentences)",
  "overall_risk": 0.0-1.0,
  "flags": [
    {{
      "title": "Risk category (e.g., Cross-Border, AML, Sanctions, PDPA/GDPR)",
      "severity": 1-5,
      "why_it_matters": "explanation",
      "recommendation": "action to take",
      "evidence": [
        {{"page": page_number, "quote": "relevant quote (max 600 chars)"}}
      ]
    }}
  ]
}}

Focus on: Cross-Border transactions, AML (Anti-Money Laundering), Sanctions, PDPA/GDPR compliance.
Return ONLY valid JSON, no markdown or extra text."""

    try:
        response = groq_client.chat.completions.create(
            model="llama3-70b-8192",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=4000,
        )
        
        content = response.choices[0].message.content.strip()
        
        # Remove markdown code blocks if present
        if content.startswith("```"):
            content = content.split("```")[1]
            if content.startswith("json"):
                content = content[4:]
            content = content.strip()
        
        result = json.loads(content)
        
        # Validate and clean
        for flag in result.get("flags", []):
            flag["evidence"] = truncate_evidence(flag.get("evidence", []))
        
        # Calculate overall_risk if missing
        if "overall_risk" not in result or result["overall_risk"] is None:
            severities = [flag.get("severity", 3) for flag in result.get("flags", [])]
            result["overall_risk"] = (sum(severities) / len(severities) / 5) if severities else 0.5
        
        return result
        
    except json.JSONDecodeError as e:
        # Retry once with stricter prompt
        response = groq_client.chat.completions.create(
            model="llama3-70b-8192",
            messages=[
                {"role": "user", "content": prompt},
                {"role": "assistant", "content": content},
                {"role": "user", "content": "Please return ONLY valid JSON without any markdown formatting."}
            ],
            temperature=0.1,
            max_tokens=4000,
        )
        content = response.choices[0].message.content.strip()
        result = json.loads(content)
        
        # Same validation
        for flag in result.get("flags", []):
            flag["evidence"] = truncate_evidence(flag.get("evidence", []))
        
        if "overall_risk" not in result:
            severities = [flag.get("severity", 3) for flag in result.get("flags", [])]
            result["overall_risk"] = (sum(severities) / len(severities) / 5) if severities else 0.5
        
        return result


@app.post("/analyze")
async def analyze_document(file: UploadFile = File(...)):
    """Non-streaming analysis endpoint"""
    if not file.filename.lower().endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are accepted")
    
    # Read file
    file_bytes = await file.read()
    
    if len(file_bytes) > MAX_SIZE_BYTES:
        raise HTTPException(status_code=413, detail=f"File size exceeds {MAX_SIZE_MB}MB limit")
    
    if len(file_bytes) == 0:
        raise HTTPException(status_code=400, detail="Empty file")
    
    try:
        # Extract text
        text, page_count = extract_text_from_pdf(file_bytes)
        
        if not text.strip():
            raise HTTPException(status_code=400, detail="Could not extract text from PDF")
        
        # Analyze
        result = analyze_with_groq(text)
        
        # Save to Supabase
        if supabase:
            try:
                supabase.table("reports").insert({
                    "user_id": "demo_user",
                    "doc_name": file.filename,
                    "summary": result.get("summary", ""),
                    "overall_risk": result.get("overall_risk", 0.5),
                    "flags": json.dumps(result.get("flags", [])),
                    "ts": int(time.time() * 1000)
                }).execute()
            except Exception as e:
                print(f"Supabase error: {e}")
        
        return {
            "doc_name": file.filename,
            "page_count": page_count,
            **result
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


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
        
        # Save to Supabase
        if supabase:
            try:
                supabase.table("reports").insert({
                    "user_id": "demo_user",
                    "doc_name": filename,
                    "summary": result.get("summary", ""),
                    "overall_risk": result.get("overall_risk", 0.5),
                    "flags": json.dumps(result.get("flags", [])),
                    "ts": int(time.time() * 1000)
                }).execute()
            except Exception as e:
                print(f"Supabase error: {e}")
        
        # Stage 4: Done
        final_data = {
            "doc_name": filename,
            "page_count": page_count,
            **result
        }
        yield f"event: done\ndata: {json.dumps(final_data)}\n\n"
        
    except Exception as e:
        yield f"event: error\ndata: {json.dumps({'error': str(e)})}\n\n"


@app.post("/analyze_sse")
async def analyze_document_sse(file: UploadFile = File(...)):
    """Streaming analysis endpoint with SSE"""
    if not file.filename.lower().endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are accepted")
    
    # Read file
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


@app.get("/reports")
async def get_reports(limit: int = 10):
    """Get recent reports from Supabase"""
    if not supabase:
        return {"reports": []}
    
    try:
        response = supabase.table("reports")\
            .select("*")\
            .order("ts", desc=True)\
            .limit(limit)\
            .execute()
        
        return {"reports": response.data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch reports: {str(e)}")


@app.get("/health")
async def health_check():
    return {"status": "ok", "groq": bool(GROQ_API_KEY), "supabase": bool(supabase)}
