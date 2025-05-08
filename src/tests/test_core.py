"""Tests for the core image processing functionality."""

import warnings

warnings.filterwarnings(
    "ignore", category=DeprecationWarning, module="importlib._bootstrap"
)
warnings.filterwarnings(
    "ignore",
    category=DeprecationWarning,
    message="builtin type.*has no __module__ attribute",
)

import pytest
from PIL import Image
import numpy as np

from rmbg.core import ImageProcessor


@pytest.fixture
def processor():
    """Create an ImageProcessor instance for testing."""
    return ImageProcessor()


@pytest.fixture
def sample_image(tmp_path):
    """Create a sample image for testing."""
    img = Image.new("RGB", (100, 100), "white")
    img_array = np.array(img)
    img_array[25:75, 25:75] = [255, 0, 0]
    return Image.fromarray(img_array)


def test_make_transparent_white(processor, sample_image, tmp_path):
    """Test making white color transparent."""
    result = processor.make_transparent(sample_image, (255, 255, 255), 10)

    assert result.mode == "RGBA"

    result_array = np.array(result)
    white_mask = (
        (result_array[:, :, 0] == 255)
        & (result_array[:, :, 1] == 255)
        & (result_array[:, :, 2] == 255)
    )
    assert np.all(result_array[white_mask, 3] == 0)


def test_make_transparent_red(processor, sample_image, tmp_path):
    """Test making red color transparent."""
    result = processor.make_transparent(sample_image, (255, 0, 0), 10)

    assert result.mode == "RGBA"

    result_array = np.array(result)
    red_mask = (
        (result_array[:, :, 0] == 255)
        & (result_array[:, :, 1] == 0)
        & (result_array[:, :, 2] == 0)
    )
    assert np.all(result_array[red_mask, 3] == 0)

    white_mask = (
        (result_array[:, :, 0] == 255)
        & (result_array[:, :, 1] == 255)
        & (result_array[:, :, 2] == 255)
    )
    assert np.all(result_array[white_mask, 3] == 255)


def test_save_image(processor, sample_image, tmp_path):
    """Test saving processed image."""
    result = processor.make_transparent(sample_image, (255, 255, 255), 10)

    output_path = tmp_path / "output.png"
    processor.save_image(result, output_path)

    assert output_path.exists()

    saved_image = Image.open(output_path)
    assert saved_image.mode == "RGBA"


def test_invalid_output_format(processor, sample_image, tmp_path):
    """Test saving with invalid output format."""
    result = processor.make_transparent(sample_image, (255, 255, 255), 10)

    output_path = tmp_path / "output.jpg"
    with pytest.raises(ValueError, match="Output must be in PNG format"):
        processor.save_image(result, output_path)
