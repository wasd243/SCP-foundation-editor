## v2.0.0-alpha.2-March 6, 2026

### Changed
- Completed the main code decomposition
- Changed the update log
- Changed `banner.py` for the startup banner
- Changed `logger.py` for the logging system
- Changed the author's real name: Zichen Wang

### Fixed
- Fixed an issue where div styles were not rendered in the editor
- Fixed an issue where CSS styles were not rendered in the editor
- Fixed an issue where JS scripts were not executed correctly in the editor

### ACS
- Updated the ACS style to the new ACS layout
- Fixed an issue where the ACS button could not respond to user clicks

### Image Block
- Fixed an issue where image blocks could not render image links correctly

### Version
- Updated the version to `v2.0.0-alpha.2`
- Updated the license to GNU AGPLv3
- Updated the author information to **Zichen Wang (wasd243)**

### Notes
- This version is the second pre-alpha release of the FTML engine
- The editor is still unstable and several features are not yet implemented
- This version mainly serves as a recovery and fallback checkpoint

---

## v2.0.0-alpha.3-March 7, 2026

### Added
- Updated the css_styles/js 
- Finished the main code decomposition

### Changed
- Changed the user tag component
- Changed the user advanced tag component
- Changed the user tag button
- Changed the user advanced tag button

### Fixed
- Fixed an issue where the error message "Sorry, the page you are looking for does not exist" was displayed when the page restarted

### Version
- Updated the version to `v2.0.0-alpha.3`
- Updated the license to GNU AGPLv3
- Updated the author information to **Zichen Wang (wasd243)**

### Notes
- This version is the third pre-alpha release of the FTML engine
- The editor is still unstable and several features are not yet implemented
- This version mainly serves as a recovery and fallback checkpoint

---

## v2.0.0-alpha.4 — March 8, 2026

### Added
- Added `insert_html_at_point.js`
- Added `parse_node.py`
- Added `utils/templates/` (css and txt templates):
  - class_warning
  - email_template
  - foundation_background
  - login_logout
  - o5_command
  - page_note
  - raisa_notice
  - terminal_001
  - terminal_shortcut
  - video_record
  - video_record2

### Changed
- Refactored `parse_node.py`
- Refactored `wikidot_exporter.py`
- Refactored `CSS_INJECTOR.py`
- Updated files in `ui/css_styles/js`
- Updated `editor.html` references to removed files

### Removed
- Removed all files in `utils/js` except `insert_html_at_point.js`
- Removed deprecated files in `ui/css_styles/js/WILL_DELETE`

### Version
- Version: `v2.0.0-alpha.4`
- License: AGPLv3
- Author: Zichen Wang (wasd243)

### Notes
- This version is the fourth pre-alpha release of the FTML engine
- The editor is still unstable and several features are not yet implemented
- This version mainly serves as a recovery and fallback checkpointe editor is still unstable and several features are not yet implemented
- This version mainly serves as a recovery and fallback checkpoint
