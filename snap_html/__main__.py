from pathlib import Path
from typing import Optional, Union, Literal

import typer
from rich import print

from . import HtmlDoc, generate_image_sync, ScreenResolution, PrintMediaResolution

app = typer.Typer(help="Generate images from HTML content")


@app.command()
def capture(
    source: str = typer.Argument(
        ..., help="HTML file path, URL, or raw HTML string"
    ),
    output: Optional[Path] = typer.Option(
        None, "--output", "-o", help="Output image file path"
    ),
    width: Optional[int] = typer.Option(
        None, "--width", "-w", help="Output width in pixels"
    ),
    height: Optional[int] = typer.Option(
        None, "--height", "-h", help="Output height in pixels"
    ),
    cm_width: Optional[float] = typer.Option(
        None, "--cm-width", help="Output width in centimeters"
    ),
    cm_height: Optional[float] = typer.Option(
        None, "--cm-height", help="Output height in centimeters"
    ),
    dpi: int = typer.Option(300, "--dpi", help="DPI for cm-based resolution"),
    scale: float = typer.Option(
        1.5, "--scale", help="Browser scale factor (zoom level)"
    ),
    timeout: Optional[float] = typer.Option(
        None, "--timeout", help="Time to wait for RENDER_COMPLETE signal (in seconds)"
    ),
) -> None:
    """Generate an image from HTML content. The source can be:
    - A file path to an HTML file
    - A URL
    - Raw HTML content
    """
    try:
        # Determine if source is a file path
        source_path = Path(source)
        if source_path.exists() and source_path.is_file():
            html_content = source_path.read_text()
            target = HtmlDoc(html=html_content)
        # Check if source is a URL
        elif source.startswith(("http://", "https://")):
            target = source
        # Treat source as raw HTML
        else:
            target = HtmlDoc(html=source)

        # Determine target resolution
        if cm_width is not None and cm_height is not None:
            # Print media resolution
            target_resolution = PrintMediaResolution(
                width=cm_width,
                height=cm_height,
                unit="cm",
                dpi=dpi,
            )
        elif width is not None and height is not None:
            # Screen resolution
            target_resolution = ScreenResolution(
                width=width,
                height=height,
            )
        else:
            # Default resolution
            target_resolution = "720p"

        # Determine as_if_show_in_screen_resolution
        as_if_show_in_screen_resolution = None
        if width is not None and height is not None and (cm_width is not None and cm_height is not None):
            # If both pixel and physical dimensions are provided, use pixel dimensions for display context
            as_if_show_in_screen_resolution = ScreenResolution(
                width=width,
                height=height,
            )

        # Generate the image
        screenshot = generate_image_sync(
            target,
            target_resolution=target_resolution,
            as_if_show_in_screen_resolution=as_if_show_in_screen_resolution,
            output_file=output,
            scale_factor=scale if as_if_show_in_screen_resolution is None else None,  # Only use scale_factor if not using as_if_show_in_screen_resolution
            render_timeout=timeout,
        )

        if output:
            print(f"[green]Image successfully saved to: {output}[/green]")
        else:
            print(
                f"[green]Image generated successfully ({len(screenshot)} bytes)[/green]"
            )

    except Exception as e:
        print(f"[red]Error: {str(e)}[/red]")
        raise typer.Exit(1)


if __name__ == "__main__":
    app()
