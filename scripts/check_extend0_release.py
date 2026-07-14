#!/usr/bin/env python3
"""Validate the Extend0 dependency in release diagnostics and SBOMs."""

from __future__ import annotations

import argparse
import json
import subprocess
import xml.etree.ElementTree as ET
from pathlib import Path


DEFAULT_PROJECT = Path("dotnet/Metastable.Platform.Cli/Metastable.Platform.Cli.csproj")


def expected_extend0_version(project: Path) -> str:
    document = ET.parse(project)
    references = [
        element
        for element in document.iter("PackageReference")
        if element.attrib.get("Include", "").casefold() == "extend0"
    ]
    if len(references) != 1:
        raise SystemExit(
            f"expected one Extend0 PackageReference in {project}, found {len(references)}"
        )

    raw_version = references[0].attrib.get("Version")
    if raw_version is None:
        version_element = references[0].find("Version")
        raw_version = version_element.text if version_element is not None else None
    if not raw_version or not (raw_version.startswith("[") and raw_version.endswith("]")):
        raise SystemExit(
            f"Extend0 must use an exact NuGet version range, found {raw_version!r}"
        )
    return raw_version[1:-1]


def check_doctor(executable: Path, project: Path) -> None:
    expected_version = expected_extend0_version(project)
    result = subprocess.run(
        [str(executable), "extend0", "doctor"],
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise SystemExit(
            f"extend0 doctor exited {result.returncode}: {result.stderr.strip()}"
        )

    try:
        status = json.loads(result.stdout)
    except json.JSONDecodeError as error:
        raise SystemExit(f"extend0 doctor returned invalid JSON: {error}") from error
    if not isinstance(status, dict):
        raise SystemExit("extend0 doctor must return a JSON object")

    package_version = status.get("package_version")
    if not isinstance(package_version, str):
        raise SystemExit("extend0 doctor did not report package_version")
    resolved_version = package_version.split("+", 1)[0]
    if resolved_version != expected_version:
        raise SystemExit(
            f"extend0 doctor reported {package_version}, expected {expected_version}"
        )
    if status.get("metadb_ready") is not True:
        raise SystemExit("extend0 doctor did not report metadb_ready=true")

    print(f"Extend0 {package_version}: MetaDB ready")


def check_sbom(sbom: Path, project: Path) -> None:
    expected_version = expected_extend0_version(project)
    with sbom.open(encoding="utf-8") as stream:
        document = json.load(stream)

    packages = document.get("packages")
    if not isinstance(packages, list):
        raise SystemExit(f"{sbom} does not contain an SPDX packages array")

    extend0_packages = [
        package
        for package in packages
        if str(package.get("name", "")).casefold() == "extend0"
    ]
    if not extend0_packages:
        raise SystemExit(f"{sbom} does not contain the resolved Extend0 package")
    versions = {str(package.get("versionInfo", "")) for package in extend0_packages}
    if versions != {expected_version}:
        raise SystemExit(
            f"{sbom} contains Extend0 versions {sorted(versions)}, "
            f"expected only {expected_version}"
        )

    print(f"SBOM contains Extend0 {expected_version}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project", type=Path, default=DEFAULT_PROJECT)
    subparsers = parser.add_subparsers(dest="command", required=True)

    doctor = subparsers.add_parser("doctor")
    doctor.add_argument("executable", type=Path)

    sbom = subparsers.add_parser("sbom")
    sbom.add_argument("document", type=Path)
    return parser


def main() -> int:
    arguments = build_parser().parse_args()
    if arguments.command == "doctor":
        check_doctor(arguments.executable, arguments.project)
    else:
        check_sbom(arguments.document, arguments.project)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
