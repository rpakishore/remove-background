"""Core image processing functionality for making colors transparent.

This module provides the fundamental functionality for making specific colors
transparent in images. It handles both image and PDF input formats.
"""

from pathlib import Path
from typing import Tuple, Union

import fitz
from PIL import Image
import numpy as np
from rich.console import Console


class ImageProcessor:
    """Core class for processing images and making colors transparent."""

    def __init__(self) -> None:
        """Initialize the ImageProcessor."""
        self._console = Console()

    def load_image(self, file_path: Union[str, Path]) -> Image.Image:
        """Load an image from a file path.

        Args:
            file_path: Path to the image file (PNG, JPG, etc.) or PDF file.

        Returns:
            PIL Image object.

        Raises:
            FileNotFoundError: If the file doesn't exist.
            ValueError: If the file format is not supported.
        """
        file_path = Path(file_path)
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        if file_path.suffix.lower() == ".pdf":
            return self._load_pdf_page(file_path)

        try:
            return Image.open(file_path)
        except Exception as e:
            raise ValueError(f"Failed to load image: {e}")

    def _load_pdf_page(self, pdf_path: Path, page_number: int = 0) -> Image.Image:
        """Load a specific page from a PDF file.

        Args:
            pdf_path: Path to the PDF file.
            page_number: Page number to load (0-based).

        Returns:
            PIL Image object of the PDF page.

        Raises:
            ValueError: If the page number is invalid or PDF is corrupted.
        """
        try:
            doc = fitz.open(pdf_path)
            if page_number >= len(doc):
                raise ValueError(f"Page number {page_number} out of range")

            page = doc[page_number]
            pix = page.get_pixmap()
            img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
            return img
        except Exception as e:
            raise ValueError(f"Failed to load PDF page: {e}")

    def make_transparent(
        self,
        image: Image.Image,
        target_color: Tuple[int, int, int],
        tolerance: int = 10,
    ) -> Image.Image:
        """Make a specific color transparent in the image.

        Args:
            image: PIL Image object to process.
            target_color: RGB tuple of the color to make transparent.
            tolerance: Color matching tolerance (0-255).

        Returns:
            PIL Image with transparency.
        """
        if image.mode != "RGBA":
            image = image.convert("RGBA")

        data = np.array(image)

        r, g, b, *_ = target_color
        mask = (
            (abs(data[:, :, 0] - r) <= tolerance)
            & (abs(data[:, :, 1] - g) <= tolerance)
            & (abs(data[:, :, 2] - b) <= tolerance)
        )

        # Create a copy of the data to avoid modifying the original
        result = data.copy()

        # Set alpha channel to 0 for matching pixels, preserve original alpha for others
        result[:, :, 3] = np.where(mask, 0, 255)

        return Image.fromarray(result)

    def save_image(
        self,
        image: Image.Image,
        output_path: Union[str, Path],
        dpi: Tuple[int, int] = (300, 300),
    ) -> None:
        """Save the processed image to a file.

        Args:
            image: PIL Image object to save.
            output_path: Path where to save the image.
            dpi: DPI resolution for the output image.

        Raises:
            ValueError: If the output format is not supported.
        """
        output_path = Path(output_path)
        if output_path.suffix.lower() != ".png":
            raise ValueError("Output must be in PNG format")

        image.save(output_path, "PNG", dpi=dpi)
