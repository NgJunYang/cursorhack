# 🚀 Quick Start Guide

Get the AI Compliance Copilot running in 5 minutes!

## Prerequisites

- Python 3.10+
- Node.js 18+
- Groq API Key → [Get here](https://console.groq.com)
- Supabase Account → [Sign up](https://supabase.com)

## Step 1: Get Your API Keys

### Groq API Key
1. Go to https://console.groq.com
2. Sign up or log in
3. Navigate to API Keys
4. Create new API key
5. Copy the key

### Supabase Setup
1. Go to https://supabase.com
2. Create a new project
3. Go to Project Settings → API
4. Copy your **Project URL** and **anon public** key
5. Go to SQL Editor and run the contents of `supabase_setup.sql`

## Step 2: Configure Backend

```bash
cd backend
cp .env.example .env
```

Edit `backend/.env`:
```bash
GROQ_API_KEY=gsk_your_actual_groq_api_key_here
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your_supabase_anon_key_here
```

## Step 3: Configure Frontend

```bash
cd ../web
cp .env.local.example .env.local
```

Edit `web/.env.local`:
```bash
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## Step 4: Run the Application

### Option A: Using Run Scripts (Recommended)

**Terminal 1 - Backend:**
```bash
./run_backend.sh
```

**Terminal 2 - Frontend:**
```bash
./run_frontend.sh
```

### Option B: Manual Setup

**Terminal 1 - Backend:**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app:app --reload --port 8000
```

**Terminal 2 - Frontend:**
```bash
cd web
npm install
npm run dev
```

## Step 5: Test It Out!

1. Open http://localhost:3000
2. Enable the "Streaming" toggle (recommended for live progress)
3. Upload a sample PDF (financial or legal document)
4. Watch the magic happen! 🎉

## Testing with Sample Data

### Create a Test PDF
You can create a simple test document with compliance keywords:

**test_document.txt content:**
```
FINANCIAL TRANSACTION REPORT

Date: October 16, 2025
Transaction ID: TXN-2025-001

This document outlines a cross-border wire transfer of $250,000 USD from
ABC Corp (USA) to XYZ Ltd (Offshore Entity). The transaction involves
multiple jurisdictions and requires AML compliance review.

The recipient entity is located in a high-risk jurisdiction according to
FATF guidelines. Additional due diligence is required under current sanctions
regulations.

Customer information has been collected according to GDPR requirements,
however there are concerns about the adequacy of beneficial ownership
disclosure.

RECOMMENDATION: Enhanced monitoring required for this transaction.
```

Convert to PDF using any tool (Google Docs, LibreOffice, etc.)

## Verify SSE Streaming

1. Open browser DevTools (F12)
2. Go to Network tab
3. Upload a PDF with streaming enabled
4. Look for `analyze_sse` request
5. You should see real-time event streams:
   - `event: progress` → `{"stage": "ingest", ...}`
   - `event: progress` → `{"stage": "extract", ...}`
   - `event: progress` → `{"stage": "analyze", ...}`
   - `event: done` → `{full report JSON}`

## Troubleshooting

### Backend won't start
- Check Python version: `python --version` (need 3.10+)
- Verify .env file exists and has valid keys
- Try: `pip install --upgrade pip`

### Frontend won't start
- Check Node version: `node --version` (need 18+)
- Delete `node_modules` and `package-lock.json`, then `npm install`
- Verify .env.local has correct API URL

### 401 Unauthorized Error
- Double-check your Groq API key
- Ensure no extra spaces in .env file
- Try regenerating the API key

### Supabase Connection Failed
- Verify Supabase URL and key are correct
- Run `supabase_setup.sql` in SQL Editor
- Check if project is active

### PDF Upload Fails
- File must be .pdf format
- Max size: 10MB
- PDF must contain extractable text (not just images)

## Running Tests

```bash
cd backend
source venv/bin/activate
pytest test_app.py -v
```

Expected output:
```
test_app.py::test_truncate_evidence PASSED
test_app.py::test_analyze_chunks_schema PASSED
test_app.py::test_overall_risk_calculation PASSED
```

## Production Deployment

### Backend (Python)
- Deploy to: Railway, Render, Fly.io, or AWS
- Set environment variables in platform
- Use `uvicorn app:app --host 0.0.0.0 --port $PORT`

### Frontend (Next.js)
- Deploy to: Vercel, Netlify, or Cloudflare Pages
- Update `NEXT_PUBLIC_API_URL` to production backend URL
- Build command: `npm run build`

## Performance Tips

1. **Groq Rate Limits**: Monitor your Groq usage at console.groq.com
2. **Supabase Limits**: Free tier = 500MB database, 2GB bandwidth/month
3. **PDF Size**: Keep under 5MB for best performance (<2s analysis)
4. **Concurrent Users**: FastAPI handles 100+ concurrent connections

## Next Steps

- [ ] Customize compliance categories in backend prompt
- [ ] Add user authentication (Supabase Auth)
- [ ] Implement rate limiting
- [ ] Add support for DOCX, TXT formats
- [ ] Deploy to production

## Support

For issues:
1. Check the main README.md
2. Review error messages in browser console
3. Check backend logs in terminal

Happy Hacking! 🎉
