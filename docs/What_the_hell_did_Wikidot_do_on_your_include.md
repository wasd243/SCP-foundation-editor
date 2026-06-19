# On the Irreversibility of `[[include]]`: Why Wikidot Includes Cannot Be Round-Tripped Through a WYSIWYG Editor

> [!IMPORTANT]
> Full data-pack WYSIWYG rendering of `[[include]]` is **not** supported, and
> never will be. This document explains why the limitation is *structural*, not
> a matter of engineering effort.
>
> This file only represents my personal opinion on the `[[include]]` issue.
> It is not a formal proposal.
> 
> The parser still expands `[[include]]` correctly. The editor does **not**
> attempt to reconstruct an editable `[[include]]` from expanded output.

## Abstract

A WYSIWYG editor requires a **bidirectional** mapping between source and
rendered output: every edit to the rendered view must map back to a unique edit
in the source. We argue that `[[include]]` cannot satisfy this requirement.
The key observation is that `[[include]]` is **not** a textual inclusion
directive like C's `#include`; it is a **parameterized macro expansion**,
closer to Rust's `macro_rules!`. Macro expansion is lossy, conditional, and —
when nested — irreversible in the information-theoretic sense. We classify the
common "import-like" constructs by reversibility and show where `[[include]]`
falls, and why WYSIWYG compounds the problem further.

## 1. A Spectrum of "Inclusion"

Not all inclusion mechanisms are equal. They differ in how much information
survives expansion.

### 1.1 Textual inclusion — *content is fixed*

```c
#include <stdio.h>
```

```css
@import url("base.css");
```

These are **pure textual substitution**. The included content is **fixed**: for
a given environment, `<stdio.h>` always expands to the same text. It takes no
arguments and has no conditional behaviour.

Because the content is fixed, a *reverse* mapping is **theoretically possible**:
obtain the content of `stdio.h`, compare it against a region of the expanded
output, and if it matches exactly, replace that region with `#include <stdio.h>`.
This is essentially library-signature detection (cf. FLIRT signatures in IDA,
or content fingerprinting). It is lossy in practice — provenance and comments
are gone — but the *matching* operation is well-defined because the target is
deterministic.

### 1.2 Symbol import — *content is determinate*

```rust
use std::collections::HashMap;
```

```python
import os
```

Rust's `use` and Python's `import` are not brute-force text substitution, but
the entity they bring into scope is still **determinate**: the same path always
refers to the same definition. No arguments, no per-call variation.

### 1.3 Parameterized macro — *content is generated*

```
[[include :scp-wiki-cn:theme:peroxide
|title="SCP Foundation"
|img=https://example.com]]
```

This is the category `[[include]]` actually belongs to, and it is fundamentally
different from §1.1 and §1.2. It is **not** textual substitution. It is a
**parameterized macro expansion**, behaviourally identical to:

```rust
macro_rules! theme_peroxide {
    ($title:expr, $img:expr) => { /* template with $title, $img spliced in */ };
}
theme_peroxide!("SCP Foundation", "https://example.com");
```

## 2. What Wikidot/ftml Actually Does

Given a parameterized include, the engine performs roughly:

1. **Fetch** the template (`theme:peroxide`).
2. **Scan** the template for variable slots (`{$title}`, `{$img}`, ...).
3. For each slot:
    - if a matching argument was supplied, **interpolate** it;
    - if not, **fall back** (often to empty, or to a default baked into the
      template).
4. Emit the resulting text.

Two properties of step 3 are fatal for reversibility:

- **Interpolation is destructive.** After expansion, `{$title}` is gone; only
  the value `"SCP Foundation"` remains, now indistinguishable from text the
  template itself contained.
- **Fall-back is silent.** If the caller passes `|img=...` but the template has
  no `{$img}` slot, the argument simply **vanishes** with no trace. From the
  output alone, you cannot even determine *which arguments were passed* — only
  which slots happened to be filled.

## 3. Why This Is Strictly Harder Than Reversing `#include`

Reversing `#include` is hard because provenance is lost (§1.1), but the target
is **deterministic**, so signature matching can work.

Reversing `[[include]]` is harder, and then impossible, for three compounding
reasons:

1. **No unique fingerprint.** The same include with different arguments expands
   to different output. There is no fixed string to match against, because the
   output is `template ⊗ arguments`, and the arguments are unknown.
   - _I tried to use `data-editor-export` and `data-editor-include` to solve that but not works by mutiple reasons like different of `[[include]]` variables/requirements etc._

2. **Arguments are unrecoverable.** Because non-matching arguments are dropped
   silently and matching ones are merged into surrounding template text, the
   expanded output is insufficient to reconstruct the argument list. The map
   from `(template, args)` to `output` is **not injective**: distinct argument
   sets can yield identical output.

3. **Nesting is multiplicative.** Real themes nest several layers of
   `[[include]]`, interleaved with `@import` and further variable
   interpolation. Each layer is independently lossy; composed, the loss is the
   product of the layers. Reversing a single parameterized macro is already
   impossible; reversing a recursive stack of them mixed with `@import` is
   information-theoretically hopeless.

This mirrors a known fact in the Rust ecosystem: `cargo expand` exists, but
there is no "`cargo unexpand`". Macro expansion is a one-way operation precisely
because it is parameterized and conditional, not a simple substitution.

## 4. WYSIWYG Raises the Bar Beyond "Reverse"

Even granting, hypothetically, that some `[[include]]` could be matched back to
its call, WYSIWYG demands more than a one-shot reverse. Decompilers like Ghidra
reconstruct *offline, static, semantically-equivalent* code; nobody edits the
decompiled output and expects it to synchronize back into a `#include` line.

WYSIWYG requires the user to **edit the expanded content live** and have those
edits **propagate back to source**. But after expansion, three sources of
content are merged and indistinguishable in the DOM:

- text authored by the user directly,
- text from the include template,
- values interpolated from arguments.

When the user edits one character of the rendered view, the editor cannot
decide whether that edit belongs to the **template**, to an **argument**, or to
the **user's own prose**. Provenance was destroyed at expansion time. There is
no correct place to write the change back.

## 5. Classification Summary

| Construct                        | Nature                        | Content     | Reversible?                          |
|----------------------------------|-------------------------------|-------------|--------------------------------------|
| `#include`, `@import`            | textual substitution          | fixed       | in principle (signature match)       |
| `use`, `import`                  | symbol import                 | determinate | n/a (no inline body)                 |
| `[[include]]` (no vars)          | macro, no args                | fixed-ish   | hard (provenance lost)               |
| `[[include]]` (with vars)        | parameterized macro           | generated   | **no** (not injective)               |
| nested `[[include]]` + `@import` | recursive parameterized macro | generated   | **information-theoretically no**     |
| any of the above **+ WYSIWYG**   | live bidirectional editing    | —           | **no** (provenance + real-time sync) |

## 6. Conclusion

`[[include]]` is not `#include`. It is `macro_rules!` — parameterized,
conditional, and routinely nested. Macro expansion is a one-way door:
you can walk through it, but you cannot walk back and recover the door,
because the output is a non-injective function of `(template, arguments)`.

WYSIWYG would require not merely walking back through that door, but doing so
*continuously and editably* — which additionally demands provenance that
expansion has already destroyed.

The parser retains full `[[include]]` support. The editor does not pretend it
can round-trip a parameterized, nested macro. This is not a limitation we
intend to "fix"; it is a property of the problem.

---

_2026-06-19_
**_wasd243_**