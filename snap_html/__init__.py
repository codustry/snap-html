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
from playwright.async_api import ViewportSize

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

Resolution = Union[PixelResolution, CMResolution]


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
    """Helper function to check if resolution is CMResolution"""
    return all(key in resolution for key in ('cm_width', 'cm_height', 'dpi'))


async def generate_image_batch(
    targets: List[Union[str, Path, HtmlDoc]],
    *,
    resolution: Optional[Resolution] = None,
    query_parameters_list: Optional[List[Optional[Dict[str, Any]]]] = None,
    output_files: Optional[List[Optional[Union[Path, str]]]] = None,
    scale_factor: float = 1.0,
) -> List[bytes]:
    """
    target could be url, path or html doc
    resolution: Can be either pixel dimensions (width/height) or physical dimensions (cm_width/cm_height/dpi)
    scale_factor: Browser zoom level (1.0 = 100%, 1.5 = 150%, etc.)
    """
    converter = UnitConverter()
    
    # Handle resolution conversion
    if resolution is None:
        resolution = {"width": 1920, "height": 1080}
    
    if is_cm_resolution(resolution):
        dpi = resolution.get('dpi', 300)
        actual_resolution: ViewportSize = {
            'width': converter.cm_to_pixels(float(resolution['cm_width']), int(dpi)),
            'height': converter.cm_to_pixels(float(resolution['cm_height']), int(dpi))
        }
    else:
        actual_resolution = ViewportSize(width=resolution['width'], height=resolution['height'])

    async with async_playwright() as p:
        browser = await p.chromium.launch(
            args=['--disable-dev-shm-usage']
        )
        context = await browser.new_context(
            viewport=actual_resolution,  # Use converted resolution
            device_scale_factor=scale_factor
        )
        screenshots: List[bytes] = []
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

            await _generate(
                context, output_file, query_parameters, screenshots, url_address
            )

        await context.close()
        await browser.close()
        return screenshots


async def _generate(
    context, output_file, query_parameters, screenshots, url_address
):
    page = await context.new_page()
    furl_url = furl(url_address)
    if query_parameters:
        for field_name, value in query_parameters.items():
            furl_url.args[field_name] = value
    await page.goto(furl_url.url, wait_until="networkidle")
    screenshot = await page.screenshot(path=output_file)
    await page.close()
    screenshots.append(screenshot)


def generate_image_batch_sync(*args: Any, **kwargs: Any) -> List[bytes]:
    return asyncio.run(
        generate_image_batch(*args, **kwargs)
    )


async def generate_image(
    target: Union[str, Path, HtmlDoc],
    *,
    resolution: Resolution,
    query_parameters: Optional[Dict[str, Any]] = None,
    output_file: Optional[Union[Path, str]] = None,
    scale_factor: float = 1.0,
) -> bytes:
    screenshots = await generate_image_batch(
        [target],
        resolution=resolution,
        query_parameters_list=[query_parameters],
        output_files=[output_file],
        scale_factor=scale_factor,
    )
    return screenshots[0]


def generate_image_sync(*args: Any, **kwargs: Any) -> bytes:
    return asyncio.run(
        generate_image(*args, **kwargs)
    )


