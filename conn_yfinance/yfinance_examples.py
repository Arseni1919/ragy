"""
Comprehensive yfinance examples - demonstrates all major capabilities.

Categories:
1. Historical Price Data
2. Company Information
3. Financial Statements
4. Options Data
5. Analyst Ratings & Targets
6. Multiple Tickers
7. Fund/ETF Data
8. Search - Text Search for Quotes & News
9. Market Information
10. Sector & Industry Data
11. Screener & EquityQuery
"""
import yfinance as yf

def print_section(title):
    print(f"\n{'='*60}")
    print(f"=== {title}")
    print('='*60)

def print_code(code):
    print(f">>> {code}")


def example_historical_data():
    """1. Historical Price Data - OHLCV"""
    print_section("Historical Price Data")

    ticker = yf.Ticker("MSFT")

    # Different time periods
    hist_5d = ticker.history(period='5d')
    print(f"5-day history: {len(hist_5d)} rows")
    print(f"Latest close: ${hist_5d['Close'].iloc[-1]:.2f}")

    # Date range query
    hist_range = ticker.history(start='2024-01-01', end='2024-12-31')
    print(f"2024 full year: {len(hist_range)} trading days")

    # Bulk download multiple tickers
    data = yf.download(['AAPL', 'GOOGL', 'MSFT'], period='1mo', progress=False)
    print(f"Bulk download: {data.shape}")

def example_company_info():
    """2. Company Information - Fundamentals"""
    print_section("Company Information")

    ticker = yf.Ticker("TSLA")
    info = ticker.info

    print(f"Name: {info.get('longName')}")
    print(f"Sector: {info.get('sector')}")
    print(f"Industry: {info.get('industry')}")
    print(f"Market Cap: ${info.get('marketCap', 0):,}")
    print(f"PE Ratio: {info.get('trailingPE', 'N/A')}")
    print(f"Dividend Yield: {info.get('dividendYield', 'N/A')}")

def example_financials():
    """3. Financial Statements"""
    print_section("Financial Statements")

    ticker = yf.Ticker("AAPL")

    # Income statement
    income_q = ticker.quarterly_income_stmt
    print(f"Quarterly income stmt: {income_q.shape}")
    if not income_q.empty:
        print(f"Latest quarter revenue: ${income_q.iloc[0, 0]:,}")

    # Balance sheet
    balance = ticker.quarterly_balance_sheet
    print(f"Quarterly balance sheet: {balance.shape}")

    # Cash flow
    cashflow = ticker.quarterly_cash_flow
    print(f"Quarterly cash flow: {cashflow.shape}")

def example_options():
    """4. Options Data"""
    print_section("Options Data")

    ticker = yf.Ticker("SPY")

    # Available expirations
    expirations = ticker.options
    print(f"Available expirations: {len(expirations)}")
    print(f"Next 3 dates: {expirations[:3]}")

    # Get option chain for nearest expiration
    if expirations:
        chain = ticker.option_chain(expirations[0])
        print(f"Calls: {len(chain.calls)} contracts")
        print(f"Puts: {len(chain.puts)} contracts")
        print(f"Sample call strike: ${chain.calls['strike'].iloc[0]:.2f}")

def example_analyst_data():
    """5. Analyst Ratings & Targets"""
    print_section("Analyst Data")

    ticker = yf.Ticker("NVDA")

    # Price targets
    targets = ticker.analyst_price_targets
    print(f"Analyst targets: {targets}")

    # Recommendations
    recommendations = ticker.recommendations
    if recommendations is not None and not recommendations.empty:
        print(f"Recommendation history: {len(recommendations)} entries")
        print(f"Latest: {recommendations.index[-1]}")

def example_multiple_tickers():
    """6. Multiple Tickers - Batch Operations"""
    print_section("Multiple Tickers")

    tickers = yf.Tickers('AAPL MSFT GOOGL')

    # Access individual tickers
    aapl_info = tickers.tickers['AAPL'].info
    print(f"AAPL: {aapl_info.get('longName')}")

    msft_info = tickers.tickers['MSFT'].info
    print(f"MSFT: {msft_info.get('longName')}")

    # Batch download
    data = yf.download(['AAPL', 'MSFT', 'GOOGL'], period='1mo', progress=False)
    print(f"Batch data shape: {data.shape}")

def example_funds():
    """7. Fund/ETF Data"""
    print_section("Fund/ETF Data")

    ticker = yf.Ticker("SPY")

    # Fund-specific info
    info = ticker.info
    print(f"Fund name: {info.get('longName')}")
    print(f"Total assets: ${info.get('totalAssets', 0):,}")

    # Top holdings (if available)
    try:
        holdings = ticker.funds_data.top_holdings
        print(f"Top holdings: {holdings}")
    except:
        print("Holdings data not available")

def example_search():
    """8. Search - Text Search for Quotes & News"""
    print_section("Search - Text Search")

    # Search for quotes and news
    print_code('search = yf.Search("artificial intelligence", max_results=5)')
    search = yf.Search("artificial intelligence", max_results=5)

    print(f"Search query: {search.query}")
    print(f"Total results: {len(search.quotes)}")

    # Display all quotes (not truncated)
    if search.quotes:
        print("\nAll quotes:")
        for i, quote in enumerate(search.quotes, 1):
            print(f"  {i}. {quote.get('symbol')} - {quote.get('shortname', 'N/A')}")
            print(f"     Type: {quote.get('quoteType', 'N/A')}")
            print(f"     Exchange: {quote.get('exchange', 'N/A')}")
            print(f"     Full quote dict: {quote}")

    # Display all news (not truncated)
    if search.news:
        print(f"\nAll news articles: {len(search.news)}")
        for i, article in enumerate(search.news, 1):
            print(f"\n  Article {i}:")
            print(f"    Title: {article.get('title', 'N/A')}")
            print(f"    Publisher: {article.get('publisher', 'N/A')}")
            print(f"    Link: {article.get('link', 'N/A')}")
            print(f"    Full article dict: {article}")

def example_market():
    """9. Market Information"""
    print_section("Market Information")

    try:
        # Get market data (requires market key like 'us_market')
        market = yf.Market('us_market')

        print(f"Market: US Market")
        print(f"Market object: {type(market)}")

        # Try to get market overview
        try:
            overview = market.overview
            if overview:
                print(f"Market overview available")
        except:
            pass

        print("Market provides broad market data and trends")
    except Exception as e:
        print(f"Market API: {str(e)[:100]}")

def example_sector_industry():
    """10. Sector & Industry Data"""
    print_section("Sector & Industry Data")

    try:
        # Get sector information
        print_code("sector = yf.Sector('technology')")
        sector = yf.Sector('technology')

        print(f"\nSector: Technology")
        print(f"Sector object: {type(sector)}")

        # Get industry information
        print()
        print_code("industry = yf.Industry('software-infrastructure')")
        industry = yf.Industry('software-infrastructure')

        print(f"\nIndustry: Software Infrastructure")
        print(f"Industry object: {type(industry)}")

        # Get top companies (full output)
        try:
            print()
            print_code("top_companies = industry.top_companies")
            top_companies = industry.top_companies
            if top_companies is not None:
                print(f"\nTop companies: {len(top_companies)}")
                print("\nAll top companies (full output):")
                print(top_companies)
        except Exception as e:
            print(f"Top companies error: {str(e)}")

        # Try to get sector overview
        try:
            print()
            print_code("overview = sector.overview")
            overview = sector.overview
            if overview:
                print(f"\nSector overview:")
                print(overview)
        except Exception as e:
            print(f"Sector overview: {str(e)}")

    except Exception as e:
        print(f"Sector/Industry API error: {str(e)}")

def example_screener():
    """11. Screener & EquityQuery"""
    print_section("Screener & EquityQuery")

    try:
        from yfinance.screener import EquityQuery, screen

        # Example 1: Predefined screen
        print("Example 1: Predefined screen")
        print_code("result = screen('most_actives')")
        result = screen('most_actives')

        if result and 'quotes' in result:
            quotes = result['quotes']
            print(f"\nMost active stocks: {len(quotes)}")
            print("\nAll results (full output):")
            for i, stock in enumerate(quotes, 1):
                print(f"\n  {i}. {stock.get('symbol')} - {stock.get('shortName', 'N/A')}")
                print(f"     Volume: {stock.get('regularMarketVolume', 0):,}")
                print(f"     Price: ${stock.get('regularMarketPrice', 0):.2f}")
                print(f"     Change: {stock.get('regularMarketChangePercent', 0):.2f}%")
                print(f"     Market Cap: ${stock.get('marketCap', 0):,}")

        # Example 2: Custom query
        print("\n" + "="*60)
        print("Example 2: Custom query")
        print_code("""custom_query = EquityQuery('and', [
    EquityQuery('gt', ['percentchange', 3]),
    EquityQuery('eq', ['region', 'us'])
])
result = screen(custom_query, count=5)""")

        custom_query = EquityQuery('and', [
            EquityQuery('gt', ['percentchange', 3]),
            EquityQuery('eq', ['region', 'us'])
        ])

        result2 = screen(custom_query, count=5)
        if result2 and 'quotes' in result2:
            quotes2 = result2['quotes']
            print(f"\nDay gainers (>3% change): {len(quotes2)}")
            print("\nAll results (full output):")
            for i, stock in enumerate(quotes2, 1):
                print(f"\n  {i}. {stock.get('symbol')} - {stock.get('shortName', 'N/A')}")
                print(f"     Price: ${stock.get('regularMarketPrice', 0):.2f}")
                print(f"     Change: {stock.get('regularMarketChangePercent', 0):.2f}%")
                print(f"     Volume: {stock.get('regularMarketVolume', 0):,}")

    except Exception as e:
        print(f"Screener API error: {str(e)}")

def run_all_examples():
    """Run all yfinance capability examples."""
    print("\n" + "="*60)
    print("yfinance Comprehensive Examples")
    print("="*60)

    example_historical_data()
    example_company_info()
    example_financials()
    example_options()
    example_analyst_data()
    example_multiple_tickers()
    example_funds()
    example_search()
    example_market()
    example_sector_industry()
    example_screener()

    print_section("Summary")
    print("""
    ✓ Historical prices - OHLCV data
    ✓ Company info - Fundamentals
    ✓ Financial statements - Income, balance, cash flow
    ✓ Options - Chains, strikes, Greeks
    ✓ Analyst data - Targets, recommendations
    ✓ Batch operations - Multiple tickers
    ✓ Fund data - ETF holdings
    ✓ Text search - Quotes and news by keyword
    ✓ Market data - Broad market information
    ✓ Sector/Industry - Classification and analysis
    ✓ Screener - Filter stocks by criteria

    Note: No API key required - uses Yahoo Finance public APIs
    """)

if __name__ == "__main__":
    run_all_examples()
