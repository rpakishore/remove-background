"""Tests for the CLI module functionality."""

import warnings
from pathlib import Path
from unittest.mock import Mock, patch

import pytest
from PIL import Image
from typer.testing import CliRunner

from rmbg.cli import main, parse_color

warnings.filterwarnings(
    "ignore", category=DeprecationWarning, module="importlib._bootstrap"
)
warnings.filterwarnings(
    "ignore",
    category=DeprecationWarning,
    message="builtin type.*has no __module__ attribute",
)


@pytest.fixture
def cli_runner():
    """Create a CLI runner for testing."""
    return CliRunner()


@pytest.fixture
def sample_image_file(tmp_path):
    """Create a sample image file for testing."""
    img = Image.new("RGB", (100, 100), "white")
    img_array = img.load()
    # Add some red pixels in the center
    for x in range(25, 75):
        for y in range(25, 75):
            img_array[x, y] = (255, 0, 0)
    
    image_path = tmp_path / "test_image.png"
    img.save(image_path)
    return image_path


class TestParseColor:
    """Test the parse_color function."""

    def test_parse_rgb_comma_separated(self):
        """Test parsing RGB color in comma-separated format."""
        result = parse_color("255,128,64")
        assert result == (255, 128, 64)

    def test_parse_hex_color(self):
        """Test parsing hex color format."""
        result = parse_color("#FF8040")
        assert result == (255, 128, 64)

    def test_parse_hex_color_lowercase(self):
        """Test parsing hex color in lowercase."""
        result = parse_color("#ff8040")
        assert result == (255, 128, 64)

    def test_parse_hex_color_with_hash(self):
        """Test parsing hex color with hash prefix."""
        result = parse_color("#FFFFFF")
        assert result == (255, 255, 255)

    def test_parse_zero_values(self):
        """Test parsing color with zero values."""
        result = parse_color("0,0,0")
        assert result == (0, 0, 0)

    def test_parse_edge_values(self):
        """Test parsing color with edge values (0 and 255)."""
        result = parse_color("0,255,128")
        assert result == (0, 255, 128)

    def test_invalid_hex_length(self):
        """Test parsing invalid hex color length."""
        with pytest.raises(ValueError, match="Hex color must be in format #RRGGBB"):
            parse_color("#FF80")

    def test_invalid_hex_format(self):
        """Test parsing invalid hex format."""
        with pytest.raises(ValueError, match="invalid literal for int"):
            parse_color("#GGHHII")

    def test_invalid_rgb_format(self):
        """Test parsing invalid RGB format."""
        with pytest.raises(ValueError, match="Color must be in format R,G,B or #RRGGBB"):
            parse_color("255,128")

    def test_invalid_rgb_values_negative(self):
        """Test parsing RGB values that are negative."""
        with pytest.raises(ValueError, match="Color must be in format R,G,B or #RRGGBB"):
            parse_color("-1,128,64")

    def test_invalid_rgb_values_too_large(self):
        """Test parsing RGB values that are too large."""
        with pytest.raises(ValueError, match="Color must be in format R,G,B or #RRGGBB"):
            parse_color("256,128,64")

    def test_invalid_rgb_values_non_numeric(self):
        """Test parsing non-numeric RGB values."""
        with pytest.raises(ValueError, match="Color must be in format R,G,B or #RRGGBB"):
            parse_color("abc,128,64")

    def test_empty_string(self):
        """Test parsing empty string."""
        with pytest.raises(ValueError, match="Color must be in format R,G,B or #RRGGBB"):
            parse_color("")

    def test_invalid_format(self):
        """Test parsing invalid format."""
        with pytest.raises(ValueError, match="Color must be in format R,G,B or #RRGGBB"):
            parse_color("invalid_format")


class TestMainFunction:
    """Test the main function with various scenarios."""

    @patch("rmbg.cli.ImageProcessor")
    def test_successful_processing(self, mock_processor_class, sample_image_file, tmp_path):
        """Test successful image processing."""
        # Setup mocks
        mock_processor = Mock()
        mock_processor_class.return_value = mock_processor
        
        # Create a mock image
        mock_image = Image.new("RGBA", (100, 100), (255, 255, 255, 255))
        mock_processor.load_image.return_value = mock_image
        mock_processor.make_transparent.return_value = mock_image
        
        output_file = tmp_path / "output.png"
        
        # Call main function
        main(sample_image_file, output_file, "255,255,255", 10)
        
        # Verify calls
        mock_processor.load_image.assert_called_once_with(sample_image_file)
        mock_processor.make_transparent.assert_called_once_with(
            mock_image, (255, 255, 255), 10
        )
        mock_processor.save_image.assert_called_once_with(
            mock_image, output_file, (300, 300)
        )

    @patch("rmbg.cli.ImageProcessor")
    def test_hex_color_processing(self, mock_processor_class, sample_image_file, tmp_path):
        """Test processing with hex color format."""
        mock_processor = Mock()
        mock_processor_class.return_value = mock_processor
        
        mock_image = Image.new("RGBA", (100, 100), (255, 255, 255, 255))
        mock_processor.load_image.return_value = mock_image
        mock_processor.make_transparent.return_value = mock_image
        
        output_file = tmp_path / "output.png"
        
        # Call main function with hex color
        main(sample_image_file, output_file, "#FF0000", 15)
        
        # Verify hex color was parsed correctly
        mock_processor.make_transparent.assert_called_once_with(
            mock_image, (255, 0, 0), 15
        )

    @patch("rmbg.cli.ImageProcessor")
    def test_custom_dpi_processing(self, mock_processor_class, sample_image_file, tmp_path):
        """Test processing with custom DPI."""
        mock_processor = Mock()
        mock_processor_class.return_value = mock_processor
        
        mock_image = Image.new("RGBA", (100, 100), (255, 255, 255, 255))
        mock_processor.load_image.return_value = mock_image
        mock_processor.make_transparent.return_value = mock_image
        
        output_file = tmp_path / "output.png"
        
        # Call main function with custom DPI
        main(sample_image_file, output_file, "255,255,255", 10, dpi=600)
        
        # Verify custom DPI was used
        mock_processor.save_image.assert_called_once_with(
            mock_image, output_file, (600, 600)
        )

    @patch("rmbg.cli.ImageProcessor")
    def test_invalid_color_format(self, mock_processor_class, sample_image_file, tmp_path):
        """Test handling of invalid color format."""
        output_file = tmp_path / "output.png"
        
        # Call main function with invalid color
        with pytest.raises(Exception):  # Typer.Exit or SystemExit
            main(sample_image_file, output_file, "invalid_color", 10)

    @patch("rmbg.cli.ImageProcessor")
    def test_file_not_found_error(self, mock_processor_class, tmp_path):
        """Test handling of file not found error."""
        mock_processor = Mock()
        mock_processor_class.return_value = mock_processor
        mock_processor.load_image.side_effect = FileNotFoundError("File not found")
        
        input_file = tmp_path / "nonexistent.png"
        output_file = tmp_path / "output.png"
        
        # Call main function with non-existent file
        with pytest.raises(Exception):  # Typer.Exit or SystemExit
            main(input_file, output_file, "255,255,255", 10)

    @patch("rmbg.cli.ImageProcessor")
    def test_image_processing_error(self, mock_processor_class, sample_image_file, tmp_path):
        """Test handling of image processing error."""
        mock_processor = Mock()
        mock_processor_class.return_value = mock_processor
        mock_processor.load_image.return_value = Image.new("RGB", (100, 100))
        mock_processor.make_transparent.side_effect = ValueError("Processing failed")
        
        output_file = tmp_path / "output.png"
        
        # Call main function with processing error
        with pytest.raises(Exception):  # Typer.Exit or SystemExit
            main(sample_image_file, output_file, "255,255,255", 10)

    @patch("rmbg.cli.ImageProcessor")
    def test_save_error(self, mock_processor_class, sample_image_file, tmp_path):
        """Test handling of save error."""
        mock_processor = Mock()
        mock_processor_class.return_value = mock_processor
        
        mock_image = Image.new("RGBA", (100, 100), (255, 255, 255, 255))
        mock_processor.load_image.return_value = mock_image
        mock_processor.make_transparent.return_value = mock_image
        mock_processor.save_image.side_effect = ValueError("Save failed")
        
        output_file = tmp_path / "output.png"
        
        # Call main function with save error
        with pytest.raises(Exception):  # Typer.Exit or SystemExit
            main(sample_image_file, output_file, "255,255,255", 10)

    @patch("rmbg.cli.ImageProcessor")
    def test_default_parameters(self, mock_processor_class, sample_image_file, tmp_path):
        """Test main function with default parameters."""
        mock_processor = Mock()
        mock_processor_class.return_value = mock_processor
        
        mock_image = Image.new("RGBA", (100, 100), (255, 255, 255, 255))
        mock_processor.load_image.return_value = mock_image
        mock_processor.make_transparent.return_value = mock_image
        
        output_file = tmp_path / "output.png"
        
        # Call main function with only required parameters
        main(sample_image_file, output_file)
        
        # Verify default values were used
        mock_processor.make_transparent.assert_called_once_with(
            mock_image, (255, 255, 255), 10
        )
        mock_processor.save_image.assert_called_once_with(
            mock_image, output_file, (300, 300)
        )


class TestCLICommandLine:
    """Test the CLI as a command line application."""

    def test_cli_help(self, cli_runner):
        """Test CLI help output."""
        from rmbg.__main__ import app
        
        result = cli_runner.invoke(app, ["--help"])
        assert result.exit_code == 0
        assert "Make specific colors transparent in images and PDFs" in result.stdout

    def test_cli_basic_usage(self, cli_runner, sample_image_file, tmp_path):
        """Test basic CLI usage."""
        from rmbg.__main__ import app
        
        output_file = tmp_path / "output.png"
        
        with patch("rmbg.cli.ImageProcessor") as mock_processor_class:
            mock_processor = Mock()
            mock_processor_class.return_value = mock_processor
            
            mock_image = Image.new("RGBA", (100, 100), (255, 255, 255, 255))
            mock_processor.load_image.return_value = mock_image
            mock_processor.make_transparent.return_value = mock_image
            
            result = cli_runner.invoke(
                app, 
                ["main", str(sample_image_file), str(output_file)]
            )
            
            assert result.exit_code == 0
            assert "Successfully processed" in result.stdout

    def test_cli_with_all_options(self, cli_runner, sample_image_file, tmp_path):
        """Test CLI with all options specified."""
        from rmbg.__main__ import app
        
        output_file = tmp_path / "output.png"
        
        with patch("rmbg.cli.ImageProcessor") as mock_processor_class:
            mock_processor = Mock()
            mock_processor_class.return_value = mock_processor
            
            mock_image = Image.new("RGBA", (100, 100), (255, 255, 255, 255))
            mock_processor.load_image.return_value = mock_image
            mock_processor.make_transparent.return_value = mock_image
            
            result = cli_runner.invoke(
                app, 
                [
                    "main",
                    str(sample_image_file), 
                    str(output_file),
                    "--color", "#FF0000",
                    "--tolerance", "20",
                    "--dpi", "600"
                ]
            )
            
            assert result.exit_code == 0
            mock_processor.make_transparent.assert_called_once_with(
                mock_image, (255, 0, 0), 20
            )
            mock_processor.save_image.assert_called_once_with(
                mock_image, output_file, (600, 600)
            )

    def test_cli_invalid_color(self, cli_runner, sample_image_file, tmp_path):
        """Test CLI with invalid color format."""
        from rmbg.__main__ import app
        
        output_file = tmp_path / "output.png"
        
        result = cli_runner.invoke(
            app, 
            ["main", str(sample_image_file), str(output_file), "--color", "invalid"]
        )
        
        assert result.exit_code == 1
        assert "Error" in result.stdout

    def test_cli_file_not_found(self, cli_runner, tmp_path):
        """Test CLI with non-existent input file."""
        from rmbg.__main__ import app
        
        input_file = tmp_path / "nonexistent.png"
        output_file = tmp_path / "output.png"
        
        result = cli_runner.invoke(
            app, 
            ["main", str(input_file), str(output_file)]
        )
        
        assert result.exit_code == 2  # Typer returns 2 for argument errors
        assert "does not exist" in result.stdout

    def test_cli_gui_command(self, cli_runner):
        """Test CLI gui command."""
        from rmbg.__main__ import app
        
        with patch("rmbg.__main__.subprocess.run") as mock_run:
            mock_run.side_effect = ImportError("Streamlit not installed")
            
            result = cli_runner.invoke(app, ["gui"])
            
            assert result.exit_code == 1
            assert "Streamlit is not installed" in result.stdout 