# `[[include]]` — Not Fully WYSIWYG-able

> [!WARNING]
> Full data-pack WYSIWYG rendering of `[[include]]` is **not** supported,
> and never will be. This is a structural limitation, not a missing feature.
>
> The parser still expands `[[include]]` correctly. The editor simply does
> **not** attempt to render included content as editable WYSIWYG.

## TL;DR

`[[include]]` is a preprocessor directive, exactly like C's `#include`.
Preprocessing is **lossy and one-way**. You cannot reliably reconstruct the
original directive from the expanded result — so it cannot be round-tripped
through a WYSIWYG editor.

## The `#include` Analogy

Consider this C program:

```c
#include <stdio.h>

int main(void) {
    printf("hello world");
}
```

After the C preprocessor runs, `#include <stdio.h>` is **gone**. In its place
sit hundreds of lines of declarations pulled in from `stdio.h`. The compiler
never sees `#include` — it only sees the expanded result.

Now try to go backwards: given the expanded translation unit, reconstruct the
exact line `#include <stdio.h>`.

You can't. The information was destroyed at expansion time:

- Which lines came from the header, and which the user wrote? Unknown.
- The same expanded output could come from many different include forms.
- Macros are already substituted; the original spelling is lost.

## Why This Applies to `[[include]]`

`[[include]]` behaves identically. `ftml` expands it into HTML, and at that
point the original directive is gone. Reconstructing it from the rendered
output faces the same wall:

- **Provenance is lost.** After expansion, included content and user-authored
  content are indistinguishable in the DOM.
- **Variable interpolation is destructive.** `{$variable}` placeholders are
  filled at expansion time. The resolved value might be plain text, an image,
  or something stranger — and the original `{$...}` structure is gone.
- **No uniform rendering rule exists.** Every include target carries its own
  CSS expectations. Some support line breaks, some don't. There is no single
  way to render "an arbitrary include" as editable content.

WYSIWYG requires a **bidirectional, editable, real-time** representation.
`[[include]]` is **dynamic, external, and placeholder-driven**. These two sets
of requirements are fundamentally incompatible.

`ftml` is excellent as a **one-way** parser (wikitext → HTML, single pass).
That is exactly the operation that works. The reverse — reconstructing an
editable `[[include]]` from expanded output — is the operation that doesn't,
for the same reason `#include` is not recompilable from its expansion.

## Verdict

Expansion is a one-way door. You can walk through it, but you can't walk back
and recover what the door looked like. `[[include]]` and `#include` are the
same door.

The parser keeps full `[[include]]` support. The editor does not pretend it
can round-trip it.

---

_2026-06-19_
**_wasd243_**