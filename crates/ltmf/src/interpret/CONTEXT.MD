## In `interpreter/`

This folder contains files related to the interpreter.

The interpreter is not finished yet. The resourcepack includer is implemented, but still needs more coverage and end-to-end testing.

Currently, the interpreter can handle most marks in ProseMirror JSON, as well as some URLs and ProseMirror attrs.

TODO:
- [x] Implement user div exporter
- [x] Implement user css exporter
- [x] Implement user span exporter
- [ ] Test the includer
- [x] Test the interpreter: attempt 1: test normal text and components
- [x] Add `[[footnoteblock]]` exporter (Fixed, only a patch is needed)
- [x] Add `Content Paragraph` exporter


### About float Image

The float image interpreter is implemented, but the parser sometimes loses metadata like `floatleft` or `floatright`.

However, this issue doesn't affect `component:image-block`, which is the most commonly used case, so the interpreter works fine in practice.

**Not planned to fix:** Adding more patches would introduce an additional maintenance burden. When the upstream parser eventually fixes this issue, our patches might cause double parsing or duplicate metadata, requiring another refactor.
