# type: ignore[attr-defined]
"""a robust, modern and high performance Python library for generating image from a html string/html file/url build on top of `playwright`"""

try:
    from importlib.metadata import PackageNotFoundError, version
except ImportError:  # pragma: no cover
    from importlib_metadata import PackageNotFoundError, version


try:
    __version__ = version(__name__)
except PackageNotFoundError:  # pragma: no cover
    __version__ = "unknown"

from typing import Dict, List, Optional, TypedDict, Union

import asyncio
import tempfile
from dataclasses import dataclass
from pathlib import Path
from textwrap import dedent

from furl import furl
from playwright import async_playwright


class Resolution(TypedDict):
    width: int
    height: int


@dataclass
class HtmlDoc:
    html: str

    @classmethod
    def create_from_html_parts(
        cls,
        body: str,
        head: str = "",
        css: str = "",
    ):
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


async def generate_image_batch(
    targets: List[Union[str, Path, HtmlDoc]],
    *,
    resolution=None,
    query_parameters_list: Optional[List[Optional[Dict]]] = None,
    output_files: Optional[List[Optional[Union[Path, str]]]] = None,
) -> List[bytes]:
    """
    target could be url, path or html doc
    """
    if resolution is None:
        resolution = {"width": 1920, "height": 1080}

    async with async_playwright() as p:
        browser = await p.chromium.launch()
        context = await browser.newContext(viewport=resolution)
        screenshots: List[bytes] = []
        for target, query_parameters, output_file in zip(
            targets, query_parameters_list, output_files
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

        await browser.close()
        return screenshots


async def _generate(
    context, output_file, query_parameters, screenshots, url_address
):
    page = await context.newPage()
    furl_url = furl(url_address)
    if query_parameters:
        for field_name, value in query_parameters.items():
            furl_url.args[field_name] = value
    await page.goto(furl_url.url)
    screenshot = await page.screenshot(path=output_file)
    screenshots.append(screenshot)


def generate_image_batch_sync(*args, **kwargs) -> bytes:
    return asyncio.get_event_loop().run_until_complete(
        generate_image_batch(*args, **kwargs)
    )


async def generate_image(
    target: Union[str, Path, HtmlDoc],
    *,
    resolution: Resolution,
    query_parameters: Optional[Dict] = None,
    output_file: Optional[Union[Path, str]] = None,
) -> bytes:
    screenshots = await generate_image_batch(
        [target],
        resolution=resolution,
        query_parameters_list=[query_parameters],
        output_files=[output_file],
    )
    return screenshots[0]


def generate_image_sync(*args, **kwargs) -> bytes:
    return asyncio.get_event_loop().run_until_complete(
        generate_image(*args, **kwargs)
    )
