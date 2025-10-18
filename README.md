# 🧠 AI Compliance Copilot (Groq + Supabase + Smithery)

**Team: [Your Team Name] | Cursor Hackathon Singapore 2025**

A production-ready AI-powered compliance analysis tool that uses Groq's ultra-fast Llama 3 API to analyze financial and legal PDFs for MAS 626 AML/CFT, PDPA, and cross-border compliance issues. Features MCP integration via Smithery for multi-agent AI workflows.

## 🚀 Features

- **Ultra-Fast Analysis**: Powered by Groq's lightning-fast Llama 3-70B model
- **Live Streaming**: Real-time progress updates with Server-Sent Events (SSE)
- **MAS 626 AML/CFT Compliance**: Comprehensive detection of Singapore AML/CFT violations
- **PDPA Compliance**: Personal Data Protection Act compliance analysis
- **Cross-Border Transaction Monitoring**: Enhanced due diligence for international transactions
- **MCP Integration**: Multi-agent workflows via Smithery MCP server
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
- **MCP Integration**: Smithery MCP Server
- **Multi-Agent AI**: ReaderAgent, ComplianceAgent, ReporterAgent
- **Export**: Markdown generation

## 🧩 Architecture

### Multi-Agent MCP Integration
The system uses Smithery MCP to enable multi-agent AI workflows:

- **ReaderAgent**: Extracts and processes text from PDF documents
- **ComplianceAgent**: Evaluates documents against MAS 626, PDPA, and cross-border regulations
- **ReporterAgent**: Generates structured compliance reports with evidence and recommendations

### MCP Tools Available
- `analyze_compliance`: Analyze PDF documents for compliance issues
- `save_report`: Store compliance reports in Supabase
- `get_reports`: Retrieve user's compliance report history
- `get_report`: Get specific report by ID

## 📋 Prerequisites

- Python 3.10+
- Node.js 18+
- Groq API key
- Supabase account
- Smithery MCP client (for multi-agent workflows)

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

**MCP Server (Terminal 2):**
```bash
cd smithery
python smithery_mcp.py
```

**Frontend (Terminal 3):**
```bash
cd web
npm run dev
```

Visit `http://localhost:3000` to access the application.

### 6. MCP Integration (Optional)

To use the multi-agent MCP features, register the server with Smithery:

```bash
# Add to your Smithery configuration
smithery add-server smithery/smithery.json
```

## 🏛️ Compliance Rules

### MAS 626 AML/CFT Rules
- Customer Due Diligence (CDD) requirements
- Enhanced Due Diligence (EDD) for high-risk customers
- Suspicious transaction reporting obligations
- Record keeping requirements (5 years minimum)
- Risk assessment and management frameworks
- Politically Exposed Persons (PEPs) screening
- Sanctions and watchlist screening

### PDPA Rules
- Consent management and withdrawal mechanisms
- Data collection purpose limitation
- Data accuracy and completeness requirements
- Data retention and disposal policies
- Cross-border data transfer restrictions
- Data breach notification obligations (72 hours)
- Individual rights (access, correction, withdrawal)

### Cross-Border Transaction Rules
- Transaction monitoring and reporting requirements
- Enhanced due diligence for international transactions
- Sanctions compliance across jurisdictions
- Regulatory reporting obligations

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

## 🧪 Testing

### Run MCP Tests
```bash
python test_mcp.py
```

### Run Demo
```bash
python demo.py
```

### Run Full Test Suite
```bash
pytest test_app.py -v
```

## 🚀 Deployment

### Quick Start (All Services)
```bash
./start.sh
```

### Individual Services

**Backend (FastAPI):**
```bash
uvicorn app:app --reload --port 8000
```

**MCP Server:**
```bash
cd smithery
python smithery_mcp.py
```

**Frontend (Next.js):**
```bash
cd web
npm run dev
```

### Production Deployment

**Backend with Gunicorn:**
```bash
pip install gunicorn
gunicorn app:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

**Frontend Build:**
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

## 🏆 Hackathon Story

**AI Compliance Copilot** was built for the Cursor Hackathon Singapore 2025 to address the critical need for automated compliance analysis in Singapore's financial sector. With the increasing complexity of MAS 626 AML/CFT and PDPA regulations, financial institutions need intelligent tools to identify compliance risks quickly and accurately.

### Problem Statement
- Manual compliance review is time-consuming and error-prone
- MAS 626 AML/CFT requirements are complex and constantly evolving
- PDPA compliance requires careful data handling and privacy protection
- Cross-border transactions need enhanced due diligence
- Traditional rule-based systems miss nuanced compliance issues

### Our Solution
- **AI-Powered Analysis**: Uses Groq's ultra-fast Llama 3 model for intelligent compliance detection
- **Multi-Agent Architecture**: Smithery MCP enables specialized AI agents for different compliance tasks
- **Real-time Processing**: Live streaming analysis with progress updates
- **Comprehensive Coverage**: MAS 626, PDPA, cross-border, and sanctions compliance
- **Actionable Insights**: Detailed evidence, recommendations, and risk scoring

### Technical Innovation
- **MCP Integration**: First compliance tool to use Smithery MCP for multi-agent workflows
- **Streaming Analysis**: Real-time progress updates using Server-Sent Events
- **Smart Rule Engine**: Dynamic compliance rule matching based on document content
- **Modern Stack**: FastAPI + Next.js + Supabase + Groq for optimal performance

## 🙏 Acknowledgments

- **Groq** for ultra-fast AI inference and Llama 3 model
- **Supabase** for database and backend services
- **Smithery** for MCP integration and multi-agent AI workflows
- **Cursor** for the amazing AI-powered development environment
- **Next.js** for the modern React framework
- **FastAPI** for the high-performance Python API

---

**Built for Cursor Hackathon Singapore 2025** 🚀

*Empowering financial institutions with AI-driven compliance analysis*