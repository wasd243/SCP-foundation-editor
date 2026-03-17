## TOC

- [v2.0.0-alpha.2-March 6, 2026](#v200-alpha2-march-6-2026)
- [v2.0.0-alpha.3-March 7, 2026](#v200-alpha3-march-7-2026)
- [v2.0.0-alpha.4-March 8, 2026](#v200-alpha4-march-8-2026)
- [v2.0.0-alpha.5-March 8-9, 2026](#v200-alpha5-march-8-9-2026)
- [v2.0.0-alpha.6-March 10, 2026](#v200-alpha6-march-10-2026)
- [v2.0.0-beta.1-March 11, 2026](#v200-beta1-march-11-2026)
- [v2.0.0-beta.5-March 14, 2026](#v200-beta5-march-14-2026)
- [v2.0.0-beta.6-March 14, 2026](#v200-beta6-march-14-2026)
- [v2.0.0-beta.7-March 15, 2026](#v200-beta7-march-15-2026)
- [v2.0.0-beta.8-March 15, 2026](#v200-beta8-march-15-2026)
- [v2.0.0-beta.9-March 16, 2026](#v200-beta9-march-16-2026)
- [v2.0.1-beta.1-March 16, 2026](#v201-beta1-march-16-2026)
- [v2.0.1-beta.2-March 17, 2026](#v201-beta2-march-17-2026)

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

- This version is the second alpha release with the FTML engine
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

- This version is the third alpha release with the FTML engine
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

- This version is the fourth alpha release with the FTML engine
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

- This version is the fifth alpha release with the FTML engine
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

- This version is the sixth alpha release with the FTML engine
- The editor is still unstable and several features are not yet implemented
- This version mainly serves as a recovery and fallback checkpoint

---

## v2.0.0-beta.1-March 11, 2026

### Added

- Added the `auto format` for image block
- Added the `collapsible` renderer for `ui`

### Changed

- Changed the `MAIN_CONTROLLER.py` code about `insert_hr`
- Changed the `menu_controller.py` code about `insert_hr`
- Changed the `run_insert_js.js` code about `insert_hr`
- Changed the `wikidot_exporter.py` code about `@@@@`
- Changed the `parse_node.py` code about `@@@@`
- Changed the `banner.py` code about this version
- Changed the `banner.py` position from `core/` to `utils/`
- Changed the `logger.py` code about this version
- Changed the `logger.py` position from `core/` to `utils/`

### Removed

- Removed `core/` folder because it is not used

### Fixed

- Fixed the issue that the `ACS夜琉璃` style button could not render successfully
- Fixed the issue that the `table` could not generate successfully
- Fixed the issue that the `image` width and height could not set automatically
- Fixed the issue that the `size` of text could not set successfully
- Fixed the issue that the `basalt code` could not parse successfully

### Version

- Updated the version to `v2.0.0-beta.1`
- LINCESE: AGPLv3
- Author: Zichen Wang (wasd243)

### Notes

- This version is the first beta release with the FTML engine
- The editor is still unstable and several features are not yet implemented
- This version mainly serves as a recovery and fallback checkpoint

## v2.0.0-beta.5-March 14, 2026

### Added

- Added the `SCPEditor.spec` file
- Added the `resource_path.py` in `utils/`
- Added the `ftml_py.dll` to the `SCPEditor.spec`
- Added the `context_menu_comp.js`
- Added the `context_menu_hr.js`
- Added the `context_menu_table.js`
- Added the `context_menu_tab.js`
- Added the `context_menu_fn.js`
- Updated the `wikidot_parser.py` code about `component`

### Changed

- Changed the `MAIN_CONTROLLER.py` code about `SCPEditor.spec`
- Changed the `ui/main_window_view.py` code about `SCPEditor.spec`

### Fixed

- Fixed the issue that the `ACS` right click menu could not render successfully

### Removed

- Removed ```js
alert("标题js加载成功，有不统一的地方目前无法修复，可能会在后续更新处理")
``` in `Title.js`

### Version

- Updated the version to `v2.0.0-beta.5`
- LINCESE: AGPLv3
- Author: Zichen Wang (wasd243)

### Notes

- This version is the fifth beta release with the FTML engine
- The editor is stable

## v2.0.0-beta.6-March 14, 2026

### Added

- Added the `clear styles.js` in `ui/css_styles/js/`
- Added the `clear styles` button in `ui/main_window_view.py`
- Added the `__init__.py` in `ui/widgets/`

### Changed

- Changed the `.gitignore` code about `Antigravity`
- Changed the `.gitignore` code about `IDE`
- Changed the `.gitignore` code about `FTML`
- Changed the `MAIN_CONTROLLER.py` code about `clear styles`
- Changed the `toolbar_controller.py` code about `clear styles`
- Changed the `main_window_view.py` code about `clear styles`
- Changed the `componentEvents.js` code about `clear styles`
- Changed the `wikidot_exporter.py` code about `clear styles`
- Changed the `banner.py` code about this version
- Changed the `logger.py` code about this version

### Fixed

- Fixed the issue that the `clear styles` button could not work
- Fixed the issue that if the user click right of `table`, the `table` could Enter a new line
- Fixed the issue that the `table` could not generate successfully

### Version

- Updated the version to `v2.0.0-beta.6`
- LINCESE: AGPLv3
- Author: Zichen Wang (wasd243)

### Notes

- This version is the sixth beta release with the FTML engine
- The editor is stable

## v2.0.0-beta.7-March 15, 2026

### Added

- Added the `monospaced font` protection to prevent the user set Chinese in `monospaced font`

### Changed

- Changed the `MAIN_CONTROLLER.py` code about `@@@@`
- Changed the `wikidot_exporter.py` code about `@@@@`
- Changed the `wikidot_parser.py` code about `@@@@`
- Changed the `parse_node.py` code about `@@@@`
- Changed the `banner.py` code about this version
- Changed the `logger.py` code about this version

### Fixed

- Fixed the issue that the `@@@@` could not render successfully
- Fixed the issue that the `@@@@` could not generate correctly
- Fixed the issue that the `monospaced font` wikidot code could not generate successfully

### Version

- Updated the version to `v2.0.0-beta.7`
- LINCESE: AGPLv3
- Author: Zichen Wang (wasd243)

### Notes

- This version is the seventh beta release with the FTML engine
- The editor is stable

## v2.0.0-beta.8-March 15, 2026

### Added

- Added the `toc.py` in `engine/process/interceptor/Components` for render and generating TOC code in wikidot

### Changed

- Changed the `wikidot_exporter.py` code about `TOC`
- Changed the `wikidot_parser` code about `TOC`
- Changed the `MAIN_INTERCEPTOR.py` code about `TOC`
- Changed the `banner.py` code about this version
- Changed the `logger.py` code about this version

### Fixed

- Fixed the issue that while user inserting a new line, the width of new line was 2*normal line
- Fixed the issue that `TOC` could not render and generate successfully

### Version

- Updated the version to `v2.0.0-beta.8`
- LINCESE: AGPLv3
- Author: Zichen Wang (wasd243)

### Notes

- This version is the eighth beta release with the FTML engine
- The editor is not stable yet

## v2.0.0-beta.9-March 16, 2026

### Changed

- Changed the `MAIN_INTERCEPTOR.py` code about `TOC`
- Changed the `MAIN_CONTROLLER.py` code about `TOC`
- Changed the `wikidot_parser.py` code about `TOC`
- Changed the `wikidot_exporter.py` code about `TOC`
- Changed the `parse_node.py` code about `TOC`
- Changed the `main_window_view.py` code about `TOC`
- Changed the `banner.py` code about this version
- Changed the `logger.py` code about this version
- #### CSS Styles Changed
    - Changed the `editor.css` code about `TOC`
    ```css
    /* --- 标题样式 --- */
    h1,
    h2,
    h3,
    h4,
    h5,
    h6,

    h1 {
        color: #901111;
        font-size: 1.6em;
    }

    h2 {
        color: #000;
        font-size: 1.4em;
    }

    h3 {
        color: #000;
        font-size: 1.2em;
    }

    h4 {
        color: #000;
        font-size: 1.1em;
    }

    h5 {
        color: #000;
        font-size: 1em;
    }

    h6 {
        color: #000;
        font-size: 1em;
    }
    ```

### Fixed

- Fixed the issue that `TOC` could not render and generate successfully
- Fixed the issue that `editor.css` could not load new line successfully

### Version

- Updated the version to `v2.0.0-beta.9`
- LINCESE: AGPLv3
- Author: Zichen Wang (wasd243)

### Notes

- This version is the ninth beta release with the FTML engine
- The editor is stable

## v2.0.1-beta.1-March 17, 2026

### Added

- Added the `Ctrl+B`, `Ctrl+I`, `Ctrl+U` shortcuts for `bold`, `italic`, `underline`

### Changed

- Changed the `MAIN_CONTROLLER.py` code about `Ctrl+B`, `Ctrl+I`, `Ctrl+U` shortcuts
- Changed the `toolbar_controller.py` code about `Ctrl+B`, `Ctrl+I`, `Ctrl+U` shortcuts
- Changed the `main_window_view.py` code about `Ctrl+B`, `Ctrl+I`, `Ctrl+U` shortcuts
- Changed the `parse_node.py` code about `@@@@` from `count-1` to `count-2`
```python
if tag == 'p':
        def expand_soft_breaks(match):
            count = len(match.group(0))
            if count <= 2:
                return "\n" * count
            # 保留一个\n作为段落分隔，后面紧连(N-2)个@@@@
            return "\n" + ("@@@@\n" * (count - 2))
        content = re.sub(r'\n{2,}', expand_soft_breaks, content)
        clean = content.replace('**', '').replace('//', '').replace('__', '').replace('^^', '').replace(',,', '').strip()
        if not clean: return "\n@@@@\n"
```
- Changed the `banner.py` code about this version
- Changed the `logger.py` code about this version

### Fixed

- Fixed the issue that `Ctrl+B`, `Ctrl+I`, `Ctrl+U` shortcuts could not work

### Version

- Updated the version to `v2.0.1-beta.1`
- LINCESE: AGPLv3
- Author: Zichen Wang (wasd243)

### Notes

- This version is the first beta release with the FTML engine
- The editor is stable

## v2.0.1-beta.2-March 18, 2026

### Changed

- Changed the `editor.css` code about `user tag`
```css
.user-tag {
    display: inline-flex;
    align-items: center;
    gap: 4px;
    font-size: 12px;
    margin: 0;
    vertical-align: middle;
}
```
- Changed the `wikidot_parser.py` code about `user tag`
```python
    html = f'<span class="scp-component user-tag" data-type="user" data-source-uuid="{{{{uuid}}}}" data-source="{{{{source}}}}" contenteditable="false" style="display:inline-flex; align-items:center; gap:4px; padding:0 2px;"><span class="user-icon" style="background:#aaa; display:inline-block; width:12px; height:12px; border-radius:50%;"></span><span class="user-name" contenteditable="true" style="color:#b01; font-weight:bold;">{_html_module.escape(name)}</span></span>&#8203;'
```
- Changed the `editor.js` code about `paste`
```javascript
    // 拦截粘贴事件，只粘贴纯文本
    document.getElementById('editor-root').addEventListener('paste', function(e) {
        e.preventDefault();
        var text = '';
        if (e.clipboardData || e.originalEvent && e.originalEvent.clipboardData) {
            text = (e.originalEvent || e).clipboardData.getData('text/plain');
        } else if (window.clipboardData) {
            text = window.clipboardData.getData('Text');
        }
        if (document.queryCommandSupported('insertText')) {
            document.execCommand('insertText', false, text);
        } else {
            document.execCommand('paste', false, text);
        }
    });
```
- Changed the `componentsEvents.js` code about `user tag`
```javascript
if (comp && !comp.matches('.image-block-box') && !comp.matches('.wikidot-table') && !comp.matches('.aim-box') && !comp.matches('.user-tag')) {
    // ...
}
```

- Changed the `banner.py` code about this version
- Changed the `logger.py` code about this version

### Fixed

- Fixed the issue that `user tag` could not render correctly

### Version

- Updated the version to `v2.0.1-beta.2`
- LINCESE: AGPLv3
- Author: Zichen Wang (wasd243)

### Notes

- This version is the second beta release with the FTML engine
- The editor is stable
