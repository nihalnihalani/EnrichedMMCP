# ==============================================================================
# FILE: app.py
#
# PURPOSE: The main FastAPI application that creates an API server that exposes
#          the data from the SQLite database with LLM integration support.
#
# USAGE: Run `python -m uvicorn app:app --reload --port 8001` in your terminal.
# ==============================================================================
import sqlalchemy as sa
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from fastapi import FastAPI, Depends, HTTPException
from fastapi.responses import JSONResponse
from typing import List, Optional
import json
from datetime import datetime

# --- Database and SQLAlchemy Setup ---

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

# --- FastAPI App Setup ---

app = FastAPI(
    title="Stock Market Data API",
    description="An API for querying historical stock market data with LLM integration support.",
    version="1.0.0"
)

# --- REST API Endpoints ---

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
    
    overview = {
        "latest_date": latest.date.isoformat() if latest.date else None,
        "latest_prices": {
            "bitcoin": latest.bitcoin_price,
            "ethereum": latest.ethereum_price,
            "apple": latest.apple_price,
            "tesla": latest.tesla_price,
            "microsoft": latest.microsoft_price,
            "google": latest.google_price,
            "nvidia": latest.nvidia_price,
            "netflix": latest.netflix_price,
            "amazon": latest.amazon_price,
            "meta": latest.meta_price,
            "gold": latest.gold_price,
            "silver": latest.silver_price,
            "crude_oil": latest.crude_oil_price,
            "sp_500": latest.s_p_500_price,
            "nasdaq_100": latest.nasdaq_100_price
        },
        "data_points": len(recent_data),
        "available_instruments": [
            "bitcoin", "ethereum", "apple", "tesla", "microsoft", 
            "google", "nvidia", "netflix", "amazon", "meta",
            "gold", "silver", "platinum", "copper", "crude_oil", 
            "natural_gas", "sp_500", "nasdaq_100", "berkshire"
        ]
    }
    
    return overview

# --- LLM Tool Definitions ---

@app.get("/tools")
async def get_tools():
    """Endpoint to get tool definitions for LLM integration"""
    tools = {
        "tools": [
            {
                "type": "function",
                "function": {
                    "name": "get_stock_data",
                    "description": "Get stock market data with filtering and pagination",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "limit": {
                                "type": "integer",
                                "description": "Maximum number of records to return (default: 100)"
                            },
                            "offset": {
                                "type": "integer",
                                "description": "Number of records to skip (default: 0)"
                            },
                            "date_eq": {
                                "type": "string",
                                "description": "Exact date filter (YYYY-MM-DD format)"
                            },
                            "date_gte": {
                                "type": "string",
                                "description": "Date greater than or equal filter (YYYY-MM-DD format)"
                            },
                            "date_lte": {
                                "type": "string",
                                "description": "Date less than or equal filter (YYYY-MM-DD format)"
                            }
                        }
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "get_latest_prices",
                    "description": "Get the most recent stock prices for all instruments",
                    "parameters": {
                        "type": "object",
                        "properties": {}
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "get_stock_data_by_id",
                    "description": "Get a specific stock data record by its ID",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "record_id": {
                                "type": "integer",
                                "description": "The ID of the record to retrieve"
                            }
                        },
                        "required": ["record_id"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "get_market_overview",
                    "description": "Get a comprehensive market overview with latest prices and statistics",
                    "parameters": {
                        "type": "object",
                        "properties": {}
                    }
                }
            }
        ]
    }
    
    return tools

@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "Stock Market Data API",
        "version": "1.0.0",
        "endpoints": {
            "rest_api": "/api/stock-datas",
            "latest_prices": "/api/latest-prices",
            "market_overview": "/api/market-overview",
            "tools": "/tools",
            "docs": "/docs"
        },
        "available_functions": [
            "get_stock_data",
            "get_latest_prices", 
            "get_stock_data_by_id",
            "get_market_overview"
        ]
    } 