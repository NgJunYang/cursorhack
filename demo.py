#!/usr/bin/env python3
"""
AI Compliance Copilot Demo Script
Demonstrates the MCP integration and compliance analysis capabilities.
"""

import asyncio
import json
import os
import sys
from pathlib import Path

# Add current directory to path
sys.path.append(str(Path(__file__).parent))

from smithery.smithery_mcp import (
    analyze_compliance_tool,
    save_report_tool,
    get_reports_tool
)

async def demo_compliance_analysis():
    """Demonstrate compliance analysis using MCP tools."""
    
    print("🧠 AI Compliance Copilot Demo")
    print("=" * 50)
    
    # Check if we have a sample PDF
    sample_pdf = "sample_compliance_doc.pdf"
    if not os.path.exists(sample_pdf):
        print(f"❌ Sample PDF not found: {sample_pdf}")
        print("Please add a sample PDF file to test the compliance analysis.")
        return
    
    print(f"📄 Analyzing sample document: {sample_pdf}")
    
    # Step 1: Analyze compliance
    print("\n1️⃣ Analyzing compliance issues...")
    analysis_result = await analyze_compliance_tool({
        "file_path": sample_pdf,
        "filename": sample_pdf
    })
    
    if analysis_result and analysis_result[0].text:
        result_data = json.loads(analysis_result[0].text)
        if result_data.get("success"):
            print("✅ Analysis completed successfully!")
            print(f"📊 Overall Risk Score: {result_data['result']['overall_risk']:.1f}%")
            print(f"🚨 Flags Found: {len(result_data['result']['flags'])}")
            
            # Display flags
            for i, flag in enumerate(result_data['result']['flags'][:3], 1):
                print(f"\n   {i}. {flag['title']} (Severity: {flag['severity']}/5)")
                print(f"      Why it matters: {flag['why_it_matters'][:100]}...")
        else:
            print(f"❌ Analysis failed: {result_data.get('error', 'Unknown error')}")
    else:
        print("❌ No analysis result received")
    
    # Step 2: Save report
    print("\n2️⃣ Saving report to database...")
    if result_data and result_data.get("success"):
        save_result = await save_report_tool({
            "user_id": "demo_user",
            "doc_name": sample_pdf,
            "summary": result_data['result']['summary'],
            "overall_risk": result_data['result']['overall_risk'],
            "flags": result_data['result']['flags']
        })
        
        if save_result and save_result[0].text:
            save_data = json.loads(save_result[0].text)
            if save_data.get("success"):
                print(f"✅ Report saved with ID: {save_data.get('report_id')}")
            else:
                print(f"❌ Failed to save report: {save_data.get('error')}")
    
    # Step 3: Retrieve reports
    print("\n3️⃣ Retrieving user reports...")
    reports_result = await get_reports_tool({"user_id": "demo_user"})
    
    if reports_result and reports_result[0].text:
        reports_data = json.loads(reports_result[0].text)
        if reports_data.get("success"):
            print(f"✅ Found {reports_data['count']} reports for demo_user")
            for report in reports_data['reports'][:3]:
                print(f"   📄 {report['doc_name']} - Risk: {report['overall_risk']:.1f}%")
        else:
            print(f"❌ Failed to retrieve reports: {reports_data.get('error')}")
    
    print("\n🎉 Demo completed!")
    print("\nTo test the full application:")
    print("1. Run: ./start.sh")
    print("2. Visit: http://localhost:3000")
    print("3. Upload a PDF document for analysis")

def create_sample_pdf():
    """Create a sample PDF for testing (placeholder)."""
    print("📝 Creating sample compliance document...")
    
    # This would create a sample PDF with compliance issues
    # For now, we'll just create a placeholder
    sample_content = """
    SAMPLE COMPLIANCE DOCUMENT
    
    This is a sample document that would contain various compliance issues
    such as missing customer due diligence information, inadequate data
    protection measures, and cross-border transaction risks.
    
    The AI Compliance Copilot would analyze this document and identify
    specific violations of MAS 626 AML/CFT and PDPA regulations.
    """
    
    with open("sample_compliance_doc.txt", "w") as f:
        f.write(sample_content)
    
    print("✅ Sample document created: sample_compliance_doc.txt")
    print("Note: Convert this to PDF format for full testing")

if __name__ == "__main__":
    # Check environment variables
    required_vars = ["GROQ_API_KEY", "SUPABASE_URL", "SUPABASE_KEY"]
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        print(f"❌ Missing environment variables: {', '.join(missing_vars)}")
        print("Please set up your .env file with the required API keys.")
        sys.exit(1)
    
    # Create sample document if it doesn't exist
    if not os.path.exists("sample_compliance_doc.pdf"):
        create_sample_pdf()
    
    # Run the demo
    asyncio.run(demo_compliance_analysis())