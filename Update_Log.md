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
- This version is the second alpha release of the FTML engine
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
- This version is the third alpha release of the FTML engine
- The editor is still unstable and several features are not yet implemented
- This version mainly serves as a recovery and fallback checkpoint

---

## v2.0.0-alpha.4-March 8, 2026

### Added
- Updated the css_styles/js
- Updated the code refactoration of `parse_node.py`
- Updated the code refactoration of `wikidot_exporter.py`
- Updated the code refactoration of `CSS_INJECTOR.py`
- Added `insert_html_at_point.js`
- Added `parse_node.py`
- Added `utils/templates/` in css and txt files:
    - `class_warning.txt`
    - `email_template.css`
    - `email_template.txt`
    - `foundation_background.css`
    - `foundation_background.txt`
    - `login_logout.css`
    - `login_logout.txt`
    - `o5_command.txt`
    - `page_note.css`
    - `page_note.txt`
    - `raisa_notice.txt`
    - `terminal_001.css`
    - `terminal_001.txt`
    - `terminal_shortcut.css`
    - `terminal_shortcut.txt`
    - `video_record.txt`
    - `video_record2.txt`

### Removed
- Removed all files in `utils/js` except `insert_html_at_point`
- Removed all files in `ui/css_styles/js/WILL_DELETE`

### Changed
- Changed `editor.html` code about files in `ui/css_styles/js/WILL_DELETE`

### Version
- Updated the version to `v2.0.0-alpha.4`
- LINCESE: AGPLv3
- Author: Zichen Wang (wasd243)

### Notes
- This version is the fourth alpha release of the FTML engine
- The editor is still unstable and several features are not yet implemented
- This version mainly serves as a recovery and fallback checkpoint

---

## v2.0.0-alpha.5-March 8-9, 2026

### Added
- Added the `collapsible.py`
- Updated the `banner.py` to alpha.5
- Updated the `logger.py` to alpha.5
- Updated the css_styles/js
- Updated the `wikidot_parser.py`
- Updated the `editor.html`
- Updated the `componentEvents.js`
- Updated the `CSS_INJECTOR.py`
- Updated the `wikidot_exporter.py`

### Changed
- Changed the `terminal_shortcut` render form from `html` to `components`
- Changed the `terminal_001` render form from `html` to `components`
- Changed the `collapsible` render form from `html` to `components`
- Changed the `email_example.py` render form from `html` to `components`
- Changed the `componentEvents.js` code about files

### Fixed
- Fixed the issue that RAISA-notice code could not generate successful
- Fixed the issue that the CSS modules could not generate on top
- Fixed the issue that the O5_command could not generate successful
- Fixed the issue that special CSS modules could not generate next to the div module
- Fixed the issue that the collapsible could not generate successful
- Fixed the issue that the email_example could not generate successful
- Fixed the issue that the terminal_001 could not generate successful
- Fixed the issue that the terminal_shortcut could not generate successful
- Fixed the issue that the "@@-----@@" could not generate successful
- Fixed the issue that the "@@-----@@" could not render successful
- Fixed the issue that the "@@@@" could not generate successful
- Fixed the issue that the "@@@@" could not render successful

### Version
- Updated the version to `v2.0.0-alpha.5`
- LINCESE: AGPLv3
- Author: Zichen Wang (wasd243)

### Notes
- This version is the fifth alpha release of the FTML engine
- The editor is still unstable and several features are not yet implemented
- This version mainly serves as a recovery and fallback checkpoint

---

### v2.0.0-alpha.6-March 10, 2026

### Added
- Added the WYSIWYG injection for:
    - `RAISA-notice`
    - `Page Note`
    - `O5-Command`
    - `Class Warning`
    - `Foundation Background`

### Changed
- Changed the `wikidot_parser.py` code about WYSIWYG injection
- Changed the `div.py` code about WYSIWYG injection
- Changed the `editor.html` code about WYSIWYG injection
- Changed the `componentEvents.js` code about WYSIWYG injection
- Changed the `CSS_INJECTOR.py` code about WYSIWYG injection
- Changed the `wikidot_exporter.py` code about WYSIWYG injection
- Changed the `banner.py` code about this version
- Changed the `logger.py` code about this version

### Removed
- Removed all temporary files in this version

### Fixed
- Fixed the issue that the `RAISA-notice` could not render with WYSIWYG injection successfully
- Fixed the issue that the `Page Note` could not render with WYSIWYG injection successfully
- Fixed the issue that the `O5-Command` could not render with WYSIWYG injection successfully
- Fixed the issue that the `Class Warning` could not render with WYSIWYG injection successfully
- Fixed the issue that the `Foundation Background` could not render with WYSIWYG injection successfully

### Version
- Updated the version to `v2.0.0-alpha.6`
- LINCESE: AGPLv3
- Author: Zichen Wang (wasd243)

### Notes
- This version is the sixth alpha release of the FTML engine
- The editor is still unstable and several features are not yet implemented
- This version mainly serves as a recovery and fallback checkpoint