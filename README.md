# AI Compliance Copilot

A production-ready AI-powered compliance analysis tool that uses Groq's ultra-fast Llama 3 API to analyze financial and legal PDFs for compliance issues.

## 🚀 Features

- **Ultra-Fast Analysis**: Powered by Groq's lightning-fast Llama 3-70B model
- **Live Streaming**: Real-time progress updates with Server-Sent Events (SSE)
- **Comprehensive Detection**: Identifies AML, sanctions, GDPR, cross-border risks, and more
- **Structured Reports**: Detailed findings with severity scores, evidence, and recommendations
- **Markdown Export**: Download analysis reports in Markdown format
- **Report History**: Store and access all compliance reports via Supabase
- **Modern UI**: Responsive design with dark/light mode toggle
- **Error Handling**: Robust validation and graceful error recovery

## 🛠 Tech Stack

- **Backend**: FastAPI (Python 3.10+)
- **LLM Engine**: Groq (llama3-70b-8192)
- **Database**: Supabase (PostgreSQL)
- **Frontend**: Next.js 14 + Tailwind CSS
- **PDF Processing**: pdfplumber + PyMuPDF
- **Export**: Markdown generation

## 📋 Prerequisites

- Python 3.10+
- Node.js 18+
- Groq API key
- Supabase account

## 🚀 Quick Start

### 1. Clone and Setup

```bash
git clone <repository-url>
cd ai-compliance-copilot
```

### 2. Backend Setup

```bash
# Install Python dependencies
pip install -r requirements.txt

# Copy environment variables
cp .env.example .env

# Edit .env with your credentials
# GROQ_API_KEY=your_groq_api_key_here
# SUPABASE_URL=your_supabase_url_here
# SUPABASE_KEY=your_supabase_anon_key_here
```

### 3. Database Setup

Run the SQL schema in your Supabase SQL editor:

```sql
-- See supabase_schema.sql for the complete schema
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

### 4. Frontend Setup

```bash
cd web
npm install
```

### 5. Run the Application

**Backend (Terminal 1):**
```bash
uvicorn app:app --reload --port 8000
```

**Frontend (Terminal 2):**
```bash
cd web
npm run dev
```

Visit `http://localhost:3000` to access the application.

## 📖 API Endpoints

### POST /analyze
Analyze a PDF document for compliance issues.

**Request:**
- `file`: PDF file (multipart/form-data)
- Max size: 10MB

**Response:**
```json
{
  "summary": "Executive summary...",
  "overall_risk": 75.5,
  "flags": [
    {
      "title": "Cross-Border Transaction Risk",
      "severity": 4,
      "why_it_matters": "This transaction involves multiple jurisdictions...",
      "recommendation": "Conduct thorough due diligence...",
      "evidence": [
        {
          "page": 1,
          "quote": "Transaction involves entities in US, EU, and Singapore..."
        }
      ]
    }
  ]
}
```

### POST /analyze_sse
Analyze a PDF with live streaming progress updates.

**Response:** Server-Sent Events stream with stages:
- `ingest`: File processing
- `extract`: Text extraction
- `analyze`: AI analysis
- `done`: Complete with full result
- `error`: Error occurred

### GET /reports
Get all reports for a user.

**Query Parameters:**
- `user_id`: User identifier (default: "demo_user")

### GET /reports/{report_id}
Get a specific report by ID.

## 🧪 Testing

Run the test suite:

```bash
pytest test_app.py -v
```

The tests verify:
- Valid JSON schema generation
- Error handling for invalid responses
- Data validation and bounds checking
- Quote truncation (≤600 chars)
- Severity and risk score validation

## 📊 Compliance Detection

The AI analyzes documents for:

- **Anti-Money Laundering (AML)**
- **Cross-border transactions**
- **Sanctions compliance**
- **Data protection (PDPA/GDPR)**
- **Financial regulations**
- **Risk management**

## 🎨 UI Features

- **Drag & Drop Upload**: Intuitive file upload interface
- **Live Progress**: Real-time analysis progress with SSE
- **Color-coded Severity**: Visual risk indicators (green/yellow/red)
- **Responsive Design**: Works on desktop and mobile
- **Dark/Light Mode**: Toggle between themes
- **Report History**: Access previous analyses
- **Markdown Export**: Download detailed reports

## 🔧 Configuration

### Environment Variables

```bash
# Required
GROQ_API_KEY=your_groq_api_key_here
SUPABASE_URL=your_supabase_url_here
SUPABASE_KEY=your_supabase_anon_key_here

# Optional
MAX_FILE_SIZE_MB=10
PORT=8000
```

### Supabase Setup

1. Create a new Supabase project
2. Run the schema from `supabase_schema.sql`
3. Get your project URL and anon key from Settings > API
4. Update your `.env` file

## 🚀 Deployment

### Backend (FastAPI)

```bash
# Production with Gunicorn
pip install gunicorn
gunicorn app:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

### Frontend (Next.js)

```bash
cd web
npm run build
npm start
```

## 📈 Performance

- **Average LLM Response**: < 3 seconds for 5-page PDFs
- **File Size Limit**: 10MB (configurable)
- **Concurrent Users**: Supports multiple simultaneous analyses
- **Error Recovery**: Graceful handling of API failures

## 🛡 Security

- **File Validation**: Only PDF files accepted
- **Size Limits**: Configurable file size restrictions
- **Input Sanitization**: All inputs validated and sanitized
- **Error Handling**: No sensitive data in error messages

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License.

## 🙏 Acknowledgments

- **Groq** for ultra-fast AI inference
- **Supabase** for database and backend services
- **Next.js** for the modern React framework
- **FastAPI** for the high-performance Python API

---

**Powered by Groq** - Building the future of AI inference 🚀