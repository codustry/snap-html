# mypy: disable-error-code="attr-defined"
"""a robust, modern and high performance Python library for generating image from a html string/html file/url build on top of `playwright`"""

try:
    from importlib.metadata import PackageNotFoundError, version
except ImportError:  # pragma: no cover
    from importlib_metadata import (
        PackageNotFoundError,  # type: ignore
        version,  # type: ignore
    )

from typing_extensions import Literal
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
    
    def inch_to_pixels(self, inch: float, dpi: int) -> int:
        """Convert inches to pixels based on DPI"""
        # Create a quantity from the inch value
        inch_quantity = inch * self.ureg.inch
        # Convert to pixels
        return int(round(inch_quantity.to(self.ureg.px).magnitude))


try:
    __version__ = version(__name__)
except PackageNotFoundError:  # pragma: no cover
    __version__ = "unknown"

import asyncio
import tempfile
from dataclasses import dataclass
from pathlib import Path
from textwrap import dedent
from typing import Any, Dict, List, Optional, TypedDict, Union

from furl import furl
from playwright.async_api import BrowserContext, ViewportSize, async_playwright
from pydantic import BaseModel


# For screen display - no DPI needed
class ScreenResolution(BaseModel):
    """Resolution type for screen display (pixel dimensions only).
    
    All fields are required.
    """
    # Pixel dimensions
    width: int
    height: int

    @property
    def px_width(self) -> int:
        return self.width

    @property
    def px_height(self) -> int:
        return self.height


class PrintMediaResolution(BaseModel):
    """Resolution type for print media that requires physical dimensions with DPI.
    
    All fields are required.
    """
    # Physical dimensions (cm)
    width: float
    height: float
    unit: Literal["cm", "in"] = "cm"
    dpi: int = 300



    @property
    def px_width(self) -> int:
        uc = UnitConverter()
        return uc.cm_to_pixels(self.width, self.dpi) if self.unit == "cm" else uc.inch_to_pixels(self.width, self.dpi)

    @property
    def px_height(self) -> int:
        uc = UnitConverter()
        return uc.cm_to_pixels(self.height, self.dpi) if self.unit == "cm" else uc.inch_to_pixels(self.height, self.dpi)


Resolution = Union[ScreenResolution, PrintMediaResolution]


# Common screen resolutions by name
STANDARD_RESOLUTIONS = {
    # Standard resolutions
    "480p": (854, 480),
    "720p": (1280, 720),
    "1080p": (1920, 1080),
    "1440p": (2560, 1440),
    "2160p": (3840, 2160),
    "4k": (3840, 2160),
    # Common alternative names
    "hd": (1280, 720),
    "fullhd": (1920, 1080),
    "fhd": (1920, 1080),
    "2k": (2560, 1440),
    "qhd": (2560, 1440),
    "uhd": (3840, 2160),
}


def parse_resolution_string(resolution_str: str) -> ScreenResolution:
    """Convert standard resolution string (e.g., '1080p') to pixel dimensions.
    
    Args:
        resolution_str: String specifying a standard resolution (e.g., '1080p', '4k')
        
    Returns:
        ScreenResolution with width and height in pixels
        
    Raises:
        ValueError: If the resolution string is not recognized
    """
    # Normalize the string (lowercase, remove spaces)
    normalized = resolution_str.lower().strip().replace(" ", "")
    
    if normalized in STANDARD_RESOLUTIONS:
        width, height = STANDARD_RESOLUTIONS[normalized]
        return ScreenResolution(width=width, height=height)
    else:
        raise ValueError(f"Unrecognized resolution format: {resolution_str}. "
                        f"Supported formats: {', '.join(sorted(STANDARD_RESOLUTIONS.keys()))}")


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



class PlaywrightManager:
    def __init__(self, viewport: ViewportSize, device_scale_factor: float):
        self.viewport = viewport
        self.device_scale_factor = device_scale_factor
        self.playwright = None
        self.browser = None
        self.context = None

    async def __aenter__(self):
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(
            args=["--disable-dev-shm-usage"]
        )
        self.context = await self.browser.new_context(
            viewport=self.viewport, device_scale_factor=self.device_scale_factor
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
            raise Exception(
                "Context not initialized. Use within 'async with' block."
            )
        return self.context

def calculate_scale_factor(resolution: Resolution, asIfShowInScreenResolution: Resolution) -> float:
    """Calculate the scale factor based on the resolution and the asIfShowInScreenResolution"""
    height_ratio = resolution.px_height / asIfShowInScreenResolution.px_height
    width_ratio = resolution.px_width / asIfShowInScreenResolution.px_width
    return max(min(height_ratio, width_ratio ), 1)



async def generate_image_batch(
    sources: List[Union[str, Path, HtmlDoc]],
    *,
    target_resolution: Union[Resolution, str] = '720p',
    as_if_show_in_screen_resolution: Optional[Union[Resolution, str]] = None,
    scale_factor: float | None = None,
    query_parameters_list: Optional[List[Optional[Dict[str, Any]]]] = None,
    output_files: Optional[List[Optional[Union[Path, str]]]] = None,
    playwright_manager: Optional[PlaywrightManager] = None,
    render_timeout: float = 10.0,
) -> List[bytes]:
    """Generate images from multiple sources in batch mode.

    Args:
        sources: List of URLs, file paths, or HTML documents to capture
        target_resolution: Can be either a Resolution object (ScreenResolution or PrintMediaResolution)
            or a string representing a standard resolution (e.g., "1080p", "4k")
        as_if_show_in_screen_resolution: Optional resolution to simulate how the content would appear on a different screen
        scale_factor: Browser zoom level (1.0 = 100%, 1.5 = 150%, etc.)
        query_parameters_list: Optional parameters to add to URLs
        output_files: Optional paths to save images
        playwright_manager: Optional PlaywrightManager (allows reuse for multiple calls)
        render_timeout: Time to wait for RENDER_COMPLETE signal (in seconds) before falling back to networkidle

    Returns:
        List[bytes]: List of screenshots as PNG bytes

    Note:
        The parameters as_if_show_in_screen_resolution and scale_factor cannot be used together.
        If both are provided, a ValueError will be raised.
    """

    # as_if_show_in_screen_resolution and scale_factor cannot coexist
    if as_if_show_in_screen_resolution and scale_factor:
        raise ValueError("as_if_show_in_screen_resolution and scale_factor cannot coexist")

    if isinstance(target_resolution, str):
        # Parse standard resolution string (e.g., "1080p", "4k")
        target_resolution = parse_resolution_string(target_resolution)

    if as_if_show_in_screen_resolution and isinstance(as_if_show_in_screen_resolution, str):
        as_if_show_in_screen_resolution = parse_resolution_string(as_if_show_in_screen_resolution)

    device_scale_factor: float = 1.0
    if as_if_show_in_screen_resolution:
        device_scale_factor = calculate_scale_factor(target_resolution, as_if_show_in_screen_resolution)
    elif scale_factor:
        device_scale_factor = scale_factor

    # output device_scale_factor
    print(f"target_resolution: {target_resolution}")
    print(f"as_if_show_in_screen_resolution: {as_if_show_in_screen_resolution}")
    print(f"scale_factor: {scale_factor}")
    print(f"device_scale_factor: {device_scale_factor}")

    # warn user if the resolution goes beyond 4k
    if target_resolution.px_width > 3840 or target_resolution.px_height > 2160:
        print(f"Warning: The resolution is beyond 4k. This may cause performance issues.")

    # Use provided manager or create a temporary one
    if playwright_manager:
        context = playwright_manager.get_context()
        close_context = False
    else:
        # Ensure we pass the correct viewport size (width, height) to PlaywrightManager
        viewport = ViewportSize(width=target_resolution.px_width, height=target_resolution.px_height)
        async with PlaywrightManager(
            viewport, device_scale_factor
        ) as manager:
            context = manager.get_context()
            close_context = True

            tasks = []
            for target, query_parameters, output_file in zip(
                sources,
                query_parameters_list or [None] * len(sources),
                output_files or [None] * len(sources),
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
                    _generate(
                        context,
                        output_file,
                        query_parameters,
                        [],
                        url_address,
                        render_timeout,
                    )
                )
            results = await asyncio.gather(*tasks)
            screenshots = [item for sublist in results for item in sublist]

            if close_context:
                await context.close()
            return screenshots

    tasks = []
    for target, query_parameters, output_file in zip(
        sources,
        query_parameters_list or [None] * len(sources),
        output_files or [None] * len(sources),
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
            _generate(
                context,
                output_file,
                query_parameters,
                [],
                url_address,
                render_timeout,
            )
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
    render_timeout: float = 10.0,
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
    return asyncio.run(generate_image_batch(*args, **kwargs))


async def generate_image(
    target: Union[str, Path, HtmlDoc],
    *,
    target_resolution: Optional[Union[Resolution, str]] = None,
    as_if_show_in_screen_resolution: Optional[Union[Resolution, str]] = None,
    query_parameters: Optional[Dict[str, Any]] = None,
    output_file: Optional[Union[Path, str]] = None,
    scale_factor: float | None = None,
    render_timeout: float = 10.0,
) -> bytes:
    """Generate an image from a target (URL, file path, or HTML document).

    Args:
        target: URL, file path, or HTML document to capture
        resolution: Viewport dimensions. Can be:
                    - ScreenResolution object (pixel dimensions only)
                    - PrintMediaResolution object (physical dimensions with DPI)
                    - String representing a standard resolution (e.g., "1080p", "4k")
                    If None, defaults to 1920x1080 pixels
        query_parameters: Optional parameters to add to URL if target is a URL
        output_file: Optional path to save the image
        scale_factor: Browser zoom level (1.0 = 100%, 1.5 = 150%, etc.)
        render_timeout: Time to wait for RENDER_COMPLETE signal before fallback

    Returns:
        bytes: Screenshot data as PNG bytes
    """
    screenshots = await generate_image_batch(
        [target],
        target_resolution=target_resolution,
        as_if_show_in_screen_resolution=as_if_show_in_screen_resolution,
        query_parameters_list=[query_parameters],
        output_files=[output_file],
        scale_factor=scale_factor,
        render_timeout=render_timeout,
    )
    return screenshots[0]


def generate_image_sync(*args: Any, **kwargs: Any) -> bytes:
    return asyncio.run(generate_image(*args, **kwargs))

if __name__ == "__main__":
    # snap-html "http://localhost:5173/report-helper/patrol-map/SKA-MS-68-002/1?threeD=false&access_token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.ewogICJyb2xlIjogInNlcnZpY2Vfcm9sZSIsCiAgImlzcyI6ICJzdXBhYmFzZSIsCiAgImlhdCI6IDE3MjY5MzgwMDAsCiAgImV4cCI6IDE4ODQ3MDQ0MDAKfQ.nGu0UWzMMRjoJ_QiDecLjKyTcDrCgIM6XPAqzdqUV6M" -o screenshot3.png --width 1280 --height 720 --cm-width 18 --cm-height 18 --dpi 600 --object-fit cover --timeout 10.0 
    generate_image_sync(
        "http://localhost:5173/report-helper/patrol-map/SKA-MS-68-002/1?threeD=false&access_token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.ewogICJyb2xlIjogInNlcnZpY2Vfcm9sZSIsCiAgImlzcyI6ICJzdXBhYmFzZSIsCiAgImlhdCI6IDE3MjY5MzgwMDAsCiAgImV4cCI6IDE4ODQ3MDQ0MDAKfQ.nGu0UWzMMRjoJ_QiDecLjKyTcDrCgIM6XPAqzdqUV6M", 
        target_resolution=ScreenResolution(width=800, height=800),
        # target_resolution=PrintMediaResolution(width=18, height=18, unit="cm", dpi=300), 
        # as_if_show_in_screen_resolution="720p", 
        output_file="screenshot4.png", 
        render_timeout=90.0,
    )
