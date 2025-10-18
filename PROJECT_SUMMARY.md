# 🧠 AI Compliance Copilot - Project Summary

**Cursor Hackathon Singapore 2025 | Team: [Your Team Name]**

## 🎯 Project Overview

AI Compliance Copilot is a comprehensive compliance analysis platform that uses AI to automatically detect MAS 626 AML/CFT, PDPA, and cross-border compliance issues in financial documents. Built with Groq's ultra-fast Llama 3 model and integrated with Smithery MCP for multi-agent AI workflows.

## 🏗️ Architecture

### Backend (FastAPI + Python)
- **FastAPI Server**: High-performance API with async support
- **Groq Integration**: Ultra-fast Llama 3-70B model for compliance analysis
- **Supabase Database**: PostgreSQL for report storage and retrieval
- **PDF Processing**: pdfplumber + PyMuPDF for text extraction
- **Compliance Rules Engine**: Comprehensive MAS 626, PDPA, and cross-border rules

### Frontend (Next.js + React)
- **Modern UI**: Responsive design with dark/light mode
- **Drag & Drop Upload**: Intuitive PDF upload interface
- **Live Streaming**: Real-time analysis progress with SSE
- **Report Dashboard**: Color-coded compliance flags and risk scores
- **Markdown Export**: Download detailed compliance reports

### MCP Integration (Smithery)
- **Multi-Agent Architecture**: ReaderAgent, ComplianceAgent, ReporterAgent
- **MCP Tools**: analyze_compliance, save_report, get_reports, get_report
- **WebSocket Server**: Real-time communication with AI agents

## 🚀 Key Features

### 1. AI-Powered Compliance Analysis
- **MAS 626 AML/CFT**: Customer due diligence, suspicious transaction reporting, record keeping
- **PDPA Compliance**: Consent management, data protection, breach notification
- **Cross-Border Monitoring**: Enhanced due diligence for international transactions
- **Sanctions Screening**: Watchlist and sanctions compliance checking

### 2. Real-Time Processing
- **Live Streaming**: Server-Sent Events for real-time progress updates
- **Multi-Stage Analysis**: Ingest → Extract → Analyze → Done
- **Progress Tracking**: Visual progress bar with stage descriptions

### 3. Comprehensive Reporting
- **Risk Scoring**: 0-100 risk assessment with severity levels
- **Evidence Extraction**: Page-specific quotes and references
- **Actionable Recommendations**: Specific remediation steps
- **Markdown Export**: Professional compliance reports

### 4. Multi-Agent AI Workflows
- **ReaderAgent**: Extracts and processes PDF content
- **ComplianceAgent**: Evaluates against regulatory requirements
- **ReporterAgent**: Generates structured compliance reports
- **MCP Integration**: Seamless communication between agents

## 🛠️ Technology Stack

### Backend
- **FastAPI**: High-performance Python web framework
- **Groq**: Ultra-fast AI inference with Llama 3-70B
- **Supabase**: PostgreSQL database with real-time features
- **pdfplumber + PyMuPDF**: Robust PDF text extraction
- **Pydantic**: Data validation and serialization

### Frontend
- **Next.js 14**: React framework with App Router
- **Tailwind CSS**: Utility-first CSS framework
- **TypeScript**: Type-safe JavaScript
- **Lucide React**: Modern icon library
- **Axios**: HTTP client for API communication

### MCP Integration
- **Smithery MCP**: Multi-agent AI platform
- **WebSocket**: Real-time communication
- **JSON Schema**: Tool definition and validation

## 📊 Compliance Rules Coverage

### MAS 626 AML/CFT (5 Rules)
- Customer Due Diligence (CDD) requirements
- Enhanced Due Diligence (EDD) for high-risk customers
- Suspicious transaction reporting obligations
- Record keeping requirements (5 years minimum)
- Risk assessment and management frameworks

### PDPA (6 Rules)
- Consent management and withdrawal mechanisms
- Data collection purpose limitation
- Data accuracy and completeness requirements
- Data retention and disposal policies
- Cross-border data transfer restrictions
- Data breach notification obligations (72 hours)

### Cross-Border & Sanctions (3 Rules)
- Cross-border transaction monitoring
- Sanctions and watchlist screening
- Enhanced due diligence for international transactions

## 🚀 Quick Start

### 1. Environment Setup
```bash
# Copy environment template
cp .env.example .env

# Edit .env with your API keys
# GROQ_API_KEY=your_groq_api_key_here
# SUPABASE_URL=your_supabase_url_here
# SUPABASE_KEY=your_supabase_anon_key_here
```

### 2. Install Dependencies
```bash
# Python dependencies
pip install -r requirements.txt

# Node.js dependencies
cd web && npm install && cd ..
```

### 3. Database Setup
```sql
-- Run in Supabase SQL editor
CREATE TABLE reports (
  id bigint generated always as identity primary key,
  user_id text not null,
  doc_name text,
  summary text,
  overall_risk double precision,
  flags jsonb,
  ts bigint
);
```

### 4. Run Application
```bash
# Start all services
./start.sh

# Or start individually:
# Backend: uvicorn app:app --reload --port 8000
# MCP: cd smithery && python smithery_mcp.py
# Frontend: cd web && npm run dev
```

### 5. Access Application
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **MCP Server**: ws://127.0.0.1:8765

## 🧪 Testing

### Run Tests
```bash
# MCP integration tests
python test_mcp.py

# Full application tests
pytest test_app.py -v

# Demo script
python demo.py
```

## 📈 Performance Metrics

- **Average Analysis Time**: < 3 seconds for 5-page PDFs
- **File Size Limit**: 10MB (configurable)
- **Concurrent Users**: Supports multiple simultaneous analyses
- **Accuracy**: AI-powered detection with human-readable explanations

## 🔒 Security Features

- **File Validation**: Only PDF files accepted
- **Size Limits**: Configurable file size restrictions
- **Input Sanitization**: All inputs validated and sanitized
- **Error Handling**: No sensitive data in error messages
- **API Rate Limiting**: Built-in protection against abuse

## 🎨 UI/UX Features

- **Responsive Design**: Works on desktop and mobile
- **Dark/Light Mode**: Toggle between themes
- **Drag & Drop**: Intuitive file upload interface
- **Live Progress**: Real-time analysis updates
- **Color-Coded Severity**: Visual risk indicators
- **Export Functionality**: Markdown report downloads

## 🏆 Hackathon Innovation

### Technical Innovation
1. **First MCP Integration**: First compliance tool using Smithery MCP
2. **Multi-Agent AI**: Specialized agents for different compliance tasks
3. **Real-Time Streaming**: Live progress updates during analysis
4. **Smart Rule Engine**: Dynamic compliance rule matching

### Business Impact
1. **Time Savings**: Reduces manual compliance review from hours to minutes
2. **Accuracy**: AI-powered detection catches nuanced compliance issues
3. **Scalability**: Handles multiple documents simultaneously
4. **Compliance**: Covers all major Singapore financial regulations

## 📝 API Endpoints

### Analysis
- `POST /analyze` - Analyze PDF document
- `POST /analyze_sse` - Analyze with live streaming

### Reports
- `GET /reports` - Get user reports
- `GET /reports/{id}` - Get specific report

### MCP Tools
- `analyze_compliance` - Analyze document via MCP
- `save_report` - Save report via MCP
- `get_reports` - Retrieve reports via MCP
- `get_report` - Get specific report via MCP

## 🚀 Future Enhancements

1. **Additional Regulations**: Add more compliance frameworks
2. **Batch Processing**: Analyze multiple documents simultaneously
3. **API Integration**: Connect with existing compliance systems
4. **Machine Learning**: Improve accuracy with user feedback
5. **Mobile App**: Native mobile application

## 📞 Support

For questions or issues:
- **Documentation**: See README.md
- **Issues**: Create GitHub issue
- **Demo**: Run `python demo.py`

---

**Built with ❤️ for Cursor Hackathon Singapore 2025**

*Empowering financial institutions with AI-driven compliance analysis*