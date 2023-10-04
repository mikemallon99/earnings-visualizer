import yfinance as yf

# Fetch data
ticker = "AAPL"
stock = yf.Ticker(ticker)

# Get company financials
financials = stock.quarterly_income_stmt
print(financials)

latest_quarter = financials.iloc[:, 0]

revenue = latest_quarter["Total Revenue"]
cogs = latest_quarter["Cost Of Revenue"]
gross_profit = latest_quarter["Gross Profit"]
opex = latest_quarter["Operating Expense"]
# rd_cost = latest_quarter["Research And Development"]
admin_cost = latest_quarter["Selling General And Administration"]
pretax_income = latest_quarter["Pretax Income"]
income_tax = latest_quarter["Tax Provision"]

