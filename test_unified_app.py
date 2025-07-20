#!/usr/bin/env python3
"""
Test script for the Unified Stock Market Analysis Platform
"""

import requests
import json
import time

def test_api_endpoints():
    """Test all API endpoints"""
    base_url = "http://localhost:8001"
    
    print("🧪 Testing Unified Stock Market Analysis Platform")
    print("=" * 60)
    
    # Test 1: Root endpoint
    print("\n1️⃣ Testing root endpoint...")
    try:
        response = requests.get(f"{base_url}/")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Root endpoint working")
            print(f"   Version: {data['version']}")
            print(f"   Description: {data['description']}")
        else:
            print(f"❌ Root endpoint failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Root endpoint error: {e}")
    
    # Test 2: Latest prices
    print("\n2️⃣ Testing latest prices...")
    try:
        response = requests.get(f"{base_url}/api/latest-prices")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Latest prices working")
            print(f"   Apple: ${data.get('apple_price', 'N/A')}")
            print(f"   Tesla: ${data.get('tesla_price', 'N/A')}")
            print(f"   Bitcoin: ${data.get('bitcoin_price', 'N/A')}")
        else:
            print(f"❌ Latest prices failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Latest prices error: {e}")
    
    # Test 3: Market overview
    print("\n3️⃣ Testing market overview...")
    try:
        response = requests.get(f"{base_url}/api/market-overview")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Market overview working")
            print(f"   Analysis date: {data.get('analysis_date', 'N/A')}")
            print(f"   Statistics available: {len(data.get('statistics', {}))}")
        else:
            print(f"❌ Market overview failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Market overview error: {e}")
    
    # Test 4: Historical analysis
    print("\n4️⃣ Testing historical analysis...")
    try:
        response = requests.get(f"{base_url}/api/historical-analysis?symbol=AAPL&days=7")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Historical analysis working")
            print(f"   Symbol: {data.get('symbol', 'N/A')}")
            print(f"   Current Price: ${data.get('current_price', 'N/A')}")
            print(f"   Price Change: {data.get('price_change_pct', 'N/A')}%")
            print(f"   Volatility: {data.get('volatility', 'N/A')}")
        else:
            print(f"❌ Historical analysis failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Historical analysis error: {e}")
    
    # Test 5: LLM tools
    print("\n5️⃣ Testing LLM tools...")
    try:
        response = requests.get(f"{base_url}/tools")
        if response.status_code == 200:
            data = response.json()
            tools = data.get('tools', [])
            print(f"✅ LLM tools working")
            print(f"   Available tools: {len(tools)}")
            for tool in tools:
                func_name = tool.get('function', {}).get('name', 'Unknown')
                print(f"   - {func_name}")
        else:
            print(f"❌ LLM tools failed: {response.status_code}")
    except Exception as e:
        print(f"❌ LLM tools error: {e}")
    
    # Test 6: Stock data with filters
    print("\n6️⃣ Testing stock data with filters...")
    try:
        response = requests.get(f"{base_url}/api/stock-datas?limit=5")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Stock data working")
            print(f"   Records returned: {len(data.get('data', []))}")
            print(f"   Total: {data.get('total', 'N/A')}")
        else:
            print(f"❌ Stock data failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Stock data error: {e}")

def test_multiple_symbols():
    """Test historical analysis for multiple symbols"""
    base_url = "http://localhost:8001"
    
    print("\n📊 Testing Multiple Symbols")
    print("=" * 40)
    
    symbols = ["AAPL", "TSLA", "MSFT", "GOOGL", "BTC", "GOLD"]
    
    for symbol in symbols:
        try:
            response = requests.get(f"{base_url}/api/historical-analysis?symbol={symbol}&days=30")
            if response.status_code == 200:
                data = response.json()
                price_change = data.get('price_change_pct', 0)
                trend = "📈" if price_change > 0 else "📉" if price_change < 0 else "➡️"
                print(f"{trend} {symbol}: ${data.get('current_price', 'N/A'):.2f} ({price_change:+.2f}%)")
            else:
                print(f"❌ {symbol}: Failed ({response.status_code})")
        except Exception as e:
            print(f"❌ {symbol}: Error - {e}")

def test_llm_integration_example():
    """Example of how to use the API with LLMs"""
    print("\n🤖 LLM Integration Example")
    print("=" * 40)
    
    base_url = "http://localhost:8001"
    
    # Get tool definitions
    try:
        response = requests.get(f"{base_url}/tools")
        if response.status_code == 200:
            tools = response.json()["tools"]
            print("✅ Tool definitions retrieved successfully")
            print(f"   Available functions: {len(tools)}")
            
            # Example of how to use with OpenAI
            print("\n📝 Example OpenAI integration:")
            print("```python")
            print("import openai")
            print("import requests")
            print()
            print("# Get tool definitions")
            print("tools_response = requests.get('http://localhost:8001/tools')")
            print("tools = tools_response.json()['tools']")
            print()
            print("# Use with OpenAI")
            print("client = openai.OpenAI(api_key='your_key')")
            print("response = client.chat.completions.create(")
            print("    model='gpt-4',")
            print("    messages=[{'role': 'user', 'content': 'Analyze Apple stock'}],")
            print("    tools=tools,")
            print("    tool_choice='auto'")
            print(")")
            print("```")
        else:
            print("❌ Failed to get tool definitions")
    except Exception as e:
        print(f"❌ LLM integration test error: {e}")

def main():
    """Main test function"""
    print("🚀 Starting Unified Application Tests")
    print("Make sure the API is running on http://localhost:8001")
    print("Run: python -m uvicorn unified_app:app --host 0.0.0.0 --port 8001")
    print()
    
    # Wait a moment for user to read
    time.sleep(2)
    
    # Run tests
    test_api_endpoints()
    test_multiple_symbols()
    test_llm_integration_example()
    
    print("\n" + "=" * 60)
    print("✅ All tests completed!")
    print("\n🎯 Next steps:")
    print("1. Start the web interface: python unified_app.py --mode web")
    print("2. Visit http://localhost:7860 for the Gradio UI")
    print("3. Check API docs at http://localhost:8001/docs")
    print("4. Use the LLM tools for AI integration")

if __name__ == "__main__":
    main() 