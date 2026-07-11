#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

from metastable_suite.dataset_semantics import manifest_to_abox
from metastable_suite.datasets import DatasetRegistry, read_events, verify_manifest, write_events

ROOT = Path(__file__).resolve().parents[1]
EVENT_SCHEMA = ROOT / "schemas" / "event.schema.json"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Convert, register and verify event datasets")
    subparsers = parser.add_subparsers(dest="command", required=True)

    convert = subparsers.add_parser("convert", help="convert an event dataset")
    convert.add_argument("source", type=Path)
    convert.add_argument("target", type=Path)
    convert.add_argument("--dataset-id", required=True)
    convert.add_argument("--source-format", choices=["ndjson", "parquet"])
    convert.add_argument("--target-format", choices=["ndjson", "parquet"], required=True)
    convert.add_argument("--partition-size", type=int, default=100_000)
    convert.add_argument("--registry", type=Path, required=True)
    convert.add_argument("--schema", type=Path, default=EVENT_SCHEMA)
    convert.add_argument("--abox", type=Path)

    verify = subparsers.add_parser("verify", help="verify all manifests in a registry")
    verify.add_argument("registry", type=Path)

    args = parser.parse_args(argv)
    if args.command == "verify":
        manifests = DatasetRegistry(args.registry).manifests()
        for manifest in manifests:
            verify_manifest(manifest)
        print(json.dumps({"verified_datasets": len(manifests)}, indent=2))
        return 0

    schema = json.loads(args.schema.read_text(encoding="utf-8"))
    manifest = write_events(
        args.target,
        args.dataset_id,
        read_events(args.source, args.source_format),
        schema,
        storage_format=args.target_format,
        partition_size=args.partition_size,
    )
    verify_manifest(manifest)
    DatasetRegistry(args.registry).register(manifest, replace=True)
    if args.abox:
        args.abox.parent.mkdir(parents=True, exist_ok=True)
        args.abox.write_text(
            json.dumps(manifest_to_abox(manifest, args.registry.as_posix()), indent=2) + "\n",
            encoding="utf-8",
        )
    print(json.dumps(manifest.as_dict(), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
