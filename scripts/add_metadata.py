from pathlib import Path
import re

ROOT = Path("resourcepack/includes")


def include_name(path: Path) -> str:
    rel = path.relative_to(ROOT).with_suffix("")
    return ":".join(rel.parts)


def inject_metadata(metadata_text: str, metadata_name: str) -> str:
    pattern = re.compile(
        r"\[\[div\s+([^\]]+?)\]\]",
        re.I | re.S
    )

    def repl(match):
        attrs = match.group(1)

        if "data-editor-export" in attrs:
            return match.group(0)

        return (
            f'[[div {attrs} '
            f'data-editor-export="include" '
            f'data-editor-include="{metadata_name}"]]'
        )

    return pattern.sub(repl, metadata_text, count=1)


for file in ROOT.rglob("*.ftml"):
    name = include_name(file)

    text = file.read_text(encoding="utf-8")

    new_text = inject_metadata(text, name)

    if new_text != text:
        file.write_text(new_text, encoding="utf-8")
        print(f"updated {file} -> {name}")