#!/usr/bin/env python3
"""
Test script to start the FastAPI server for development
"""

import uvicorn
import os
import sys

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

if __name__ == "__main__":
    print("🚀 Starting AI Foundry Agent Backend for testing...")
    print("📱 API Documentation: http://localhost:8001/docs")
    print("🔧 OpenAPI Spec: http://localhost:8001/redoc")
    print("❤️  Health Check: http://localhost:8001/health")
    print("🤖 Chat API: http://localhost:8001/api/v1/chat")
    print("🔬 Agent API: http://localhost:8001/api/v1/agent")
    print("\n⚠️  Note: Using mock responses since Azure services are not configured")
    print("Press Ctrl+C to stop the server\n")
    
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8001,
        reload=True,
        log_level="info"
    )