<!--- Heading --->
<div align="center">
  <h1>RMBG - Remove Background</h1>
  <p>
    A powerful Python tool for removing backgrounds from images and PDFs, featuring both CLI and GUI interfaces.
  </p>
  <a href="https://rpakishore.github.io/remove-background">Documentation</a>
</div>
<br />

![GitHub commit activity](https://img.shields.io/github/commit-activity/m/rpakishore/remove-background)
![GitHub last commit](https://img.shields.io/github/last-commit/rpakishore/remove-background)
![Python Version](https://img.shields.io/badge/python-3.12%2B-blue)
![License](https://img.shields.io/badge/license-MPL%202.0-green)

<!-- Table of Contents -->
<h2>Table of Contents</h2>

- [Screenshot](#screenshot)
- [Features](#features)
- [Getting Started](#getting-started)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
- [Usage](#usage)
  - [Command Line Interface](#command-line-interface)
  - [Graphical User Interface](#graphical-user-interface)
- [Roadmap](#roadmap)
- [License](#license)
- [Contact](#contact)


## Screenshot
![Screengrab.png](./documents/Screengrab.png)

<!-- Features -->
## Features

- Remove backgrounds from images with high precision
- Process PDF documents and remove backgrounds from their pages
- Multiple output format support (PNG, JPEG, PDF)
- Command-line interface for batch processing
- User-friendly GUI built with Streamlit
- Fast and efficient processing
- Extensible architecture for custom background removal algorithms

<!-- Getting Started -->
## Getting Started

### Prerequisites

- uv package manager

### Installation

Clone this repo and run

```bash
# Using uv
uv run streamlit run src\rmbg\gui.py
```

<!-- Usage -->
## Usage

### Command Line Interface

```bash
# Remove background from an image
uv run rmbg process image.jpg

# Process a PDF file
uv run rmbg process document.pdf

# Specify output format
uv run rmbg process image.jpg --format png

# Process multiple files
uv run rmbg process *.jpg
```

### Graphical User Interface

Launch the GUI application:

```bash
uv run streamlit run src\rmbg\gui.py
```

The GUI provides an intuitive interface for:
- Uploading and processing images
- Previewing results
- Adjusting processing parameters
- Batch processing multiple files

<!-- Roadmap -->
## Roadmap

- [x] Set up a skeletal framework
- [x] Implement basic image processing
- [x] Add PDF support
- [x] Create CLI interface
- [x] Develop GUI application
- [ ] Add support for more image formats
- [ ] Implement batch processing optimization
- [ ] Add custom background removal algorithms
- [ ] Create plugin system for extensibility

<!-- License -->
## License

This project is licensed under the Mozilla Public License 2.0 (MPL 2.0) - see the [LICENSE](/LICENSE) file for details.

<!-- Contact -->
## Contact

Arun Kishore - [@rpakishore](mailto:pypi@rpakishore.co.in)

Project Link: [https://github.com/rpakishore/remove-background](https://github.com/rpakishore/remove-background)
