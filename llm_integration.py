# ==============================================================================
# FILE: llm_integration.py
#
# PURPOSE: Demonstrates how to get the tool/function definitions from the
#          running enrichmcp API to provide to an LLM.
#
# USAGE: Run `python llm_integration.py` in a separate terminal *after* the
#        uvicorn server is running.
# ==============================================================================
import requests
import json

def get_llm_tool_definition():
    """
    Fetches the GraphQL schema from the running app and formats it
    as a tool definition for an LLM.
    """
    # The enrichmcp app exposes its tool definitions at this endpoint
    tools_url = "http://127.0.0.1:8001/tools"

    print(f"Attempting to fetch tool definitions from {tools_url}...")

    try:
        # Fetch the tool definitions
        response = requests.get(tools_url)
        response.raise_for_status()  # Raise an exception for bad status codes
        
        tools = response.json()

        print("\n--- LLM Tool/Function Definition ---")
        print("This JSON would be passed to your LLM agent (e.g., OpenAI, Gemini, LangChain).")
        print("It tells the LLM what functions it can call and what parameters they take.")
        print(json.dumps(tools, indent=2))
        
        print("\n--- Example LLM Interaction ---")
        print("You could now ask an LLM a question like:")
        print("'What was the tesla_price and apple_price on 2024-02-02?'")
        print("\nThe LLM would see from the definition that it has a tool `stockDatas` that can filter by date.")
        print("It would then construct and execute a GraphQL query to your API to get the answer.")
        
    except requests.exceptions.RequestException as e:
        print(f"\nError: Could not connect to the server at {tools_url}.")
        print("Please ensure the uvicorn server is running (`python -m uvicorn app:app --reload --port 8001`).")
        print(f"Details: {e}")

def test_api_endpoints():
    """Test the API endpoints to ensure they're working correctly."""
    base_url = "http://127.0.0.1:8001"
    
    print("\n--- Testing API Endpoints ---")
    
    try:
        # Test the REST API endpoint
        print("Testing REST API endpoint...")
        response = requests.get(f"{base_url}/api/stock-datas?limit=3")
        response.raise_for_status()
        
        result = response.json()
        print("✅ REST API endpoint working")
        print(f"Retrieved {len(result.get('data', []))} records")
        
        # Test the latest prices endpoint
        print("\nTesting latest prices endpoint...")
        response = requests.get(f"{base_url}/api/latest-prices")
        response.raise_for_status()
        
        result = response.json()
        print("✅ Latest prices endpoint working")
        print(f"Latest date: {result.get('date', 'N/A')}")
        print(f"Bitcoin price: ${result.get('bitcoin_price', 'N/A')}")
        print(f"Apple price: ${result.get('apple_price', 'N/A')}")
        
        # Test the market overview endpoint
        print("\nTesting market overview endpoint...")
        response = requests.get(f"{base_url}/api/market-overview")
        response.raise_for_status()
        
        result = response.json()
        print("✅ Market overview endpoint working")
        print(f"Latest date: {result.get('latest_date', 'N/A')}")
        print(f"Available instruments: {len(result.get('available_instruments', []))}")
        
    except requests.exceptions.RequestException as e:
        print(f"❌ API test failed: {e}")
        print("Make sure the server is running with: python -m uvicorn app:app --reload --port 8001")

if __name__ == "__main__":
    get_llm_tool_definition()
    test_api_endpoints() 