# snap-html

<div align="center">

[![Build status](https://github.com/codustry/snap-html/workflows/build/badge.svg?branch=master&event=push)](https://github.com/codustry/snap-html/actions?query=workflow%3Abuild)
[![Python Version](https://img.shields.io/pypi/pyversions/snap-html.svg)](https://pypi.org/project/snap-html/)
[![Dependencies Status](https://img.shields.io/badge/dependencies-up%20to%20date-brightgreen.svg)](https://github.com/codustry/snap-html/pulls?utf8=%E2%9C%93&q=is%3Apr%20author%3Aapp%2Fdependabot)

[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Security: bandit](https://img.shields.io/badge/security-bandit-green.svg)](https://github.com/PyCQA/bandit)
[![Pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)](https://github.com/codustry/snap-html/blob/master/.pre-commit-config.yaml)
[![Semantic Versions](https://img.shields.io/badge/%F0%9F%9A%80-semantic%20versions-informational.svg)](https://github.com/codustry/snap-html/releases)
[![License](https://img.shields.io/github/license/codustry/snap-html)](https://github.com/codustry/snap-html/blob/master/LICENSE)

A robust, modern and high-performance Python library for generating images from HTML content.
Built on top of `playwright` for reliability and speed.

</div>

## 📋 Overview

**snap-html** is a Python library that allows you to generate images from:
- HTML strings
- HTML files
- URLs

### Key Features

- ✅ **Modern & Complete**: Async-ready, sync support, fully typed
- 🚀 **High Performance**: Built-in batch generator for processing multiple pages
- 🔧 **Easy Setup**: Built on Playwright with simplified browser installation
- 📐 **Precise Output**: Support for both pixel and physical dimensions (cm, inches)
- 🖼️ **Flexible Display**: Multiple object-fit options (contain, cover, fill)
- 🖨️ **Print-Ready**: Combined PrintMediaResolution for precise document sizing
- 💪 **Developer Friendly**: Sensible defaults with optional fine-tuning
- ⏱️ **Precise Timing**: Custom `RENDER_COMPLETE` signal for perfect screenshot timing

## 🧑‍💻 Development

### Modern Tooling

This project uses modern Python development tools:

- [**Mise**](https://mise.jdx.dev/): Runtime management and task orchestration
- [**uv**](https://github.com/astral-sh/uv): Fast Python package management
- [**Ruff**](https://astral.sh/ruff): Modern code formatting and linting

### Setup Development Environment

1. **Clone and setup**:
   ```bash
   git clone https://github.com/codustry/snap-html.git
   cd snap-html
   ```

2. **With Mise** (recommended):
   ```bash
   # Install Mise if you don't have it
   curl https://mise.run | sh
   
   # Setup project
   mise install
   mise run install
   ```

3. **With uv and venv**:
   ```bash
   # Create and activate virtual environment
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   
   # Install uv if you don't have it
   curl -LsSf https://astral.sh/uv/install.sh | sh
   
   # Install dependencies
   uv sync
   # With dev dependencies
   uv sync --dev
   ```

### Development Workflow

```bash
# Common development tasks with mise
mise run test        # Run tests
mise run format      # Format code
mise run check       # Run style checks
mise run check-safety # Run safety checks
mise run lint        # Run all checks
mise run build       # Build package
mise run publish     # Publish to PyPI

# Virtual environment management
mise run venv        # Create venv
mise run sync        # Install dependencies
mise run sync-dev    # Install dev dependencies
```

### Project Structure

```
snap-html/
├── .mise.toml            # Mise configuration and tasks
├── .mise/tasks/          # Custom task scripts
├── pyproject.toml        # Python project configuration
├── snap_html/            # Source code
└── tests/                # Test suite
```

## 📥 Installation

**With uv** (recommended):
```bash
uv add snap-html

# Install playwright browsers
python -m playwright install
```

**With pip**:
```bash
pip install -U snap-html
python -m playwright install
```

**System dependencies** (Linux only):
```bash
# Option 1: Install all required dependencies
sudo playwright install-deps

# Option 2: Manual installation
sudo apt-get install libwoff1 libevent-2.1-7t64 libgstreamer-plugins-base1.0-0 \
  libgstreamer-gl1.0-0 libgstreamer-plugins-bad1.0-0 libenchant-2-2 libsecret-1-0 \
  libhyphen0 libmanette-0.2-0
```

## 📸 Usage

### Basic Usage

```python
from snap_html import generate_image_sync
from pathlib import Path

# Capture from URL
screenshot = generate_image_sync(
    "https://www.example.com",
    resolution={"width": 1920, "height": 1080},
    output_file=Path("screenshot.png")
)

# Capture with physical dimensions (in centimeters)
screenshot = generate_image_sync(
    "https://www.example.com",
    resolution={
        "cm_width": 21,      # A4 width
        "cm_height": 29.7,   # A4 height
        "dpi": 300          # Print quality DPI
    },
    output_file=Path("high_quality.png")
)
```

### Resolution Options

The library supports multiple ways to specify output resolution:

1. **Pixel Dimensions**:
```python
resolution = {
    "width": 1920,    # Width in pixels
    "height": 1080    # Height in pixels
}
```

2. **Physical Dimensions**:
```python
resolution = {
    "cm_width": 21,    # Width in centimeters
    "cm_height": 29.7, # Height in centimeters
    "dpi": 300        # Dots per inch (optional, defaults to 300)
}
```

3. **Combined Print Media Resolution**:
```python
resolution = {
    # Screen dimensions (viewport)
    "width": 1920,     # Width in pixels
    "height": 1080,    # Height in pixels
    
    # Physical dimensions (print)
    "cm_width": 21,    # Width in centimeters
    "cm_height": 29.7, # Height in centimeters
    "dpi": 300,        # Dots per inch (optional, defaults to 300)
    
    # How content should fit within viewport (optional)
    "object_fit": "contain"  # Options: "contain", "cover", "fill", "none"
}
```

### Object Fit Options

When using combined dimensions, you can control how content fits:

- `"contain"` (default): Scale to fit while maintaining aspect ratio
- `"cover"`: Scale to fill while maintaining aspect ratio (may crop)
- `"fill"`: Stretch to fill (may distort proportions) 
- `"none"`: No scaling applied

```python
# In resolution dictionary
screenshot = generate_image_sync(
    "https://www.example.com",
    resolution={
        "width": 1920, "height": 1080,
        "cm_width": 21, "cm_height": 29.7,
        "dpi": 300,
        "object_fit": "cover"
    }
)

# Or as a separate parameter
screenshot = generate_image_sync(
    "https://www.example.com",
    resolution={
        "width": 1920, "height": 1080,
        "cm_width": 21, "cm_height": 29.7,
        "dpi": 300
    },
    object_fit="contain"
)
```

### Batch Processing

For better performance when capturing multiple screenshots:

```python
from snap_html import generate_image_batch_sync

screenshots = generate_image_batch_sync(
    targets=["https://example1.com", "https://example2.com"],
    resolution={"width": 1920, "height": 1080},
    output_files=["screenshot1.png", "screenshot2.png"]
)
```

### Advanced Examples

```python
from snap_html import generate_image_sync

# With all optional parameters using defaults
screenshot = generate_image_sync("https://www.example.com")

# Print media resolution with object-fit
screenshot = generate_image_sync(
    "https://www.example.com",
    resolution={
        "width": 1920, "height": 1080,
        "cm_width": 21, "cm_height": 29.7,
        "dpi": 300,
        "object_fit": "contain"
    },
    scale_factor=1.5  # Increase zoom level for sharper text
)
```

### Render Complete Signal

For pages with dynamic content or JavaScript animations, you can control exactly when the screenshot is taken using the `RENDER_COMPLETE` signal:

```python
from snap_html import generate_image_sync

# Specify a longer timeout for waiting for the RENDER_COMPLETE signal
screenshot = generate_image_sync(
    "https://www.example.com",
    render_timeout=15.0  # Wait up to 15 seconds for RENDER_COMPLETE signal
)
```

In your HTML/JavaScript, add a console log message to signal when rendering is complete:

```html
<script>
  // After your page is fully rendered and ready for screenshot
  window.addEventListener('load', function() {
    // Do any final rendering tasks
    setTimeout(function() {
      console.log('RENDER_COMPLETE');
    }, 500); // Add a small delay if needed
  });
</script>
```

This is particularly useful for:
- Pages with dynamic content loading
- JavaScript animations or transitions
- Asynchronous data fetching
- Custom rendering logic

If the `RENDER_COMPLETE` signal is not received within the specified timeout, snap-html will fall back to using the "networkidle" state to determine when to take the screenshot.

## 🖥️ CLI Usage

**Basic commands**:

```bash
# Basic usage with pixel dimensions
snap-html capture https://example.com -o screenshot.png --width 1920 --height 1080

# Using physical dimensions (e.g., A4 paper size)
snap-html capture input.html --cm-width 21.0 --cm-height 29.7 --dpi 300 -o output.png

# Capture with custom scale factor
snap-html capture https://example.com -o screenshot.png --width 1024 --height 768 --scale 2.0

# Using both pixel and physical dimensions with object-fit
snap-html capture https://example.com -o screenshot.png --width 1920 --height 1080 --cm-width 21.0 --cm-height 29.7 --object-fit cover

# Wait for RENDER_COMPLETE signal with custom timeout
snap-html capture https://example.com -o screenshot.png --render-timeout 15.0
```

**Available Options**:
```
  -o, --output PATH         Output image file path
  -w, --width INTEGER       Output width in pixels
  -h, --height INTEGER      Output height in pixels
  --cm-width FLOAT          Output width in centimeters
  --cm-height FLOAT         Output height in centimeters
  --dpi INTEGER             DPI for cm-based resolution [default: 300]
  --scale FLOAT             Browser scale factor (zoom level) [default: 1.5]
  --object-fit TEXT         How content fits viewport: contain, cover, fill, none [default: contain]
  --render-timeout FLOAT    Time to wait for RENDER_COMPLETE signal (in seconds) [default: 10.0]
  --help                    Show this message and exit.
```

## 📦 Releases & Versioning

We follow [Semantic Versions](https://semver.org/) specification. You can see all releases on the [GitHub Releases](https://github.com/codustry/snap-html/releases) page.

## 🛡️ License

This project is licensed under the terms of the `MIT` license. See [LICENSE](https://github.com/codustry/snap-html/blob/master/LICENSE) for more details.

## 🔄 Alternatives

1. [html2image](https://github.com/vgalin/html2image)

## 📃 Citation

```
@misc{snap-html,
  author = {codustry},
  title = {A robust, modern and high performance Python library for generating images from HTML},
  year = {2021},
  publisher = {GitHub},
  journal = {GitHub repository},
  howpublished = {\url{https://github.com/codustry/snap-html}}
}
```
