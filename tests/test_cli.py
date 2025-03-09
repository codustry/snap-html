
import pytest
from typer.testing import CliRunner

from snap_html.__main__ import app

runner = CliRunner()


@pytest.fixture
def sample_html_file(tmp_path):
    html_content = """
        <html>
            <head><title>Test Page</title></head>
            <body><h1>Hello World</h1></body>
        </html>
    """
    file_path = tmp_path / "test.html"
    file_path.write_text(html_content)
    return file_path


def test_capture_from_html_file(sample_html_file, tmp_path):
    output_file = tmp_path / "output.png"
    result = runner.invoke(
        app,
        [
            "capture",
            str(sample_html_file),
            "--output",
            str(output_file),
            "--width",
            "800",
            "--height",
            "600",
        ],
    )
    assert result.exit_code == 0
    assert output_file.exists()
    assert "Image successfully saved" in result.stdout


def test_capture_from_url(tmp_path):
    output_file = tmp_path / "url_output.png"
    result = runner.invoke(
        app,
        [
            "capture",
            "https://example.com",
            "-o",
            str(output_file),
            "--width",
            "1024",
            "--height",
            "768",
        ],
    )
    assert result.exit_code == 0
    assert output_file.exists()
    assert "Image successfully saved" in result.stdout


def test_capture_with_cm_resolution(sample_html_file, tmp_path):
    output_file = tmp_path / "cm_output.png"
    result = runner.invoke(
        app,
        [
            "capture",
            str(sample_html_file),
            "--output",
            str(output_file),
            "--cm-width",
            "21.0",
            "--cm-height",
            "29.7",
            "--dpi",
            "300",
        ],
    )
    assert result.exit_code == 0
    assert output_file.exists()
    assert "Image successfully saved" in result.stdout


def test_capture_from_raw_html(tmp_path):
    output_file = tmp_path / "raw_output.png"
    html_content = "<html><body><h1>Test</h1></body></html>"
    result = runner.invoke(
        app,
        [
            "capture",
            html_content,
            "--output",
            str(output_file),
            "--width",
            "800",
            "--height",
            "600",
        ],
    )
    assert result.exit_code == 0
    assert output_file.exists()
    assert "Image successfully saved" in result.stdout


def test_capture_with_scale_factor(sample_html_file, tmp_path):
    output_file = tmp_path / "scaled_output.png"
    result = runner.invoke(
        app,
        [
            "capture",
            str(sample_html_file),
            "--output",
            str(output_file),
            "--width",
            "800",
            "--height",
            "600",
            "--scale",
            "2.0",
        ],
    )
    assert result.exit_code == 0
    assert output_file.exists()
    assert "Image successfully saved" in result.stdout


def test_capture_with_invalid_input():
    result = runner.invoke(
        app,
        [
            "capture",
            "nonexistent_file.html",
            "--width",
            "800",
            "--height",
            "600",
        ],
    )
    assert result.exit_code == 1
    assert "Error" in result.stdout


def test_capture_with_missing_dimensions(sample_html_file, tmp_path):
    """Test that default resolution is used when no dimensions are provided"""
    output_file = tmp_path / "default_output.png"
    result = runner.invoke(
        app, ["capture", str(sample_html_file), "--output", str(output_file)]
    )
    assert result.exit_code == 0
    assert output_file.exists()
    assert "Image successfully saved" in result.stdout


def test_capture_without_output_file(sample_html_file):
    """Test that the command works without specifying an output file"""
    result = runner.invoke(
        app,
        ["capture", str(sample_html_file), "--width", "800", "--height", "600"],
    )
    assert result.exit_code == 0
    assert "Image generated successfully" in result.stdout
