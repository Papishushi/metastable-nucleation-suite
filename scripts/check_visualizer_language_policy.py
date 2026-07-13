"""Enforce the Rust/WASM-only application boundary accepted in ADR 0002."""

from __future__ import annotations

import subprocess
from collections.abc import Iterable
from pathlib import Path


BANNED_SUFFIXES = {".js", ".mjs", ".cjs", ".ts", ".tsx"}
GENERATED_BINDING_ALLOWLIST = {
    "visualizer/generated/metastable_visualizer.js",
    "visualizer/generated/metastable_visualizer.d.ts",
}


def find_violations(paths: Iterable[str]) -> list[str]:
    """Return forbidden tracked application-language paths."""
    return sorted(
        path
        for path in paths
        if Path(path).suffix.lower() in BANNED_SUFFIXES
        and path not in GENERATED_BINDING_ALLOWLIST
    )


def tracked_paths(root: Path) -> list[str]:
    """Read repository paths from Git so build output never affects the policy."""
    result = subprocess.run(
        ["git", "ls-files"],
        cwd=root,
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout.splitlines()


def main() -> int:
    """Fail when handwritten JavaScript or TypeScript enters the repository."""
    root = Path(__file__).resolve().parents[1]
    violations = find_violations(tracked_paths(root))
    if violations:
        print("Rust/WASM visualizer policy violation:")
        for path in violations:
            print(f"- {path}")
        return 1

    print("Rust/WASM visualizer policy satisfied")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
