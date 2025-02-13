# snap-html

<div align="center">

[![Build status](https://github.com/codustry/snap-html/workflows/build/badge.svg?branch=master&event=push)](https://github.com/codustry/snap-html/actions?query=workflow%3Abuild)
[![Python Version](https://img.shields.io/pypi/pyversions/snap-html.svg)](https://pypi.org/project/snap-html/)
[![Dependencies Status](https://img.shields.io/badge/dependencies-up%20to%20date-brightgreen.svg)](https://github.com/codustry/snap-html/pulls?utf8=%E2%9C%93&q=is%3Apr%20author%3Aapp%2Fdependabot)

[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Security: bandit](https://img.shields.io/badge/security-bandit-green.svg)](https://github.com/PyCQA/bandit)
[![Pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)](https://github.com/codustry/snap-html/blob/master/.pre-commit-config.yaml)
[![Semantic Versions](https://img.shields.io/badge/%F0%9F%9A%80-semantic%20versions-informational.svg)](https://github.com/codustry/snap-html/releases)
[![License](https://img.shields.io/github/license/codustry/snap-html)](https://github.com/codustry/snap-html/blob/master/LICENSE)

a robust, modern and high performance Python library for generating image from a html string/html file/url build on top of `playwright`

</div>

## Highlight

- All Basics, Async ready, Sync support, Fully Typed
- Builtin batch generator for higher performance
- Build on top of the giant `playwright`, simplified of headless browser and driver installation
- Accept html/css string, and You can use with `jinja2` for html templating

### TODO

- Maybe you would like to add [gitmoji](https://gitmoji.carloscuesta.me/) to commit names. This is really funny. 😄

For building and deployment:

- `GitHub` integration.
- [`Makefile`](https://github.com/codustry/snap-html/blob/master/Makefile#L89) for building routines. Everything is already set up for security checks, codestyle checks, code formatting, testing, linting, docker builds, etc. More details at [Makefile summary](#makefile-usage)).
- [Dockerfile](https://github.com/codustry/snap-html/blob/master/docker/Dockerfile) for your package.
- `Github Actions` with predefined [build workflow](https://github.com/codustry/snap-html/blob/master/.github/workflows/build.yml) as the default CI/CD.
- Always up-to-date dependencies with [`@dependabot`](https://dependabot.com/) (You will only [enable it](https://docs.github.com/en/github/administering-a-repository/enabling-and-disabling-version-updates#enabling-github-dependabot-version-updates)).
- Automatic drafts of new releases with [`Release Drafter`](https://github.com/marketplace/actions/release-drafter). It creates a list of changes based on labels in merged `Pull Requests`. You can see labels (aka `categories`) in [`release-drafter.yml`](https://github.com/codustry/snap-html/blob/master/.github/release-drafter.yml). Works perfectly with [Semantic Versions](https://semver.org/) specification.

For creating your open source community:

- Ready-to-use [Pull Requests templates](https://github.com/codustry/snap-html/blob/master/.github/PULL_REQUEST_TEMPLATE.md) and several [Issue templates](https://github.com/codustry/snap-html/tree/master/.github/ISSUE_TEMPLATE).
- Files such as: `LICENSE`, `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md`, and `SECURITY.md` are generated automatically.
- [`Stale bot`](https://github.com/apps/stale) that closes abandoned issues after a period of inactivity. (You will only [need to setup free plan](https://github.com/marketplace/stale)). Configuration is [here](https://github.com/codustry/snap-html/blob/master/.github/.stale.yml).
- [Semantic Versions](https://semver.org/) specification with [`Release Drafter`](https://github.com/marketplace/actions/release-drafter).

## Installation

```bash
pip install -U snap-html

python -m playwright install

# Install system dependencies for Linux (required for browsers)
sudo playwright install-deps
# Or manually install dependencies:
sudo apt-get install libwoff1 libevent-2.1-7t64 libgstreamer-plugins-base1.0-0 libgstreamer-gl1.0-0 libgstreamer-plugins-bad1.0-0 libenchant-2-2 libsecret-1-0 libhyphen0 libmanette-0.2-0
```

or install with `Poetry`

```bash
poetry add snap-html
```

Then you can run

```bash
snap-html --help
```

```bash
snap-html --name Roman
```

or if installed with `Poetry`:

```bash
poetry run snap-html --help
```

```bash
poetry run snap-html --name Roman
```

### Makefile usage

[`Makefile`](https://github.com/codustry/snap-html/blob/master/Makefile) contains many functions for fast assembling and convenient work.

<details>
<summary>1. Download Poetry</summary>
<p>

```bash
make download-poetry
```

</p>
</details>

<details>
<summary>2. Install all dependencies and pre-commit hooks</summary>
<p>

```bash
make install
```

If you do not want to install pre-commit hooks, run the command with the NO_PRE_COMMIT flag:

```bash
make install NO_PRE_COMMIT=1
```

</p>
</details>

<details>
<summary>3. Check the security of your code</summary>
<p>

```bash
make check-safety
```

This command launches a `Poetry` and `Pip` integrity check as well as identifies security issues with `Safety` and `Bandit`. By default, the build will not crash if any of the items fail. But you can set `STRICT=1` for the entire build, or you can configure strictness for each item separately.

```bash
make check-safety STRICT=1
```

or only for `safety`:

```bash
make check-safety SAFETY_STRICT=1
```

multiple

```bash
make check-safety PIP_STRICT=1 SAFETY_STRICT=1
```

> List of flags for `check-safety` (can be set to `1` or `0`): `STRICT`, `POETRY_STRICT`, `PIP_STRICT`, `SAFETY_STRICT`, `BANDIT_STRICT`.

</p>
</details>

<details>
<summary>4. Check the codestyle</summary>
<p>

The command is similar to `check-safety` but to check the code style, obviously. It uses `Black`, `Darglint`, `Isort`, and `Mypy` inside.

```bash
make check-style
```

It may also contain the `STRICT` flag.

```bash
make check-style STRICT=1
```

> List of flags for `check-style` (can be set to `1` or `0`): `STRICT`, `BLACK_STRICT`, `DARGLINT_STRICT`, `ISORT_STRICT`, `MYPY_STRICT`.

</p>
</details>

<details>
<summary>5. Run all the codestyle formaters</summary>
<p>

Codestyle uses `pre-commit` hooks, so ensure you've run `make install` before.

```bash
make codestyle
```

</p>
</details>

<details>
<summary>6. Run tests</summary>
<p>

```bash
make test
```

</p>
</details>

<details>
<summary>7. Run all the linters</summary>
<p>

```bash
make lint
```

the same as:

```bash
make test && make check-safety && make check-style
```

> List of flags for `lint` (can be set to `1` or `0`): `STRICT`, `POETRY_STRICT`, `PIP_STRICT`, `SAFETY_STRICT`, `BANDIT_STRICT`, `BLACK_STRICT`, `DARGLINT_STRICT`, `ISORT_STRICT`, `MYPY_STRICT`.

</p>
</details>

<details>
<summary>8. Build docker</summary>
<p>

```bash
make docker
```

which is equivalent to:

```bash
make docker VERSION=latest
```

More information [here](https://github.com/codustry/snap-html/tree/master/docker).

</p>
</details>

<details>
<summary>9. Cleanup docker</summary>
<p>

```bash
make clean_docker
```

or to remove all build

```bash
make clean
```

More information [here](https://github.com/codustry/snap-html/tree/master/docker).

</p>
</details>

## 📈 Releases

You can see the list of available releases on the [GitHub Releases](https://github.com/codustry/snap-html/releases) page.

We follow [Semantic Versions](https://semver.org/) specification.

We use [`Release Drafter`](https://github.com/marketplace/actions/release-drafter). As pull requests are merged, a draft release is kept up-to-date listing the changes, ready to publish when you're ready. With the categories option, you can categorize pull requests in release notes using labels.

For Pull Request this labels are configured, by default:

|               **Label**               |  **Title in Releases**  |
| :-----------------------------------: | :---------------------: |
|       `enhancement`, `feature`        |       🚀 Features       |
| `bug`, `refactoring`, `bugfix`, `fix` | 🔧 Fixes & Refactoring  |
|       `build`, `ci`, `testing`        | 📦 Build System & CI/CD |
|              `breaking`               |   💥 Breaking Changes   |
|            `documentation`            |    📝 Documentation     |
|            `dependencies`             | ⬆️ Dependencies updates |

You can update it in [`release-drafter.yml`](https://github.com/codustry/snap-html/blob/master/.github/release-drafter.yml).

GitHub creates the `bug`, `enhancement`, and `documentation` labels for you. Dependabot creates the `dependencies` label. Create the remaining labels on the Issues tab of your GitHub repository, when you need them.

## 🛡 License

[![License](https://img.shields.io/github/license/codustry/snap-html)](https://github.com/codustry/snap-html/blob/master/LICENSE)

This project is licensed under the terms of the `MIT` license. See [LICENSE](https://github.com/codustry/snap-html/blob/master/LICENSE) for more details.

## 📃 Citation

```
@misc{snap-html,
  author = {codustry},
  title = {a robust, modern and high performance Python library for generating image from a html string/html file/url build on top of `playwright`},
  year = {2021},
  publisher = {GitHub},
  journal = {GitHub repository},
  howpublished = {\url{https://github.com/codustry/snap-html}}
}
```

## Credits

This project was generated with [`python-package-template`](https://github.com/TezRomacH/python-package-template).

## Alternative

1. <https://github.com/vgalin/html2image>

## Usage

### Basic Usage

```python
from snap_html import generate_image_sync
from pathlib import Path

# Capture from URL
screenshot = generate_image_sync(
    "https://www.example.com",
    resolution={"width": 1920, "height": 1080},
    output_file=Path("screenshot.png")
)

# Capture with physical dimensions (in centimeters)
screenshot = generate_image_sync(
    "https://www.example.com",
    resolution={
        "cm_width": 21,      # A4 width
        "cm_height": 29.7,   # A4 height
        "dpi": 300          # Print quality DPI
    },
    output_file=Path("high_quality.png")
)
```

### Resolution Options

The library supports two ways to specify output resolution:

1. Pixel Dimensions:

```python
resolution = {
    "width": 1920,    # Width in pixels
    "height": 1080    # Height in pixels
}
```

2. Physical Dimensions:

```python
resolution = {
    "cm_width": 21,    # Width in centimeters
    "cm_height": 29.7, # Height in centimeters
    "dpi": 300        # Dots per inch (optional, defaults to 300)
}
```

### Batch Processing

For better performance when capturing multiple screenshots:

```python
from snap_html import generate_image_batch_sync

screenshots = generate_image_batch_sync(
    targets=["https://example1.com", "https://example2.com"],
    resolution={"width": 1920, "height": 1080},
    output_files=["screenshot1.png", "screenshot2.png"]
)
```

## CLI Usage

snap-html provides a command-line interface for quick image captures:

```bash
# Basic usage with pixel dimensions
snap-html capture https://example.com -o screenshot.png --width 1920 --height 1080

# Using physical dimensions (e.g., A4 paper size)
snap-html capture input.html --cm-width 21.0 --cm-height 29.7 --dpi 300 -o output.png

# Capture with custom scale factor
snap-html capture https://example.com -o screenshot.png --width 1024 --height 768 --scale 2.0
```

### CLI Options

```
Options:
  -o, --output PATH         Output image file path
  -w, --width INTEGER       Output width in pixels
  -h, --height INTEGER      Output height in pixels
  --cm-width FLOAT         Output width in centimeters
  --cm-height FLOAT        Output height in centimeters
  --dpi INTEGER            DPI for cm-based resolution [default: 300]
  --scale FLOAT            Browser scale factor (zoom level) [default: 1.0]
  --help                   Show this message and exit.
```

The CLI supports three types of input:

1. URLs (e.g., https://example.com)
2. HTML files (e.g., page.html)
3. Raw HTML strings
