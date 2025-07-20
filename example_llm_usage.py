# ==============================================================================
# FILE: example_llm_usage.py
#
# PURPOSE: Demonstrates how to use the Stock Market Data API with LLMs
#          like OpenAI, Gemini, or LangChain.
#
# USAGE: Run `python example_llm_usage.py` to see example interactions.
# ==============================================================================
import requests
import json
from typing import Dict, Any

class StockMarketLLMClient:
    """Client for integrating stock market data with LLMs."""
    
    def __init__(self, base_url: str = "http://127.0.0.1:8001"):
        self.base_url = base_url
        self.tools = self._get_tools()
    
    def _get_tools(self) -> Dict[str, Any]:
        """Fetch tool definitions from the API."""
        response = requests.get(f"{self.base_url}/tools")
        response.raise_for_status()
        return response.json()
    
    def get_tool_definitions(self) -> Dict[str, Any]:
        """Get tool definitions for LLM integration."""
        return self.tools
    
    def execute_function_call(self, function_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a function call and return the result."""
        if function_name == "get_stock_data":
            params = {}
            if "limit" in arguments:
                params["limit"] = arguments["limit"]
            if "offset" in arguments:
                params["offset"] = arguments["offset"]
            if "date_eq" in arguments:
                params["date_eq"] = arguments["date_eq"]
            if "date_gte" in arguments:
                params["date_gte"] = arguments["date_gte"]
            if "date_lte" in arguments:
                params["date_lte"] = arguments["date_lte"]
            
            response = requests.get(f"{self.base_url}/api/stock-datas", params=params)
            response.raise_for_status()
            return response.json()
            
        elif function_name == "get_latest_prices":
            response = requests.get(f"{self.base_url}/api/latest-prices")
            response.raise_for_status()
            return response.json()
            
        elif function_name == "get_stock_data_by_id":
            record_id = arguments["record_id"]
            response = requests.get(f"{self.base_url}/api/stock-datas/{record_id}")
            response.raise_for_status()
            return response.json()
            
        elif function_name == "get_market_overview":
            response = requests.get(f"{self.base_url}/api/market-overview")
            response.raise_for_status()
            return response.json()
        
        else:
            raise ValueError(f"Unknown function: {function_name}")
    
    def format_response_for_llm(self, function_name: str, result: Dict[str, Any]) -> str:
        """Format the API response into a human-readable format for the LLM."""
        if function_name == "get_stock_data":
            data = result.get("data", [])
            if not data:
                return "No stock data found for the specified criteria."
            
            formatted = f"Found {len(data)} records:\n\n"
            for record in data[:5]:  # Show first 5 records
                date = record.get("date", "Unknown")
                formatted += f"Date: {date}\n"
                formatted += f"  Bitcoin: ${record.get('bitcoin_price', 'N/A')}\n"
                formatted += f"  Apple: ${record.get('apple_price', 'N/A')}\n"
                formatted += f"  Tesla: ${record.get('tesla_price', 'N/A')}\n"
                formatted += f"  Gold: ${record.get('gold_price', 'N/A')}\n"
                formatted += f"  S&P 500: ${record.get('s_p_500_price', 'N/A')}\n\n"
            
            if len(data) > 5:
                formatted += f"... and {len(data) - 5} more records."
            
            return formatted
            
        elif function_name == "get_latest_prices":
            date = result.get("date", "Unknown")
            formatted = f"Latest stock prices as of {date}:\n\n"
            formatted += f"Bitcoin: ${result.get('bitcoin_price', 'N/A')}\n"
            formatted += f"Ethereum: ${result.get('ethereum_price', 'N/A')}\n"
            formatted += f"Apple: ${result.get('apple_price', 'N/A')}\n"
            formatted += f"Tesla: ${result.get('tesla_price', 'N/A')}\n"
            formatted += f"Microsoft: ${result.get('microsoft_price', 'N/A')}\n"
            formatted += f"Google: ${result.get('google_price', 'N/A')}\n"
            formatted += f"Nvidia: ${result.get('nvidia_price', 'N/A')}\n"
            formatted += f"Gold: ${result.get('gold_price', 'N/A')}\n"
            formatted += f"Silver: ${result.get('silver_price', 'N/A')}\n"
            formatted += f"Crude Oil: ${result.get('crude_oil_price', 'N/A')}\n"
            formatted += f"S&P 500: ${result.get('s_p_500_price', 'N/A')}\n"
            formatted += f"Nasdaq 100: ${result.get('nasdaq_100_price', 'N/A')}\n"
            
            return formatted
            
        elif function_name == "get_stock_data_by_id":
            date = result.get("date", "Unknown")
            formatted = f"Stock data for record ID {result.get('id', 'Unknown')} (Date: {date}):\n\n"
            formatted += f"Bitcoin: ${result.get('bitcoin_price', 'N/A')}\n"
            formatted += f"Apple: ${result.get('apple_price', 'N/A')}\n"
            formatted += f"Tesla: ${result.get('tesla_price', 'N/A')}\n"
            formatted += f"Gold: ${result.get('gold_price', 'N/A')}\n"
            formatted += f"S&P 500: ${result.get('s_p_500_price', 'N/A')}\n"
            
            return formatted
            
        elif function_name == "get_market_overview":
            latest_date = result.get("latest_date", "Unknown")
            latest_prices = result.get("latest_prices", {})
            instruments = result.get("available_instruments", [])
            
            formatted = f"Market Overview as of {latest_date}:\n\n"
            formatted += "Latest Prices:\n"
            for instrument, price in latest_prices.items():
                if price is not None:
                    formatted += f"  {instrument.title()}: ${price}\n"
            
            formatted += f"\nAvailable Instruments ({len(instruments)}):\n"
            formatted += ", ".join(instruments)
            
            return formatted
        
        else:
            return f"Function {function_name} returned: {json.dumps(result, indent=2)}"

def simulate_llm_interaction():
    """Simulate how an LLM would interact with the API."""
    client = StockMarketLLMClient()
    
    print("=== Stock Market Data API - LLM Integration Example ===\n")
    
    # Example 1: Get latest prices
    print("1. LLM Request: 'What are the latest stock prices?'")
    print("LLM would call: get_latest_prices()")
    result = client.execute_function_call("get_latest_prices", {})
    response = client.format_response_for_llm("get_latest_prices", result)
    print("Response:")
    print(response)
    print("\n" + "="*60 + "\n")
    
    # Example 2: Get data for a specific date
    print("2. LLM Request: 'What were the stock prices on 2024-02-02?'")
    print("LLM would call: get_stock_data(date_eq='2024-02-02')")
    result = client.execute_function_call("get_stock_data", {"date_eq": "2024-02-02"})
    response = client.format_response_for_llm("get_stock_data", result)
    print("Response:")
    print(response)
    print("\n" + "="*60 + "\n")
    
    # Example 3: Get market overview
    print("3. LLM Request: 'Give me a market overview'")
    print("LLM would call: get_market_overview()")
    result = client.execute_function_call("get_market_overview", {})
    response = client.format_response_for_llm("get_market_overview", result)
    print("Response:")
    print(response)
    print("\n" + "="*60 + "\n")
    
    # Example 4: Get data for a date range
    print("4. LLM Request: 'Show me stock data from January 2024'")
    print("LLM would call: get_stock_data(date_gte='2024-01-01', date_lte='2024-01-31', limit=5)")
    result = client.execute_function_call("get_stock_data", {
        "date_gte": "2024-01-01",
        "date_lte": "2024-01-31",
        "limit": 5
    })
    response = client.format_response_for_llm("get_stock_data", result)
    print("Response:")
    print(response)
    print("\n" + "="*60 + "\n")
    
    # Show tool definitions
    print("5. Tool Definitions for LLM:")
    print("These would be passed to the LLM to tell it what functions are available:")
    print(json.dumps(client.get_tool_definitions(), indent=2))

if __name__ == "__main__":
    simulate_llm_interaction() 