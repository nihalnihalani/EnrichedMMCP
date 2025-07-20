# 📊 Unified Stock Market Analysis Platform

A comprehensive platform that combines **enrich MCP** historical data access with **Consilium MCP** visual consensus engine for advanced financial analysis and expert decision-making.

## 🚀 Features

### Core Capabilities
- **📈 Historical Stock Data**: Access comprehensive market data with REST API
- **🤖 AI Consensus Engine**: Multi-expert analysis and decision-making (when Consilium available)
- **🔍 Research Tools**: Web search, Wikipedia, SEC filings, and more
- **📊 Raw Material Analysis**: Correlation analysis between commodities and tech stocks
- **🔧 LLM Integration**: OpenAI-compatible function schemas for easy LLM integration

### Supported Assets
- **Tech Stocks**: AAPL, TSLA, MSFT, GOOGL, NVDA, NFLX, AMZN, META
- **Indices**: SPY (S&P 500), QQQ (Nasdaq 100)
- **Commodities**: GOLD, SILVER, PLATINUM, COPPER, OIL, NATURAL_GAS
- **Cryptocurrencies**: BTC, ETH
- **Other**: BRK (Berkshire Hathaway)

## 🛠️ Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/nihalnihalani/EnrichedMMCP.git
   cd EnrichedMMCP
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up the database** (if not already done):
   ```bash
   python database_setup.py
   ```

4. **Set up environment variables** (optional):
   ```bash
   # Create .env file
   echo "MISTRAL_API_KEY=your_mistral_key_here" > .env
   echo "SAMBANOVA_API_KEY=your_sambanova_key_here" >> .env
   ```

## 🚀 Usage

### Option 1: Unified Application (Recommended)

Run both the REST API and web interface simultaneously:

```bash
python unified_app.py
```

This will start:
- **REST API**: http://localhost:8001
- **Web UI**: http://localhost:7860
- **API Docs**: http://localhost:8001/docs

### Option 2: REST API Only

```bash
python unified_app.py --mode api
# or
python -m uvicorn unified_app:app --reload --port 8001
```

### Option 3: Web Interface Only

```bash
python unified_app.py --mode web
```

### Option 4: Custom Ports

```bash
python unified_app.py --port 8002 --web-port 7861
```

## 📡 REST API Endpoints

### Core Endpoints

#### `GET /api/stock-datas`
Get historical stock data with filtering options.

**Parameters:**
- `limit` (int, default: 100): Maximum number of records
- `offset` (int, default: 0): Number of records to skip
- `date_eq` (string): Exact date filter (YYYY-MM-DD)
- `date_gte` (string): Date greater than or equal to
- `date_lte` (string): Date less than or equal to

**Example:**
```bash
curl "http://localhost:8001/api/stock-datas?limit=10&date_gte=2024-01-01"
```

#### `GET /api/latest-prices`
Get the most recent stock prices and market data.

**Example:**
```bash
curl "http://localhost:8001/api/latest-prices"
```

#### `GET /api/market-overview`
Get comprehensive market overview with latest prices and 30-day statistics.

**Example:**
```bash
curl "http://localhost:8001/api/market-overview"
```

#### `GET /api/historical-analysis`
Get detailed historical analysis for a specific stock symbol.

**Parameters:**
- `symbol` (string, required): Stock symbol to analyze
- `days` (int, default: 30): Number of days to analyze

**Example:**
```bash
curl "http://localhost:8001/api/historical-analysis?symbol=AAPL&days=30"
```

#### `GET /tools`
Get LLM function definitions for OpenAI-compatible function calling.

**Example:**
```bash
curl "http://localhost:8001/tools"
```

## 🤖 LLM Integration

The platform provides OpenAI-compatible function schemas for easy integration with LLMs:

### Available Functions

1. **`get_stock_data`**: Get historical stock market data with filtering
2. **`get_latest_prices`**: Get the most recent stock prices
3. **`get_market_overview`**: Get comprehensive market overview
4. **`get_historical_analysis`**: Get detailed analysis for specific symbols

### Example LLM Usage

```python
import requests

# Get function definitions
tools_response = requests.get("http://localhost:8001/tools")
tools = tools_response.json()["tools"]

# Use with OpenAI API
import openai

client = openai.OpenAI(api_key="your_openai_key")

response = client.chat.completions.create(
    model="gpt-4",
    messages=[
        {"role": "user", "content": "Analyze Apple stock performance over the last 30 days"}
    ],
    tools=tools,
    tool_choice="auto"
)
```

## 🌐 Web Interface

The Gradio web interface provides an intuitive way to interact with the platform:

### Available Tabs

1. **🔌 API Information**: Test API connectivity and view endpoint documentation
2. **📊 Quick Analysis**: Get instant analysis for any supported stock symbol
3. **🌍 Market Overview**: View comprehensive market data and statistics
4. **🤖 AI Consensus**: Multi-expert analysis (when Consilium components are available)

### Features

- **Real-time API testing**: Verify API connectivity
- **Interactive stock analysis**: Select symbols and time periods
- **Market statistics**: View 30-day price ranges and averages
- **AI consensus engine**: Get expert opinions on financial questions

## 📊 Data Analysis Examples

### Stock Performance Analysis

```python
import requests

# Get Apple stock analysis
response = requests.get("http://localhost:8001/api/historical-analysis?symbol=AAPL&days=30")
data = response.json()

print(f"Current Price: ${data['current_price']:.2f}")
print(f"Price Change: {data['price_change_pct']:.2f}%")
print(f"Volatility: {data['volatility']:.2f}")
```

### Market Overview

```python
# Get comprehensive market overview
response = requests.get("http://localhost:8001/api/market-overview")
data = response.json()

# Latest prices
for key, value in data['latest_prices'].items():
    if 'price' in key.lower() and value is not None:
        print(f"{key}: ${value}")

# Statistics
for key, stat in data['statistics'].items():
    if 'price' in key.lower():
        print(f"{key}: Avg=${stat['avg_30d']:.2f}, Range=${stat['min_30d']:.2f}-${stat['max_30d']:.2f}")
```

## 🔧 Configuration

### Environment Variables

- `MISTRAL_API_KEY`: Mistral AI API key for consensus engine
- `SAMBANOVA_API_KEY`: SambaNova API key for consensus engine
- `MODERATOR_MODEL`: Default moderator model (default: "mistral")

### Database Configuration

The platform uses SQLite by default. The database file is `stock_market.db` and contains:
- Historical price data for all supported assets
- Volume data where available
- Date-based indexing for efficient queries

## 🧪 Testing

### API Testing

```bash
# Test basic connectivity
curl "http://localhost:8001/"

# Test stock data endpoint
curl "http://localhost:8001/api/stock-datas?limit=5"

# Test historical analysis
curl "http://localhost:8001/api/historical-analysis?symbol=AAPL&days=7"
```

### Web Interface Testing

1. Open http://localhost:7860 in your browser
2. Navigate to the "API Information" tab
3. Click "Test API Connection"
4. Try the "Quick Analysis" tab with different symbols

## 📈 Use Cases

### 1. Investment Research
- Analyze historical performance of stocks
- Compare multiple assets
- Get market overview for decision-making

### 2. LLM Integration
- Provide financial data to AI assistants
- Enable automated market analysis
- Support investment recommendations

### 3. Academic Research
- Access historical market data
- Perform correlation analysis
- Study market trends and patterns

### 4. Trading Applications
- Real-time market data access
- Historical trend analysis
- Risk assessment tools

## 🔍 Troubleshooting

### Common Issues

1. **Database not found**: Run `python database_setup.py`
2. **Port already in use**: Use different ports with `--port` and `--web-port`
3. **Consilium components missing**: The platform will run with basic functionality
4. **API not responding**: Check if the server is running on the correct port

### Logs

The application provides detailed logging:
- API requests and responses
- Database operations
- Error messages and stack traces

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- **enrich MCP**: For the historical data access framework
- **Consilium MCP**: For the visual consensus engine
- **FastAPI**: For the high-performance web framework
- **Gradio**: For the beautiful web interface
- **SQLAlchemy**: For the database ORM

## 📞 Support

For questions, issues, or contributions:
- Open an issue on GitHub
- Check the documentation at http://localhost:8001/docs
- Review the testing guide in `TESTING_GUIDE.md`

---

**Unified Stock Market Analysis Platform v2.0.0** - Combining the power of historical data with AI consensus for smarter financial decisions. 