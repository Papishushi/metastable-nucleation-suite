from metastable_suite.report import build_report


def test_reference_report_contains_reproducibility_provenance():
    report = build_report(10_000, 7)
    provenance = report["provenance"]
    assert provenance["python_version"]
    assert provenance["numpy_version"]
    assert provenance["rng_algorithm"] == "PCG64"
    assert provenance["configuration"]["seed"] == 7
    assert provenance["configuration"]["catalog_version"] == 1
    assert provenance["configuration"]["specification_version"] == 1
