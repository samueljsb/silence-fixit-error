# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

## Unreleased

### Fixed

- The `fix_silenced_fixit_error` module was not part of the built wheel, so the
  `fix-silenced-fixit-error` did not work:

  ```pytb
  ModuleNotFoundError: No module named 'fix_silenced_fixit_error'
  ```

  That module has been added to the package so is now available when installed via `pip`.

## 0.3.0 -- 2023-10-17

### Fixed

- Multi-line error messages are now handled correctly.

## 0.2.0 -- 2023-10-13

### Added

- A command to auto-fix violations silenced with a `fixme` comment

  This allows the existing violations to be fixed once there is an auto-fix
  available.

## 0.1.0 -- 2023-10-10

First release.
