from dataclasses import dataclass


@dataclass
class Command:
    name: str
    description: str
    tip: str


COMMANDS = [
    Command("search", "Search the web", "Usage: search"),
    Command("extract", "Extract relevant days", "Usage: extract"),
    Command("create_index", "Create 365-day index", "Usage: create_index"),
    Command("list", "List all collections", "Usage: list"),
    Command("stats", "Show database statistics", "Usage: stats"),
    Command("status", "Check collection status", "Usage: status"),
    Command("delete_index", "Delete a collection", "Usage: delete_index"),
    Command("health", "API health check", "Usage: health"),
    Command("info", "Embedding model info", "Usage: info"),
    Command("jobs", "List scheduled jobs", "Usage: jobs"),
    Command("create_job", "Create scheduled job", "Usage: create_job"),
    Command("delete_job", "Delete scheduled job", "Usage: delete_job"),
    Command("sample", "Inspect a document", "Usage: sample"),
    Command("head_index", "Show first 5 documents", "Usage: head_index"),
    Command("tail_index", "Show last 5 documents", "Usage: tail_index"),
    Command("change_emb", "Change embedding model", "Usage: change_emb"),
    Command("xray", "Visualize similarity timeline", "Usage: xray"),
    Command("help", "Show this help", "Usage: help"),
    Command("exit", "Exit CLI", "Usage: exit or quit"),
    Command("shutdown", "Exit CLI and stop API", "Usage: shutdown"),
]

COMMAND_MAP = {cmd.name: cmd for cmd in COMMANDS}
