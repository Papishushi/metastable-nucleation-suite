from datetime import datetime

from metastable_suite.report import _git_commit, build_report


def test_reference_report_contains_reproducibility_provenance():
    report = build_report(10_000, 7)
    provenance = report["provenance"]
    assert provenance["python_version"]
    assert provenance["numpy_version"]
    assert provenance["rng_algorithm"] == "PCG64"
    assert provenance["configuration"]["seed"] == 7
    assert provenance["configuration"]["catalog_version"] == 1
    assert provenance["configuration"]["specification_version"] == 1

    started = datetime.fromisoformat(provenance["execution_started_at_utc"])
    ended = datetime.fromisoformat(provenance["execution_ended_at_utc"])
    generated = datetime.fromisoformat(provenance["generated_at_utc"])
    assert started <= ended <= generated


def test_git_commit_is_independent_of_process_working_directory(tmp_path, monkeypatch):
    expected = _git_commit()
    monkeypatch.chdir(tmp_path)
    assert _git_commit() == expected
