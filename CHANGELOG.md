# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- Command Line Interface (CLI) for capturing screenshots
- Support for both pixel and physical (cm) dimensions in CLI
- CLI options for scale factor and DPI settings

### Fixed

- Fixed unit conversion in UnitConverter class to properly handle Pint quantity objects
- Improved DPI and resolution handling for more accurate image sizing

### Changed

- Adjusted default device scale factor to 1.5 (150% zoom) for better image quality
