#!/usr/bin/env python3
from __future__ import annotations

import argparse
import gzip
import os
from pathlib import Path
import stat
import tarfile
import time
import zipfile


def normalized_epoch() -> int:
    return int(os.environ.get("SOURCE_DATE_EPOCH", "315532800"))


def relative_files(root: Path) -> list[Path]:
    return sorted(path for path in root.rglob("*") if path.is_file())


def write_zip(source: Path, output: Path, epoch: int) -> None:
    timestamp = time.gmtime(max(epoch, 315532800))[:6]
    with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for path in relative_files(source):
            relative = path.relative_to(source).as_posix()
            info = zipfile.ZipInfo(relative, timestamp)
            info.compress_type = zipfile.ZIP_DEFLATED
            info.create_system = 3
            mode = stat.S_IMODE(path.stat().st_mode)
            info.external_attr = mode << 16
            archive.writestr(info, path.read_bytes(), compress_type=zipfile.ZIP_DEFLATED, compresslevel=9)


def write_tar_gz(source: Path, output: Path, epoch: int) -> None:
    with output.open("wb") as raw:
        with gzip.GzipFile(filename="", mode="wb", fileobj=raw, mtime=epoch, compresslevel=9) as compressed:
            with tarfile.open(fileobj=compressed, mode="w", format=tarfile.PAX_FORMAT) as archive:
                for path in relative_files(source):
                    relative = path.relative_to(source).as_posix()
                    info = archive.gettarinfo(path, arcname=relative)
                    info.uid = 0
                    info.gid = 0
                    info.uname = ""
                    info.gname = ""
                    info.mtime = epoch
                    with path.open("rb") as content:
                        archive.addfile(info, content)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("source", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    source = args.source.resolve()
    output = args.output.resolve()
    if not source.is_dir():
        parser.error(f"source directory does not exist: {source}")
    output.parent.mkdir(parents=True, exist_ok=True)
    epoch = normalized_epoch()
    if output.name.endswith(".tar.gz"):
        write_tar_gz(source, output, epoch)
    elif output.suffix == ".zip":
        write_zip(source, output, epoch)
    else:
        parser.error("output must end in .zip or .tar.gz")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
