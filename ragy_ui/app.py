from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, Static
from textual.containers import Container, Center

ASCII_LOGO = """[bold #0066FF]██████╗    █████╗    ██████╗   ██╗   ██╗[/bold #0066FF]
[bold #0080FF]██╔══██╗  ██╔══██╗  ██╔════╝   ╚██╗ ██╔╝[/bold #0080FF]
[bold #0099FF]██████╔╝  ███████║  ██║  ███╗   ╚████╔╝ [/bold #0099FF]
[bold #00BBFF]██╔══██╗  ██╔══██║  ██║   ██║    ╚██╔╝  [/bold #00BBFF]
[bold #00DDFF]██║  ██║  ██║  ██║  ╚██████╔╝     ██║   [/bold #00DDFF]
[bold cyan]╚═╝  ╚═╝  ╚═╝  ╚═╝   ╚═════╝      ╚═╝   [/bold cyan]"""

SUBTITLE = "[dim]✧[/dim] [dim]⋆[/dim] [dim]✦[/dim] [dim]･[/dim] [dim]°[/dim] [dim]✧[/dim]  [italic #00DDFF]RAG a Year[/italic #00DDFF]  [dim]✧[/dim] [dim]°[/dim] [dim]･[/dim] [dim]✦[/dim] [dim]⋆[/dim] [dim]✧[/dim]"


class RagyApp(App):
    CSS_PATH = "app.css"
    BINDINGS = [("q", "quit", "Quit")]

    def compose(self) -> ComposeResult:
        yield Header()
        yield Container(
            Center(Static(ASCII_LOGO, id="logo")),
            Center(Static(SUBTITLE, id="subtitle")),
            Center(Static("\n[dim]Press [bold yellow]'q'[/bold yellow] to quit[/dim]", id="help")),
        )
        yield Footer()


app = RagyApp()

if __name__ == "__main__":
    app.run()
