#!/usr/bin/env python3
"""
Simple test script to check if the upload endpoint is working
"""

import requests
import os

def test_upload_endpoint():
    """Test the upload endpoint with a simple request"""
    
    # Test if backend is responding
    try:
        response = requests.get("http://localhost:8000/api/health")
        print(f"✅ Backend health check: {response.status_code}")
        print(f"   Response: {response.json()}")
    except Exception as e:
        print(f"❌ Backend not responding: {e}")
        return
    
    # Test upload endpoint (without file)
    try:
        response = requests.post("http://localhost:8000/api/upload/")
        print(f"📤 Upload endpoint test: {response.status_code}")
        if response.status_code != 422:  # 422 is expected for missing files
            print(f"   Response: {response.text}")
    except Exception as e:
        print(f"❌ Upload endpoint error: {e}")

if __name__ == "__main__":
    print("🧪 Testing Shrimp Vision Upload Endpoint")
    print("=" * 40)
    test_upload_endpoint()
