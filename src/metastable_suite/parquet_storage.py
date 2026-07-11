from __future__ import annotations

from datetime import datetime, timezone
import json
from pathlib import Path
from typing import Iterable, Iterator, Mapping

from .dataset_models import (
    DatasetManifest,
    DatasetPartitionManifest,
    PARQUET_MEDIA_TYPE,
    aggregate_dataset_hash,
    event_validator,
    sha256_file,
    validate_event,
)

_JSON_COLUMNS = ("settings", "outcome