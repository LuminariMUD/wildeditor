#!/usr/bin/env python3
"""
Test if Docker container with --network host can reach local services
"""

import requests

print("🔍 Testing Docker Network Access to Host Services")
print("="*50)

# Test 1: Backend API (we know this works)
print("\n1️⃣ Testing Backend API at localhost:8000")
try:
    response = requests.get("http://localhost:8000/api/health", timeout=2)
    print(f"✅ Backend accessible: {response.status_code}")
except Exception as e:
    print(f"❌ Backend error: {e}")

# Test 2: MCP Server 
print("\n2️⃣ Testing MCP Server at localhost:8001")
try:
    response = requests.get("http://localhost:8001/health", timeout=2)
    print(f"✅ MCP accessible: {response.status_code}")
except Exception as e:
    print(f"❌ MCP error: {e}")

# Test 3: Ollama API
print("\n3️⃣ Testing Ollama at localhost:11434")
try:
    response = requests.get("http://localhost:11434/api/tags", timeout=2)
    print(f"✅ Ollama accessible: {response.status_code}")
    data = response.json()
    print(f"   Models: {[m['name'] for m in data.get('models', [])]}")
except Exception as e:
    print(f"❌ Ollama error: {e}")

# Test 4: Different URL formats for Ollama
print("\n4️⃣ Testing different Ollama URL formats:")
urls = [
    "http://localhost:11434",
    "http://127.0.0.1:11434",
    "http://0.0.0.0:11434",
    "http://host.docker.internal:11434"
]

for url in urls:
    try:
        response = requests.get(f"{url}/api/tags", timeout=1)
        print(f"✅ {url} works")
    except:
        print(f"❌ {url} fails")

print("\n" + "="*50)
print("💡 Recommendation:")
print("Use the URL format that works above in OLLAMA_BASE_URL")