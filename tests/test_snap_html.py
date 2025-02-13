import pytest
from snap_html import (
    generate_image,
    generate_image_sync,
    generate_image_batch,
    generate_image_batch_sync,
    HtmlDoc,
    UnitConverter,
)

@pytest.fixture
def sample_html():
    return HtmlDoc.create_from_html_parts(
        body="<h1>Hello World</h1>",
        head="<title>Test Page</title>",
        css="h1 { color: blue; }"
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

@pytest.mark.asyncio
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

@pytest.mark.asyncio
async def test_generate_image_from_url():
    screenshot = await generate_image(
        "https://example.com",
        resolution={"cm_width": 10.0, "cm_height": 7.5, "dpi": 300}
    )
    assert isinstance(screenshot, bytes)
    assert len(screenshot) > 0

@pytest.mark.asyncio
async def test_generate_image_with_cm_resolution(unit_converter):
    screenshot = await generate_image(
        "https://example.com",
        resolution={"cm_width": 21.0, "cm_height": 29.7, "dpi": 300}
    )
    assert isinstance(screenshot, bytes)
    assert len(screenshot) > 0

@pytest.mark.asyncio
async def test_generate_image_batch(sample_html, tmp_path):
    output_file1 = tmp_path / "test1.png"
    output_file2 = tmp_path / "test2.png"
    
    targets = [
        sample_html,
        "https://example.com"
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

@pytest.mark.asyncio
async def test_generate_image_with_query_params():
    query_params = {"param1": "value1", "param2": "value2"}
    screenshot = await generate_image(
        "https://httpbin.org/get",
        resolution={"width": 800, "height": 600},
        query_parameters=query_params
    )
    assert isinstance(screenshot, bytes)
    assert len(screenshot) > 0

@pytest.mark.asyncio
async def test_generate_image_with_scale_factor():
    screenshot = await generate_image(
        "https://example.com",
        resolution={"width": 800, "height": 600},
        scale_factor=2.0
    )
    assert isinstance(screenshot, bytes)
    assert len(screenshot) > 0 