# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- Command Line Interface (CLI) for capturing screenshots
- Support for both pixel and physical (cm) dimensions in CLI
- CLI options for scale factor and DPI settings
- New PrintMediaResolution type that combines pixel and CM dimensions
- Object-fit options (contain, cover, fill, none) for controlling how content fits in viewport
- Optional resolution parameter with sensible defaults

### Fixed

- Fixed unit conversion in UnitConverter class to properly handle Pint quantity objects
- Improved DPI and resolution handling for more accurate image sizing
- Fixed type checking issues with resolution parameters

### Changed

- Adjusted default device scale factor to 1.5 (150% zoom) for better image quality
- Modified resolution handling to support both screen and print media dimensions
- Made resolution parameter optional with sensible defaults
- Made object_fit parameter optional with a default value of "contain"
