TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "list_collections",
            "description": "Lists all available indexed topics/collections in the database. Use this first to discover what data is available.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "ragy_extractor",
            "description": "Search a specific collection in the 365-day indexed database for relevant days. Returns dates with content (or just dates if date-only mode).",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search query to find relevant days"
                    },
                    "collection_name": {
                        "type": "string",
                        "description": "Name of the collection to search (from list_collections)"
                    },
                    "top_k": {
                        "type": "integer",
                        "description": "Number of top results to return",
                        "default": 10
                    }
                },
                "required": ["query", "collection_name"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "tavily_search",
            "description": "Search the web for current information. Use when database has no content (date-only mode) or for recent/live data.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search query"
                    }
                },
                "required": ["query"]
            }
        }
    }
]
