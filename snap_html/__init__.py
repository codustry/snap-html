# mypy: disable-error-code="attr-defined"
"""a robust, modern and high performance Python library for generating image from a html string/html file/url build on top of `playwright`"""

try:
    from importlib.metadata import version
    from importlib.metadata import PackageNotFoundError
except ImportError:  # pragma: no cover
    from importlib_metadata import version  # type: ignore
    from importlib_metadata import PackageNotFoundError  # type: ignore

import pint

class UnitConverter:
    def __init__(self):
        self.ureg = pint.UnitRegistry()
    
    def cm_to_pixels(self, cm: float, dpi: int) -> int:
        """Convert centimeters to pixels based on DPI"""
        # Create a quantity from the cm value
        cm_quantity = cm * self.ureg.cm
        # Convert to inches
        inches = cm_quantity.to(self.ureg.inch).magnitude
        # Calculate pixels
        return int(round(inches * dpi))

try:
    __version__ = version(__name__)
except PackageNotFoundError:  # pragma: no cover
    __version__ = "unknown"

from typing import Dict, List, Optional, TypedDict, Union, Any
from playwright.async_api import ViewportSize, BrowserContext

import asyncio
import tempfile
from dataclasses import dataclass
from pathlib import Path
from textwrap import dedent

from furl import furl
from playwright.async_api import async_playwright


class PixelResolution(TypedDict):
    width: int
    height: int

class CMResolution(TypedDict):
    cm_width: float
    cm_height: float
    dpi: int

# Supported object-fit values (similar to CSS object-fit)
class ObjectFit:
    CONTAIN = "contain"  # Scale to fit within viewport while maintaining aspect ratio
    COVER = "cover"      # Scale to fill viewport while maintaining aspect ratio
    FILL = "fill"        # Stretch to fill viewport (may distort)
    NONE = "none"        # No scaling

class PrintMediaResolution(TypedDict, total=False):
    """
    Combined resolution type that can contain both pixel and physical dimensions.
    All fields are optional, with sensible defaults applied when missing.
    
    Defaults:
    - width/height: 1920x1080 if not provided
    - dpi: 300 if not provided
    - object_fit: "contain" if not provided
    """
    # Pixel dimensions
    width: int
    height: int
    # Physical dimensions (cm)
    cm_width: float
    cm_height: float
    dpi: int
    # How content should fit in the viewport
    object_fit: str

Resolution = Union[PixelResolution, CMResolution, PrintMediaResolution]


@dataclass
class HtmlDoc:
    html: str

    @classmethod
    def create_from_html_parts(
        cls,
        body: str,
        head: str = "",
        css: str = "",
    ) -> "HtmlDoc":
        prepared_html = f"""\
                <html>
                <head>
                    {head}
                    <style>
                        {css}
                    </style>
                </head>

                <body>
                    {body}
                </body>
                </html>
                """
        prepared_html = dedent(prepared_html)
        return cls(html=prepared_html)


def is_cm_resolution(resolution: Resolution) -> bool:
    """Helper function to check if resolution is CMResolution or has CM attributes"""
    return 'cm_width' in resolution and 'cm_height' in resolution


def has_pixel_dimensions(resolution: Resolution) -> bool:
    """Helper function to check if resolution has pixel dimensions"""
    return 'width' in resolution and 'height' in resolution


class PlaywrightManager:
    def __init__(self, viewport: ViewportSize, device_scale_factor: float):
        self.viewport = viewport
        self.device_scale_factor = device_scale_factor
        self.playwright = None
        self.browser = None
        self.context = None

    async def __aenter__(self):
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(args=['--disable-dev-shm-usage'])
        self.context = await self.browser.new_context(
            viewport=self.viewport,
            device_scale_factor=self.device_scale_factor
        )
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.context:
            await self.context.close()
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()

    def get_context(self) -> BrowserContext:
        if self.context is None:
            raise Exception("Context not initialized. Use within 'async with' block.")
        return self.context


async def generate_image_batch(
    targets: List[Union[str, Path, HtmlDoc]],
    *,
    resolution: Optional[Resolution] = None,
    query_parameters_list: Optional[List[Optional[Dict[str, Any]]]] = None,
    output_files: Optional[List[Optional[Union[Path, str]]]] = None,
    scale_factor: float = 1.5,
    playwright_manager: Optional[PlaywrightManager] = None,
    render_timeout: float = 10.0,
    object_fit: str = ObjectFit.CONTAIN,
) -> List[bytes]:
    """
    target could be url, path or html doc
    resolution: Can be either pixel dimensions (width/height) or physical dimensions (cm_width/cm_height/dpi)
                or a combined PrintMediaResolution
    scale_factor: Browser zoom level (1.0 = 100%, 1.5 = 150%, etc.)
    render_timeout: Time to wait for RENDER_COMPLETE signal (in seconds) before falling back to networkidle
    object_fit: How content should fit in the viewport (contain, cover, fill, none), defaults to contain
    """
    converter = UnitConverter()
    
    # Handle resolution conversion
    if resolution is None:
        # Default to HD resolution if nothing specified
        resolution = {"width": 1920, "height": 1080}
    
    # Extract object_fit from resolution if present, otherwise use the parameter value which defaults to CONTAIN
    content_fit = resolution.get('object_fit', object_fit) if isinstance(resolution, dict) else object_fit
    
    # Initialize viewport dimensions
    has_cm = is_cm_resolution(resolution)
    has_pixels = has_pixel_dimensions(resolution)
    
    # Determine the actual viewport size based on the resolution type
    if has_cm:
        dpi = int(resolution.get('dpi', 300))
        cm_width = float(resolution.get('cm_width', 0))
        cm_height = float(resolution.get('cm_height', 0))
        
        # Convert cm to pixels
        pixel_width = converter.cm_to_pixels(cm_width, dpi)
        pixel_height = converter.cm_to_pixels(cm_height, dpi)
        
        # If we also have pixel dimensions, we'll use them for viewport and scale the content
        if has_pixels:
            screen_width = int(resolution.get('width', 1920))
            screen_height = int(resolution.get('height', 1080))
            
            # Calculate the scale needed to fit the content
            if content_fit == ObjectFit.CONTAIN:
                scale_ratio = min(screen_width / pixel_width, screen_height / pixel_height)
            elif content_fit == ObjectFit.COVER:
                scale_ratio = max(screen_width / pixel_width, screen_height / pixel_height)
            elif content_fit == ObjectFit.FILL:
                # No need to calculate ratio, we'll stretch to fill
                actual_resolution = ViewportSize(width=screen_width, height=screen_height)
                # Adjust content scale
                device_scale = scale_factor * (dpi / 96.0)  # 96 is typical screen DPI
                scale_ratio = 1.0
            else:  # ObjectFit.NONE or invalid value
                scale_ratio = 1.0
                
            if content_fit in [ObjectFit.CONTAIN, ObjectFit.COVER]:
                # Apply the scaling
                actual_resolution = ViewportSize(
                    width=screen_width,
                    height=screen_height
                )
                # Adjust device scale factor to achieve proper rendering
                device_scale = scale_factor * scale_ratio * (dpi / 96.0)
            else:
                actual_resolution = ViewportSize(width=screen_width, height=screen_height)
                device_scale = scale_factor * (dpi / 96.0)
        else:
            # Only CM dimensions provided
            actual_resolution = ViewportSize(width=pixel_width, height=pixel_height)
            device_scale = scale_factor
    elif has_pixels:
        # Only pixel dimensions provided
        screen_width = int(resolution.get('width', 1920))
        screen_height = int(resolution.get('height', 1080))
        actual_resolution = ViewportSize(width=screen_width, height=screen_height)
        device_scale = scale_factor
    else:
        # No valid dimensions provided, use default
        actual_resolution = ViewportSize(width=1920, height=1080)
        device_scale = scale_factor

    # Use provided manager or create a temporary one
    if playwright_manager:
        context = playwright_manager.get_context()
        close_context = False
    else:
        async with PlaywrightManager(actual_resolution, device_scale) as manager:
            context = manager.get_context()
            close_context = True

            tasks = []
            for target, query_parameters, output_file in zip(
                targets,
                query_parameters_list or [None] * len(targets),
                output_files or [None] * len(targets)
            ):
                if isinstance(target, Path):
                    url_address = f"file://{target.absolute()}"
                elif isinstance(target, HtmlDoc):
                    with tempfile.NamedTemporaryFile(
                        mode="w", suffix=".html", delete=False
                    ) as tf:
                        tf.write(target.html)
                        url_address = f"file://{tf.name}"
                else:
                    url_address = target

                tasks.append(
                    _generate(context, output_file, query_parameters, [], url_address, render_timeout)
                )
            results = await asyncio.gather(*tasks)
            screenshots = [item for sublist in results for item in sublist]

            if close_context:
                await context.close()
            return screenshots

    tasks = []
    for target, query_parameters, output_file in zip(
        targets,
        query_parameters_list or [None] * len(targets),
        output_files or [None] * len(targets)
    ):
        if isinstance(target, Path):
            url_address = f"file://{target.absolute()}"
        elif isinstance(target, HtmlDoc):
            with tempfile.NamedTemporaryFile(
                mode="w", suffix=".html", delete=False
            ) as tf:
                tf.write(target.html)
                url_address = f"file://{tf.name}"
        else:
            url_address = target

        tasks.append(
            _generate(context, output_file, query_parameters, [], url_address, render_timeout)
        )

    results = await asyncio.gather(*tasks)
    screenshots = [item for sublist in results for item in sublist]
    return screenshots


async def _generate(
    context: BrowserContext, 
    output_file: Optional[Union[Path, str]], 
    query_parameters: Optional[Dict[str, Any]], 
    screenshots: List[bytes], 
    url_address: str,
    render_timeout: float = 10.0
) -> List[bytes]:
    page = await context.new_page()
    
    # Set up console message listener
    render_complete = asyncio.Event()
    
    def handle_console(msg):
        if msg.text == "RENDER_COMPLETE":
            render_complete.set()
    
    page.on("console", handle_console)
    
    furl_url = furl(url_address)
    if query_parameters:
        for field_name, value in query_parameters.items():
            furl_url.args[field_name] = value
            
    # Navigate to the page and wait for network idle
    await page.goto(furl_url.url, wait_until="networkidle")
    
    # Wait for the render complete signal with a timeout
    try:
        await asyncio.wait_for(render_complete.wait(), timeout=render_timeout)
        # Signal was received, continue to screenshot
    except asyncio.TimeoutError:
        # Fall back to networkidle if no RENDER_COMPLETE signal is received
        # We don't need to do anything here as we've already waited for networkidle
        pass
        
    # Take the screenshot immediately after timeout or signal
    screenshot = await page.screenshot(path=output_file)
    
    # Clean up resources
    await page.close()
    
    return [screenshot]


def generate_image_batch_sync(*args: Any, **kwargs: Any) -> List[bytes]:
    return asyncio.run(
        generate_image_batch(*args, **kwargs)
    )


async def generate_image(
    target: Union[str, Path, HtmlDoc],
    *,
    resolution: Optional[Resolution] = None,
    query_parameters: Optional[Dict[str, Any]] = None,
    output_file: Optional[Union[Path, str]] = None,
    scale_factor: float = 1.5,
    render_timeout: float = 10.0,
    object_fit: str = ObjectFit.CONTAIN,
) -> bytes:
    """
    Generate an image from a target (URL, file path, or HTML document).
    
    Args:
        target: URL, file path, or HTML document to capture
        resolution: Viewport dimensions in pixels or cm. Can be:
                   - PixelResolution (width, height)
                   - CMResolution (cm_width, cm_height, dpi)
                   - PrintMediaResolution (combination of both with optional object_fit)
                   If None, defaults to 1920x1080 pixels
        query_parameters: Optional parameters to add to URL if target is a URL
        output_file: Optional path to save the image
        scale_factor: Browser zoom level (1.0 = 100%, 1.5 = 150%, etc.)
        render_timeout: Time to wait for RENDER_COMPLETE signal before fallback
        object_fit: How content should fit in viewport (contain, cover, fill, none), defaults to contain
    
    Returns:
        bytes: The screenshot as bytes
    """
    screenshots = await generate_image_batch(
        [target],
        resolution=resolution,
        query_parameters_list=[query_parameters],
        output_files=[output_file],
        scale_factor=scale_factor,
        render_timeout=render_timeout,
        object_fit=object_fit,
    )
    return screenshots[0]


def generate_image_sync(*args: Any, **kwargs: Any) -> bytes:
    return asyncio.run(
        generate_image(*args, **kwargs)
    )


