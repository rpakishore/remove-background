"""
Command Line Interface for the image transparency tool.

This module provides a CLI interface for making colors transparent in images
using Typer for argument parsing and rich for console output.
"""

from pathlib import Path

import typer
from rich.console import Console
from rich.panel import Panel

from .core import ImageProcessor

console = Console()


def parse_color(color_str: str) -> tuple[int, int, int]:
	"""
	Parse color string into RGB tuple.

	Args:
	    color_str: Color string in format "R,G,B" or hex "#RRGGBB".

	Returns:
	    RGB tuple of integers.

	Raises:
	    ValueError: If color string format is invalid.

	"""
	if color_str.startswith("#"):
		color_str = color_str.lstrip("#")
		if len(color_str) != 6:
			raise ValueError("Hex color must be in format #RRGGBB")
		return tuple(int(color_str[i : i + 2], 16) for i in (0, 2, 4))
	try:
		r, g, b = map(int, color_str.split(","))
		if not all(0 <= x <= 255 for x in (r, g, b)):
			raise ValueError
		return (r, g, b)
	except ValueError:
		raise ValueError("Color must be in format R,G,B or #RRGGBB") from None


def main(
	input_file: Path,
	output_file: Path,
	color: str = "255,255,255",
	tolerance: int = 10,
	page: int | None = None,
	dpi: int = 300,
) -> None:
	"""
	Make a specific color transparent in an image or PDF page.

	Args:
	    input_file: Path to input image or PDF file.
	    output_file: Path to output PNG file.
	    color: Target color in format R,G,B or #RRGGBB (default: white).
	    tolerance: Color matching tolerance (0-255).
	    page: PDF page number (0-based, default: first page).
	    dpi: Output DPI for PNG files.

	"""
	try:
		target_color = parse_color(color)

		processor = ImageProcessor()

		with console.status("Loading image..."):
			image = processor.load_image(input_file)

		with console.status("Processing image..."):
			result = processor.make_transparent(image, target_color, tolerance)

		with console.status("Saving result..."):
			processor.save_image(result, output_file, (dpi, dpi))

		console.print(
			Panel(
				f"Successfully processed [bold]{input_file}[/] to [bold]{output_file}[/]",
				title="Success",
				border_style="green",
			)
		)

	except Exception as e:
		console.print(
			Panel(
				str(e),
				title="Error",
				border_style="red",
			)
		)
		raise typer.Exit(1) from None
