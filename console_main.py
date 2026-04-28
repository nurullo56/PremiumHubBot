# main.py
from utils.console import log, console, ProgressTracker, create_table
import time

# Simple logging
log.success("Server started on port 8000")
log.error("Database connection failed")
log.warning("High memory usage detected")
log.info("Processing 100 records")

# Panel
log.panel("Bot Status", "✅ Running\n📊 1234 users\n⚡ 45 req/s", style="green")

# Progress bar
with ProgressTracker.create() as progress:
    task = progress.add_task("[cyan]Processing...", total=100)
    for i in range(100):
        time.sleep(0.01)
        progress.update(task, advance=1)

# Table
table = create_table("Users", ["ID", "Name", "Status"])
table.add_row("1", "Nurulloh", "[green]Active[/green]")
table.add_row("2", "John", "[red]Banned[/red]")
console.print(table)

# JSON pretty print
data = {"bot": "PremiumHub", "users": 1234, "active": True}
console.print_json(data=data)