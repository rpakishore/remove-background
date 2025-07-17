"""Streamlit GUI for the image transparency tool.

This module provides a graphical user interface for making colors transparent
in images using Streamlit and streamlit-image-coordinates for color selection.
"""

import io
import tempfile
from pathlib import Path
from typing import Tuple

import streamlit as st
from streamlit_image_coordinates import streamlit_image_coordinates as sic
from rmbg.core import ImageProcessor


def hex_to_rgb(hex_color: str) -> Tuple[int, int, int]:
    """Convert hex color to RGB tuple.

    Args:
        hex_color: Hex color string (e.g., "#RRGGBB").

    Returns:
        RGB tuple of integers.
    """
    hex_color = hex_color.lstrip("#")
    return tuple(int(hex_color[i : i + 2], 16) for i in (0, 2, 4))


def rgb_to_hex(rgb: Tuple[int, int, int]) -> str:
    """Convert RGB tuple to hex color.

    Args:
        rgb: RGB tuple of integers.

    Returns:
        Hex color string.
    """
    return f"#{rgb[0]:02x}{rgb[1]:02x}{rgb[2]:02x}"


def main() -> None:
    """Run the Streamlit GUI application."""
    st.set_page_config(
        page_title="Remove Background",
        page_icon="🎨",
        layout="wide",
    )

    st.title("Remove Background")
    st.markdown(
        "Upload an image or PDF and select a color to make it transparent. "
        "Adjust the tolerance to control the transparency effect."
    )

    uploaded_file = st.file_uploader(
        "Choose an image or PDF file",
        type=["png", "jpg", "jpeg", "pdf"],
    )

    if uploaded_file is None:
        st.info("Please upload a file to begin.")
        return

    processor = ImageProcessor()

    try:
        # Create a temporary file with a unique name
        with tempfile.NamedTemporaryFile(delete=False, suffix=Path(uploaded_file.name).suffix) as temp_file:
            temp_file.write(uploaded_file.getvalue())
            temp_path = Path(temp_file.name)

        image = processor.load_image(temp_path)

        # Try to delete the temp file, but don't fail if it's still in use
        try:
            temp_path.unlink()
        except (OSError, PermissionError):
            # File might still be in use, that's okay
            pass

    except Exception as e:
        st.error(f"Error loading file: {e}")
        return

    st.subheader("Color Selection")
    
    # Add toggle for color selection method
    color_method = st.radio(
        "Choose how to select the color:",
        ["Color picker", "Click on image"],
        horizontal=True
    )

    target_color = None
    selected_color = None

    if color_method == "Click on image":
        st.markdown("Click on the image below to select a color to make transparent.")

        _l, _r = st.columns([4, 1])
        with _l:
            coord = sic(image, width=600, key="pil")

        if coord is not None:
            x = int(coord["x"] * image.size[0] / coord["width"])
            y = int(coord["y"] * image.size[1] / coord["height"])

            target_color = image.getpixel((x, y))
            selected_color = rgb_to_hex(target_color)

            _r.markdown(f"Selected color: {selected_color}")

            _r.markdown(
                f'<div style="width: 50px; height: 50px; background-color: {selected_color}; border: 1px solid black;"></div>',
                unsafe_allow_html=True,
            )
    else:
        st.markdown("Use the color picker below to select a color to make transparent.")
        
        picked_color = st.color_picker(
            "Choose a color",
            value="#ffffff",
            key="color_picker"
        )
        
        if picked_color:
            target_color = hex_to_rgb(picked_color)
            selected_color = picked_color
            
            col1, col2 = st.columns([1, 3])
            with col1:
                st.markdown(f"Selected color: {selected_color}")
                st.markdown(
                    f'<div style="width: 50px; height: 50px; background-color: {selected_color}; border: 1px solid black;"></div>',
                    unsafe_allow_html=True,
                )

    tolerance = st.slider(
        "Color tolerance",
        min_value=0,
        max_value=255,
        value=10,
        help="Higher values will match more similar colors",
    )
    
    if target_color is None:
        st.warning("Please select a color first.")
        st.stop()

    if st.button("Make Transparent", key="make_transparent_button"):
        with st.spinner("Processing image..."):
            result = processor.make_transparent(image, target_color, tolerance)

            st.subheader("Result")
            st.image(result)

            buf = io.BytesIO()
            result.save(buf, format="PNG")
            st.download_button(
                "Download Result",
                buf.getvalue(),
                file_name="transparent.png",
                mime="image/png",
            )


if __name__ == "__main__":
    main()
