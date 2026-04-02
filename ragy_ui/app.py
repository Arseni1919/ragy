from textual.app import App, ComposeResult
from textual.widgets import Header, Static, Input
from textual.containers import VerticalScroll, Container
from textual.suggester import Suggester
from textual import events

from ragy_ui.constants import ASCII_LOGO, SUBTITLE, SLASH_COMMANDS


class SlashCommandSuggester(Suggester):
    def __init__(self):
        super().__init__(use_cache=True, case_sensitive=False)

    async def get_suggestion(self, value: str) -> str | None:
        """Get suggestion for slash commands only."""
        if not value.startswith("/"):
            return None

        for cmd in SLASH_COMMANDS:
            if cmd.startswith(value.lower()) and cmd != value:
                return cmd

        return None


class RagyApp(App):
    CSS_PATH = "app.css"
    BINDINGS = [("q", "quit", "Quit")]

    def compose(self) -> ComposeResult:
        yield Header()
        with VerticalScroll(id="chat-history"):
            yield Static(ASCII_LOGO, classes="message logo")
            yield Static(SUBTITLE, classes="message subtitle")
        with Container(id="input-container"):
            yield Input(
                placeholder="Type a message...",
                id="chat-input",
                suggester=SlashCommandSuggester()
            )

    async def on_key(self, event: events.Key) -> None:
        """Handle Tab key to accept autocomplete."""
        if event.key == "tab":
            chat_input = self.query_one("#chat-input", Input)

            if hasattr(chat_input, "_suggestion") and chat_input._suggestion:
                event.prevent_default()
                event.stop()
                chat_input.value = chat_input._suggestion
                chat_input.cursor_position = len(chat_input._suggestion)

    def on_input_submitted(self, event: Input.Submitted) -> None:
        text = event.value
        if text.strip():
            chat_history = self.query_one("#chat-history", VerticalScroll)
            chat_history.mount(Static(f"[bold cyan]You:[/bold cyan] {text}", classes="message user"))
            event.input.value = ""
            chat_history.scroll_end(animate=False)


app = RagyApp()

if __name__ == "__main__":
    app.run()
