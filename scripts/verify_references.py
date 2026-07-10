#!/usr/bin/env python3
from __future__ import annotations

import argparse
from difflib import SequenceMatcher
import json
from pathlib import Path
import re
import sys
import time
import unicodedata
from urllib.error import HTTPError, URLError
from urllib.parse import quote
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
BIB_PATH = ROOT / "references.bib"
SOURCES_PATH = ROOT / "docs" / "09_fuentes_por_experimento.md"
CROSSREF_BASE = "https://api.crossref.org/works/"
USER_AGENT = "metastable-nucleation-suite/0.1 (reference verification; mailto:repository-maintainer@example.invalid)"


def parse_bibtex(text: str) -> dict[str, dict[str, str]]:
    entries: dict[str, dict[str, str]] = {}
    blocks = re.split(r"(?=^@)", text, flags=re.MULTILINE)
    for block in blocks:
        block = block.strip()
        if not block:
            continue
        header = re.match(r"@\w+\s*\{\s*([^,]+),", block)
        if not header:
            raise ValueError(f"invalid BibTeX entry header: {block[:80]!r}")
        key = header.group(1).strip()
        fields: dict[str, str] = {}
        position = header.end()
        while position < len(block):
            field_match = re.search(r"([A-Za-z][A-Za-z0-9_-]*)\s*=\s*\{", block[position:])
            if not field_match:
                break
            name = field_match.group(1).lower()
            value_start = position + field_match.end()
            depth = 1
            cursor = value_start
            while cursor < len(block) and depth:
                if block[cursor] == "{":
                    depth += 1
                elif block[cursor] == "}":
                    depth -= 1
                cursor += 1
            if depth:
                raise ValueError(f"unclosed field {name!r} in {key!r}")
            fields[name] = block[value_start : cursor - 1].strip()
            position = cursor
        entries[key] = fields
    return entries


def normalize_text(value: str) -> str:
    value = value.replace("--", "-")
    value = re.sub(r"\\['\"`^~=.uvHckbdtr]\{?([A-Za-z])\}?", r"\1", value)
    value = value.replace("\\v", "").replace("\\'", "")
    value = unicodedata.normalize("NFKD", value)
    value = "".join(character for character in value if not unicodedata.combining(character))
    value = value.casefold()
    return " ".join(re.findall(r"[a-z0-9]+", value))


def title_similarity(left: str, right: str) -> float:
    return SequenceMatcher(None, normalize_text(left), normalize_text(right)).ratio()


def crossref_year(message: dict) -> int | None:
    for field in ("published-print", "published-online", "issued", "created"):
        date_parts = message.get(field, {}).get("date-parts")
        if date_parts and date_parts[0]:
            return int(date_parts[0][0])
    return None


def fetch_crossref(doi: str, retries: int = 3) -> dict:
    endpoint = CROSSREF_BASE + quote(doi, safe="")
    request = Request(endpoint, headers={"User-Agent": USER_AGENT, "Accept": "application/json"})
    last_error: Exception | None = None
    for attempt in range(retries):
        try:
            with urlopen(request, timeout=25) as response:
                payload = json.load(response)
            if payload.get("status") != "ok":
                raise RuntimeError(f"Crossref returned status {payload.get('status')!r}")
            return payload["message"]
        except (HTTPError, URLError, TimeoutError, json.JSONDecodeError, RuntimeError) as exc:
            last_error = exc
            if attempt + 1 < retries:
                time.sleep(1.5 * (attempt + 1))
    raise RuntimeError(f"could not query Crossref for {doi}: {last_error}")


def cited_keys(text: str) -> set[str]:
    keys: set[str] = set()
    for line in text.splitlines():
        if not line.startswith("| E"):
            continue
        keys.update(re.findall(r"`([A-Za-z0-9_:-]+)`", line))
    return keys


def validate_metadata(key: str, fields: dict[str, str], metadata: dict) -> list[str]:
    errors: list[str] = []
    doi = fields.get("doi")
    registered_doi = metadata.get("DOI")
    if not doi or not registered_doi or doi.casefold() != registered_doi.casefold():
        errors.append(f"{key}: DOI mismatch: bib={doi!r}, Crossref={registered_doi!r}")

    registered_titles = metadata.get("title") or []
    if not registered_titles:
        errors.append(f"{key}: Crossref has no title")
    else:
        similarity = title_similarity(fields.get("title", ""), registered_titles[0])
        if similarity < 0.90:
            errors.append(
                f"{key}: title mismatch ({similarity:.2%} similar): "
                f"bib={fields.get('title')!r}; Crossref={registered_titles[0]!r}"
            )

    bib_year = fields.get("year")
    registered_year = crossref_year(metadata)
    if bib_year and registered_year and int(bib_year) != registered_year:
        errors.append(f"{key}: year mismatch: bib={bib_year}, Crossref={registered_year}")

    bib_volume = fields.get("volume")
    registered_volume = metadata.get("volume")
    if bib_volume and registered_volume and normalize_text(bib_volume) != normalize_text(str(registered_volume)):
        errors.append(f"{key}: volume mismatch: bib={bib_volume!r}, Crossref={registered_volume!r}")

    bib_pages = fields.get("pages")
    registered_pages = metadata.get("page") or metadata.get("article-number")
    if bib_pages and registered_pages:
        normalized_bib_pages = normalize_text(bib_pages)
        normalized_registered_pages = normalize_text(str(registered_pages))
        if normalized_bib_pages != normalized_registered_pages:
            errors.append(f"{key}: pages mismatch: bib={bib_pages!r}, Crossref={registered_pages!r}")

    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description="Verify BibTeX references against Crossref")
    parser.add_argument("--no-network", action="store_true", help="only validate local keys and DOI syntax")
    args = parser.parse_args()

    entries = parse_bibtex(BIB_PATH.read_text(encoding="utf-8"))
    used_keys = cited_keys(SOURCES_PATH.read_text(encoding="utf-8"))
    errors: list[str] = []

    missing_keys = used_keys - entries.keys()
    uncited_keys = entries.keys() - used_keys
    if missing_keys:
        errors.append(f"references used but absent from references.bib: {sorted(missing_keys)}")
    if uncited_keys:
        errors.append(f"references present but absent from the experiment map: {sorted(uncited_keys)}")

    doi_pattern = re.compile(r"^10\.\d{4,9}/\S+$", re.IGNORECASE)
    for key, fields in sorted(entries.items()):
        doi = fields.get("doi")
        if not doi:
            errors.append(f"{key}: missing DOI")
            continue
        if not doi_pattern.fullmatch(doi):
            errors.append(f"{key}: malformed DOI {doi!r}")
            continue
        if args.no_network:
            continue
        try:
            metadata = fetch_crossref(doi)
        except RuntimeError as exc:
            errors.append(f"{key}: {exc}")
            continue
        entry_errors = validate_metadata(key, fields, metadata)
        errors.extend(entry_errors)
        if not entry_errors:
            print(f"OK {key}: {doi} — {(metadata.get('title') or [''])[0]}")

    if errors:
        print("Reference verification failed:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1

    print(f"Reference verification passed: {len(entries)} DOI records and {len(used_keys)} cited keys.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
