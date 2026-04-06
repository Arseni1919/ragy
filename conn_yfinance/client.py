"""
yfinance client for accessing Yahoo Finance data.
No API key required - uses public Yahoo Finance APIs.
"""
import yfinance as yf

def get_ticker(symbol: str):
    """Get a Ticker object for a symbol."""
    return yf.Ticker(symbol)

def get_tickers(symbols: str):
    """Get Tickers object for multiple symbols."""
    return yf.Tickers(symbols)

def download_data(tickers, period='1mo', **kwargs):
    """Download historical data for ticker(s)."""
    return yf.download(tickers, period=period, **kwargs)
