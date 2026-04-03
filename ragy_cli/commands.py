from dataclasses import dataclass


@dataclass
class Command:
    name: str
    description: str
    tip: str


COMMANDS = [
    Command("search", "Search the web", "Usage: search"),
    Command("extract", "Extract relevant days", "Usage: extract"),
    Command("create", "Create 365-day index", "Usage: create"),
    Command("list", "List all collections", "Usage: list"),
    Command("show", "Show database content", "Usage: show"),
    Command("status", "Check collection status", "Usage: status"),
    Command("delete", "Delete a collection", "Usage: delete"),
    Command("health", "API health check", "Usage: health"),
    Command("info", "Embedding model info", "Usage: info"),
    Command("jobs", "Scheduler jobs", "Usage: jobs"),
    Command("help", "Show this help", "Usage: help"),
    Command("exit", "Exit CLI", "Usage: exit or quit"),
    Command("shutdown", "Exit CLI and stop API", "Usage: shutdown"),
]

COMMAND_MAP = {cmd.name: cmd for cmd in COMMANDS}
