# AGENTS.md

## Project Overview

This project is a ProseMirror-based WYSIWYG editor for SCP Wiki / Wikidot content.

The editor is NOT a generic rich text editor.

The goal is:

```text
Wikitext
    ↕
ProseMirror JSON
    ↕
WYSIWYG Editor
```

The project contains a custom exporter, interpreter, include resolver, resource pack loader, and multiple Wikidot-specific components.

Preserving export correctness is more important than adding new features.

---

# RULES MUST FOLLOW

## 1. Do NOT redesign the architecture

Do not introduce new architectures, frameworks, abstractions, or pipelines unless explicitly requested.

Do not replace existing exporter/interpreter/include systems.

Do not rewrite working code.

---

## 2. Export correctness is the highest priority

The editor exists to generate valid Wikidot Wikitext.

When making changes:

- preserve exporter behavior
- preserve include behavior
- preserve resource pack compatibility
- preserve existing Wikitext output

Never sacrifice export correctness for code elegance.

---

## 3. Do NOT introduce unnecessary dependencies

Before adding a dependency:

- check whether the functionality already exists
- prefer standard library solutions
- prefer existing project dependencies

Avoid dependency bloat.

---

## 4. Respect existing module boundaries

Current include architecture:

```text
variable_loader.rs
    ↓
SQLite mapping table
    ↓
search.rs
    ↓
generator.rs
```

Responsibilities:

- variable_loader.rs loads mappings
- search.rs performs lookups
- generator.rs generates Wikitext

Do not merge responsibilities.

Do not move SQL logic into generator.rs.

Do not move generation logic into search.rs.

---

## 5. ProseMirror data is the source of truth

Use:

- node attrs
- node content
- data-editor metadata

when available.

Do not reconstruct information from rendered HTML when structured data already exists.

Avoid HTML parsing whenever possible.

---

## 6. Keep solutions simple

Prefer:

- functions
- modules
- enums
- traits

Avoid unnecessary abstractions.

Avoid Java-style factory/provider/manager patterns.

Simple code is preferred over clever code.

---

## 7. Do NOT remove debugging information without permission

Keep existing:

- logs
- assertions
- error messages

unless explicitly requested.

---

## 8. When uncertain

Stop and explain the uncertainty.

Do not guess.

Do not silently change behavior.

Do not invent exporter logic.

Ask for clarification instead.

---

## 9. When use SQL

Do not hardcode SQL inline.

Directly use `**.sql` files.

Do not create test SQL tables, directly use `crates/ltmf/src/interpreter/include/variable_name_config_table.sql`.

---

# Development Philosophy

This project prioritizes:

1. Correctness
2. Maintainability
3. Export fidelity
4. Simplicity

over:

1. Clever abstractions
2. Framework purity
3. Architectural experiments
4. Premature optimization
