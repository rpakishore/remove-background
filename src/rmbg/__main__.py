"""Command-line entry point for the rmbg package.

This module provides entry points for both CLI and GUI interfaces.
"""

import sys
from pathlib import Path

import typer
from rich.console import Console

from rmbg import cli

app = typer.Typer(
    name="rmbg",
    help="Make specific colors transparent in images and PDFs.",
    add_completion=False,
)
console = Console()


@app.command()
def main(
    input_file: Path = typer.Argument(
        ...,
        help="Path to input image or PDF file",
        exists=True,
        dir_okay=False,
    ),
    output_file: Path = typer.Argument(
        ...,
        help="Path to output PNG file",
        dir_okay=False,
    ),
    color: str = typer.Option(
        "255,255,255",
        "--color",
        "-c",
        help="Target color in format R,G,B or #RRGGBB (default: white)",
    ),
    tolerance: int = typer.Option(
        10,
        "--tolerance",
        "-t",
        help="Color matching tolerance (0-255)",
        min=0,
        max=255,
    ),
    page: int = typer.Option(
        None,
        "--page",
        "-p",
        help="PDF page number (0-based, default: first page)",
        min=0,
    ),
    dpi: int = typer.Option(
        300,
        "--dpi",
        help="Output DPI for PNG files",
        min=72,
        max=1200,
    ),
) -> None:
    """Make a specific color transparent in an image or PDF page."""
    cli.main(input_file, output_file, color, tolerance, page, dpi)


@app.command()
def gui() -> None:
    """Launch the Streamlit GUI interface."""
    try:
        import subprocess
        import sys

        gui_path = Path(__file__).parent / "gui.py"
        subprocess.run([
            sys.executable, "-m", "streamlit", "run",
            str(gui_path)
        ], check=True)
    except ImportError:
        console.print(
            "[red]Error: Streamlit is not installed. "
            "Please install it with 'uv pip install streamlit'[/red]"
        )
        sys.exit(1)
    except subprocess.CalledProcessError as e:
        console.print(f"[red]Error launching GUI: {e}[/red]")
        sys.exit(1)


if __name__ == "__main__":
    app()
