"""Basic yfinance client test - validates connection and data retrieval."""
from conn_yfinance.client import get_ticker, download_data

print("Testing yfinance client...")

# Test 1: Single ticker info
ticker = get_ticker("AAPL")
info = ticker.info
print(f"✓ Company: {info.get('longName', 'N/A')}")
print(f"✓ Sector: {info.get('sector', 'N/A')}")
print(f"✓ Market Cap: ${info.get('marketCap', 0):,}")

# Test 2: Historical data
hist = download_data("AAPL", period="5d")
print(f"✓ Downloaded {len(hist)} days of data")
latest_close = hist['Close'].iloc[-1]
if hasattr(latest_close, 'item'):
    latest_close = latest_close.item()
print(f"✓ Latest close: ${latest_close:.2f}")

print("\n✅ All tests passed!")
