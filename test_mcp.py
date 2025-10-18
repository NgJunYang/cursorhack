#!/usr/bin/env python3
"""
Test script for MCP integration
Tests the Smithery MCP server functionality.
"""

import asyncio
import json
import os
import sys
from pathlib import Path

# Add current directory to path
sys.path.append(str(Path(__file__).parent))

async def test_mcp_tools():
    """Test all MCP tools."""
    
    print("🧪 Testing MCP Tools")
    print("=" * 30)
    
    # Import MCP functions
    from smithery.smithery_mcp import (
        analyze_compliance_tool,
        save_report_tool,
        get_reports_tool,
        get_report_tool
    )
    
    # Test 1: Analyze compliance (with dummy data)
    print("\n1️⃣ Testing analyze_compliance_tool...")
    try:
        # Create a dummy PDF content for testing
        dummy_pdf_content = """
        CUSTOMER DUE DILIGENCE FORM
        
        Customer Name: John Doe
        ID Number: S1234567A
        Business Purpose: Investment advisory services
        
        Note: This document lacks proper beneficial owner identification
        and does not include enhanced due diligence for high-risk customers.
        """
        
        # Write dummy content to a file
        with open("test_document.txt", "w") as f:
            f.write(dummy_pdf_content)
        
        result = await analyze_compliance_tool({
            "file_path": "test_document.txt",
            "filename": "test_document.txt"
        })
        
        if result and result[0].text:
            data = json.loads(result[0].text)
            if data.get("success"):
                print("✅ analyze_compliance_tool working")
                print(f"   Risk Score: {data['result']['overall_risk']:.1f}%")
                print(f"   Flags: {len(data['result']['flags'])}")
            else:
                print(f"❌ analyze_compliance_tool failed: {data.get('error')}")
        else:
            print("❌ No response from analyze_compliance_tool")
            
    except Exception as e:
        print(f"❌ Error testing analyze_compliance_tool: {e}")
    
    # Test 2: Save report
    print("\n2️⃣ Testing save_report_tool...")
    try:
        dummy_report = {
            "user_id": "test_user",
            "doc_name": "test_document.txt",
            "summary": "Test compliance analysis",
            "overall_risk": 75.5,
            "flags": [
                {
                    "title": "Missing CDD Documentation",
                    "severity": 4,
                    "why_it_matters": "MAS 626 requires comprehensive CDD",
                    "recommendation": "Implement proper CDD procedures",
                    "evidence": [
                        {
                            "page": 1,
                            "quote": "Customer information appears incomplete"
                        }
                    ]
                }
            ]
        }
        
        result = await save_report_tool(dummy_report)
        
        if result and result[0].text:
            data = json.loads(result[0].text)
            if data.get("success"):
                print("✅ save_report_tool working")
                print(f"   Report ID: {data.get('report_id')}")
            else:
                print(f"❌ save_report_tool failed: {data.get('error')}")
        else:
            print("❌ No response from save_report_tool")
            
    except Exception as e:
        print(f"❌ Error testing save_report_tool: {e}")
    
    # Test 3: Get reports
    print("\n3️⃣ Testing get_reports_tool...")
    try:
        result = await get_reports_tool({"user_id": "test_user"})
        
        if result and result[0].text:
            data = json.loads(result[0].text)
            if data.get("success"):
                print("✅ get_reports_tool working")
                print(f"   Reports found: {data['count']}")
            else:
                print(f"❌ get_reports_tool failed: {data.get('error')}")
        else:
            print("❌ No response from get_reports_tool")
            
    except Exception as e:
        print(f"❌ Error testing get_reports_tool: {e}")
    
    # Test 4: Get specific report
    print("\n4️⃣ Testing get_report_tool...")
    try:
        result = await get_report_tool({"report_id": 1})
        
        if result and result[0].text:
            data = json.loads(result[0].text)
            if data.get("success"):
                print("✅ get_report_tool working")
                print(f"   Report: {data['report']['doc_name']}")
            else:
                print(f"❌ get_report_tool failed: {data.get('error')}")
        else:
            print("❌ No response from get_report_tool")
            
    except Exception as e:
        print(f"❌ Error testing get_report_tool: {e}")
    
    # Cleanup
    if os.path.exists("test_document.txt"):
        os.remove("test_document.txt")
    
    print("\n🎉 MCP testing completed!")

if __name__ == "__main__":
    # Check environment variables
    required_vars = ["GROQ_API_KEY", "SUPABASE_URL", "SUPABASE_KEY"]
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        print(f"❌ Missing environment variables: {', '.join(missing_vars)}")
        print("Please set up your .env file with the required API keys.")
        sys.exit(1)
    
    asyncio.run(test_mcp_tools())