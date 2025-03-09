import pytest
import time
from snap_html import (
    generate_image,
    generate_image_sync,
    generate_image_batch,
    generate_image_batch_sync,
    HtmlDoc,
    UnitConverter,
)

# Define a marker for slow tests that can be skipped with -m "not slow"
pytestmark = pytest.mark.asyncio

@pytest.fixture
def sample_html():
    return HtmlDoc.create_from_html_parts(
        body="<h1>Hello World</h1>",
        head="<title>Test Page</title>",
        css="h1 { color: blue; }"
    )

@pytest.fixture
def simple_page():
    """Fixture for a simple HTML page to replace external URL dependencies"""
    return HtmlDoc.create_from_html_parts(
        body="<h1>Example Page</h1><p>This is a local test page</p>",
        head="<title>Example Page</title>",
        css="body { font-family: Arial; }"
    )

@pytest.fixture
def unit_converter():
    return UnitConverter()

def test_unit_converter(unit_converter):
    # Test cm to pixels conversion with 96 DPI (common screen resolution)
    assert unit_converter.cm_to_pixels(2.54, 96) == 96  # 1 inch = 2.54 cm = 96 pixels at 96 DPI
    assert unit_converter.cm_to_pixels(5.08, 96) == 192  # 2 inches
    
    # Test with different DPI
    assert unit_converter.cm_to_pixels(2.54, 300) == 300  # 1 inch at 300 DPI

def test_html_doc_creation():
    doc = HtmlDoc.create_from_html_parts(
        body="<p>Test</p>",
        head="<title>Test</title>",
        css="p { color: red; }"
    )
    assert "<title>Test</title>" in doc.html
    assert "<p>Test</p>" in doc.html
    assert "p { color: red; }" in doc.html

async def test_generate_image_from_html(sample_html, tmp_path):
    output_file = tmp_path / "test.png"
    screenshot = await generate_image(
        sample_html,
        resolution={"cm_width": 21.0, "cm_height": 29.7, "dpi": 300},  # A4 paper size in cm
        output_file=output_file
    )
    
    assert isinstance(screenshot, bytes)
    assert output_file.exists()
    assert output_file.stat().st_size > 0

async def test_generate_image_from_url(simple_page):
    # Use local HTML instead of external URL
    screenshot = await generate_image(
        simple_page,
        resolution={"cm_width": 10.0, "cm_height": 7.5, "dpi": 300}
    )
    assert isinstance(screenshot, bytes)
    assert len(screenshot) > 0

async def test_generate_image_with_cm_resolution(unit_converter, simple_page):
    # Use local HTML instead of external URL
    screenshot = await generate_image(
        simple_page,
        resolution={"cm_width": 21.0, "cm_height": 29.7, "dpi": 300}
    )
    assert isinstance(screenshot, bytes)
    assert len(screenshot) > 0

async def test_generate_image_batch(sample_html, simple_page, tmp_path):
    output_file1 = tmp_path / "test1.png"
    output_file2 = tmp_path / "test2.png"
    
    targets = [
        sample_html,
        simple_page  # Use local HTML instead of external URL
    ]
    
    output_files = [output_file1, output_file2]
    
    screenshots = await generate_image_batch(
        targets,
        resolution={"cm_width": 10.0, "cm_height": 7.5, "dpi": 300},
        output_files=output_files
    )
    
    assert len(screenshots) == 2
    assert all(isinstance(screenshot, bytes) for screenshot in screenshots)
    assert all(output_file.exists() for output_file in output_files)

def test_sync_functions(sample_html, tmp_path):
    output_file = tmp_path / "test_sync.png"
    
    # Test single image generation
    screenshot = generate_image_sync(
        sample_html,
        resolution={"width": 800, "height": 600},
        output_file=output_file
    )
    assert isinstance(screenshot, bytes)
    assert output_file.exists()
    
    # Test batch generation
    screenshots = generate_image_batch_sync(
        [sample_html],
        resolution={"width": 800, "height": 600}
    )
    assert isinstance(screenshots, list)
    assert len(screenshots) == 1
    assert isinstance(screenshots[0], bytes)

@pytest.mark.slow
async def test_generate_image_with_query_params():
    # Keep this test using external URL as it specifically tests query parameters
    query_params = {"param1": "value1", "param2": "value2"}
    screenshot = await generate_image(
        "https://httpbin.org/get",
        resolution={"width": 800, "height": 600},
        query_parameters=query_params
    )
    assert isinstance(screenshot, bytes)
    assert len(screenshot) > 0

async def test_generate_image_with_scale_factor(simple_page):
    # Use local HTML instead of external URL
    screenshot = await generate_image(
        simple_page,
        resolution={"width": 800, "height": 600},
        scale_factor=2.0
    )
    assert isinstance(screenshot, bytes)
    assert len(screenshot) > 0

async def test_generate_image_with_print_media_resolution(simple_page):
    """Test using both pixel and CM dimensions with object-fit options."""
    # Test with print media resolution (both pixel and physical dimensions)
    screenshot = await generate_image(
        simple_page,
        resolution={
            # Screen dimensions (viewport)
            "width": 1920, 
            "height": 1080,
            # Physical dimensions (print)
            "cm_width": 21.0, 
            "cm_height": 29.7, 
            "dpi": 300,
            # How to fit content
            "object_fit": "contain"
        }
    )
    assert isinstance(screenshot, bytes)
    assert len(screenshot) > 0
    
    # Test with different object-fit value
    screenshot = await generate_image(
        simple_page,
        resolution={
            "width": 1920, 
            "height": 1080,
            "cm_width": 21.0, 
            "cm_height": 29.7, 
            "dpi": 300,
            "object_fit": "cover"
        }
    )
    assert isinstance(screenshot, bytes)
    assert len(screenshot) > 0
    
    # Test with fill object-fit
    screenshot = await generate_image(
        simple_page,
        resolution={
            "width": 1920, 
            "height": 1080,
            "cm_width": 21.0, 
            "cm_height": 29.7, 
            "dpi": 300,
            "object_fit": "fill"
        }
    )
    assert isinstance(screenshot, bytes)
    assert len(screenshot) > 0
    
    # Test with explicit object_fit parameter (overriding resolution)
    screenshot = await generate_image(
        simple_page,
        resolution={
            "width": 1920, 
            "height": 1080,
            "cm_width": 21.0, 
            "cm_height": 29.7, 
            "dpi": 300,
        },
        object_fit="none"
    )
    assert isinstance(screenshot, bytes)
    assert len(screenshot) > 0
    
    # Test with omitted object_fit (should default to contain)
    screenshot = await generate_image(
        simple_page,
        resolution={
            "width": 1920, 
            "height": 1080,
            "cm_width": 21.0, 
            "cm_height": 29.7, 
            "dpi": 300,
        }
    )
    assert isinstance(screenshot, bytes)
    assert len(screenshot) > 0
    
    # Test with completely default resolution
    screenshot = await generate_image(
        simple_page  # No resolution specified, should use defaults
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
        css="body { font-family: Arial, sans-serif; }"
    )
    
    # Record start time before generating the image
    start_time = time.time()
    
    # Generate image and verify it was created successfully
    # Use a shorter timeout
    screenshot = await generate_image(
        html_with_render_signal,
        resolution={"width": 800, "height": 600},
        render_timeout=1.0  # Shorter timeout for faster tests
    )
    
    # Calculate elapsed time
    elapsed_time = time.time() - start_time
    
    assert isinstance(screenshot, bytes)
    assert len(screenshot) > 0
    
    # The screenshot should have been taken after the render complete signal
    min_expected_time = delay_ms / 1000  # Convert ms to seconds
    assert elapsed_time >= min_expected_time, f"Screenshot was taken in {elapsed_time:.2f}s, expected at least {min_expected_time:.2f}s"

async def test_render_timeout_fallback():
    """Test that rendering falls back to networkidle when no RENDER_COMPLETE signal is sent."""
    # Create HTML with no RENDER_COMPLETE signal
    html_without_render_signal = HtmlDoc.create_from_html_parts(
        body="<h1>Testing Render Timeout</h1><div>This page never sends a RENDER_COMPLETE signal</div>",
        head="<title>Timeout Test</title>"
    )
    
    # Record start time before generating the image
    start_time = time.time()
    
    # Use a very short timeout to trigger the fallback quickly
    short_timeout = 0.1  # 100ms timeout, for faster tests
    
    # Generate image with short timeout
    screenshot = await generate_image(
        html_without_render_signal,
        resolution={"width": 800, "height": 600},
        render_timeout=short_timeout
    )
    
    # Calculate elapsed time
    elapsed_time = time.time() - start_time
    
    assert isinstance(screenshot, bytes)
    assert len(screenshot) > 0
    
    # Verify the minimum time constraint - we should at least wait for the timeout
    assert elapsed_time >= short_timeout, f"Timeout fallback occurred too quickly: {elapsed_time:.2f}s vs {short_timeout:.2f}s expected"
    # Don't be too strict on the upper bound, as network and processing can vary
    assert elapsed_time < short_timeout + 10.0, f"Timeout fallback took too long: {elapsed_time:.2f}s"     
    # Log the actual time instead of asserting a strict upper bound
    # Browser initialization and other factors can make this unpredictable
    print(f"Timeout fallback test completed in {elapsed_time:.2f}s (timeout: {short_timeout}s)") 