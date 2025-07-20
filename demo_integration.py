#!/usr/bin/env python3
"""
Demonstration script for Consilium MCP + Enrich MCP Integration
Shows how historical market data is integrated into expert consensus
"""
import requests
import json

def demo_enrich_mcp_api():
    """Demonstrate the Enrich MCP API capabilities"""
    print("🌐 Enrich MCP API Demonstration")
    print("=" * 50)
    
    base_url = "http://localhost:8001"
    
    # Demo 1: Get available functions
    print("\n📋 Available Functions:")
    response = requests.get(f"{base_url}/tools")
    tools = response.json()
    
    historical_functions = [f['function']['name'] for f in tools['tools'] 
                          if 'historical' in f['function']['name'] or 'market' in f['function']['name']]
    
    for func in historical_functions:
        print(f"  • {func}")
    
    # Demo 2: Market overview
    print("\n📊 Market Overview:")
    response = requests.get(f"{base_url}/api/market-overview")
    overview = response.json()
    
    latest_prices = overview['latest_prices']
    print(f"  Latest Date: {overview['latest_date']}")
    print(f"  Bitcoin: ${latest_prices['bitcoin']:,.2f}")
    print(f"  Ethereum: ${latest_prices['ethereum']:,.2f}")
    print(f"  Apple: ${latest_prices['apple']:,.2f}")
    print(f"  Tesla: ${latest_prices['tesla']:,.2f}")
    
    # Demo 3: Historical data
    print("\n📈 Historical Data Sample:")
    response = requests.get(f"{base_url}/api/stock-datas?limit=3")
    data = response.json()
    
    for record in data['data']:
        date = record['date'][:10]  # Just the date part
        print(f"  {date}: Bitcoin ${record['bitcoin_price']:,.2f}, Apple ${record['apple_price']:,.2f}")

def demo_consilium_integration():
    """Demonstrate how Consilium MCP would use the integration"""
    print("\n🎭 Consilium MCP Integration Demonstration")
    print("=" * 50)
    
    print("\n🔍 Example Expert Consensus Scenario:")
    print("Question: 'Should we invest in Bitcoin or Ethereum based on recent performance?'")
    
    print("\n📊 Step 1: Research Agent detects historical data need")
    print("  Query: 'bitcoin vs ethereum performance comparison'")
    print("  Detection: Historical keywords + instrument mentions")
    print("  Routing: EnrichMCPHistoricalDataTool")
    
    print("\n📈 Step 2: Historical data analysis")
    print("  Function: get_market_comparison")
    print("  Parameters: instruments=['bitcoin', 'ethereum'], timeframe='last 30 days'")
    print("  Analysis: Price performance, volatility, trends")
    
    print("\n🤖 Step 3: LLM function calling")
    print("  LLM receives function definitions")
    print("  LLM calls: get_historical_market_data(instrument='bitcoin', analysis_type='trend')")
    print("  Result: '📈 Bitcoin trend: Upward (+6.98%) with moderate volatility...'")
    
    print("\n💬 Step 4: Expert synthesis")
    print("  Lead Analyst: 'Based on historical data, Bitcoin shows stronger upward momentum...'")
    print("  Research Specialist: 'Ethereum has higher volatility but better long-term growth...'")
    print("  Strategic Advisor: 'Consider portfolio diversification given different risk profiles...'")
    
    print("\n🎯 Step 5: Consensus recommendation")
    print("  Final Answer: 'Recommend 60% Bitcoin, 40% Ethereum based on historical performance...'")

def demo_query_examples():
    """Show example queries that would trigger historical data integration"""
    print("\n🎯 Example Queries That Trigger Historical Data Integration")
    print("=" * 60)
    
    examples = [
        {
            "query": "What's the trend for Bitcoin over the last month?",
            "tool": "EnrichMCPHistoricalDataTool",
            "function": "get_historical_market_data",
            "analysis": "Trend analysis with price change and volatility"
        },
        {
            "query": "Compare Apple vs Tesla performance in 2024",
            "tool": "EnrichMCPHistoricalDataTool", 
            "function": "get_market_comparison",
            "analysis": "Relative performance, returns, risk comparison"
        },
        {
            "query": "How has the market performed overall recently?",
            "tool": "EnrichMCPHistoricalDataTool",
            "function": "get_market_overview_data", 
            "analysis": "Comprehensive market summary with latest prices"
        },
        {
            "query": "What's the volatility of Ethereum compared to traditional stocks?",
            "tool": "EnrichMCPHistoricalDataTool",
            "function": "get_market_comparison",
            "analysis": "Volatility analysis across asset classes"
        },
        {
            "query": "Should I invest in gold or silver based on historical trends?",
            "tool": "EnrichMCPHistoricalDataTool",
            "function": "get_market_comparison",
            "analysis": "Commodity performance and correlation analysis"
        }
    ]
    
    for i, example in enumerate(examples, 1):
        print(f"\n{i}. Query: '{example['query']}'")
        print(f"   Tool: {example['tool']}")
        print(f"   Function: {example['function']}")
        print(f"   Analysis: {example['analysis']}")

def demo_integration_benefits():
    """Demonstrate the benefits of the integration"""
    print("\n🚀 Integration Benefits")
    print("=" * 30)
    
    benefits = [
        "📊 Data-Driven Decisions: Expert consensus backed by historical market data",
        "🔍 Comprehensive Analysis: Combines real-time research with historical context", 
        "🎯 Smart Routing: Automatically detects when historical data is needed",
        "🤖 LLM Integration: Native function calling for seamless AI interaction",
        "👁️ Visual Feedback: Real-time progress indicators in the roundtable",
        "📈 Rich Analysis: Trend, volatility, performance, and comparison metrics",
        "🔄 Multi-Source: Historical data integrated with web, academic, and financial research",
        "⚡ Fast Access: Direct API calls to historical database"
    ]
    
    for benefit in benefits:
        print(f"  {benefit}")

def main():
    """Run the complete demonstration"""
    print("🎭 Consilium MCP + Enrich MCP Integration Demo")
    print("=" * 60)
    
    # Check if server is running
    try:
        response = requests.get("http://localhost:8001/", timeout=5)
        print("✅ Enrich MCP server is running")
    except:
        print("❌ Enrich MCP server is not running")
        print("Please start with: python -m uvicorn app:app --reload --port 8001")
        return
    
    # Run demonstrations
    demo_enrich_mcp_api()
    demo_consilium_integration()
    demo_query_examples()
    demo_integration_benefits()
    
    print("\n" + "=" * 60)
    print("🎉 Integration Demo Complete!")
    print("\n📝 Next Steps:")
    print("1. Test with real LLM function calling")
    print("2. Validate in Consilium MCP roundtable")
    print("3. Try complex queries combining historical + real-time data")
    print("4. Explore additional analysis types and visualizations")

if __name__ == "__main__":
    main() 