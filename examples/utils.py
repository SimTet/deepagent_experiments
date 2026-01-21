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
        if message.content:  # Only add non-empty content
            parts.append(message.content)
    elif isinstance(message.content, list):
        # Handle complex content like tool calls (Anthropic format)
        for item in message.content:
            if isinstance(item, str):
                if item:  # Only add non-empty strings
                    parts.append(item)
            elif isinstance(item, dict):
                if item.get("type") == "text":
                    text = item.get("text", "")
                    if text:
                        parts.append(text)
                elif item.get("type") == "tool_use":
                    parts.append(f"\n🔧 Tool Call: {item['name']}")
                    parts.append(f"   Args: {json.dumps(item.get('input', {}), indent=2)}")
                    parts.append(f"   ID: {item.get('id', 'N/A')}")
                    tool_calls_processed = True
            else:
                parts.append(str(item))
    elif message.content is not None:
        parts.append(str(message.content))

    # Handle tool calls attached to the message (OpenAI/Gemini format)
    # Check both message.tool_calls and additional_kwargs for compatibility
    tool_calls = None
    if not tool_calls_processed:
        # Standard LangChain format
        if hasattr(message, "tool_calls") and message.tool_calls:
            tool_calls = message.tool_calls
        # Gemini/Google format - check additional_kwargs
        elif hasattr(message, "additional_kwargs"):
            additional = message.additional_kwargs or {}
            # Check for function_call (single call format)
            if "function_call" in additional:
                fc = additional["function_call"]
                tool_calls = [{
                    "name": fc.get("name", "unknown"),
                    "args": json.loads(fc.get("arguments", "{}")) if isinstance(fc.get("arguments"), str) else fc.get("arguments", {}),
                    "id": fc.get("id", "N/A"),
                }]
            # Check for tool_calls in additional_kwargs
            elif "tool_calls" in additional:
                tool_calls = additional["tool_calls"]

    if tool_calls:
        for tool_call in tool_calls:
            # Handle both dict format and object format
            if isinstance(tool_call, dict):
                name = tool_call.get("name", "unknown")
                args = tool_call.get("args", tool_call.get("arguments", {}))
                tc_id = tool_call.get("id", "N/A")
            else:
                # Object format (e.g., ToolCall namedtuple or class)
                name = getattr(tool_call, "name", "unknown")
                args = getattr(tool_call, "args", getattr(tool_call, "arguments", {}))
                tc_id = getattr(tool_call, "id", "N/A")

            # Parse args if it's a JSON string
            if isinstance(args, str):
                try:
                    args = json.loads(args)
                except json.JSONDecodeError:
                    pass

            parts.append(f"\n🔧 Tool Call: {name}")
            parts.append(f"   Args: {json.dumps(args, indent=2) if isinstance(args, dict) else str(args)}")
            parts.append(f"   ID: {tc_id}")

    # If no content and no tool calls, show placeholder
    if not parts:
        parts.append("(No content)")

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
