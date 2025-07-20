# 🧪 Raw Material Tech Analysis - Testing Guide

## 🚀 **Quick Start Testing**

### **Prerequisites:**
1. **Start Enrich MCP Server:**
   ```bash
   cd MCP/enrich_mcp
   python app.py
   ```
   Server should be running on `http://localhost:8001`

2. **Install Dependencies:**
   ```bash
   cd MCP/consilium_mcp
   pip install -r requirements.txt
   ```

## 📋 **Testing Methods**

### **Method 1: Predefined Scenarios**
Run the scenario test script to see 5 different analysis scenarios:

```bash
python test_scenario.py
```

**Scenarios Tested:**
- Copper price impact on Apple and Tesla
- Investment recommendations based on commodity prices
- Oil and gas impact on cloud services
- Semiconductor material sensitivity
- Deep multi-source research

### **Method 2: Interactive Testing**
Run the interactive test to input your own queries:

```bash
python interactive_test.py
```

**Example Queries to Try:**
- "How do copper prices affect Apple and Tesla?"
- "Should I buy tech stocks given current oil prices?"
- "Which tech stocks are most vulnerable to rising material costs?"
- "Recommend tech stocks based on commodity price trends"
- "How do natural gas prices affect data center costs?"

### **Method 3: Consilium MCP Integration**
Simulate how it works in the roundtable:

```bash
python test_consilium_integration.py
```

## 🔍 **Manual Testing Commands**

### **Test Individual Components:**

1. **Test Raw Material Tool Directly:**
   ```bash
   cd MCP/consilium_mcp
   python -c "from research_tools.raw_material_tech_analysis import RawMaterialTechAnalysisTool; tool = RawMaterialTechAnalysisTool(); result = tool.search('copper prices affect tech stocks'); print(result)"
   ```

2. **Test Research Agent Routing:**
   ```bash
   python -c "from research_tools.research_agent import EnhancedResearchAgent; agent = EnhancedResearchAgent(); print(agent._route_query_to_tool('copper prices affect tech stocks'))"
   ```

3. **Test Full Integration:**
   ```bash
   python -c "from research_tools.research_agent import EnhancedResearchAgent; agent = EnhancedResearchAgent(); result = agent.search('How do copper prices affect Apple and Tesla?'); print(result)"
   ```

## 🎯 **Specific Scenarios to Test**

### **Scenario 1: Material Price Increases**
**Query:** "Copper prices just surged 20%. Which tech stocks should I avoid?"
**Expected:** Analysis of high-material-sensitivity stocks to avoid

### **Scenario 2: Energy Cost Impact**
**Query:** "How do natural gas prices affect Microsoft and Google?"
**Expected:** Analysis of data center energy costs and cloud services

### **Scenario 3: Investment Recommendations**
**Query:** "Recommend tech stocks to buy based on current commodity prices"
**Expected:** Buy/sell recommendations with risk levels

### **Scenario 4: Supply Chain Analysis**
**Query:** "Supply chain disruptions affecting copper. Impact on semiconductors?"
**Expected:** Analysis of supply chain vulnerabilities

### **Scenario 5: Portfolio Diversification**
**Query:** "How should I diversify my tech portfolio given material price risks?"
**Expected:** Diversification strategy based on material sensitivity

## 🔧 **Troubleshooting**

### **Common Issues:**

1. **"Enrich MCP server is not running"**
   - Solution: Start the server with `cd MCP/enrich_mcp && python app.py`

2. **"No module named 'smolagents'"**
   - This is expected and handled gracefully
   - Web search will show a warning but other tools work fine

3. **"Import error"**
   - Make sure you're in the correct directory
   - Check that all dependencies are installed

4. **"No data found"**
   - Check that the enrich MCP server has data
   - Try different date ranges in your queries

### **Debug Mode:**
To see detailed routing information:
```bash
python -c "from research_tools.research_agent import EnhancedResearchAgent; agent = EnhancedResearchAgent(); print('Available tools:', list(agent.tools.keys())); print('Routing test:', agent._route_query_to_tool('copper prices affect tech stocks'))"
```

## 📊 **Expected Output Analysis**

### **Raw Material Analysis Output Should Include:**
- **Material Impact Analysis:** How each material affects tech companies
- **Investment Implications:** Opportunities and risks
- **Market Timing:** When to act based on trends
- **Portfolio Diversification:** Low vs high material sensitivity
- **Monitoring Points:** Key indicators to watch

### **Investment Recommendations Should Include:**
- **BUY RECOMMENDATIONS:** Stocks to consider buying
- **SELL/AVOID RECOMMENDATIONS:** Stocks to avoid
- **Risk Levels:** High/Medium/Low risk assessments
- **Correlation Data:** Statistical relationships
- **Current Prices:** Latest price information

## 🎭 **Consilium MCP Integration Testing**

### **Full Roundtable Simulation:**
1. Lead Analyst asks investment question
2. Research Agent performs raw material analysis
3. Experts synthesize findings
4. Final consensus recommendation

### **Test in Real Consilium MCP:**
1. Start Consilium MCP: `cd MCP/consilium_mcp && python app.py`
2. Ask the Lead Analyst: "How do copper prices affect tech stocks?"
3. Watch the research agent perform analysis
4. See expert consensus form

## 📈 **Performance Testing**

### **Response Time Testing:**
```bash
import time
from research_tools.research_agent import EnhancedResearchAgent

agent = EnhancedResearchAgent()
start_time = time.time()
result = agent.search("copper prices affect tech stocks")
end_time = time.time()
print(f"Response time: {end_time - start_time:.2f} seconds")
```

### **Load Testing:**
Test multiple queries in sequence to ensure stability.

## ✅ **Success Criteria**

A successful test should show:
- ✅ Raw material analysis tool routes correctly
- ✅ Historical data integration works
- ✅ Investment recommendations generated
- ✅ Correlation analysis performed
- ✅ Multi-source research capability
- ✅ Error handling works gracefully
- ✅ Response times under 5 seconds

## 🚀 **Next Steps After Testing**

1. **Integration with Consilium MCP:** Test in the full roundtable environment
2. **Real Market Data:** Validate with current market conditions
3. **Performance Optimization:** Fine-tune response times
4. **Additional Features:** Add more material types or analysis methods 