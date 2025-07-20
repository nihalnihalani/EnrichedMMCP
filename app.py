# ==============================================================================
# FILE: app.py
#
# PURPOSE: Simplified unified application combining stock market API with 
#          basic research tools and a clean Gradio interface.
#
# USAGE: Run `python app.py` to start both API and web interface
# ==============================================================================

import gradio as gr
import requests
import json
import os
import asyncio
from datetime import datetime
from typing import Dict, List, Any, Optional
from dotenv import load_dotenv
import sqlalchemy as sa
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from fastapi import FastAPI, Depends, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import threading

# Import research tools
try:
    from MCP.consilium_mcp.research_tools import EnhancedResearchAgent
    RESEARCH_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Research tools not available: {e}")
    RESEARCH_AVAILABLE = False

# Load environment variables
load_dotenv()

# ==============================================================================
# DATABASE SETUP
# ==============================================================================

DATABASE_URL = "sqlite+aiosqlite:///stock_market.db"
engine = create_async_engine(DATABASE_URL, echo=False)
async_session_factory = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
Base = declarative_base()

def create_stock_orm_model():
    """Creates the SQLAlchemy ORM model for stock data."""
    class StockData(Base):
        __tablename__ = 'stock_data'
        
        id = sa.Column(sa.Integer, primary_key=True)
        date = sa.Column(sa.DateTime)
        natural_gas_price = sa.Column(sa.Float)
        natural_gas_vol = sa.Column(sa.Float)
        crude_oil_price = sa.Column(sa.Float)
        crude_oil_vol = sa.Column(sa.Float)
        copper_price = sa.Column(sa.Float)
        copper_vol = sa.Column(sa.Float)
        bitcoin_price = sa.Column(sa.Float)
        bitcoin_vol = sa.Column(sa.Float)
        platinum_price = sa.Column(sa.Float)
        platinum_vol = sa.Column(sa.Float)
        ethereum_price = sa.Column(sa.Float)
        ethereum_vol = sa.Column(sa.Float)
        s_p_500_price = sa.Column(sa.Float)
        nasdaq_100_price = sa.Column(sa.Float)
        nasdaq_100_vol = sa.Column(sa.Float)
        apple_price = sa.Column(sa.Float)
        apple_vol = sa.Column(sa.Float)
        tesla_price = sa.Column(sa.Float)
        tesla_vol = sa.Column(sa.Float)
        microsoft_price = sa.Column(sa.Float)
        microsoft_vol = sa.Column(sa.Float)
        silver_price = sa.Column(sa.Float)
        silver_vol = sa.Column(sa.Float)
        google_price = sa.Column(sa.Float)
        google_vol = sa.Column(sa.Float)
        nvidia_price = sa.Column(sa.Float)
        nvidia_vol = sa.Column(sa.Float)
        berkshire_price = sa.Column(sa.Integer)
        berkshire_vol = sa.Column(sa.Float)
        netflix_price = sa.Column(sa.Float)
        netflix_vol = sa.Column(sa.Float)
        amazon_price = sa.Column(sa.Float)
        amazon_vol = sa.Column(sa.Float)
        meta_price = sa.Column(sa.Float)
        meta_vol = sa.Column(sa.Float)
        gold_price = sa.Column(sa.Float)
        gold_vol = sa.Column(sa.Float)
    
    return StockData

StockData = create_stock_orm_model()

# ==============================================================================
# FASTAPI APP
# ==============================================================================

app = FastAPI(
    title="Stock Market Analysis",
    description="Simple stock market data API with research tools",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

async def get_session() -> AsyncSession:
    async with async_session_factory() as session:
        yield session

@app.get("/")
async def root():
    return {
        "message": "Stock Market Analysis API",
        "endpoints": {
            "latest_prices": "/api/latest-prices",
            "market_overview": "/api/market-overview",
            "stock_data": "/api/stock-datas",
            "historical": "/api/historical-analysis?symbol=AAPL&days=30",
            "tools": "/tools"
        }
    }

@app.get("/api/latest-prices")
async def get_latest_prices(session: AsyncSession = Depends(get_session)):
    """Get latest stock prices"""
    result = await session.execute(
        sa.select(StockData).order_by(StockData.date.desc()).limit(1)
    )
    record = result.scalar_one_or_none()
    
    if not record:
        raise HTTPException(status_code=404, detail="No data available")
    
    return {
        "date": record.date.isoformat() if record.date else None,
        "prices": {
            "bitcoin": record.bitcoin_price,
            "ethereum": record.ethereum_price,
            "apple": record.apple_price,
            "tesla": record.tesla_price,
            "microsoft": record.microsoft_price,
            "google": record.google_price,
            "nvidia": record.nvidia_price,
            "netflix": record.netflix_price,
            "amazon": record.amazon_price,
            "meta": record.meta_price,
            "gold": record.gold_price,
            "silver": record.silver_price,
            "crude_oil": record.crude_oil_price,
            "sp_500": record.s_p_500_price,
            "nasdaq": record.nasdaq_100_price
        }
    }

@app.get("/api/market-overview")
async def get_market_overview(session: AsyncSession = Depends(get_session)):
    """Get market overview"""
    result = await session.execute(
        sa.select(StockData).order_by(StockData.date.desc()).limit(1)
    )
    latest = result.scalar_one_or_none()
    
    if not latest:
        raise HTTPException(status_code=404, detail="No data available")
    
    return {
        "latest_date": latest.date.isoformat() if latest.date else None,
        "available_instruments": [
            "bitcoin", "ethereum", "apple", "tesla", "microsoft", 
            "google", "nvidia", "netflix", "amazon", "meta",
            "gold", "silver", "platinum", "copper", "crude_oil", 
            "natural_gas", "sp_500", "nasdaq_100", "berkshire"
        ]
    }

@app.get("/api/stock-datas")
async def get_stock_datas(
    limit: int = 100,
    offset: int = 0,
    session: AsyncSession = Depends(get_session)
):
    """Get stock data with pagination"""
    query = sa.select(StockData).limit(limit).offset(offset)
    result = await session.execute(query)
    records = result.scalars().all()
    
    data = []
    for record in records:
        record_dict = {}
        for column in StockData.__table__.columns:
            value = getattr(record, column.name)
            if isinstance(value, datetime):
                value = value.isoformat()
            record_dict[column.name] = value
        data.append(record_dict)
    
    return {"data": data, "total": len(data)}

@app.get("/api/historical-analysis")
async def get_historical_analysis(
    symbol: str,
    days: int = 30,
    session: AsyncSession = Depends(get_session)
):
    """Get historical analysis for a symbol"""
    # Map symbol to column name
    symbol_map = {
        "AAPL": "apple_price",
        "TSLA": "tesla_price", 
        "MSFT": "microsoft_price",
        "GOOGL": "google_price",
        "NVDA": "nvidia_price",
        "NFLX": "netflix_price",
        "AMZN": "amazon_price",
        "META": "meta_price",
        "BTC": "bitcoin_price",
        "ETH": "ethereum_price",
        "GOLD": "gold_price",
        "SILVER": "silver_price",
        "OIL": "crude_oil_price",
        "SP500": "s_p_500_price",
        "NASDAQ": "nasdaq_100_price"
    }
    
    column_name = symbol_map.get(symbol.upper())
    if not column_name:
        raise HTTPException(status_code=400, detail=f"Symbol {symbol} not supported")
    
    # Get historical data
    result = await session.execute(
        sa.select(StockData).order_by(StockData.date.desc()).limit(days)
    )
    records = result.scalars().all()
    
    if not records:
        raise HTTPException(status_code=404, detail="No data available")
    
    # Extract prices
    prices = []
    dates = []
    for record in reversed(records):  # Oldest first
        price = getattr(record, column_name)
        if price is not None:
            prices.append(price)
            dates.append(record.date.isoformat() if record.date else None)
    
    if not prices:
        raise HTTPException(status_code=404, detail="No price data available")
    
    # Calculate basic statistics
    current_price = prices[-1]
    price_change = current_price - prices[0] if len(prices) > 1 else 0
    percent_change = (price_change / prices[0] * 100) if prices[0] != 0 else 0
    
    return {
        "symbol": symbol.upper(),
        "current_price": current_price,
        "price_change": price_change,
        "percent_change": round(percent_change, 2),
        "data_points": len(prices),
        "prices": prices,
        "dates": dates
    }

@app.get("/tools")
async def get_tools():
    """Get available tools for LLM integration"""
    return {
        "tools": [
            {
                "type": "function",
                "function": {
                    "name": "get_latest_prices",
                    "description": "Get latest stock market prices",
                    "parameters": {"type": "object", "properties": {}}
                }
            },
            {
                "type": "function", 
                "function": {
                    "name": "get_market_overview",
                    "description": "Get market overview and available instruments",
                    "parameters": {"type": "object", "properties": {}}
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "get_historical_analysis",
                    "description": "Get historical price analysis for a symbol",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "symbol": {
                                "type": "string",
                                "description": "Stock symbol (e.g., AAPL, TSLA, BTC)"
                            },
                            "days": {
                                "type": "integer",
                                "description": "Number of days to analyze (default: 30)"
                            }
                        },
                        "required": ["symbol"]
                    }
                }
            }
        ]
    }

# ==============================================================================
# GRADIO INTERFACE
# ==============================================================================

def create_simple_interface():
    """Create a simplified Gradio interface"""
    
    def get_latest_prices_ui():
        """Get latest prices from API"""
        try:
            response = requests.get("http://localhost:8001/api/latest-prices")
            if response.status_code == 200:
                data = response.json()
                prices = data.get("prices", {})
                
                result = f"**Latest Prices ({data.get('date', 'N/A')})**\n\n"
                for symbol, price in prices.items():
                    if price is not None:
                        result += f"• {symbol.upper()}: ${price:,.2f}\n"
                return result
            else:
                return f"Error: {response.status_code}"
        except Exception as e:
            return f"Error: {str(e)}"
    
    def analyze_symbol_ui(symbol, days):
        """Analyze a specific symbol"""
        if not symbol:
            return "Please enter a symbol"
        
        try:
            response = requests.get(f"http://localhost:8001/api/historical-analysis?symbol={symbol}&days={days}")
            if response.status_code == 200:
                data = response.json()
                
                result = f"**{data['symbol']} Analysis ({days} days)**\n\n"
                result += f"• Current Price: ${data['current_price']:,.2f}\n"
                result += f"• Price Change: ${data['price_change']:,.2f}\n"
                result += f"• Percent Change: {data['percent_change']}%\n"
                result += f"• Data Points: {data['data_points']}\n"
                
                return result
            else:
                return f"Error: {response.status_code} - {response.text}"
        except Exception as e:
            return f"Error: {str(e)}"
    
    def research_query_ui(query):
        """Research a query using available tools"""
        if not query:
            return "Please enter a research query"
        
        if not RESEARCH_AVAILABLE:
            return "Research tools not available"
        
        try:
            agent = EnhancedResearchAgent()
            result = agent.search(query, research_depth="quick")
            return f"**Research Results for: {query}**\n\n{result}"
        except Exception as e:
            return f"Research error: {str(e)}"
    
    def get_market_overview_ui():
        """Get market overview"""
        try:
            response = requests.get("http://localhost:8001/api/market-overview")
            if response.status_code == 200:
                data = response.json()
                
                result = f"**Market Overview ({data.get('latest_date', 'N/A')})**\n\n"
                result += "**Available Instruments:**\n"
                instruments = data.get("available_instruments", [])
                for i, instrument in enumerate(instruments, 1):
                    result += f"{i}. {instrument.upper()}\n"
                
                return result
            else:
                return f"Error: {response.status_code}"
        except Exception as e:
            return f"Error: {str(e)}"
    
    # Create the interface
    with gr.Blocks(title="Stock Market Analysis", theme=gr.themes.Soft()) as interface:
        gr.Markdown("# 📈 Stock Market Analysis")
        gr.Markdown("Simple interface for stock market data and research")
        
        with gr.Tabs():
            # Prices Tab
            with gr.TabItem("💰 Prices"):
                gr.Markdown("### Latest Market Prices")
                prices_btn = gr.Button("Get Latest Prices", variant="primary")
                prices_output = gr.Textbox(label="Results", lines=10)
                prices_btn.click(get_latest_prices_ui, outputs=prices_output)
            
            # Analysis Tab
            with gr.TabItem("📊 Analysis"):
                gr.Markdown("### Symbol Analysis")
                with gr.Row():
                    symbol_input = gr.Textbox(label="Symbol", placeholder="AAPL, TSLA, BTC...")
                    days_input = gr.Slider(minimum=1, maximum=365, value=30, step=1, label="Days")
                analyze_btn = gr.Button("Analyze", variant="primary")
                analysis_output = gr.Textbox(label="Analysis Results", lines=10)
                analyze_btn.click(analyze_symbol_ui, inputs=[symbol_input, days_input], outputs=analysis_output)
            
            # Research Tab
            with gr.TabItem("🔍 Research"):
                gr.Markdown("### Market Research")
                research_input = gr.Textbox(label="Research Query", placeholder="What is the current state of AI stocks?")
                research_btn = gr.Button("Research", variant="primary")
                research_output = gr.Textbox(label="Research Results", lines=15)
                research_btn.click(research_query_ui, inputs=research_input, outputs=research_output)
            
            # Overview Tab
            with gr.TabItem("📋 Overview"):
                gr.Markdown("### Market Overview")
                overview_btn = gr.Button("Get Overview", variant="primary")
                overview_output = gr.Textbox(label="Market Overview", lines=10)
                overview_btn.click(get_market_overview_ui, outputs=overview_output)
        
        # Footer
        gr.Markdown("---")
        gr.Markdown("**API Endpoints:** `/api/latest-prices`, `/api/market-overview`, `/api/historical-analysis`, `/tools`")
    
    return interface

# ==============================================================================
# MAIN APPLICATION
# ==============================================================================

def start_api_server():
    """Start the FastAPI server in a separate thread"""
    uvicorn.run(app, host="0.0.0.0", port=8001, log_level="info")

def main():
    """Main function to start both API and Gradio interface"""
    print("🚀 Starting Stock Market Analysis Platform...")
    
    # Start API server in background
    api_thread = threading.Thread(target=start_api_server, daemon=True)
    api_thread.start()
    
    print("📖 API Documentation: http://localhost:8001/docs")
    print("🔧 API Root: http://localhost:8001/")
    
    # Wait a moment for API to start
    import time
    time.sleep(2)
    
    # Start Gradio interface
    print("🌐 Starting Web Interface...")
    interface = create_simple_interface()
    interface.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False,
        show_error=True
    )

if __name__ == "__main__":
    main() 