# Code Review: `src/` (alpha.4)

## Scope

This review covers only the `src/` folder of the project. Issues are grouped by type and include source references for follow-up.

## Summary

The editor code is functional in broad structure, but several areas need hardening before the feature set is reliable: untrusted HTML is passed through multiple DOM/editor paths, IPC parsing lacks error recovery, some UI controls are placeholders, and editor state is held in a module-level singleton rather than a reactive lifecycle-aware store. There are also maintainability issues around duplicated editor watcher code and global event usage.

## Correctness and Runtime Behavior

### 1. Parser IPC has no failure handling (TODO)

`SyncToParser()` awaits `parse_wikidot` directly inside a global message listener without `try/catch`. If the Tauri command rejects or returns malformed data, the listener will fail silently at runtime and no user-facing recovery path exists.

- `src/ipc/Extensions/CodeView/SyncToParser.ts:20-35`
- `src/ipc/Extensions/CodeView/SyncToParser.ts:26`

**Recommendation:** Wrap the parser call and HTML conversion in `try/catch`, dispatch a typed error event or update UI state, and avoid leaving the editor in a stale state.

### 2. Full editor content is replaced on every parser sync (waiting to update until exporter implementation)

Parser output is applied with `setContent(html)`, replacing the entire TipTap document. This can discard the current selection, undo history context, unsaved in-editor edits, and plugin-managed state every time the code-view iframe posts a change.

- `src/components/editor/ToolBar/CodeView/RenderSyncHTMLToEditor.vue:6-9`
- `src/ipc/Extensions/CodeView/SyncToParser.ts:31-34`

**Recommendation:** Consider incremental transactions, conflict detection, selection preservation, or a debounced apply step with explicit user confirmation. (waiting to update until exporter implementation)

### 3. Context menu state is derived from a non-reactive singleton (TODO)

`ContextMenu.vue` uses computed values that read `getEditor()` directly. The editor reference is a module-level variable, not reactive, so the computed values only update when Vue re-renders for another reason. This can make context-menu type detection stale after selection or editor lifecycle changes.

- `src/stores/editor/instance.ts:3-10`
- `src/components/editor/ContextMenu.vue:15-33`

**Recommendation:** Store the editor instance in a reactive store/ref or pass selection-derived state into the context menu when it opens.

### 4. Right-click selection handling ignores valid position `0` (TODO)

`posAtCoords()` can return a position object whose `pos` is `0`. The current truthy check uses `if (position)`, so it is safe for the object itself, but it does not validate whether `position.pos` is a usable text selection position before calling `setTextSelection`. Edge positions can throw in ProseMirror depending on document structure.

- `src/components/editor/EditorCanvas.vue:14-22`

**Recommendation:** Validate the returned position against the current document and handle selection failures gracefully.

### 5. Footnote list movement uses positions from a pre-delete document (TODO)

`moveFootnoteListToBottom()` finds the footnote list in the current doc, deletes it, then inserts `footnoteList.node` at `tr.doc.content.size`. Because the transaction document changes after deletion, this path should be carefully tested for mapping correctness, especially when the footnote list is not the final node.

- `src/stores/btnToolBar/btnNonIncludeComponents/btnFootnote.ts:187-203`
- `src/stores/btnToolBar/btnNonIncludeComponents/btnFootnote.ts:238-240`

**Recommendation:** Add tests for inserting footnotes when the list is in the middle of a document and when multiple footnotes already exist.

## Security and Data Safety

### 1. Parser HTML is assigned through `innerHTML` and then inserted into the editor (NOT PLANNED)

The parser result is passed to `scanDOMandReplace()`, assigned into `template.innerHTML`, returned as HTML, and then inserted into TipTap with `setContent`. If parser output can contain unsafe tags or attributes, this creates an XSS/security risk in the Tauri webview.

- `src/ipc/Extensions/CodeView/SyncToParser.ts:26-34`
- `src/ipc/Extensions/CodeView/htmlAdapter/scanDOMandReplace.ts:21-43`
- `src/components/editor/ToolBar/CodeView/RenderSyncHTMLToEditor.vue:6-9`

**Recommendation:** Sanitize parser output with an allowlist before DOM insertion and before `setContent`. Consider stripping scripts, event-handler attributes, dangerous URLs, and unexpected inline styles.

### 2. Attribute preservation is broad and includes inline styles

The HTML preservation layer keeps attributes including `style`, `id`, `role`, `type`, and ARIA fields. Combined with preserved arbitrary tags, unsafe or layout-breaking content can persist inside the editor.

- `src/stores/editor/extensions/WJtags/htmlPreserveE.ts:139-154`
- `src/stores/editor/extensions/WJtags/htmlPreserveE.ts:180-183`
- `src/stores/editor/extensions/WJtags/htmlPreserveE.ts:267-279`

**Recommendation:** Narrow preserved attributes per tag and sanitize style values. Avoid preserving attributes that are not required for FTML round-tripping.

### 3. Code-view iframe is not sandboxed (TODO)

The code-view panel renders an iframe with a dynamic `src` and no `sandbox`, `allow`, or origin restrictions in markup. Message handling checks origin/source, but the iframe itself still has broad capabilities.

- `src/components/editor/ToolBar/CodeView.vue:58-63`
- `src/ipc/Extensions/CodeView/SyncToParser.ts:21-24`

**Recommendation:** Add a restrictive `sandbox` policy and only grant capabilities explicitly required by the code editor.

## Reliability and Error Handling

### 1. Production console logging leaks editor content (TODO)

`SyncToParser()` logs the full code-view payload every time content changes. This can expose user-authored page content in developer tools/log captures and may be expensive for large documents.

- `src/ipc/Extensions/CodeView/SyncToParser.ts:28-29`

**Recommendation:** Remove these logs or guard them behind a development-only debug flag that redacts large content.

### 2. Code-view open errors are only logged (TODO)

When `open_code_view_window` fails, the UI only writes to `console.error`; there is no visible error state, retry guidance, or disabled/loading state.

- `src/components/editor/ToolBar/CodeView.vue:21-27`

**Recommendation:** Add user-visible error feedback and loading state so repeated clicks cannot race multiple open attempts.

### 3. Deprecated copy command is used without result handling (NOT PLANNED)

The copy context-menu item uses `document.execCommand("copy")`, which is deprecated and returns a success boolean that is ignored.

- `src/components/editor/ContextMenu/DefaultContextMenu/Copy.vue:1-4`

**Recommendation:** Prefer the Clipboard API where available and report failure or fall back deliberately.

## Type Safety

### 1. TypeScript suppression hides the `onCreate` type mismatch (@ts-ignore)

`EditorCanvas.vue` suppresses a type issue on the `onCreate` callback. This bypasses one of the main checks protecting the editor lifecycle integration.

- `src/components/editor/EditorCanvas.vue:33-39`

**Recommendation:** Type the callback parameter correctly using TipTap's editor event types instead of suppressing the error.

### 2. Generic DOM event casting is too loose (TODO)

`renderSyncHTMLToEditor()` accepts a generic `Event` and casts it to `CustomEvent<string>`. If another event with the same name or malformed detail is dispatched, non-string content can be passed to `setContent`.

- `src/components/editor/ToolBar/CodeView/RenderSyncHTMLToEditor.vue:6-9`

**Recommendation:** Validate `event instanceof CustomEvent` and `typeof event.detail === "string"` before applying content.

### 3. Preserved attributes use broad records and casts (Temparatory Ignore, waiting to fix)

The HTML preservation code converts arbitrary DOM attributes into generic records and casts node attributes back to records. This is flexible but hides schema mistakes and malformed attributes.

- `src/stores/editor/extensions/WJtags/htmlPreserveE.ts:180-183`
- `src/stores/editor/extensions/WJtags/htmlPreserveE.ts:288-303`

**Recommendation:** Define a stricter attribute type and centralize validation/normalization for preserved HTML attributes.

## Maintainability and Architecture

### 1. Editor instance is managed as a global mutable singleton (NOT PLANNED)

The editor instance is stored in a module-level variable and imported throughout toolbar/context-menu logic. This makes lifecycle, testing, and multi-editor support harder and creates non-reactive dependencies.

- `src/stores/editor/instance.ts:3-10`
- `src/components/editor/EditorCanvas.vue:37-39`
- `src/stores/btnToolBar/btnActions/btnUndo.ts:1-5`

**Recommendation:** Move editor state to a Vue/Pinia store or provide/inject pattern, exposing typed commands rather than allowing every module to pull the raw editor.

### 2. Repeated polling logic exists for editor readiness (TODO)

Both title and font-size dropdowns poll every 100ms until the editor exists, then register similar `selectionUpdate` and `transaction` listeners. This duplicates lifecycle code and can be fragile if more controls follow the same pattern.

- `src/components/editor/ToolBar/Formats/Size/ListTitle.vue:14-45`
- `src/components/editor/ToolBar/Formats/Size/ListTitle.vue:58-79`
- `src/components/editor/ToolBar/Formats/Size/ListSize.vue:13-45`
- `src/components/editor/ToolBar/Formats/Size/ListSize.vue:58-79`

**Recommendation:** Introduce a shared composable for editor readiness and editor event subscriptions.

### 3. Global window events are used as an internal event bus (NOT PLANNED)

Parser results are dispatched through `window.dispatchEvent()` and consumed by a hidden Vue component. This is difficult to trace, weakly typed, and not scoped to a component or editor instance.

- `src/ipc/Extensions/CodeView/SyncToParser.ts:31-34`
- `src/components/editor/ToolBar/CodeView/RenderSyncHTMLToEditor.vue:11-17`

**Recommendation:** Replace global events with a typed composable/store or direct callback registration tied to the code-view component lifecycle.

### 4. `main.ts` and `App.vue` both import global CSS (TODO)

Global styles are imported in `main.ts`, while `App.vue` imports `global.css` again. This creates duplicate side effects and makes style ownership less clear.

- `src/main.ts:6-18`
- `src/App.vue:1-4`

**Recommendation:** Keep global stylesheet imports in one entry point, preferably `main.ts`.

## Feature Completeness and UX

### 1. Several toolbar cards are placeholders with no behavior (NOT PLANNED)

Multiple non-include toolbar components render buttons but do not perform any action. They also omit `type="button"`, which can cause accidental form submission if these components are ever rendered inside a form.

- `src/components/editor/ToolBar/NonIncludeComponents/SiteURLs.vue:1-4`
- `src/components/editor/ToolBar/NonIncludeComponents/divBlock.vue:1-4`
- `src/components/editor/ToolBar/NonIncludeComponents/Image.vue:1-4`
- `src/components/editor/ToolBar/NonIncludeComponents/ModuleRate.vue:1-4`
- `src/components/editor/ToolBar/NonIncludeComponents/URLs.vue:1-4`
- `src/components/editor/ToolBar/NonIncludeComponents/Users.vue:1-4`
- `src/components/editor/ToolBar/NonIncludeComponents/cssModule.vue:1-4`
- `src/components/editor/ToolBar/NonIncludeComponents/Note.vue:1-4`

**Recommendation:** Disable unfinished buttons with explanatory labels/tooltips, or hide them until implemented.

### 2. Code block feature exposes a TODO alert

The Code card calls a `TODO_code` function and shows a blocking `alert()` instead of integrating with editor commands or being disabled.

- `src/components/editor/ToolBar/NonIncludeComponents/Code.vue:1-9`

**Recommendation:** Replace the alert with a real command, a disabled state, or a non-blocking notification.

### 3. Toolbar controls do not expose disabled/active states consistently (TODO)

Toolbar actions call editor commands directly but generally do not disable themselves when the editor is unavailable or when a command cannot run.

- `src/components/editor/ToolBar/Actions/Undo.vue:1-7`
- `src/stores/btnToolBar/btnActions/btnUndo.ts:1-5`

**Recommendation:** Use `editor.can()` and editor availability state to render disabled/active UI states consistently.

## Accessibility

### 1. Icon-only buttons lack accessible labels (Not Planned)

The code-view button displays only `</>` and the close button displays only `×`. Neither has an `aria-label`, so screen-reader users may not get meaningful names.

- `src/components/editor/ToolBar/CodeView.vue:35-42`
- `src/components/editor/ToolBar/CodeView.vue:51-57`

**Recommendation:** Add `aria-label` or visually hidden text for icon-only controls.

### 2. Dropdown menus lack full combobox/menu semantics (Not Planned)

The title and font-size dropdowns expose `aria-expanded`, but the menu/list items do not include roles, relationship attributes, keyboard navigation, or outside-click behavior.

- `src/components/editor/ToolBar/Formats/Size/ListTitle.vue:82-105`
- `src/components/editor/ToolBar/Formats/Size/ListSize.vue:82-105`

**Recommendation:** Implement keyboard navigation and appropriate `button`/`menu` or combobox semantics.

## Verification Notes

- `npm run build` was attempted from the project root.
- The build did not reach source diagnostics because `vue-tsc` failed under the current Node/TypeScript tooling with: `Search string not found: "/supportedTSExtensions = .*(?=;)/"`.
- This verification failure is outside the requested `src/` review scope, but it currently prevents using the build as a validation signal for `src/` changes.

## Priority Recommendations

1. Sanitize and validate parser HTML before it reaches the DOM/editor.
2. Add error handling and user feedback around code-view parsing/opening.
3. Replace the global editor singleton and global window event bus with reactive, typed application state.
4. Remove TypeScript suppression and tighten event/attribute types.
5. Disable, hide, or implement placeholder toolbar controls before release.
