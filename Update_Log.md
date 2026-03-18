# Changelog


All notable changes to this project will be documented in this file.

---

## [v2.0.1-beta.4] - 2026-03-19

### Added

- Added `middle` button on toolbar

### Changed

- Updated `parse_node.py` for `middle` button
- Updated `main_window_view.py` for `middle` button

### Fixed

- Fixed `[[size xxx]]text[[/size]]` generate issue

---

## [v2.0.1-beta.4] - 2026-03-18

### Added
- Added `TOC` component support
- Added toolbar button for `prevent enter key`
- Added toolbar button for `no @@@@`
- Added `prevent enter key` to `main_window_view.py`
- Added `no @@@@` to `main_window_view.py`

### Changed
- Updated `parse_node.py` for newline handling
- Updated `wikidot_parser.py` for newline handling
- Updated `MAIN_CONTROLLER.py` for newline handling
- Updated `main_window_view.py` for newline handling
- Updated `editor.js` for prevent enter key
- Updated `main_window_view.py` for prevent enter key

### Fixed
- Fixed newline width issue
- Fixed enter key issue
- Fixed paste issue
- Fixed TOC generation issue

---

## [v2.0.1-beta.3] - 2026-03-18

### Fixed
- Fixed CSS duplicate output issue
- Fixed empty CSS block output issue
- Fixed extra newline output issue
- Fixed `TOC` could not be inserted
- Fixed `TOC` could not be removed
- Fixed `TOC` could not be updated
- Fixed `[[module CSS]]` could not be removed
- Fixed `[[module CSS]]` could not be updated

### Removed

- Removed `TOC` from toolbar

---

## [v2.0.1-beta.2] - 2026-03-18

### Changed
- Updated `editor.css` for user tag
- Updated `wikidot_parser.py` for user tag rendering
- Improved paste handling (plain text only)
- Updated component event filtering

### Fixed
- Fixed user tag rendering issues

---

## [v2.0.1-beta.1] - 2026-03-17

### Added
- Added shortcuts: `Ctrl+B`, `Ctrl+I`, `Ctrl+U`

### Changed
- Improved newline handling logic in `parse_node.py`

### Fixed
- Fixed shortcut keys not working

---

## [v2.0.0-beta.9] - 2026-03-16

### Changed
- Refactored TOC logic across parser and controller
- Updated heading styles in `editor.css`

### Fixed
- Fixed TOC rendering issues
- Fixed CSS newline loading issue

---

## [v2.0.0-beta.8] - 2026-03-15

### Added
- Added TOC component support

### Fixed
- Fixed TOC rendering issues
- Fixed newline width issue

---

## [v2.0.0-beta.7] - 2026-03-15

### Added
- Added monospaced font protection

### Fixed
- Fixed `@@@@` rendering issues

---

## [v2.0.0-beta.6] - 2026-03-14

### Added
- Added clear styles feature

### Fixed
- Fixed table and style issues

---

## [v2.0.0-beta.5] - 2026-03-14

### Added
- Added context menu system

### Fixed
- Fixed ACS menu issues

---

## [v2.0.0-beta.1] - 2026-03-11

### Added
- Added image auto format
- Added collapsible UI renderer

---

## [v2.0.0-alpha.6] - 2026-03-10

### Added
- Added WYSIWYG injection system

---

## [v2.0.0-alpha.5] - 2026-03-08~09

### Added
- Added collapsible component

---

## [v2.0.0-alpha.4] - 2026-03-08

### Added
- Major parser refactor

---

## [v2.0.0-alpha.3] - 2026-03-07

### Added
- UI component updates

---

## [v2.0.0-alpha.2] - 2026-03-06

### Changed
- Initial modular refactor
