from dataclasses import dataclass


@dataclass
class Command:
    name: str
    description: str
    tip: str


COMMAND_GROUPS = {
    "Index Management": [
        Command("create_index", "Create 365-day index", "Usage: create_index"),
        Command("delete_index", "Delete a collection", "Usage: delete_index"),
        Command("upload_csv", "Upload CSV to collection", "Usage: upload_csv"),
    ],
    "Query & Extract": [
        Command("extract", "Extract relevant days", "Usage: extract"),
        Command("search_web", "Search web/financial data", "Usage: search_web"),
    ],
    "Browse": [
        Command("list", "List all collections", "Usage: list"),
        Command("status", "Check collection status", "Usage: status"),
        Command("sample", "Inspect a document", "Usage: sample"),
        Command("head_index", "Show first 5 documents", "Usage: head_index"),
        Command("tail_index", "Show last 5 documents", "Usage: tail_index"),
    ],
    "Analysis": [
        Command("stats", "Show database statistics", "Usage: stats"),
        Command("xray", "Visualize similarity timeline", "Usage: xray"),
    ],
    "Scheduling": [
        Command("jobs", "List scheduled jobs", "Usage: jobs"),
        Command("create_job", "Create scheduled job", "Usage: create_job"),
        Command("delete_job", "Delete scheduled job", "Usage: delete_job"),
    ],
    "System": [
        Command("health", "API health check", "Usage: health"),
        Command("info", "Embedding model info", "Usage: info"),
        Command("change_emb", "Change embedding model", "Usage: change_emb"),
        Command("help", "Show this help", "Usage: help"),
        Command("exit", "Exit CLI", "Usage: exit or quit"),
        Command("shutdown", "Exit CLI and stop API", "Usage: shutdown"),
    ],
}

COMMANDS = [cmd for group in COMMAND_GROUPS.values() for cmd in group]
COMMAND_MAP = {cmd.name: cmd for cmd in COMMANDS}
