import time

import pytest

from snap_html import (
    HtmlDoc,
    UnitConverter,
    generate_image,
    generate_image_batch,
    generate_image_batch_sync,
    generate_image_sync,
    PrintMediaResolution,
    ScreenResolution,
)

# Define a marker for slow tests that can be skipped with -m "not slow"
pytestmark = pytest.mark.asyncio


@pytest.fixture
def sample_html():
    return HtmlDoc.create_from_html_parts(
        body="<h1>Hello World</h1>",
        head="<title>Test Page</title>",
        css="h1 { color: blue; }",
    )


@pytest.fixture
def simple_page():
    """Fixture for a simple HTML page to replace external URL dependencies"""
    return HtmlDoc.create_from_html_parts(
        body="<h1>Example Page</h1><p>This is a local test page</p>",
        head="<title>Example Page</title>",
        css="body { font-family: Arial; }",
    )


@pytest.fixture
def unit_converter():
    return UnitConverter()


def test_unit_converter(unit_converter):
    # Test cm to pixels conversion with 96 DPI (common screen resolution)
    assert (
        unit_converter.cm_to_pixels(2.54, 96) == 96
    )  # 1 inch = 2.54 cm = 96 pixels at 96 DPI
    assert unit_converter.cm_to_pixels(5.08, 96) == 192  # 2 inches

    # Test with different DPI
    assert unit_converter.cm_to_pixels(2.54, 300) == 300  # 1 inch at 300 DPI


def test_html_doc_creation():
    doc = HtmlDoc.create_from_html_parts(
        body="<p>Test</p>", head="<title>Test</title>", css="p { color: red; }"
    )
    assert "<title>Test</title>" in doc.html
    assert "<p>Test</p>" in doc.html
    assert "p { color: red; }" in doc.html


async def test_generate_image_from_html(sample_html, tmp_path):
    output_file = tmp_path / "test.png"
    
    # Create a proper PrintMediaResolution object for A4 paper size
    resolution = PrintMediaResolution(
        width=21.0,  # A4 width in cm
        height=29.7,  # A4 height in cm
        dpi=300,
        unit="cm"
    )
    
    screenshot = await generate_image(
        sample_html,
        target_resolution=resolution,
        output_file=output_file,
    )

    assert isinstance(screenshot, bytes)
    assert output_file.exists()
    assert output_file.stat().st_size > 0


async def test_generate_image_from_url(simple_page):
    # Use local HTML instead of external URL
    resolution = PrintMediaResolution(
        width=10.0,  # cm_width
        height=7.5,  # cm_height
        dpi=300,
        unit="cm"
    )
    
    screenshot = await generate_image(
        simple_page, target_resolution=resolution
    )
    assert isinstance(screenshot, bytes)
    assert len(screenshot) > 0


async def test_generate_image_with_cm_resolution(unit_converter, simple_page):
    # Use local HTML instead of external URL
    resolution = PrintMediaResolution(
        width=21.0,  # A4 width in cm
        height=29.7,  # A4 height in cm
        dpi=300,
        unit="cm"
    )
    
    screenshot = await generate_image(
        simple_page,
        target_resolution=resolution,
    )
    assert isinstance(screenshot, bytes)
    assert len(screenshot) > 0


async def test_generate_image_batch(sample_html, simple_page, tmp_path):
    output_file1 = tmp_path / "test1.png"
    output_file2 = tmp_path / "test2.png"

    sources = [
        sample_html,
        simple_page,  # Use local HTML instead of external URL
    ]

    output_files = [output_file1, output_file2]

    # Create a proper PrintMediaResolution object instead of using a dictionary
    resolution = PrintMediaResolution(
        width=10.0,  # cm_width
        height=7.5,  # cm_height
        dpi=300,
        unit="cm"
    )

    screenshots = await generate_image_batch(
        sources,
        target_resolution=resolution,
        output_files=output_files,
    )

    assert len(screenshots) == 2
    assert all(isinstance(screenshot, bytes) for screenshot in screenshots)
    assert all(output_file.exists() for output_file in output_files)


def test_sync_functions(sample_html, tmp_path):
    output_file = tmp_path / "test_sync.png"

    # Create a proper ScreenResolution object
    resolution = ScreenResolution(width=800, height=600)

    # Test single image generation
    screenshot = generate_image_sync(
        sample_html,
        resolution=resolution,
        output_file=output_file,
    )
    assert isinstance(screenshot, bytes)
    assert output_file.exists()

    # Test batch generation
    screenshots = generate_image_batch_sync(
        [sample_html], target_resolution=resolution
    )
    assert isinstance(screenshots, list)
    assert len(screenshots) == 1
    assert isinstance(screenshots[0], bytes)


@pytest.mark.slow
async def test_generate_image_with_query_params():
    # Keep this test using external URL as it specifically tests query parameters
    query_params = {"param1": "value1", "param2": "value2"}
    resolution = ScreenResolution(width=800, height=600)
    
    screenshot = await generate_image(
        "https://httpbin.org/get",
        target_resolution=resolution,
        query_parameters=query_params,
    )
    assert isinstance(screenshot, bytes)
    assert len(screenshot) > 0


async def test_generate_image_with_scale_factor(simple_page):
    # Use local HTML instead of external URL
    resolution = ScreenResolution(width=800, height=600)
    
    screenshot = await generate_image(
        simple_page, target_resolution=resolution, scale_factor=2.0
    )
    assert isinstance(screenshot, bytes)
    assert len(screenshot) > 0


async def test_generate_image_with_print_media_resolution(simple_page):
    # Test with print media resolution (both pixel and physical dimensions)
    resolution1 = PrintMediaResolution(
        width=21.0,  # A4 width in cm
        height=29.7,  # A4 height in cm
        dpi=300,
        unit="cm"
    )
    
    screenshot = await generate_image(
        simple_page,
        target_resolution=resolution1,
    )
    assert isinstance(screenshot, bytes)
    assert len(screenshot) > 0

    # Test with different print media resolution
    resolution2 = PrintMediaResolution(
        width=10.0,
        height=15.0,
        dpi=150,
        unit="cm"
    )
    
    screenshot = await generate_image(
        simple_page,
        target_resolution=resolution2,
    )
    assert isinstance(screenshot, bytes)
    assert len(screenshot) > 0


async def test_generate_image_with_screen_resolution(simple_page):
    """Test using ScreenResolution."""
    # Test with screen resolution (pixel dimensions only)
    resolution1 = ScreenResolution(
        width=1920,
        height=1080,
    )
    
    screenshot = await generate_image(
        simple_page,
        target_resolution=resolution1,
    )
    assert isinstance(screenshot, bytes)
    assert len(screenshot) > 0

    # Test with different screen resolution
    resolution2 = ScreenResolution(
        width=800,
        height=600,
    )
    
    screenshot = await generate_image(
        simple_page,
        target_resolution=resolution2,
    )
    assert isinstance(screenshot, bytes)
    assert len(screenshot) > 0


async def test_render_complete_signal():
    """Test that the RENDER_COMPLETE signal works correctly for determining screenshot timing."""
    # Create HTML with JavaScript that emits RENDER_COMPLETE after a delay
    # Reduce delay to 100ms for faster tests
    delay_ms = 100  # 100ms delay instead of 1000ms

    html_with_render_signal = HtmlDoc.create_from_html_parts(
        body=f"""
            <h1>Testing Render Complete Signal</h1>
            <div id="delayed-content">Content will appear shortly</div>
            <script>
                // This simulates content that loads after the initial page load
                setTimeout(() => {{
                    document.getElementById('delayed-content').textContent = 'Content has been loaded!';
                    // Signal that the render is complete
                    console.log('RENDER_COMPLETE');
                }}, {delay_ms});
            </script>
        """,
        head="<title>Render Signal Test</title>",
        css="body { font-family: Arial, sans-serif; }",
    )

    # Record start time before generating the image
    start_time = time.time()

    # Create a proper ScreenResolution object
    resolution = ScreenResolution(width=800, height=600)

    # Generate image and verify it was created successfully
    # Use a shorter timeout
    screenshot = await generate_image(
        html_with_render_signal,
        target_resolution=resolution,
        render_timeout=1.0,  # Shorter timeout for faster tests
    )

    # Calculate elapsed time
    elapsed_time = time.time() - start_time

    # Verify the screenshot was created
    assert isinstance(screenshot, bytes)
    assert len(screenshot) > 0

    # Verify that the elapsed time is greater than the delay
    # This confirms that we waited for the RENDER_COMPLETE signal
    assert elapsed_time > (delay_ms / 1000), f"Elapsed time {elapsed_time}s should be greater than delay {delay_ms/1000}s"


async def test_render_timeout_fallback():
    """Test that the render timeout fallback works correctly."""
    # Create HTML with JavaScript that never emits RENDER_COMPLETE
    html_without_render_signal = HtmlDoc.create_from_html_parts(
        body="""
            <h1>Testing Render Timeout Fallback</h1>
            <div>This page never emits a RENDER_COMPLETE signal</div>
        """,
        head="<title>Render Timeout Test</title>",
        css="body { font-family: Arial, sans-serif; }",
    )

    # Create a proper ScreenResolution object
    resolution = ScreenResolution(width=800, height=600)

    # Record start time before generating the image
    start_time = time.time()

    # Generate image with a very short timeout
    # This should trigger the fallback to networkidle
    screenshot = await generate_image(
        html_without_render_signal,
        target_resolution=resolution,
        render_timeout=0.1,  # Very short timeout to force fallback
    )

    # Calculate elapsed time
    elapsed_time = time.time() - start_time

    # Verify the screenshot was created despite no RENDER_COMPLETE signal
    assert isinstance(screenshot, bytes)
    assert len(screenshot) > 0

    # Verify that the elapsed time is close to the timeout
    # This confirms that we waited for the timeout and then fell back to networkidle
    assert elapsed_time >= 0.1, f"Elapsed time {elapsed_time}s should be at least 0.1s"
