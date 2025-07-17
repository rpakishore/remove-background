"""
.. include:: ../../README.md
"""

from .cli import main as cli_main
from .core import ImageProcessor
from .gui import main as gui_main

__version__ = "0.1.0"
__all__ = ["ImageProcessor", "cli_main", "gui_main"]
