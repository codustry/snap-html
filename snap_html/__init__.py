# type: ignore[attr-defined]
"""a robust, modern and high performance Python library for generating image from a html string/html file/url build on top of `playwright`"""

try:
    from importlib.metadata import version, PackageNotFoundError
except ImportError:  # pragma: no cover
    from importlib_metadata import version, PackageNotFoundError


try:
    __version__ = version(__name__)
except PackageNotFoundError:  # pragma: no cover
    __version__ = "unknown"

import asyncio
import tempfile
from dataclasses import dataclass
from pathlib import Path
from textwrap import dedent
from typing import TypedDict, Optional, Dict, List, Union

from playwright import async_playwright
from furl import furl


class Resolution(TypedDict):
    width: int
    height: int


@dataclass
class HtmlDoc:
    body: str
    head: str = ''
    css: str = ''

    def compile_html(self):
        prepared_html = f"""\
                <html>
                <head>
                    {self.head}
                    <style>
                        {self.css}
                    </style>
                </head>

                <body>
                    {self.body}
                </body>
                </html>
                """
        return dedent(prepared_html)


async def generate_image_batch(targets: List[Union[str, Path, HtmlDoc]], *, resolution=None,
                               query_parameters_list: Optional[List[Optional[Dict]]] = None,
                               output_files: Optional[List[Optional[Union[Path, str]]]] = None) -> List[bytes]:
    """
    target could be url, path or html doc
    """
    if resolution is None:
        resolution = {'width': 1920, 'height': 1080}

    async with async_playwright() as p:
        browser = await p.chromium.launch()
        context = await browser.newContext(viewport=resolution)
        screenshots: List[bytes] = []
        for target, query_parameters, output_file in zip(targets, query_parameters_list, output_files):

            if isinstance(target, Path):
                url_address = f"file://{target.absolute()}"

            elif isinstance(target, HtmlDoc):
                with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False) as tf:
                    content = target.compile_html()
                    tf.write(content)
                    url_address = f"file://{tf.name}"

            else:
                url_address = target

            await _generate(context, output_file, query_parameters, screenshots, url_address)

        await browser.close()
        return screenshots


async def _generate(context, output_file, query_parameters, screenshots, url_address):
    page = await context.newPage()
    furl_url = furl(url_address)
    if query_parameters:
        for field_name, value in query_parameters.items():
            furl_url.args[field_name] = value
    await page.goto(furl_url.url)
    screenshot = await page.screenshot(path=output_file)
    screenshots.append(screenshot)


def generate_image_batch_sync(*args, **kwargs) -> bytes:
    return asyncio.get_event_loop().run_until_complete(generate_image_batch(*args, **kwargs))


async def generate_image(target: Union[str, Path, HtmlDoc], *, resolution: Resolution,
                         query_parameters: Optional[Dict] = None,
                         output_file: Optional[Union[Path, str]] = None) -> bytes:
    screenshots = await generate_image_batch([target], resolution=resolution, query_parameters_list=[query_parameters],
                                             output_files=[output_file])
    return screenshots[0]


def generate_image_sync(*args, **kwargs) -> bytes:
    return asyncio.get_event_loop().run_until_complete(generate_image(*args, **kwargs))

