# Stock Market Data API with LLM Integration

This project demonstrates how to create a powerful API for stock market data that can be easily integrated with LLMs. The API provides REST endpoints and automatic tool definitions for LLM integration, making it simple for LLMs to query financial information.

## Features

- **REST API**: Clean REST endpoints for querying stock market data
- **LLM Integration Ready**: Built-in tool definitions that can be directly used with LLM agents
- **Data Cleaning**: Automatic cleaning of CSV data including column name sanitization and numeric conversion
- **Async Support**: Full async/await support for high-performance database operations
- **Multiple Query Types**: Support for filtering, pagination, and date range queries

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Set Up the Database

First, run the database setup script to load your CSV data into SQLite:

```bash
python database_setup.py
```

This script will:
- Read the `Stock Market Dataset 2.csv` file
- Clean column names and data types
- Load the data into a SQLite database
- Create the necessary table structure

### 3. Start the API Server

```bash
python -m uvicorn app:app --reload --port 8001
```

The server will start at `http://127.0.0.1:8001`

### 4. Test the Integration

In a separate terminal, run:

```bash
python llm_integration.py
```

This will fetch the tool definitions that can be used with LLMs.

## API Endpoints

### REST API Endpoints
- **Stock Data**: `http://127.0.0.1:8001/api/stock-datas`
- **Latest Prices**: `http://127.0.0.1:8001/api/latest-prices`
- **Market Overview**: `http://127.0.0.1:8001/api/market-overview`
- **Documentation**: `http://127.0.0.1:8001/docs`

### Tool Definitions for LLMs
- **URL**: `http://127.0.0.1:8001/tools`

## Example Queries

### REST API Query Examples
```bash
# Get latest stock data
curl "http://127.0.0.1:8001/api/stock-datas?limit=10"

# Get data for a specific date
curl "http://127.0.0.1:8001/api/stock-datas?date_eq=2024-02-02"

# Get data for a date range
curl "http://127.0.0.1:8001/api/stock-datas?date_gte=2024-01-01&date_lte=2024-01-31"

# Get latest prices
curl "http://127.0.0.1:8001/api/latest-prices"

# Get market overview
curl "http://127.0.0.1:8001/api/market-overview"
```

## LLM Integration

The API automatically generates tool definitions that can be used with LLM agents. Here's how to integrate:

### 1. Get Tool Definitions
```python
import requests

response = requests.get("http://127.0.0.1:8001/tools")
tools = response.json()
```

### 2. Use with OpenAI
```python
from openai import OpenAI

client = OpenAI()

# Pass the tools to your LLM
response = client.chat.completions.create(
    model="gpt-4",
    messages=[
        {"role": "user", "content": "What are the latest stock prices?"}
    ],
    tools=tools,
    tool_choice="auto"
)
```

### 3. Use with LangChain
```python
from langchain.agents import AgentExecutor, create_openai_tools_agent
from langchain_openai import ChatOpenAI

# Create agent with the tools
agent = create_openai_tools_agent(
    llm=ChatOpenAI(model="gpt-4"),
    tools=tools,
    prompt=prompt
)

agent_executor = AgentExecutor(agent=agent, tools=tools)
result = agent_executor.invoke({"input": "What are the latest stock prices?"})
```

### 4. Use the Example Client
```python
from example_llm_usage import StockMarketLLMClient

client = StockMarketLLMClient()
tools = client.get_tool_definitions()

# Execute a function call
result = client.execute_function_call("get_latest_prices", {})
formatted_response = client.format_response_for_llm("get_latest_prices", result)
print(formatted_response)
```

## Available Data Fields

The API automatically exposes all columns from your CSV file. Based on your stock market dataset, you'll have access to:

### Cryptocurrencies
- `bitcoin_price`, `bitcoin_vol`
- `ethereum_price`, `ethereum_vol`

### Tech Stocks
- `apple_price`, `apple_vol`
- `tesla_price`, `tesla_vol`
- `microsoft_price`, `microsoft_vol`
- `google_price`, `google_vol`
- `nvidia_price`, `nvidia_vol`
- `netflix_price`, `netflix_vol`
- `amazon_price`, `amazon_vol`
- `meta_price`, `meta_vol`

### Commodities
- `natural_gas_price`, `natural_gas_vol`
- `crude_oil_price`, `crude_oil_vol`
- `copper_price`, `copper_vol`
- `gold_price`, `gold_vol`
- `silver_price`, `silver_vol`
- `platinum_price`, `platinum_vol`

### Market Indices
- `sp_500_price`
- `nasdaq_100_price`, `nasdaq_100_vol`

### Other
- `berkshire_price`, `berkshire_vol`

## Query Examples

### Get Latest Prices
```bash
curl "http://127.0.0.1:8001/api/latest-prices"
```

### Filter by Date Range
```bash
curl "http://127.0.0.1:8001/api/stock-datas?date_gte=2024-01-01&date_lte=2024-02-01&limit=10"
```

### Get Market Overview
```bash
curl "http://127.0.0.1:8001/api/market-overview"
```

### Get Specific Date Data
```bash
curl "http://127.0.0.1:8001/api/stock-datas?date_eq=2024-01-02"
```

## Advanced Features

### Custom Endpoints
You can add custom endpoints to the FastAPI app for complex business logic:

```python
@app.get("/api/custom-analysis")
async def get_custom_analysis(session: AsyncSession = Depends(get_session)):
    # Custom logic here
    return {"analysis": "Custom market analysis"}
```

### Available Filters
The API provides several filtering options:

- **Date Equality**: `date_eq=2024-02-02`
- **Date Range**: `date_gte=2024-01-01&date_lte=2024-01-31`
- **Pagination**: `limit=10&offset=20`

## Troubleshooting

### Database Issues
If you encounter database errors:
1. Delete the `stock_market.db` file
2. Run `python database_setup.py` again
3. Restart the server

### Import Errors
If you get import errors for any packages:
```bash
pip install -r requirements.txt
```

### Server Won't Start
Check that:
1. All dependencies are installed
2. The database file exists
3. Port 8000 is not in use

## Development

### Adding New Data Sources
1. Update the CSV file
2. Run `python database_setup.py` to reload the database
3. Restart the server

### Customizing the API
Modify `app.py` to add custom resolvers, middleware, or additional functionality.

## License

This project is open source and available under the MIT License. 