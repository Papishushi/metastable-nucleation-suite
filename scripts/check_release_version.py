#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from xml.etree import ElementTree

try:
    import tomllib
except ModuleNotFoundError:  # Python 3.10
    import tomli as tomllib

ROOT = Path(__file__).resolve().parents[1]
SEMVER = re.compile(
    r"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)"
    r"(?:-([0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*))?$"
)


def canonical_version() -> str:
    version = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
    if not SEMVER.fullmatch(version):
        raise ValueError(f"VERSION is not supported SemVer: {version!r}")
    return version


def python_distribution_version(version: str) -> str:
    from packaging.version import InvalidVersion, Version

    try:
        parsed = Version(version)
    except InvalidVersion as exc:
        raise ValueError(f"version cannot be represented as PEP 440: {version!r}") from exc

    if "-" in version and not parsed.is_prerelease:
        raise ValueError(
            "SemVer prerelease does not map to a PEP 440 prerelease: "
            f"{version!r} -> {parsed.public!r}"
        )
    return parsed.public


def citation_version() -> str:
    text = (ROOT / "CITATION.cff").read_text(encoding="utf-8")
    match = re.search(r"(?m)^version:\s*([^\s]+)\s*$", text)
    if match is None:
        raise ValueError("CITATION.cff has no version field")
    return match.group(1)


def dotnet_version() -> str:
    document = ElementTree.parse(ROOT / "dotnet" / "Directory.Build.props")
    version = document.findtext("./PropertyGroup/Version")
    if version is None or not version.strip():
        raise ValueError("dotnet/Directory.Build.props has no Version property")
    return version.strip()


def validate_metadata(tag: str | None = None) -> str:
    version = canonical_version()
    python_distribution_version(version)
    pyproject = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    project = pyproject["project"]
    if "version" in project:
        raise ValueError("pyproject.toml must derive version dynamically from VERSION")
    if "version" not in project.get("dynamic", []):
        raise ValueError("pyproject.toml must declare dynamic version metadata")
    if citation_version() != version:
        raise ValueError("CITATION.cff version does not match VERSION")
    if dotnet_version() != version:
        raise ValueError("dotnet/Directory.Build.props version does not match VERSION")
    if tag is not None:
        normalized = tag.removeprefix("refs/tags/")
        if normalized != f"v{version}":
            raise ValueError(
                f"release tag {normalized!r} does not match canonical version v{version}"
            )
    return version


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--tag")
    parser.add_argument("--github-output", type=Path)
    args = parser.parse_args()
    try:
        version = validate_metadata(args.tag)
    except (ElementTree.ParseError, KeyError, OSError, ValueError) as exc:
        print(f"release metadata validation failed: {exc}", file=sys.stderr)
        return 1
    print(version)
    if args.github_output is not None:
        with args.github_output.open("a", encoding="utf-8") as output:
            output.write(f"version={version}\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
