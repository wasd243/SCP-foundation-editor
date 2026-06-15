## In `interpreter/`

This folder contains files related to the interpreter.

The interpreter is not finished yet. The resourcepack includer is implemented, but still needs more coverage and end-to-end testing.

Currently, the interpreter can handle most marks in ProseMirror JSON, as well as some URLs and ProseMirror attrs.

TODO:

- [x] Implement user div exporter
- [x] Implement user css exporter
- [ ] Implement user span exporter
- [ ] Test the includer
- [x] Test the interpreter: attempt 1: test normal text and components
- [x] Add `[[footnoteblock]]` exporter (Fixed, only a patch is needed)
- [x] Add `Content Paragraph` exporter
