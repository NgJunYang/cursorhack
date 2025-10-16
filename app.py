import os
import json
import asyncio
import time
from typing import List, Dict, Any, Optional
from fastapi import FastAPI, File, UploadFile, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, JSONResponse
from pydantic import BaseModel, Field
import pdfplumber
import fitz  # PyMuPDF
from groq import Groq
from supabase import create_client, Client
from dotenv import load_dotenv
import logging

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(title="AI Compliance Copilot", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuration
MAX_FILE_SIZE = int(os.getenv("MAX_FILE_SIZE_MB", 10)) * 1024 * 1024  # 10MB
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# Initialize clients
if not GROQ_API_KEY:
    raise ValueError("GROQ_API_KEY environment variable is required")
if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("SUPABASE_URL and SUPABASE_KEY environment variables are required")

groq_client = Groq(api_key=GROQ_API_KEY)
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Pydantic models
class Evidence(BaseModel):
    page: int
    quote: str = Field(..., max_length=600)

class ComplianceFlag(BaseModel):
    title: str
    severity: int = Field(..., ge=1, le=5)
    why_it_matters: str
    recommendation: str
    evidence: List[Evidence]

class AnalysisResult(BaseModel):
    summary: str
    overall_risk: float = Field(..., ge=0, le=100)
    flags: List[ComplianceFlag]

class Report(BaseModel):
    id: Optional[int] = None
    user_id: str
    doc_name: str
    summary: str
    overall_risk: float
    flags: List[ComplianceFlag]
    ts: int

# Utility functions
def extract_text_from_pdf(file_content: bytes) -> str:
    """Extract text from PDF using both pdfplumber and PyMuPDF as fallback."""
    try:
        # Try pdfplumber first
        import io
        with pdfplumber.open(io.BytesIO(file_content)) as pdf:
            text = ""
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
            if text.strip():
                return text.strip()
    except Exception as e:
        logger.warning(f"pdfplumber failed: {e}")
    
    try:
        # Fallback to PyMuPDF
        doc = fitz.open(stream=file_content, filetype="pdf")
        text = ""
        for page_num in range(doc.page_count):
            page = doc[page_num]
            text += page.get_text() + "\n"
        doc.close()
        return text.strip()
    except Exception as e:
        logger.error(f"PyMuPDF also failed: {e}")
        raise HTTPException(status_code=400, detail="Unable to extract text from PDF")

def analyze_chunks(text: str, filename: str) -> AnalysisResult:
    """Analyze text using Groq LLM and return structured compliance report."""
    
    # Truncate text if too long (keep first 50k chars for now)
    if len(text) > 50000:
        text = text[:50000] + "\n\n[Text truncated for analysis...]"
    
    prompt = f"""
Analyze the following financial/legal document for compliance issues. Return a JSON response with this exact structure:

{{
  "summary": "Executive summary of the document and key compliance findings",
  "overall_risk": 75.5,
  "flags": [
    {{
      "title": "Cross-Border Transaction Risk",
      "severity": 4,
      "why_it_matters": "This transaction involves multiple jurisdictions with different regulatory requirements",
      "recommendation": "Conduct thorough due diligence on all parties and ensure compliance with all applicable regulations",
      "evidence": [
        {{
          "page": 1,
          "quote": "Transaction involves entities in US, EU, and Singapore..."
        }}
      ]
    }}
  ]
}}

Focus on these compliance areas:
- Anti-Money Laundering (AML)
- Cross-border transactions
- Sanctions compliance
- Data protection (PDPA/GDPR)
- Financial regulations
- Risk management

Document: {filename}
Content:
{text}

Return only valid JSON, no additional text.
"""

    try:
        response = groq_client.chat.completions.create(
            model="llama3-70b-8192",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1,
            max_tokens=4000
        )
        
        content = response.choices[0].message.content.strip()
        
        # Try to parse JSON
        try:
            data = json.loads(content)
        except json.JSONDecodeError:
            # Try to extract JSON from response
            import re
            json_match = re.search(r'\{.*\}', content, re.DOTALL)
            if json_match:
                data = json.loads(json_match.group())
            else:
                raise ValueError("No valid JSON found in response")
        
        # Validate and structure the response
        flags = []
        for flag_data in data.get("flags", []):
            evidence = []
            for ev in flag_data.get("evidence", []):
                evidence.append(Evidence(
                    page=ev.get("page", 1),
                    quote=ev.get("quote", "")[:600]  # Ensure max 600 chars
                ))
            
            flags.append(ComplianceFlag(
                title=flag_data.get("title", "Unknown Issue"),
                severity=max(1, min(5, flag_data.get("severity", 3))),
                why_it_matters=flag_data.get("why_it_matters", ""),
                recommendation=flag_data.get("recommendation", ""),
                evidence=evidence
            ))
        
        # Calculate overall risk if not provided
        overall_risk = data.get("overall_risk")
        if overall_risk is None and flags:
            avg_severity = sum(flag.severity for flag in flags) / len(flags)
            overall_risk = (avg_severity / 5) * 100
        
        return AnalysisResult(
            summary=data.get("summary", "Analysis completed"),
            overall_risk=min(100, max(0, overall_risk or 0)),
            flags=flags
        )
        
    except Exception as e:
        logger.error(f"Groq analysis failed: {e}")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

# API Endpoints
@app.get("/")
async def root():
    return {"message": "AI Compliance Copilot API", "version": "1.0.0"}

@app.post("/analyze")
async def analyze_document(file: UploadFile = File(...)):
    """Analyze a PDF document for compliance issues."""
    
    # Validate file
    if not file.filename.lower().endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")
    
    # Check file size
    file_content = await file.read()
    if len(file_content) > MAX_FILE_SIZE:
        raise HTTPException(status_code=413, detail=f"File too large. Maximum size: {MAX_FILE_SIZE // (1024*1024)}MB")
    
    if len(file_content) == 0:
        raise HTTPException(status_code=400, detail="Empty file")
    
    try:
        # Extract text
        text = extract_text_from_pdf(file_content)
        if not text.strip():
            raise HTTPException(status_code=400, detail="No text found in PDF")
        
        # Analyze
        result = analyze_chunks(text, file.filename)
        
        # Save to database
        report = Report(
            user_id="demo_user",  # In production, get from auth
            doc_name=file.filename,
            summary=result.summary,
            overall_risk=result.overall_risk,
            flags=result.flags,
            ts=int(time.time())
        )
        
        # Convert to dict for Supabase
        report_dict = report.dict()
        report_dict["flags"] = [flag.dict() for flag in result.flags]
        
        supabase.table("reports").insert(report_dict).execute()
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Analysis error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.post("/analyze_sse")
async def analyze_document_sse(file: UploadFile = File(...)):
    """Analyze a PDF document with Server-Sent Events for live progress."""
    
    # Validate file
    if not file.filename.lower().endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")
    
    # Check file size
    file_content = await file.read()
    if len(file_content) > MAX_FILE_SIZE:
        raise HTTPException(status_code=413, detail=f"File too large. Maximum size: {MAX_FILE_SIZE // (1024*1024)}MB")
    
    if len(file_content) == 0:
        raise HTTPException(status_code=400, detail="Empty file")
    
    async def generate_events():
        try:
            # Stage 1: Ingest
            yield f"data: {json.dumps({'stage': 'ingest', 'message': 'Processing uploaded file...'})}\n\n"
            await asyncio.sleep(0.5)
            
            # Stage 2: Extract
            yield f"data: {json.dumps({'stage': 'extract', 'message': 'Extracting text from PDF...'})}\n\n"
            text = extract_text_from_pdf(file_content)
            if not text.strip():
                yield f"data: {json.dumps({'stage': 'error', 'message': 'No text found in PDF'})}\n\n"
                return
            
            await asyncio.sleep(0.5)
            
            # Stage 3: Analyze
            yield f"data: {json.dumps({'stage': 'analyze', 'message': 'Analyzing compliance issues with Groq AI...'})}\n\n"
            result = analyze_chunks(text, file.filename)
            
            # Stage 4: Done
            yield f"data: {json.dumps({'stage': 'done', 'message': 'Analysis complete', 'result': result.dict()})}\n\n"
            
            # Save to database
            report = Report(
                user_id="demo_user",
                doc_name=file.filename,
                summary=result.summary,
                overall_risk=result.overall_risk,
                flags=result.flags,
                ts=int(time.time())
            )
            
            report_dict = report.dict()
            report_dict["flags"] = [flag.dict() for flag in result.flags]
            
            supabase.table("reports").insert(report_dict).execute()
            
        except Exception as e:
            logger.error(f"SSE analysis error: {e}")
            yield f"data: {json.dumps({'stage': 'error', 'message': str(e)})}\n\n"
    
    return StreamingResponse(
        generate_events(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        }
    )

@app.get("/reports")
async def get_reports(user_id: str = "demo_user"):
    """Get all reports for a user."""
    try:
        response = supabase.table("reports").select("*").eq("user_id", user_id).order("ts", desc=True).execute()
        return {"reports": response.data}
    except Exception as e:
        logger.error(f"Error fetching reports: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch reports")

@app.get("/reports/{report_id}")
async def get_report(report_id: int):
    """Get a specific report by ID."""
    try:
        response = supabase.table("reports").select("*").eq("id", report_id).execute()
        if not response.data:
            raise HTTPException(status_code=404, detail="Report not found")
        return response.data[0]
    except Exception as e:
        logger.error(f"Error fetching report: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch report")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)