# utils/console.py
from rich.console import Console
from rich.theme import Theme
from rich.table import Table
from rich.panel import Panel
from rich.progress import (
    Progress,
    SpinnerColumn,
    TextColumn,
    BarColumn,
    TaskProgressColumn,
    TimeRemainingColumn,
)
from typing import Any

# Custom theme
custom_theme = Theme({
    "success": "bold green",
    "error": "bold red",
    "warning": "bold yellow",
    "info": "bold cyan",
    "debug": "dim white",
})

console = Console(theme=custom_theme)


class Logger:
    """Production-ready logger with Rich formatting"""
    
    @staticmethod
    def success(message: str, **kwargs: Any) -> None:
        console.print(f"✅ {message}", style="success", **kwargs)
    
    @staticmethod
    def error(message: str, **kwargs: Any) -> None:
        console.print(f"❌ {message}", style="error", **kwargs)
    
    @staticmethod
    def warning(message: str, **kwargs: Any) -> None:
        console.print(f"⚠️  {message}", style="warning", **kwargs)
    
    @staticmethod
    def info(message: str, **kwargs: Any) -> None:
        console.print(f"ℹ️  {message}", style="info", **kwargs)
    
    @staticmethod
    def debug(message: str, **kwargs: Any) -> None:
        console.print(f"🐛 {message}", style="debug", **kwargs)
    
    @staticmethod
    def panel(title: str, content: str, style: str = "info") -> None:
        console.print(Panel(content, title=title, border_style=style))


class ProgressTracker:
    """Reusable progress bar context manager"""
    
    @staticmethod
    def create() -> Progress:
        return Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TaskProgressColumn(),
            TimeRemainingColumn(),
            console=console,
        )


def create_table(title: str, columns: list[str]) -> Table:
    """Factory for styled tables"""
    table = Table(title=title, show_header=True, header_style="bold magenta")
    for col in columns:
        table.add_column(col)
    return table


# Singleton instance
log = Logger()