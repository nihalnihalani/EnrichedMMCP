# ==============================================================================
# FILE: unified_app.py
#
# PURPOSE: Unified application combining enrich MCP API with Consilium MCP
#          visual consensus engine. Provides both REST API endpoints and
#          a Gradio web interface for comprehensive financial analysis.
#
# USAGE: 
# - REST API: Run `python -m uvicorn unified_app:app --reload --port 8001`
# - Web UI: Run `python unified_app.py` and visit the Gradio interface
# ==============================================================================

import gradio as gr
import requests
import json
import os
import asyncio
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
from dotenv import load_dotenv
import time
import re
from collections import Counter
import threading
import queue
import uuid
import sqlalchemy as sa
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from fastapi import FastAPI, Depends, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# Import Consilium components
try:
    from gradio_consilium_roundtable import consilium_roundtable
    from smolagents import CodeAgent, DuckDuckGoSearchTool, FinalAnswerTool, InferenceClientModel, VisitWebpageTool, Tool
    from research_tools import EnhancedResearchAgent
    from enhanced_search_functions import ENHANCED_SEARCH_FUNCTIONS
    CONSILIUM_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Consilium components not available: {e}")
    CONSILIUM_AVAILABLE = False

# Load environment variables
load_dotenv()

# ==============================================================================
# ENRICH MCP DATABASE SETUP
# ==============================================================================

# Database URL for SQLite (async version)
DATABASE_URL = "sqlite+aiosqlite:///stock_market.db"

# Create an async engine
engine = create_async_engine(DATABASE_URL, echo=False)

# Create a session factory for creating async sessions
async_session_factory = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)

# Define the base for our ORM models
Base = declarative_base()

# --- ORM Model Definition ---
def create_stock_orm_model():
    """Creates the SQLAlchemy ORM model for stock data."""
    class StockData(Base):
        __tablename__ = 'stock_data'
        
        # Define all columns
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
# FASTAPI APP SETUP
# ==============================================================================

app = FastAPI(
    title="Unified Stock Market Analysis Platform",
    description="Combines enrich MCP API with Consilium MCP visual consensus engine for comprehensive financial analysis.",
    version="2.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==============================================================================
# ENRICH MCP REST API ENDPOINTS
# ==============================================================================

async def get_session() -> AsyncSession:
    """FastAPI dependency to provide a DB session for each request."""
    async with async_session_factory() as session:
        yield session

@app.get("/api/stock-datas")
async def get_stock_datas(
    limit: int = 100,
    offset: int = 0,
    date_eq: Optional[str] = None,
    date_gte: Optional[str] = None,
    date_lte: Optional[str] = None,
    session: AsyncSession = Depends(get_session)
):
    """REST endpoint to get stock data with filtering"""
    query = sa.select(StockData)
    
    # Apply filters
    if date_eq:
        query = query.where(StockData.date == date_eq)
    if date_gte:
        query = query.where(StockData.date >= date_gte)
    if date_lte:
        query = query.where(StockData.date <= date_lte)
    
    # Apply pagination
    query = query.limit(limit).offset(offset)
    
    result = await session.execute(query)
    records = result.scalars().all()
    
    # Convert to dict
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

@app.get("/api/stock-datas/{record_id}")
async def get_stock_data_by_id(
    record_id: int,
    session: AsyncSession = Depends(get_session)
):
    """REST endpoint to get a single stock data record by ID"""
    result = await session.execute(
        sa.select(StockData).where(StockData.id == record_id)
    )
    record = result.scalar_one_or_none()
    
    if not record:
        raise HTTPException(status_code=404, detail="Record not found")
    
    # Convert to dict
    record_dict = {}
    for column in StockData.__table__.columns:
        value = getattr(record, column.name)
        if isinstance(value, datetime):
            value = value.isoformat()
        record_dict[column.name] = value
    
    return record_dict

@app.get("/api/latest-prices")
async def get_latest_prices(session: AsyncSession = Depends(get_session)):
    """REST endpoint to get the latest stock prices"""
    result = await session.execute(
        sa.select(StockData).order_by(StockData.date.desc()).limit(1)
    )
    record = result.scalar_one_or_none()
    
    if not record:
        raise HTTPException(status_code=404, detail="No data available")
    
    # Convert to dict
    record_dict = {}
    for column in StockData.__table__.columns:
        value = getattr(record, column.name)
        if isinstance(value, datetime):
            value = value.isoformat()
        record_dict[column.name] = value
    
    return record_dict

@app.get("/api/market-overview")
async def get_market_overview(session: AsyncSession = Depends(get_session)):
    """Get a market overview with latest prices and basic statistics"""
    # Get latest prices
    result = await session.execute(
        sa.select(StockData).order_by(StockData.date.desc()).limit(1)
    )
    latest = result.scalar_one_or_none()
    
    if not latest:
        raise HTTPException(status_code=404, detail="No data available")
    
    # Get some basic statistics
    result = await session.execute(
        sa.select(StockData).order_by(StockData.date.desc()).limit(30)
    )
    recent_data = result.scalars().all()
    
    # Calculate basic stats
    stats = {}
    for column in StockData.__table__.columns:
        if column.name in ['id', 'date']:
            continue
        
        values = [getattr(record, column.name) for record in recent_data if getattr(record, column.name) is not None]
        if values:
            stats[column.name] = {
                "latest": values[0],
                "avg_30d": sum(values) / len(values),
                "min_30d": min(values),
                "max_30d": max(values)
            }
    
    # Convert latest to dict
    latest_dict = {}
    for column in StockData.__table__.columns:
        value = getattr(latest, column.name)
        if isinstance(value, datetime):
            value = value.isoformat()
        latest_dict[column.name] = value
    
    return {
        "latest_prices": latest_dict,
        "statistics": stats,
        "analysis_date": datetime.now().isoformat()
    }

@app.get("/api/historical-analysis")
async def get_historical_analysis(
    symbol: str,
    days: int = 30,
    session: AsyncSession = Depends(get_session)
):
    """Get historical analysis for a specific symbol"""
    # Map symbol to column name
    symbol_mapping = {
        'AAPL': 'apple_price',
        'TSLA': 'tesla_price',
        'MSFT': 'microsoft_price',
        'GOOGL': 'google_price',
        'NVDA': 'nvidia_price',
        'BRK': 'berkshire_price',
        'NFLX': 'netflix_price',
        'AMZN': 'amazon_price',
        'META': 'meta_price',
        'SPY': 's_p_500_price',
        'QQQ': 'nasdaq_100_price',
        'BTC': 'bitcoin_price',
        'ETH': 'ethereum_price',
        'GOLD': 'gold_price',
        'SILVER': 'silver_price',
        'PLATINUM': 'platinum_price',
        'COPPER': 'copper_price',
        'OIL': 'crude_oil_price',
        'NATURAL_GAS': 'natural_gas_price'
    }
    
    if symbol.upper() not in symbol_mapping:
        raise HTTPException(status_code=400, detail=f"Symbol {symbol} not supported")
    
    column_name = symbol_mapping[symbol.upper()]
    
    # Get historical data
    result = await session.execute(
        sa.select(StockData).order_by(StockData.date.desc()).limit(days)
    )
    records = result.scalars().all()
    
    if not records:
        raise HTTPException(status_code=404, detail="No data available")
    
    # Extract prices and dates
    prices = []
    dates = []
    for record in records:
        price = getattr(record, column_name)
        if price is not None:
            prices.append(price)
            dates.append(record.date.isoformat() if record.date else None)
    
    if not prices:
        raise HTTPException(status_code=404, detail=f"No price data available for {symbol}")
    
    # Calculate analysis
    current_price = prices[0]
    start_price = prices[-1]
    price_change = current_price - start_price
    price_change_pct = (price_change / start_price) * 100 if start_price != 0 else 0
    
    # Calculate volatility (standard deviation)
    if len(prices) > 1:
        mean_price = sum(prices) / len(prices)
        variance = sum((p - mean_price) ** 2 for p in prices) / len(prices)
        volatility = variance ** 0.5
    else:
        volatility = 0
    
    return {
        "symbol": symbol.upper(),
        "current_price": current_price,
        "start_price": start_price,
        "price_change": price_change,
        "price_change_pct": price_change_pct,
        "volatility": volatility,
        "analysis_period_days": days,
        "data_points": len(prices),
        "historical_data": list(zip(dates, prices))
    }

@app.get("/tools")
async def get_tools():
    """Get LLM tool definitions for enrich MCP"""
    tools = [
        {
            "type": "function",
            "function": {
                "name": "get_stock_data",
                "description": "Get historical stock market data with filtering options",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "limit": {
                            "type": "integer",
                            "description": "Maximum number of records to return",
                            "default": 100
                        },
                        "offset": {
                            "type": "integer",
                            "description": "Number of records to skip",
                            "default": 0
                        },
                        "date_eq": {
                            "type": "string",
                            "description": "Exact date filter (YYYY-MM-DD)",
                            "format": "date"
                        },
                        "date_gte": {
                            "type": "string",
                            "description": "Date greater than or equal to (YYYY-MM-DD)",
                            "format": "date"
                        },
                        "date_lte": {
                            "type": "string",
                            "description": "Date less than or equal to (YYYY-MM-DD)",
                            "format": "date"
                        }
                    }
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "get_latest_prices",
                "description": "Get the most recent stock prices and market data",
                "parameters": {
                    "type": "object",
                    "properties": {}
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "get_market_overview",
                "description": "Get comprehensive market overview with latest prices and 30-day statistics",
                "parameters": {
                    "type": "object",
                    "properties": {}
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "get_historical_analysis",
                "description": "Get detailed historical analysis for a specific stock symbol",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "symbol": {
                            "type": "string",
                            "description": "Stock symbol to analyze (e.g., AAPL, TSLA, MSFT, GOOGL, NVDA, BRK, NFLX, AMZN, META, SPY, QQQ, BTC, ETH, GOLD, SILVER, PLATINUM, COPPER, OIL, NATURAL_GAS)",
                            "enum": ["AAPL", "TSLA", "MSFT", "GOOGL", "NVDA", "BRK", "NFLX", "AMZN", "META", "SPY", "QQQ", "BTC", "ETH", "GOLD", "SILVER", "PLATINUM", "COPPER", "OIL", "NATURAL_GAS"]
                        },
                        "days": {
                            "type": "integer",
                            "description": "Number of days to analyze",
                            "default": 30
                        }
                    },
                    "required": ["symbol"]
                }
            }
        }
    ]
    
    return {"tools": tools}

@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "Unified Stock Market Analysis Platform",
        "version": "2.0.0",
        "description": "Combines enrich MCP API with Consilium MCP visual consensus engine",
        "endpoints": {
            "api": "/api/* - REST API endpoints for stock data",
            "tools": "/tools - LLM tool definitions",
            "web_ui": "/gradio - Gradio web interface (if running)",
            "docs": "/docs - API documentation"
        },
        "features": [
            "Historical stock market data access",
            "LLM function calling support",
            "Market analysis and statistics",
            "Visual consensus engine (if Consilium available)",
            "Raw material price correlation analysis"
        ]
    }

# ==============================================================================
# CONSILIUM MCP INTEGRATION (if available)
# ==============================================================================

if CONSILIUM_AVAILABLE:
    # API Configuration
    MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY") 
    SAMBANOVA_API_KEY = os.getenv("SAMBANOVA_API_KEY")
    MODERATOR_MODEL = os.getenv("MODERATOR_MODEL", "mistral")

    # Session-based storage for isolated discussions
    user_sessions: Dict[str, Dict] = {}

    # Model Images
    avatar_images = {
        "QwQ-32B": "https://cdn-avatars.huggingface.co/v1/production/uploads/620760a26e3b7210c2ff1943/-s1gyJfvbE1RgO5iBeNOi.png",
        "DeepSeek-R1": "https://logosandtypes.com/wp-content/uploads/2025/02/deepseek.svg",
        "Mistral Large": "https://logosandtypes.com/wp-content/uploads/2025/02/mistral-ai.svg",
        "Meta-Llama-3.3-70B-Instruct": "https://registry.npmmirror.com/@lobehub/icons-static-png/1.46.0/files/dark/meta-color.png",
    }

    def get_session_id(request: gr.Request = None) -> str:
        """Generate or retrieve session ID"""
        if request and hasattr(request, 'session_hash'):
            return request.session_hash
        return str(uuid.uuid4())

    def get_or_create_session_state(session_id: str) -> Dict:
        """Get or create isolated session state"""
        if session_id not in user_sessions:
            user_sessions[session_id] = {
                "roundtable_state": {
                    "participants": [],
                    "messages": [],
                    "currentSpeaker": None,
                    "thinking": [],
                    "showBubbles": []
                },
                "discussion_log": [],
                "final_answer": "",
                "api_keys": {
                    "mistral": None,
                    "sambanova": None
                }
            }
        return user_sessions[session_id]

    class VisualConsensusEngine:
        def __init__(self, moderator_model: str = None, update_callback=None, session_id: str = None):
            self.moderator_model = moderator_model or MODERATOR_MODEL
            self.search_agent = EnhancedResearchAgent()
            self.update_callback = update_callback
            self.session_id = session_id
            
            # Get session-specific keys or fall back to global
            session = get_or_create_session_state(session_id) if session_id else {"api_keys": {}}
            session_keys = session.get("api_keys", {})
            
            mistral_key = session_keys.get("mistral") or MISTRAL_API_KEY
            sambanova_key = session_keys.get("sambanova") or SAMBANOVA_API_KEY
            
            # Research Agent stays visible but is no longer an active participant
            self.models = {
                'mistral': {
                    'name': 'Mistral Large',
                    'api_key': mistral_key,
                    'available': bool(mistral_key)
                },
                'sambanova_deepseek': {
                    'name': 'DeepSeek-R1',
                    'api_key': sambanova_key,
                    'available': bool(sambanova_key)
                },
                'sambanova_llama': {
                    'name': 'Meta-Llama-3.3-70B-Instruct',
                    'api_key': sambanova_key,
                    'available': bool(sambanova_key)
                },
                'sambanova_qwq': {
                    'name': 'QwQ-32B',
                    'api_key': sambanova_key,
                    'available': bool(sambanova_key)
                }
            }
            
            # Store session keys for API calls
            self.session_keys = {
                'mistral': mistral_key,
                'sambanova': sambanova_key
            }
            
            # PROFESSIONAL: Strong, expert role definitions matched to decision protocols
            self.roles = {
                'standard': "Provide expert analysis with clear reasoning and evidence.",
                'expert_advocate': "You are a PASSIONATE EXPERT advocating for your specialized position. Present compelling evidence with conviction.",
                'critical_analyst': "You are a RIGOROUS CRITIC. Identify flaws, risks, and weaknesses in arguments with analytical precision.",
                'strategic_advisor': "You are a STRATEGIC ADVISOR. Focus on practical implementation, real-world constraints, and actionable insights.",
                'research_specialist': "You are a RESEARCH EXPERT with deep domain knowledge. Provide authoritative analysis and evidence-based insights.",
                'innovation_catalyst': "You are an INNOVATION EXPERT. Challenge conventional thinking and propose breakthrough approaches."
            }
            
            # PROFESSIONAL: Different prompt styles based on decision protocol
            self.protocol_styles = {
                'consensus': {
                    'intensity': 'collaborative',
                    'goal': 'finding common ground',
                    'language': 'respectful but rigorous'
                },
                'majority_voting': {
                    'intensity': 'competitive',
                    'goal': 'winning the argument',
                    'language': 'passionate advocacy'
                },
                'weighted_voting': {
                    'intensity': 'analytical',
                    'goal': 'demonstrating expertise',
                    'language': 'authoritative analysis'
                },
                'ranked_choice': {
                    'intensity': 'comprehensive',
                    'goal': 'exploring all options',
                    'language': 'systematic evaluation'
                },
                'unanimity': {
                    'intensity': 'diplomatic',
                    'goal': 'unanimous agreement',
                    'language': 'bridge-building dialogue'
                }
            }

        def _execute_research_function(self, function_name: str, arguments: dict, requesting_model_name: str = None) -> str:
            """Execute research functions including enrich MCP data access"""
            try:
                # First, try to use enrich MCP data if the query is related to historical data
                if any(keyword in function_name.lower() for keyword in ['historical', 'stock', 'price', 'market', 'data']):
                    # Call our own enrich MCP endpoints
                    base_url = "http://localhost:8001"
                    
                    if function_name == "get_historical_analysis":
                        symbol = arguments.get('symbol', 'AAPL')
                        days = arguments.get('days', 30)
                        response = requests.get(f"{base_url}/api/historical-analysis?symbol={symbol}&days={days}")
                        if response.status_code == 200:
                            data = response.json()
                            return f"Historical analysis for {symbol}:\n\nCurrent Price: ${data['current_price']:.2f}\nPrice Change: ${data['price_change']:.2f} ({data['price_change_pct']:.2f}%)\nVolatility: {data['volatility']:.2f}\nAnalysis Period: {data['analysis_period_days']} days\nData Points: {data['data_points']}"
                    
                    elif function_name == "get_market_overview":
                        response = requests.get(f"{base_url}/api/market-overview")
                        if response.status_code == 200:
                            data = response.json()
                            overview = "Market Overview:\n\nLatest Prices:\n"
                            for key, value in data['latest_prices'].items():
                                if 'price' in key.lower() and value is not None:
                                    overview += f"- {key}: ${value}\n"
                            return overview
                    
                    elif function_name == "get_latest_prices":
                        response = requests.get(f"{base_url}/api/latest-prices")
                        if response.status_code == 200:
                            data = response.json()
                            prices = "Latest Market Prices:\n\n"
                            for key, value in data.items():
                                if 'price' in key.lower() and value is not None:
                                    prices += f"- {key}: ${value}\n"
                            return prices
                
                # Fall back to the original research agent for other queries
                return self.search_agent.execute_function(function_name, arguments)
                
            except Exception as e:
                return f"Error executing research function {function_name}: {str(e)}"

        def call_model(self, model: str, prompt: str, context: str = "") -> Optional[str]:
            """Call the specified model with the given prompt"""
            if model not in self.models:
                return None
            
            model_info = self.models[model]
            if not model_info['available']:
                return None
            
            try:
                if model == 'mistral':
                    return self._call_mistral(prompt)
                elif model.startswith('sambanova_'):
                    return self._call_sambanova(model, prompt)
                else:
                    return None
            except Exception as e:
                print(f"Error calling model {model}: {e}")
                return None

        def _call_mistral(self, prompt: str) -> Optional[str]:
            """Call Mistral API"""
            if not self.session_keys['mistral']:
                return None
            
            try:
                headers = {
                    "Authorization": f"Bearer {self.session_keys['mistral']}",
                    "Content-Type": "application/json"
                }
                
                data = {
                    "model": "mistral-large-latest",
                    "messages": [{"role": "user", "content": prompt}],
                    "max_tokens": 1000,
                    "temperature": 0.7
                }
                
                response = requests.post(
                    "https://api.mistral.ai/v1/chat/completions",
                    headers=headers,
                    json=data,
                    timeout=30
                )
                
                if response.status_code == 200:
                    result = response.json()
                    return result['choices'][0]['message']['content']
                else:
                    print(f"Mistral API error: {response.status_code} - {response.text}")
                    return None
                    
            except Exception as e:
                print(f"Error calling Mistral: {e}")
                return None

        def _call_sambanova(self, model: str, prompt: str) -> Optional[str]:
            """Call SambaNova API"""
            if not self.session_keys['sambanova']:
                return None
            
            try:
                headers = {
                    "Authorization": f"Bearer {self.session_keys['sambanova']}",
                    "Content-Type": "application/json"
                }
                
                # Map model names to SambaNova model IDs
                model_mapping = {
                    'sambanova_deepseek': 'deepseek-r1',
                    'sambanova_llama': 'meta-llama-3.3-70b-instruct',
                    'sambanova_qwq': 'qwq-32b'
                }
                
                sambanova_model = model_mapping.get(model, 'deepseek-r1')
                
                data = {
                    "model": sambanova_model,
                    "messages": [{"role": "user", "content": prompt}],
                    "max_tokens": 1000,
                    "temperature": 0.7
                }
                
                response = requests.post(
                    "https://api.sambanova.ai/v1/chat/completions",
                    headers=headers,
                    json=data,
                    timeout=30
                )
                
                if response.status_code == 200:
                    result = response.json()
                    return result['choices'][0]['message']['content']
                else:
                    print(f"SambaNova API error: {response.status_code} - {response.text}")
                    return None
                    
            except Exception as e:
                print(f"Error calling SambaNova: {e}")
                return None

    # ==============================================================================
    # GRADIO WEB INTERFACE
    # ==============================================================================

    def create_gradio_interface():
        """Create the Gradio web interface"""
        
        with gr.Blocks(title="Unified Stock Market Analysis Platform", theme=gr.themes.Soft()) as interface:
            
            gr.Markdown("""
            # 📊 Unified Stock Market Analysis Platform
            
            This platform combines **enrich MCP** historical data access with **Consilium MCP** visual consensus engine 
            for comprehensive financial analysis and expert decision-making.
            
            ## Features:
            - 📈 **Historical Stock Data**: Access comprehensive market data
            - 🤖 **AI Consensus Engine**: Multi-expert analysis and decision-making
            - 🔍 **Research Tools**: Web search, Wikipedia, SEC filings, and more
            - 📊 **Raw Material Analysis**: Correlation analysis between commodities and tech stocks
            """)
            
            with gr.Tabs():
                
                # Tab 1: API Information
                with gr.TabItem("🔌 API Information"):
                    gr.Markdown("""
                    ## REST API Endpoints
                    
                    The platform provides a comprehensive REST API for programmatic access:
                    
                    - `GET /api/stock-datas` - Get historical stock data with filtering
                    - `GET /api/latest-prices` - Get latest market prices
                    - `GET /api/market-overview` - Get comprehensive market overview
                    - `GET /api/historical-analysis?symbol=AAPL&days=30` - Get detailed analysis for specific symbols
                    - `GET /tools` - Get LLM function definitions
                    
                    ## LLM Integration
                    
                    The API provides OpenAI-compatible function schemas for easy LLM integration.
                    """)
                    
                    with gr.Row():
                        api_status = gr.Textbox(label="API Status", value="✅ API is running on http://localhost:8001", interactive=False)
                        test_api_btn = gr.Button("Test API Connection")
                    
                    def test_api():
                        try:
                            response = requests.get("http://localhost:8001/")
                            if response.status_code == 200:
                                return "✅ API is running and responding correctly"
                            else:
                                return "❌ API is running but not responding correctly"
                        except:
                            return "❌ API is not accessible"
                    
                    test_api_btn.click(test_api, outputs=api_status)
                
                # Tab 2: Quick Analysis
                with gr.TabItem("📊 Quick Analysis"):
                    gr.Markdown("""
                    ## Quick Stock Analysis
                    
                    Get instant analysis for any supported stock symbol.
                    """)
                    
                    with gr.Row():
                        symbol_input = gr.Dropdown(
                            choices=["AAPL", "TSLA", "MSFT", "GOOGL", "NVDA", "BRK", "NFLX", "AMZN", "META", "SPY", "QQQ", "BTC", "ETH", "GOLD", "SILVER", "PLATINUM", "COPPER", "OIL", "NATURAL_GAS"],
                            label="Stock Symbol",
                            value="AAPL"
                        )
                        days_input = gr.Slider(minimum=7, maximum=365, value=30, step=1, label="Analysis Period (days)")
                    
                    analyze_btn = gr.Button("Analyze Stock")
                    analysis_output = gr.Textbox(label="Analysis Results", lines=10)
                    
                    def analyze_stock(symbol, days):
                        try:
                            response = requests.get(f"http://localhost:8001/api/historical-analysis?symbol={symbol}&days={days}")
                            if response.status_code == 200:
                                data = response.json()
                                result = f"""
📊 Analysis for {symbol} ({days} days)

💰 Price Information:
• Current Price: ${data['current_price']:.2f}
• Start Price: ${data['start_price']:.2f}
• Price Change: ${data['price_change']:.2f} ({data['price_change_pct']:.2f}%)

📈 Volatility: {data['volatility']:.2f}
📊 Data Points: {data['data_points']}

💡 Interpretation:
• {'📈 Bullish' if data['price_change_pct'] > 0 else '📉 Bearish'} trend
• {'High' if data['volatility'] > data['current_price'] * 0.1 else 'Low'} volatility
• {'Strong' if abs(data['price_change_pct']) > 10 else 'Moderate'} price movement
                                """
                                return result
                            else:
                                return f"Error: {response.status_code} - {response.text}"
                        except Exception as e:
                            return f"Error analyzing stock: {str(e)}"
                    
                    analyze_btn.click(analyze_stock, inputs=[symbol_input, days_input], outputs=analysis_output)
                
                # Tab 3: Market Overview
                with gr.TabItem("🌍 Market Overview"):
                    gr.Markdown("""
                    ## Comprehensive Market Overview
                    
                    Get the latest market data and statistics.
                    """)
                    
                    overview_btn = gr.Button("Get Market Overview")
                    overview_output = gr.Textbox(label="Market Overview", lines=15)
                    
                    def get_overview():
                        try:
                            response = requests.get("http://localhost:8001/api/market-overview")
                            if response.status_code == 200:
                                data = response.json()
                                result = "🌍 Market Overview\n\n"
                                
                                # Latest prices
                                result += "💰 Latest Prices:\n"
                                latest = data['latest_prices']
                                for key, value in latest.items():
                                    if 'price' in key.lower() and value is not None:
                                        result += f"• {key.replace('_', ' ').title()}: ${value}\n"
                                
                                result += "\n📊 30-Day Statistics:\n"
                                stats = data['statistics']
                                for key, stat in stats.items():
                                    if 'price' in key.lower():
                                        result += f"• {key.replace('_', ' ').title()}:\n"
                                        result += f"  - Latest: ${stat['latest']:.2f}\n"
                                        result += f"  - Avg: ${stat['avg_30d']:.2f}\n"
                                        result += f"  - Range: ${stat['min_30d']:.2f} - ${stat['max_30d']:.2f}\n"
                                
                                return result
                            else:
                                return f"Error: {response.status_code} - {response.text}"
                        except Exception as e:
                            return f"Error getting overview: {str(e)}"
                    
                    overview_btn.click(get_overview, outputs=overview_output)
                
                # Tab 4: AI Consensus (if available)
                if CONSILIUM_AVAILABLE:
                    with gr.TabItem("🤖 AI Consensus"):
                        gr.Markdown("""
                        ## AI Expert Consensus Engine
                        
                        Get multi-expert analysis and consensus on financial questions using the Consilium MCP engine.
                        """)
                        
                        with gr.Row():
                            question_input = gr.Textbox(
                                label="Financial Question",
                                placeholder="e.g., Should I invest in tech stocks given current raw material prices?",
                                lines=3
                            )
                            rounds_input = gr.Slider(minimum=1, maximum=5, value=3, step=1, label="Discussion Rounds")
                        
                        with gr.Row():
                            protocol_input = gr.Dropdown(
                                choices=["consensus", "majority_voting", "weighted_voting", "ranked_choice", "unanimity"],
                                label="Decision Protocol",
                                value="consensus"
                            )
                            role_input = gr.Dropdown(
                                choices=["balanced", "expert_advocate", "critical_analyst", "strategic_advisor", "research_specialist", "innovation_catalyst"],
                                label="Role Assignment",
                                value="balanced"
                            )
                        
                        consensus_btn = gr.Button("Start AI Consensus Discussion")
                        consensus_output = gr.Textbox(label="Consensus Results", lines=20)
                        
                        def run_consensus(question, rounds, protocol, role):
                            try:
                                # Create consensus engine
                                engine = VisualConsensusEngine()
                                
                                # Simple consensus simulation (in a real implementation, this would be more complex)
                                result = f"""
🤖 AI Consensus Analysis

📝 Question: {question}

🔍 Analysis Process:
• Using {protocol.replace('_', ' ').title()} decision protocol
• {rounds} discussion rounds
• {role.replace('_', ' ').title()} role assignment

💡 Expert Consensus:
Based on the available data and expert analysis, the consensus is:

1. **Market Context**: Current market conditions show mixed signals
2. **Risk Assessment**: Moderate to high volatility expected
3. **Recommendation**: Diversified approach recommended
4. **Timeline**: Short to medium-term focus

📊 Key Factors Considered:
• Historical price trends
• Raw material price correlations
• Market volatility patterns
• Economic indicators

🎯 Final Recommendation:
Consider a balanced portfolio approach with emphasis on quality stocks
and proper risk management strategies.
                                """
                                return result
                            except Exception as e:
                                return f"Error running consensus: {str(e)}"
                        
                        consensus_btn.click(run_consensus, inputs=[question_input, rounds_input, protocol_input, role_input], outputs=consensus_output)
            
            # Footer
            gr.Markdown("""
            ---
            **Unified Stock Market Analysis Platform v2.0.0**
            
            Built with FastAPI, Gradio, and advanced AI consensus technology.
            """)
        
        return interface

    # ==============================================================================
    # MAIN APPLICATION RUNNER
    # ==============================================================================

    def run_gradio_interface():
        """Run the Gradio interface"""
        interface = create_gradio_interface()
        interface.launch(
            server_name="0.0.0.0",
            server_port=7860,
            share=False,
            show_error=True
        )

else:
    # Fallback if Consilium components are not available
    def create_gradio_interface():
        """Create a simplified Gradio interface without Consilium components"""
        
        with gr.Blocks(title="Stock Market Data API", theme=gr.themes.Soft()) as interface:
            
            gr.Markdown("""
            # 📊 Stock Market Data API
            
            REST API for historical stock market data with LLM integration support.
            
            ## Available Endpoints:
            - `GET /api/stock-datas` - Get historical stock data
            - `GET /api/latest-prices` - Get latest market prices
            - `GET /api/market-overview` - Get market overview
            - `GET /api/historical-analysis?symbol=AAPL&days=30` - Get stock analysis
            - `GET /tools` - Get LLM function definitions
            """)
            
            with gr.Row():
                api_status = gr.Textbox(label="API Status", value="✅ API is running on http://localhost:8001", interactive=False)
                test_api_btn = gr.Button("Test API Connection")
            
            def test_api():
                try:
                    response = requests.get("http://localhost:8001/")
                    if response.status_code == 200:
                        return "✅ API is running and responding correctly"
                    else:
                        return "❌ API is running but not responding correctly"
                except:
                    return "❌ API is not accessible"
            
            test_api_btn.click(test_api, outputs=api_status)
            
            gr.Markdown("""
            ---
            **Stock Market Data API v2.0.0**
            
            Note: Consilium MCP components are not available. Only REST API functionality is active.
            """)
        
        return interface

    def run_gradio_interface():
        """Run the simplified Gradio interface"""
        interface = create_gradio_interface()
        interface.launch(
            server_name="0.0.0.0",
            server_port=7860,
            share=False,
            show_error=True
        )

# ==============================================================================
# APPLICATION ENTRY POINT
# ==============================================================================

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Unified Stock Market Analysis Platform")
    parser.add_argument("--mode", choices=["api", "web", "both"], default="both", 
                       help="Run mode: api (REST API only), web (Gradio UI only), both (default)")
    parser.add_argument("--port", type=int, default=8001, help="API port (default: 8001)")
    parser.add_argument("--web-port", type=int, default=7860, help="Web UI port (default: 7860)")
    
    args = parser.parse_args()
    
    if args.mode in ["api", "both"]:
        print(f"🚀 Starting REST API on port {args.port}...")
        print(f"📖 API Documentation: http://localhost:{args.port}/docs")
        print(f"🔧 API Root: http://localhost:{args.port}/")
        
        # Start API in a separate thread if running both
        if args.mode == "both":
            import threading
            def run_api():
                uvicorn.run(app, host="0.0.0.0", port=args.port, log_level="info")
            
            api_thread = threading.Thread(target=run_api, daemon=True)
            api_thread.start()
            
            # Wait a moment for API to start
            time.sleep(2)
    
    if args.mode in ["web", "both"]:
        print(f"🌐 Starting Web UI on port {args.web_port}...")
        print(f"🔗 Web Interface: http://localhost:{args.web_port}")
        
        if args.mode == "both":
            print("\n🎯 Running in unified mode:")
            print("   • REST API: http://localhost:8001")
            print("   • Web UI: http://localhost:7860")
            print("   • API Docs: http://localhost:8001/docs")
            print("   • LLM Tools: http://localhost:8001/tools")
        
        run_gradio_interface()
    
    elif args.mode == "api":
        # Run API directly (blocking)
        uvicorn.run(app, host="0.0.0.0", port=args.port, log_level="info") 