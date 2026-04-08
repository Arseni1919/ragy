"""
Application-wide constants.
"""

AVAILABLE_SOURCES = ['bright_data', 'tavily', 'yfinance']

SOURCE_DESCRIPTIONS = {
    'tavily': 'web search',
    'yfinance': 'financial data',
    'bright_data': 'web search via Bright Data'
}

def get_sources_prompt() -> str:
    """Generate user-facing prompt for available sources."""
    desc = ', '.join([f"{src} ({SOURCE_DESCRIPTIONS[src]})" for src in AVAILABLE_SOURCES])
    return f"Available data sources: {desc}"
