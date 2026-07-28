from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def replace_once(path: str, old: str, new: str) -> None:
    target = ROOT / path
    content = target.read_text(encoding="utf-8")
    if old in content:
        if content.count(old) != 1:
            raise RuntimeError(f"expected one match in {path}, found {content.count(old)}")
        target.write_text(content.replace(old, new), encoding="utf-8")
        return
    if new not in content:
        raise RuntimeError(f"expected remediation pattern not found in {path}")


def main() -> None:
    replacements = [
        (
            "scripts/check_control_plane_contract.py",
            'raise ValueError("control-plane OpenAPI has no paths object")',
            'raise TypeError("control-plane OpenAPI has no paths object")',
        ),
        (
            "scripts/check_control_plane_contract.py",
            'raise ValueError(f"invalid OpenAPI operation: {method.upper()} {path}")',
            'raise TypeError(f"invalid OpenAPI operation: {method.upper()} {path}")',
        ),
        (
            "scripts/check_control_plane_contract.py",
            'raise ValueError("ExperimentRequest must be an object schema")',
            'raise TypeError("ExperimentRequest must be an object schema")',
        ),
        (
            "scripts/check_control_plane_contract.py",
            'raise ValueError("ExperimentRequest must declare its properties")',
            'raise TypeError("ExperimentRequest must declare its properties")',
        ),
        (
            "scripts/check_control_plane_contract.py",
            'raise ValueError("Run transitions must be an array schema")',
            'raise TypeError("Run transitions must be an array schema")',
        ),
        (
            "scripts/package_release.py",
            '''    with output.open("wb") as raw:\n        with gzip.GzipFile(filename="", mode="wb", fileobj=raw, mtime=epoch, compresslevel=9) as compressed:\n            with tarfile.open(fileobj=compressed, mode="w", format=tarfile.PAX_FORMAT) as archive:\n                for path in relative_files(source):\n                    relative = path.relative_to(source).as_posix()\n                    info = archive.gettarinfo(path, arcname=relative)\n                    info.uid = 0\n                    info.gid = 0\n                    info.uname = ""\n                    info.gname = ""\n                    info.mtime = epoch\n                    with path.open("rb") as content:\n                        archive.addfile(info, content)\n''',
            '''    with (\n        output.open("wb") as raw,\n        gzip.GzipFile(\n            filename="",\n            mode="wb",\n            fileobj=raw,\n            mtime=epoch,\n            compresslevel=9,\n        ) as compressed,\n        tarfile.open(\n            fileobj=compressed,\n            mode="w",\n            format=tarfile.PAX_FORMAT,\n        ) as archive,\n    ):\n        for path in relative_files(source):\n            relative = path.relative_to(source).as_posix()\n            info = archive.gettarinfo(path, arcname=relative)\n            info.uid = 0\n            info.gid = 0\n            info.uname = ""\n            info.gname = ""\n            info.mtime = epoch\n            with path.open("rb") as content:\n                archive.addfile(info, content)\n''',
        ),
        (
            "scripts/semantic_execute.py",
            "        except Exception:\n            return False\n",
            "        except Exception:  # noqa: BLE001 -- reject any unreadable or invalid artifact\n            return False\n",
        ),
        (
            "scripts/verify_references.py",
            '''    if bib_pages and registered_pages:\n        if normalize_text(bib_pages) != normalize_text(str(registered_pages)):\n            errors.append(f"{key}: pages mismatch: bib={bib_pages!r}, Crossref={registered_pages!r}")\n''',
            '''    if (\n        bib_pages\n        and registered_pages\n        and normalize_text(bib_pages) != normalize_text(str(registered_pages))\n    ):\n        errors.append(f"{key}: pages mismatch: bib={bib_pages!r}, Crossref={registered_pages!r}")\n''',
        ),
        (
            "services/scientific_worker.py",
            'raise ValueError("request_id must be a UUID string")',
            'raise TypeError("request_id must be a UUID string")',
        ),
        (
            "src/metastable_suite/campaigns.py",
            "        except Exception:\n            return False\n",
            "        except Exception:  # noqa: BLE001 -- isolate validator plugin failures\n            return False\n",
        ),
        (
            "src/metastable_suite/campaigns.py",
            '''    dataset_path = dataset.get("mns:datasetPath")\n    if not isinstance(dataset_path, str) or (\n        Path(dataset_path).resolve() != events.resolve()\n    ):\n        return False\n    return True\n''',
            '''    dataset_path = dataset.get("mns:datasetPath")\n    return (\n        isinstance(dataset_path, str)\n        and Path(dataset_path).resolve() == events.resolve()\n    )\n''',
        ),
        (
            "src/metastable_suite/campaigns.py",
            "        except Exception as exc:\n            events_path.unlink(missing_ok=True)\n",
            "        except Exception as exc:  # noqa: BLE001 -- failure policy records backend errors\n            events_path.unlink(missing_ok=True)\n",
        ),
        (
            "src/metastable_suite/dataset_ndjson.py",
            "    def __enter__(self) -> EventDatasetWriter:\n",
            "    # Keep Python 3.10 support without adding typing_extensions solely for Self.\n    def __enter__(self) -> EventDatasetWriter:  # noqa: PYI034\n",
        ),
        (
            "src/metastable_suite/dataset_ndjson.py",
            'raise ValueError(f"event at line {line_number} is not an object")',
            'raise TypeError(f"event at line {line_number} is not an object")',
        ),
        (
            "src/metastable_suite/dataset_registry.py",
            'raise ValueError(f"dataset registry entry {dataset_id!r} must be an object")',
            'raise TypeError(f"dataset registry entry {dataset_id!r} must be an object")',
        ),
        (
            "src/metastable_suite/dataset_registry.py",
            'raise ValueError("dataset registry must be an object")',
            'raise TypeError("dataset registry must be an object")',
        ),
        (
            "src/metastable_suite/dataset_registry.py",
            'raise ValueError("dataset registry must contain a datasets object")',
            'raise TypeError("dataset registry must contain a datasets object")',
        ),
        (
            "src/metastable_suite/transports.py",
            "import socket\nimport time\n",
            "import socket\nimport time\nfrom contextlib import suppress\n",
        ),
        (
            "src/metastable_suite/transports.py",
            '''        try:\n            self.disconnect()\n        except Exception:\n            # Preserve the terminal transport error even if closing the failed handle also fails.\n            pass\n''',
            '''        # Preserve the terminal transport error even if closing the failed handle also fails.\n        with suppress(Exception):\n            self.disconnect()\n''',
        ),
        (
            "src/metastable_suite/transports.py",
            '''        if resource is not None:\n            try:\n                resource.close()\n            except Exception:\n                pass\n        if manager is not None:\n            try:\n                manager.close()\n            except Exception:\n                pass\n''',
            '''        if resource is not None:\n            with suppress(Exception):\n                resource.close()\n        if manager is not None:\n            with suppress(Exception):\n                manager.close()\n''',
        ),
        (
            "tests/test_campaigns.py",
            "    except Exception:\n        return False\n",
            "    except Exception:  # noqa: BLE001 -- test helper mirrors validator isolation\n        return False\n",
        ),
    ]
    for path, old, new in replacements:
        replace_once(path, old, new)


if __name__ == "__main__":
    main()
