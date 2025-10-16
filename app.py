import io
import json
import math
import os
import re
import time
from datetime import datetime
from typing import Any, Dict, Generator, Iterable, List, Optional, Tuple

import fitz  # PyMuPDF
import pdfplumber
from dotenv import load_dotenv
from fastapi import FastAPI, File, HTTPException, UploadFile, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, StreamingResponse
from groq import Groq
from pydantic import BaseModel, Field, ValidationError, field_validator

# Load env
load_dotenv()

MAX_SIZE_MB = int(os.getenv("MAX_SIZE_MB", "10"))
ALLOWED_ORIGINS = [o.strip() for o in os.getenv("ALLOWED_ORIGINS", "*").split(",")]
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
SUPABASE_REPORTS_TABLE = os.getenv("SUPABASE_REPORTS_TABLE", "reports")
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")

# --- Pydantic Schemas ---

class EvidenceItem(BaseModel):
    page: int = Field(ge=1)
    quote: str = Field(min_length=1, max_length=600)

class FlagItem(BaseModel):
    title: str
    severity: int = Field(ge=1, le=5)
    why_it_matters: str
    recommendation: str
    evidence: List[EvidenceItem] = Field(default_factory=list)

class ReportOut(BaseModel):
    summary: str
    overall_risk: float = Field(ge=0.0)
    flags: List[FlagItem]

    @field_validator("flags")
    @classmethod
    def ensure_quotes_len(cls, v: List[FlagItem]) -> List[FlagItem]:
        for flag in v:
            for ev in flag.evidence:
                if len(ev.quote) > 600:
                    ev.quote = ev.quote[:600]
        return v

# --- Utilities ---

def chunk_text(text: str, max_chars: int = 7000, overlap: int = 400) -> List[str]:
    text = text.strip()
    if not text:
        return []
    chunks: List[str] = []
    start = 0
    n = len(text)
    while start < n:
        end = min(start + max_chars, n)
        chunks.append(text[start:end])
        if end == n:
            break
        start = max(0, end - overlap)
    return chunks


def extract_text_with_pymupdf(pdf_bytes: bytes) -> Tuple[str, int]:
    with fitz.open(stream=pdf_bytes, filetype="pdf") as d:
        pages = d.page_count
        parts: List[str] = []
        for i in range(pages):
            page = d.load_page(i)
            parts.append(page.get_text("text"))
        return "\n\n".join(parts), pages


def extract_text_with_pdfplumber(pdf_bytes: bytes) -> Tuple[str, int]:
    with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
        parts: List[str] = []
        for p in pdf.pages:
            parts.append(p.extract_text() or "")
        return "\n\n".join(parts), len(pdf.pages)


def extract_pdf_text(pdf_bytes: bytes) -> Tuple[str, int]:
    # Try PyMuPDF first (usually more robust). Fallback to pdfplumber.
    try:
        return extract_text_with_pymupdf(pdf_bytes)
    except Exception:
        pass
    try:
        return extract_text_with_pdfplumber(pdf_bytes)
    except Exception:
        pass
    return "", 0


def build_prompt(chunk: str) -> List[Dict[str, str]]:
    system = (
        "You are an expert compliance analyst for financial and legal documents.\n"
        "Return ONLY valid JSON following this schema strictly, with no extra text: \n"
        "{\n  \"summary\": string,\n  \"overall_risk\": number,\n  \"flags\": [\n    {\n      \"title\": string,\n      \"severity\": integer 1-5,\n      \"why_it_matters\": string,\n      \"recommendation\": string,\n      \"evidence\": [ { \"page\": integer>=1, \"quote\": string<=600 } ]\n    }\n  ]\n}\n"
        "Guidelines: Identify red flags (Cross-Border, AML, Sanctions, PDPA/GDPR, etc.)."
        " Keep quotes <= 600 characters. If risk is missing, estimate as mean(severity)/5*100."
    )
    user = (
        "Analyze the following document excerpt for compliance risks and produce the JSON report.\n\n"
        f"Document excerpt:\n{chunk}"
    )
    return [
        {"role": "system", "content": system},
        {"role": "user", "content": user},
    ]


def groq_client() -> Groq:
    if not GROQ_API_KEY:
        raise RuntimeError("Missing GROQ_API_KEY")
    return Groq(api_key=GROQ_API_KEY)


def call_groq_json(chunk: str, retry: int = 2) -> Dict[str, Any]:
    client = groq_client()
    last_error: Optional[Exception] = None
    for attempt in range(retry + 1):
        try:
            messages = build_prompt(chunk)
            resp = client.chat.completions.create(
                model="llama3-70b-8192",
                temperature=0.2,
                max_tokens=2048,
                messages=messages,
            )
            content = resp.choices[0].message.content or ""
            data = force_parse_json(content)
            validated = validate_and_postprocess(data)
            return validated
        except Exception as e:
            last_error = e
            # Retry once with a stricter reminder
            chunk_short = chunk[:5000]
            try:
                resp = client.chat.completions.create(
                    model="llama3-70b-8192",
                    temperature=0.0,
                    max_tokens=2048,
                    messages=[
                        {"role": "system", "content": "Return only strict JSON per schema; no markdown, no prose."},
                        {"role": "user", "content": f"Strict JSON report for:\n{chunk_short}"},
                    ],
                )
                content = resp.choices[0].message.content or ""
                data = force_parse_json(content)
                validated = validate_and_postprocess(data)
                return validated
            except Exception as e2:
                last_error = e2
                continue
    raise RuntimeError(f"Groq parsing failed: {last_error}")


def force_parse_json(s: str) -> Dict[str, Any]:
    # Remove code fences and try to extract the largest JSON object
    s = s.strip()
    s = re.sub(r"^```[a-zA-Z]*", "", s)
    s = re.sub(r"```$", "", s)
    # Find JSON object boundaries
    match = re.search(r"\{[\s\S]*\}", s)
    candidate = match.group(0) if match else s
    try:
        return json.loads(candidate)
    except json.JSONDecodeError:
        # Try to repair common issues: trailing commas
        candidate2 = re.sub(r",\s*([}\]])", r"\1", candidate)
        return json.loads(candidate2)


def validate_and_postprocess(obj: Dict[str, Any]) -> Dict[str, Any]:
    # Ensure schema and clamp quotes
    if "flags" not in obj:
        obj["flags"] = []
    # Default overall risk if missing
    if obj.get("overall_risk") in (None, ""):
        obj["overall_risk"] = 0.0
    # Validate with Pydantic (will clip quotes via validator)
    try:
        report = ReportOut(**obj)
    except ValidationError as ve:
        # Attempt to coerce minimal shape
        flags = obj.get("flags") or []
        safe_flags: List[Dict[str, Any]] = []
        for f in flags:
            sev = int(float(f.get("severity", 3)))
            sev = max(1, min(5, sev))
            evidence = []
            for ev in f.get("evidence", []) or []:
                page = int(ev.get("page", 1))
                quote = str(ev.get("quote", ""))[:600]
                evidence.append({"page": max(1, page), "quote": quote})
            safe_flags.append({
                "title": str(f.get("title", "Risk")),
                "severity": sev,
                "why_it_matters": str(f.get("why_it_matters", "")),
                "recommendation": str(f.get("recommendation", "")),
                "evidence": evidence,
            })
        summary = str(obj.get("summary", ""))
        overall_risk = float(obj.get("overall_risk") or 0.0)
        report = ReportOut(summary=summary, overall_risk=overall_risk, flags=safe_flags)
    # Compute default overall risk if zero or missing based on mean severity
    if not report.overall_risk or report.overall_risk <= 0:
        if report.flags:
            mean_sev = sum(f.severity for f in report.flags) / len(report.flags)
            report.overall_risk = round((mean_sev / 5.0) * 100.0, 2)
        else:
            report.overall_risk = 0.0
    # Clamp quotes once more
    for f in report.flags:
        for ev in f.evidence:
            if len(ev.quote) > 600:
                ev.quote = ev.quote[:600]
    return json.loads(report.model_dump_json())


# --- Supabase (optional) ---
try:
    from supabase import create_client, Client  # type: ignore
except Exception:
    create_client = None  # type: ignore
    Client = Any  # type: ignore

_supabase: Optional[Client] = None

def get_supabase() -> Optional[Client]:
    global _supabase
    if _supabase is not None:
        return _supabase
    if not SUPABASE_URL or not SUPABASE_KEY or create_client is None:
        return None
    try:
        _supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
        return _supabase
    except Exception:
        return None


def save_report(user_id: str, doc_name: str, report: Dict[str, Any]) -> None:
    client = get_supabase()
    if client is None:
        return
    try:
        payload = {
            "user_id": user_id,
            "doc_name": doc_name,
            "summary": report.get("summary", ""),
            "overall_risk": float(report.get("overall_risk", 0.0)),
            "flags": report.get("flags", []),
            "ts": int(time.time() * 1000),
        }
        client.table(SUPABASE_REPORTS_TABLE).insert(payload).execute()
    except Exception:
        # best-effort; ignore storage failures
        pass


def list_reports(user_id: str, limit: int = 20) -> List[Dict[str, Any]]:
    client = get_supabase()
    if client is None:
        return []
    try:
        res = (
            client.table(SUPABASE_REPORTS_TABLE)
            .select("id,user_id,doc_name,summary,overall_risk,flags,ts")
            .eq("user_id", user_id)
            .order("ts", desc=True)
            .limit(limit)
            .execute()
        )
        if hasattr(res, "data"):
            return list(res.data or [])
        return []
    except Exception:
        return []


# --- Core analysis API ---

def analyze_chunks(chunks: List[str]) -> Dict[str, Any]:
    if not chunks:
        raise ValueError("No content to analyze")
    # Strategy: If single chunk, analyze directly. If many, analyze first 2-3 chunks and merge.
    results: List[Dict[str, Any]] = []
    budget = min(3, len(chunks))
    for i in range(budget):
        result = call_groq_json(chunks[i])
        results.append(result)
    # Merge results: concat flags, combine summaries, compute overall risk as mean
    merged_flags: List[Dict[str, Any]] = []
    summaries: List[str] = []
    risks: List[float] = []
    for r in results:
        summaries.append(str(r.get("summary", "")))
        risks.append(float(r.get("overall_risk", 0.0)))
        for f in r.get("flags", []) or []:
            # Ensure quotes clipped
            for ev in f.get("evidence", []) or []:
                if isinstance(ev.get("quote"), str) and len(ev["quote"]) > 600:
                    ev["quote"] = ev["quote"][:600]
            merged_flags.append(f)
    if not risks:
        risks = [0.0]
    overall = round(sum(risks) / len(risks), 2)
    combined_summary = ("\n\n").join(s for s in summaries if s).strip() or "No significant risks identified."
    final = {"summary": combined_summary, "overall_risk": overall, "flags": merged_flags}
    final = validate_and_postprocess(final)
    return final


app = FastAPI(title="Compliance Copilot (Groq Edition)")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS if ALLOWED_ORIGINS != ["*"] else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def _read_all(file: UploadFile) -> bytes:
    data = file.file.read()
    if hasattr(file.file, "seek"):
        try:
            file.file.seek(0)
        except Exception:
            pass
    return data


@app.post("/analyze")
async def analyze(file: UploadFile = File(...), user_id: str = Query(default="anonymous")):
    if file.content_type not in ("application/pdf", "application/octet-stream"):
        raise HTTPException(status_code=400, detail="Only PDF files are accepted")
    data = _read_all(file)
    size_mb = len(data) / (1024 * 1024)
    if size_mb > MAX_SIZE_MB:
        raise HTTPException(status_code=413, detail=f"File too large. Max {MAX_SIZE_MB} MB")
    text, pages = extract_pdf_text(data)
    if not text.strip():
        raise HTTPException(status_code=400, detail="Could not extract text from PDF")
    chunks = chunk_text(text)
    try:
        report = analyze_chunks(chunks)
    except RuntimeError as re_err:
        raise HTTPException(status_code=500, detail=str(re_err))
    # Save best-effort
    save_report(user_id=user_id or "anonymous", doc_name=file.filename or "document.pdf", report=report)
    return JSONResponse(content=report)


def sse_event(event: str, data: Any) -> bytes:
    payload = json.dumps(data, ensure_ascii=False)
    return f"event: {event}\ndata: {payload}\n\n".encode("utf-8")


@app.post("/analyze_sse")
async def analyze_sse(file: UploadFile = File(...), user_id: str = Query(default="anonymous")):
    if file.content_type not in ("application/pdf", "application/octet-stream"):
        raise HTTPException(status_code=400, detail="Only PDF files are accepted")

    def gen() -> Generator[bytes, None, None]:
        try:
            data = _read_all(file)
            size_mb = len(data) / (1024 * 1024)
            if size_mb > MAX_SIZE_MB:
                yield sse_event("error", {"message": f"File too large. Max {MAX_SIZE_MB} MB"})
                return
            yield sse_event("ingest", {"filename": file.filename, "size_mb": round(size_mb, 3)})

            text, pages = extract_pdf_text(data)
            if not text.strip():
                yield sse_event("error", {"message": "Could not extract text from PDF"})
                return
            chunks = chunk_text(text)
            yield sse_event("extract", {"pages": pages, "chars": len(text), "chunks": len(chunks)})

            yield sse_event("analyze", {"status": "started"})
            try:
                report = analyze_chunks(chunks)
            except Exception as e:
                yield sse_event("error", {"message": f"Analysis failed: {str(e)}"})
                return
            # Persist
            try:
                save_report(user_id=user_id or "anonymous", doc_name=file.filename or "document.pdf", report=report)
            except Exception:
                pass
            yield sse_event("done", report)
        except HTTPException as he:
            yield sse_event("error", {"message": he.detail})
        except Exception as e:
            yield sse_event("error", {"message": f"Unexpected error: {str(e)}"})

    headers = {
        "Content-Type": "text/event-stream",
        "Cache-Control": "no-cache",
        "Connection": "keep-alive",
        "X-Accel-Buffering": "no",  # for nginx
    }
    return StreamingResponse(gen(), headers=headers, media_type="text/event-stream")


@app.get("/reports")
async def get_reports(user_id: str = Query(default="anonymous"), limit: int = Query(default=20, ge=1, le=100)):
    items = list_reports(user_id=user_id, limit=limit)
    return JSONResponse(content={"reports": items})
