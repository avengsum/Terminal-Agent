from rich.console import Console
from rich.layout import Layout
from rich.panel import Panel
from rich.text import Text
from rich.live import Live
import time

console = Console()

def create_layout() -> Layout:
    """Creates the layout for the TUI."""
    layout = Layout()

    layout.split(
        Layout(name="header", size=3),
        Layout(ratio=1, name="main"),
        Layout(size=10, name="footer"),
    )

    layout["main"].split_row(Layout(name="side"), Layout(name="body", ratio=2))
    layout["side"].split(Layout(name="status"), Layout(name="tasks"))
    layout["body"].split(Layout(name="conversation"), Layout(name="logs"))
    layout["footer"].split_row(Layout(name="input"), Layout(name="help"))

    return layout

def draw_header() -> Panel:
    """Draws the header panel."""
    grid = Text(
        "AI Coding Agent",
        justify="center",
        style="bold magenta",
    )
    return Panel(grid, title="[bold green]TUI[/bold green]")

def draw_status() -> Panel:
    """Draws the agent status panel."""
    status_text = Text(
        "Status: Idle\n"
        "Current Task: None\n"
        "Last Action: None",
        style="yellow"
    )
    return Panel(status_text, title="[bold blue]Agent Status[/bold blue]")

def draw_tasks() -> Panel:
    """Draws the tasks panel."""
    task_text = Text(
        "1. [ ] Task 1\n"
        "2. [ ] Task 2\n"
        "3. [ ] Task 3",
        style="cyan"
    )
    return Panel(task_text, title="[bold blue]Tasks[/bold blue]")

def draw_conversation() -> Panel:
    """Draws the conversation panel."""
    conversation_text = Text(
        "User: Hello\n"
        "Agent: Hi there!",
        style="green"
    )
    return Panel(conversation_text, title="[bold blue]Conversation[/bold blue]")

def draw_logs() -> Panel:
    """Draws the logs panel."""
    log_text = Text(
        "Log messages will appear here...",
        style="dim"
    )
    return Panel(log_text, title="[bold blue]Logs[/bold blue]")

def draw_input(input_text: str = "") -> Panel:
    """Draws the user input panel."""
    return Panel(Text(f"> {input_text}", style="bold"), title="[bold blue]Input[/bold blue]")

def draw_help() -> Panel:
    """Draws the help panel."""
    help_text = Text(
        "Type 'exit' to quit.",
        style="dim"
    )
    return Panel(help_text, title="[bold blue]Help[/bold blue]")

def run():
    layout = create_layout()
    layout["header"].update(draw_header())
    layout["status"].update(draw_status())
    layout["tasks"].update(draw_tasks())
    layout["conversation"].update(draw_conversation())
    layout["logs"].update(draw_logs())
    layout["help"].update(draw_help())

    user_input = ""

    with Live(layout, console=console, screen=True, redirect_stderr=False) as live:
        while True:
            layout["input"].update(draw_input(user_input))
            
            # This is a simplified input handling. 
            # For a real application, we would use a library like `pynput` or `keyboard`
            # to handle key presses without blocking.
            # For now, we'll just simulate a non-blocking input.
            
            # A proper implementation would be:
            # key = console.input() 
            # but that blocks.
            
            # Let's just exit for now to prove the loop works.
            time.sleep(1)
            user_input += "a"
            if len(user_input) > 10:
                break


if __name__ == "__main__":
    run()
