#!/usr/bin/env python3
"""
AI Compliance Copilot MCP Server
Provides tools for compliance analysis and report management via Smithery MCP.
"""

import asyncio
import json
import os
import sys
import time
from typing import Any, Dict, List, Optional
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from mcp.server import Server
from mcp.server.models import InitializationOptions
from mcp.server.stdio import stdio_server
from mcp.types import (
    CallToolRequest,
    CallToolResult,
    ListToolsRequest,
    ListToolsResult,
    Tool,
    TextContent,
    ImageContent,
    EmbeddedResource,
)

# Import our compliance analysis functions
from app import analyze_chunks, extract_text_from_pdf, Report
from supabase import create_client, Client

# Initialize MCP server
server = Server("ai-compliance-copilot")

# Initialize Supabase client
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase: Optional[Client] = None

if SUPABASE_URL and SUPABASE_KEY:
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

@server.list_tools()
async def handle_list_tools() -> List[Tool]:
    """List available MCP tools."""
    return [
        Tool(
            name="analyze_compliance",
            description="Analyze a PDF document for compliance issues using AI",
            inputSchema={
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "Path to the PDF file to analyze"
                    },
                    "filename": {
                        "type": "string", 
                        "description": "Original filename of the document"
                    }
                },
                "required": ["file_path", "filename"]
            }
        ),
        Tool(
            name="save_report",
            description="Save a compliance analysis report to the database",
            inputSchema={
                "type": "object",
                "properties": {
                    "user_id": {
                        "type": "string",
                        "description": "User ID for the report"
                    },
                    "doc_name": {
                        "type": "string",
                        "description": "Document name"
                    },
                    "summary": {
                        "type": "string",
                        "description": "Executive summary of the analysis"
                    },
                    "overall_risk": {
                        "type": "number",
                        "description": "Overall risk score (0-100)"
                    },
                    "flags": {
                        "type": "array",
                        "description": "List of compliance flags found",
                        "items": {
                            "type": "object",
                            "properties": {
                                "title": {"type": "string"},
                                "severity": {"type": "integer", "minimum": 1, "maximum": 5},
                                "why_it_matters": {"type": "string"},
                                "recommendation": {"type": "string"},
                                "evidence": {
                                    "type": "array",
                                    "items": {
                                        "type": "object",
                                        "properties": {
                                            "page": {"type": "integer"},
                                            "quote": {"type": "string"}
                                        }
                                    }
                                }
                            }
                        }
                    }
                },
                "required": ["user_id", "doc_name", "summary", "overall_risk", "flags"]
            }
        ),
        Tool(
            name="get_reports",
            description="Retrieve compliance reports for a user",
            inputSchema={
                "type": "object",
                "properties": {
                    "user_id": {
                        "type": "string",
                        "description": "User ID to get reports for",
                        "default": "demo_user"
                    }
                }
            }
        ),
        Tool(
            name="get_report",
            description="Get a specific compliance report by ID",
            inputSchema={
                "type": "object",
                "properties": {
                    "report_id": {
                        "type": "integer",
                        "description": "ID of the report to retrieve"
                    }
                },
                "required": ["report_id"]
            }
        )
    ]

@server.call_tool()
async def handle_call_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
    """Handle tool calls."""
    
    if name == "analyze_compliance":
        return await analyze_compliance_tool(arguments)
    elif name == "save_report":
        return await save_report_tool(arguments)
    elif name == "get_reports":
        return await get_reports_tool(arguments)
    elif name == "get_report":
        return await get_report_tool(arguments)
    else:
        raise ValueError(f"Unknown tool: {name}")

async def analyze_compliance_tool(arguments: Dict[str, Any]) -> List[TextContent]:
    """Analyze a PDF file for compliance issues."""
    file_path = arguments["file_path"]
    filename = arguments["filename"]
    
    try:
        # Read the PDF file
        with open(file_path, "rb") as f:
            file_content = f.read()
        
        # Extract text from PDF
        text = extract_text_from_pdf(file_content)
        if not text.strip():
            return [TextContent(
                type="text",
                text=json.dumps({
                    "error": "No text found in PDF",
                    "success": False
                }, indent=2)
            )]
        
        # Analyze the document
        result = analyze_chunks(text, filename)
        
        return [TextContent(
            type="text",
            text=json.dumps({
                "success": True,
                "result": result.dict(),
                "filename": filename
            }, indent=2)
        )]
        
    except Exception as e:
        return [TextContent(
            type="text",
            text=json.dumps({
                "error": str(e),
                "success": False
            }, indent=2)
        )]

async def save_report_tool(arguments: Dict[str, Any]) -> List[TextContent]:
    """Save a compliance report to the database."""
    if not supabase:
        return [TextContent(
            type="text",
            text=json.dumps({
                "error": "Supabase not configured",
                "success": False
            }, indent=2)
        )]
    
    try:
        # Create report object
        report = Report(
            user_id=arguments["user_id"],
            doc_name=arguments["doc_name"],
            summary=arguments["summary"],
            overall_risk=arguments["overall_risk"],
            flags=arguments["flags"],
            ts=int(time.time())
        )
        
        # Convert to dict for Supabase
        report_dict = report.dict()
        report_dict["flags"] = [flag if isinstance(flag, dict) else flag.dict() for flag in arguments["flags"]]
        
        # Insert into database
        response = supabase.table("reports").insert(report_dict).execute()
        
        return [TextContent(
            type="text",
            text=json.dumps({
                "success": True,
                "report_id": response.data[0]["id"] if response.data else None,
                "message": "Report saved successfully"
            }, indent=2)
        )]
        
    except Exception as e:
        return [TextContent(
            type="text",
            text=json.dumps({
                "error": str(e),
                "success": False
            }, indent=2)
        )]

async def get_reports_tool(arguments: Dict[str, Any]) -> List[TextContent]:
    """Get all reports for a user."""
    if not supabase:
        return [TextContent(
            type="text",
            text=json.dumps({
                "error": "Supabase not configured",
                "success": False
            }, indent=2)
        )]
    
    try:
        user_id = arguments.get("user_id", "demo_user")
        response = supabase.table("reports").select("*").eq("user_id", user_id).order("ts", desc=True).execute()
        
        return [TextContent(
            type="text",
            text=json.dumps({
                "success": True,
                "reports": response.data,
                "count": len(response.data)
            }, indent=2)
        )]
        
    except Exception as e:
        return [TextContent(
            type="text",
            text=json.dumps({
                "error": str(e),
                "success": False
            }, indent=2)
        )]

async def get_report_tool(arguments: Dict[str, Any]) -> List[TextContent]:
    """Get a specific report by ID."""
    if not supabase:
        return [TextContent(
            type="text",
            text=json.dumps({
                "error": "Supabase not configured",
                "success": False
            }, indent=2)
        )]
    
    try:
        report_id = arguments["report_id"]
        response = supabase.table("reports").select("*").eq("id", report_id).execute()
        
        if not response.data:
            return [TextContent(
                type="text",
                text=json.dumps({
                    "error": "Report not found",
                    "success": False
                }, indent=2)
            )]
        
        return [TextContent(
            type="text",
            text=json.dumps({
                "success": True,
                "report": response.data[0]
            }, indent=2)
        )]
        
    except Exception as e:
        return [TextContent(
            type="text",
            text=json.dumps({
                "error": str(e),
                "success": False
            }, indent=2)
        )]

async def main():
    """Main entry point for the MCP server."""
    # Run the server using stdio
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="ai-compliance-copilot",
                server_version="1.0.0",
                capabilities=server.get_capabilities(
                    notification_options=None,
                    experimental_capabilities={}
                )
            )
        )

if __name__ == "__main__":
    asyncio.run(main())