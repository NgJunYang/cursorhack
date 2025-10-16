#!/usr/bin/env python3
"""
Demo script for AI Compliance Copilot
Uploads a sample PDF and demonstrates the analysis workflow
"""

import requests
import json
import time
import os
from pathlib import Path

# Configuration
BACKEND_URL = "http://localhost:8000"
SAMPLE_PDF_PATH = "sample_document.pdf"

def create_sample_pdf():
    """Create a sample PDF for testing if it doesn't exist."""
    try:
        from reportlab.pdfgen import canvas
        from reportlab.lib.pagesizes import letter
        
        c = canvas.Canvas(SAMPLE_PDF_PATH, pagesize=letter)
        
        # Page 1
        c.drawString(100, 750, "SAMPLE FINANCIAL DOCUMENT")
        c.drawString(100, 720, "Cross-Border Transaction Agreement")
        c.drawString(100, 690, "")
        c.drawString(100, 660, "This document outlines a transaction between entities")
        c.drawString(100, 630, "located in the United States, European Union, and Singapore.")
        c.drawString(100, 600, "The transaction involves the transfer of funds across")
        c.drawString(100, 570, "multiple jurisdictions with varying regulatory requirements.")
        c.drawString(100, 540, "")
        c.drawString(100, 510, "Key Terms:")
        c.drawString(100, 480, "- Amount: $2,500,000 USD")
        c.drawString(100, 450, "- Parties: US Corp, EU Ltd, SG Holdings")
        c.drawString(100, 420, "- Jurisdictions: New York, London, Singapore")
        c.drawString(100, 390, "- Compliance: Subject to AML and sanctions screening")
        c.drawString(100, 360, "")
        c.drawString(100, 330, "Data Protection Notice:")
        c.drawString(100, 300, "This document contains personal data subject to GDPR")
        c.drawString(100, 270, "and PDPA regulations in the respective jurisdictions.")
        
        c.showPage()
        
        # Page 2
        c.drawString(100, 750, "RISK ASSESSMENT")
        c.drawString(100, 720, "")
        c.drawString(100, 690, "The following risks have been identified:")
        c.drawString(100, 660, "")
        c.drawString(100, 630, "1. Cross-border regulatory compliance")
        c.drawString(100, 600, "2. Anti-money laundering requirements")
        c.drawString(100, 570, "3. Sanctions screening obligations")
        c.drawString(100, 540, "4. Data protection compliance")
        c.drawString(100, 510, "")
        c.drawString(100, 480, "Recommendations:")
        c.drawString(100, 450, "- Conduct enhanced due diligence")
        c.drawString(100, 420, "- Implement ongoing monitoring")
        c.drawString(100, 390, "- Regular compliance reviews")
        
        c.save()
        print(f"✅ Created sample PDF: {SAMPLE_PDF_PATH}")
        return True
        
    except ImportError:
        print("❌ reportlab not installed. Install with: pip install reportlab")
        return False
    except Exception as e:
        print(f"❌ Error creating sample PDF: {e}")
        return False

def test_regular_analysis():
    """Test the regular /analyze endpoint."""
    print("\n🔍 Testing Regular Analysis...")
    
    if not os.path.exists(SAMPLE_PDF_PATH):
        print("Creating sample PDF...")
        if not create_sample_pdf():
            return False
    
    try:
        with open(SAMPLE_PDF_PATH, 'rb') as f:
            files = {'file': f}
            response = requests.post(f"{BACKEND_URL}/analyze", files=files)
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Analysis completed successfully!")
            print(f"📊 Overall Risk: {result['overall_risk']:.1f}%")
            print(f"🚩 Flags Found: {len(result['flags'])}")
            print(f"📝 Summary: {result['summary'][:100]}...")
            return True
        else:
            print(f"❌ Analysis failed: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error during analysis: {e}")
        return False

def test_streaming_analysis():
    """Test the streaming /analyze_sse endpoint."""
    print("\n🌊 Testing Streaming Analysis...")
    
    if not os.path.exists(SAMPLE_PDF_PATH):
        print("Creating sample PDF...")
        if not create_sample_pdf():
            return False
    
    try:
        with open(SAMPLE_PDF_PATH, 'rb') as f:
            files = {'file': f}
            response = requests.post(f"{BACKEND_URL}/analyze_sse", files=files, stream=True)
        
        if response.status_code == 200:
            print("✅ Streaming analysis started!")
            
            for line in response.iter_lines():
                if line:
                    line_str = line.decode('utf-8')
                    if line_str.startswith('data: '):
                        try:
                            data = json.loads(line_str[6:])
                            stage = data.get('stage', 'unknown')
                            message = data.get('message', '')
                            
                            if stage == 'ingest':
                                print(f"📁 {message}")
                            elif stage == 'extract':
                                print(f"📄 {message}")
                            elif stage == 'analyze':
                                print(f"🤖 {message}")
                            elif stage == 'done':
                                print(f"✅ {message}")
                                result = data.get('result', {})
                                print(f"📊 Overall Risk: {result.get('overall_risk', 0):.1f}%")
                                print(f"🚩 Flags Found: {len(result.get('flags', []))}")
                                return True
                            elif stage == 'error':
                                print(f"❌ Error: {message}")
                                return False
                                
                        except json.JSONDecodeError:
                            continue
            return True
        else:
            print(f"❌ Streaming analysis failed: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error during streaming analysis: {e}")
        return False

def test_reports_endpoint():
    """Test the /reports endpoint."""
    print("\n📋 Testing Reports Endpoint...")
    
    try:
        response = requests.get(f"{BACKEND_URL}/reports?user_id=demo_user")
        
        if response.status_code == 200:
            data = response.json()
            reports = data.get('reports', [])
            print(f"✅ Found {len(reports)} reports")
            
            if reports:
                latest = reports[0]
                print(f"📄 Latest: {latest.get('doc_name', 'Unknown')}")
                print(f"📊 Risk: {latest.get('overall_risk', 0):.1f}%")
                print(f"🚩 Flags: {len(latest.get('flags', []))}")
            return True
        else:
            print(f"❌ Reports fetch failed: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error fetching reports: {e}")
        return False

def check_backend_health():
    """Check if the backend is running."""
    try:
        response = requests.get(f"{BACKEND_URL}/")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Backend is running: {data.get('message', 'Unknown')}")
            return True
        else:
            print(f"❌ Backend health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Cannot connect to backend: {e}")
        print("💡 Make sure to start the backend with: uvicorn app:app --reload --port 8000")
        return False

def main():
    """Run the complete demo."""
    print("🚀 AI Compliance Copilot Demo")
    print("=" * 40)
    
    # Check backend health
    if not check_backend_health():
        return
    
    # Test regular analysis
    regular_success = test_regular_analysis()
    
    # Test streaming analysis
    streaming_success = test_streaming_analysis()
    
    # Test reports endpoint
    reports_success = test_reports_endpoint()
    
    # Summary
    print("\n📊 Demo Summary")
    print("=" * 20)
    print(f"Regular Analysis: {'✅' if regular_success else '❌'}")
    print(f"Streaming Analysis: {'✅' if streaming_success else '❌'}")
    print(f"Reports Endpoint: {'✅' if reports_success else '❌'}")
    
    if all([regular_success, streaming_success, reports_success]):
        print("\n🎉 All tests passed! The AI Compliance Copilot is working correctly.")
        print("🌐 Visit http://localhost:3000 to use the web interface.")
    else:
        print("\n⚠️  Some tests failed. Check the error messages above.")
    
    # Cleanup
    if os.path.exists(SAMPLE_PDF_PATH):
        os.remove(SAMPLE_PDF_PATH)
        print(f"🧹 Cleaned up sample PDF")

if __name__ == "__main__":
    main()