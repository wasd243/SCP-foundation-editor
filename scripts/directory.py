from __future__ import annotations

from pathlib import Path
import fnmatch
import os
import sys
from dataclasses import dataclass


@dataclass(frozen=True)
class IgnoreRule:
    pattern: str
    negated: bool
    anchored: bool
    dir_only: bool


class GitIgnoreMatcher:
    def __init__(self, root: Path, gitignore_path: Path) -> None:
        self.root = root
        self.rules: list[IgnoreRule] = []
        self._load_rules(gitignore_path)

    def _load_rules(self, gitignore_path: Path) -> None:
        if not gitignore_path.exists():
            return

        for raw_line in gitignore_path.read_text(encoding="utf-8").splitlines():
            line = raw_line.strip()
            if not line or line.startswith("#"):
                continue

            negated = line.startswith("!")
            if negated:
                line = line[1:].strip()
                if not line:
                    continue

            anchored = line.startswith("/")
            if anchored:
                line = line[1:]

            dir_only = line.endswith("/")
            if dir_only:
                line = line[:-1]

            line = line.strip()
            if not line:
                continue

            self.rules.append(
                IgnoreRule(
                    pattern=line.replace("\\", "/"),
                    negated=negated,
                    anchored=anchored,
                    dir_only=dir_only,
                )
            )

    def is_ignored(self, path: Path, is_dir: bool) -> bool:
        try:
            rel_path = path.relative_to(self.root).as_posix()
        except ValueError:
            return False

        ignored = False
        for rule in self.rules:
            if self._matches_rule(rel_path, rule, is_dir):
                ignored = not rule.negated
        return ignored

    @staticmethod
    def _matches_rule(rel_path: str, rule: IgnoreRule, is_dir: bool) -> bool:
        if rule.dir_only and not is_dir:
            return False

        if "/" in rule.pattern:
            if rule.anchored:
                return fnmatch.fnmatch(rel_path, rule.pattern)
            return fnmatch.fnmatch(rel_path, rule.pattern) or fnmatch.fnmatch(
                rel_path, f"*/{rule.pattern}"
            )

        parts = rel_path.split("/")
        return any(fnmatch.fnmatch(part, rule.pattern) for part in parts)


def print_tree(root: Path, matcher: GitIgnoreMatcher, prefix: str = "") -> None:
    try:
        entries = sorted(
            (entry for entry in os.scandir(root)),
            key=lambda e: (not e.is_dir(follow_symlinks=False), e.name.lower()),
        )
    except PermissionError:
        return

    visible_entries = []
    for entry in entries:
        entry_path = Path(entry.path)
        is_dir = entry.is_dir(follow_symlinks=False)
        if matcher.is_ignored(entry_path, is_dir):
            continue
        visible_entries.append((entry, is_dir))

    total = len(visible_entries)
    for index, (entry, is_dir) in enumerate(visible_entries):
        is_last = index == total - 1
        branch = "\\-- " if is_last else "|-- "
        print(f"{prefix}{branch}{entry.name}")
        if is_dir:
            child_prefix = f"{prefix}{'    ' if is_last else '|   '}"
            print_tree(Path(entry.path), matcher, child_prefix)


def resolve_gitignore(root: Path) -> Path | None:
    local_gitignore = root / ".gitignore"
    if local_gitignore.exists():
        return local_gitignore

    repo_gitignore = Path(__file__).resolve().parents[1] / ".gitignore"
    if repo_gitignore.exists():
        return repo_gitignore

    return None


def main() -> None:
    raw_path = sys.argv[1] if len(sys.argv) > 1 else input("请输入绝对路径: ").strip()
    root = Path(raw_path).expanduser().resolve()

    if not root.is_absolute():
        print("错误：请输入绝对路径。")
        return
    if not root.exists():
        print(f"错误：路径不存在 -> {root}")
        return
    if not root.is_dir():
        print(f"错误：该路径不是文件夹 -> {root}")
        return

    gitignore_path = resolve_gitignore(root)
    matcher = GitIgnoreMatcher(root=root, gitignore_path=gitignore_path or Path(""))

    print(root)
    print_tree(root, matcher)


if __name__ == "__main__":
    main()
