from pathlib import Path
import re
import subprocess
import sys

import pytest

from metastable_suite import __version__
from scripts.check_release_version import (
    canonical_version,
    python_distribution_version,
    validate_metadata,
)

ROOT = Path(__file__).resolve().parents[1]


def test_python_version_matches_canonical_version():
    assert __version__ == canonical_version()


def test_release_metadata_is_consistent():
    version = validate_metadata()
    assert version == __version__
    assert validate_metadata(f"v{version}") == version


def test_release_metadata_rejects_mismatched_tag():
    result = subprocess.run(
        [sys.executable, "scripts/check_release_version.py", "--tag", "v9.9.9"],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 1
    assert "does not match canonical version" in result.stderr


def test_canonical_version_is_semver_without_build_metadata():
    assert re.fullmatch(r"\d+\.\d+\.\d+(?:-[0-9A-Za-z.-]+)?", __version__)


def test_python_distribution_version_normalizes_semver_prerelease():
    assert python_distribution_version("0.3.0-rc.1") == "0.3.0rc1"
    assert python_distribution_version("0.3.0-beta.2") == "0.3.0b2"
    assert python_distribution_version("0.3.0-alpha.4") == "0.3.0a4"


def test_python_distribution_version_rejects_numeric_semver_prerelease():
    with pytest.raises(ValueError, match="does not map to a PEP 440 prerelease"):
        python_distribution_version("0.3.0-1")


def test_release_workflow_marks_unstable_versions_as_github_prereleases():
    workflow = (ROOT / ".github" / "workflows" / "release.yml").read_text(
        encoding="utf-8"
    )

    assert "needs.metadata.outputs.stable }}' != \"true\"" in workflow
    assert "release_flags+=(--prerelease)" in workflow
    assert '"${release_flags[@]}"' in workflow
