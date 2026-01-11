"""Utility functions for displaying messages and prompts in Jupyter notebooks."""

import json
import re
from pathlib import Path

from rich.console import Console
from rich.panel import Panel
from rich.text import Text

console = Console()


def extract_chart_path(text: str) -> tuple[str, Path | None]:
    """Extract chart path from text and return cleaned text with optional chart path."""
    chart_pattern = r"\[CHART:([^\]]+)\]"
    match = re.search(chart_pattern, text)

    chart_path = None
    if match:
        chart_path = Path(match.group(1))
        if not chart_path.exists():
            chart_path = None
        # Remove the marker from the text
        text = re.sub(chart_pattern, "", text).strip()

    return text, chart_path


def display_chart(chart_path: Path) -> None:
    """Display a chart image in Jupyter notebook."""
    try:
        from IPython.display import Image, display
        display(Image(filename=str(chart_path)))
    except ImportError:
        pass  # Not in Jupyter environment


def format_message_content(message):
    """Convert message content to displayable string."""
    parts = []
    tool_calls_processed = False

    # Handle main content
    if isinstance(message.content, str):
        parts.append(message.content)
    elif isinstance(message.content, list):
        # Handle complex content like tool calls (Anthropic format)
        for item in message.content:
            if isinstance(item, str):
                parts.append(item)
            elif isinstance(item, dict):
                if item.get("type") == "text":
                    parts.append(item["text"])
                elif item.get("type") == "tool_use":
                    parts.append(f"\n🔧 Tool Call: {item['name']}")
                    parts.append(f"   Args: {json.dumps(item['input'], indent=2)}")
                    parts.append(f"   ID: {item.get('id', 'N/A')}")
                    tool_calls_processed = True
            else:
                parts.append(str(item))
    else:
        parts.append(str(message.content))

    # Handle tool calls attached to the message (OpenAI format) - only if not already processed
    if not tool_calls_processed and hasattr(message, "tool_calls") and message.tool_calls:
        for tool_call in message.tool_calls:
            parts.append(f"\n🔧 Tool Call: {tool_call['name']}")
            parts.append(f"   Args: {json.dumps(tool_call['args'], indent=2)}")
            parts.append(f"   ID: {tool_call['id']}")

    return "\n".join(parts)


def format_messages(messages):
    """Format and display a list of messages with Rich formatting."""
    for m in messages:
        msg_type = m.__class__.__name__.replace("Message", "")
        content = format_message_content(m)

        if msg_type == "Human":
            console.print(Panel(content, title="🧑 Human", border_style="blue"))
        elif msg_type == "Ai":
            console.print(Panel(content, title="🤖 Assistant", border_style="green"))
        elif msg_type == "Tool":
            # Check for chart markers and display charts after the panel
            cleaned_content, chart_path = extract_chart_path(content)
            console.print(Panel(cleaned_content, title="🔧 Tool Output", border_style="yellow"))
            if chart_path:
                display_chart(chart_path)
        else:
            console.print(Panel(content, title=f"📝 {msg_type}", border_style="white"))


def format_message(messages):
    """Alias for format_messages for backward compatibility."""
    return format_messages(messages)


def show_prompt(prompt_text: str, title: str = "Prompt", border_style: str = "blue"):
    """Display a prompt with rich formatting and XML tag highlighting.

    Args:
        prompt_text: The prompt string to display
        title: Title for the panel (default: "Prompt")
        border_style: Border color style (default: "blue")
    """
    # Create a formatted display of the prompt
    formatted_text = Text(prompt_text)
    formatted_text.highlight_regex(r"<[^>]+>", style="bold blue")  # Highlight XML tags
    formatted_text.highlight_regex(r"##[^#\n]+", style="bold magenta")  # Highlight headers
    formatted_text.highlight_regex(r"###[^#\n]+", style="bold cyan")  # Highlight sub-headers

    # Display in a panel for better presentation
    console.print(
        Panel(
            formatted_text,
            title=f"[bold green]{title}[/bold green]",
            border_style=border_style,
            padding=(1, 2),
        )
    )
