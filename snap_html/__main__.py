import typer
from pathlib import Path
from typing import Optional
from rich import print
from . import generate_image_sync, HtmlDoc

app = typer.Typer(help="Generate images from HTML content")

@app.command()
def capture(
    source: str = typer.Argument(..., help="HTML file path, URL, or raw HTML string"),
    output: Path = typer.Option(
        None,
        "--output", 
        "-o",
        help="Output image file path"
    ),
    width: Optional[int] = typer.Option(
        None,
        "--width",
        "-w",
        help="Output width in pixels"
    ),
    height: Optional[int] = typer.Option(
        None,
        "--height",
        "-h",
        help="Output height in pixels"
    ),
    cm_width: Optional[float] = typer.Option(
        None,
        "--cm-width",
        help="Output width in centimeters"
    ),
    cm_height: Optional[float] = typer.Option(
        None,
        "--cm-height",
        help="Output height in centimeters"
    ),
    dpi: int = typer.Option(
        300,
        "--dpi",
        help="DPI for cm-based resolution"
    ),
    scale: float = typer.Option(
        1.0,
        "--scale",
        help="Browser scale factor (zoom level)"
    )
) -> None:
    """
    Generate an image from HTML content. The source can be:
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
        elif source.startswith(('http://', 'https://')):
            target = source
        # Treat source as raw HTML
        else:
            target = HtmlDoc(html=source)

        # Determine resolution type
        if cm_width is not None and cm_height is not None:
            resolution = {
                "cm_width": cm_width,
                "cm_height": cm_height,
                "dpi": dpi
            }
        elif width is not None and height is not None:
            resolution = {
                "width": width,
                "height": height
            }
        else:
            resolution = {
                "width": 1920,
                "height": 1080
            }

        # Generate the image
        screenshot = generate_image_sync(
            target,
            resolution=resolution,
            output_file=output,
            scale_factor=scale
        )

        if output:
            print(f"[green]Image successfully saved to: {output}[/green]")
        else:
            print(f"[green]Image generated successfully ({len(screenshot)} bytes)[/green]")

    except Exception as e:
        print(f"[red]Error: {str(e)}[/red]")
        raise typer.Exit(1)

if __name__ == "__main__":
    app() 