#!/usr/bin/env python3
"""
Validate iptv-org generated XMLTV, GZIP and JSON files before publication.

The validator intentionally fails closed:
- missing or empty files are rejected
- malformed XML / JSON / GZIP is rejected
- an unexpectedly tiny guide is rejected
- XMLTV programmes must have valid channel, start and stop attributes
- programme stop times must be later than start times
- GZIP content must match guide.xml byte-for-byte
"""

from __future__ import annotations

import gzip
import json
import sys
import xml.etree.ElementTree as ET
from datetime import datetime
from pathlib import Path


MIN_CHANNELS = 10
MIN_PROGRAMMES = 100
MIN_FILE_SIZE = 100


def fail(message: str) -> None:
    print(f"::error::{message}", file=sys.stderr)
    raise SystemExit(1)


def parse_xmltv_datetime(value: str, label: str) -> datetime:
    value = value.strip()
    if not value:
        fail(f"XMLTV {label} timestamp is empty")

    # XMLTV commonly uses YYYYMMDDhhmmss with an optional timezone suffix.
    core = value[:14]
    if len(core) != 14 or not core.isdigit():
        fail(f"Invalid XMLTV {label} timestamp: {value!r}")

    try:
        return datetime.strptime(core, "%Y%m%d%H%M%S")
    except ValueError as exc:
        fail(f"Invalid XMLTV {label} timestamp {value!r}: {exc}")


def validate_xml(path: Path) -> tuple[int, int]:
    if not path.is_file():
        fail(f"Missing XMLTV file: {path}")
    if path.stat().st_size < MIN_FILE_SIZE:
        fail(f"XMLTV file is unexpectedly small: {path.stat().st_size} bytes")

    try:
        tree = ET.parse(path)
    except (ET.ParseError, OSError) as exc:
        fail(f"Cannot parse XMLTV: {exc}")

    root = tree.getroot()
    if root.tag != "tv":
        fail(f"Unexpected XML root element: {root.tag!r}; expected 'tv'")

    channels = root.findall("channel")
    programmes = root.findall("programme")

    if len(channels) < MIN_CHANNELS:
        fail(
            f"Too few channels: {len(channels)} "
            f"(minimum required: {MIN_CHANNELS})"
        )

    if len(programmes) < MIN_PROGRAMMES:
        fail(
            f"Too few programmes: {len(programmes)} "
            f"(minimum required: {MIN_PROGRAMMES})"
        )

    channel_ids = {
        item.get("id")
        for item in channels
        if item.get("id")
    }

    if not channel_ids:
        fail("No channel IDs were found in XMLTV")

    invalid_programmes = 0
    missing_channel_refs = 0

    for index, programme in enumerate(programmes, start=1):
        channel_id = programme.get("channel", "").strip()
        start = programme.get("start", "").strip()
        stop = programme.get("stop", "").strip()

        if not channel_id or not start or not stop:
            invalid_programmes += 1
            continue

        if channel_id not in channel_ids:
            missing_channel_refs += 1

        start_dt = parse_xmltv_datetime(start, f"start at programme {index}")
        stop_dt = parse_xmltv_datetime(stop, f"stop at programme {index}")

        if stop_dt <= start_dt:
            fail(
                f"Programme {index} has stop <= start "
                f"({start!r} -> {stop!r})"
            )

    if invalid_programmes:
        fail(f"{invalid_programmes} programmes have missing required attributes")

    if missing_channel_refs:
        print(
            f"::warning::{missing_channel_refs} programmes reference channel "
            "IDs not declared in this XML file"
        )

    return len(channels), len(programmes)


def validate_gzip(xml_path: Path, gzip_path: Path) -> None:
    if not gzip_path.is_file():
        fail(f"Missing GZIP file: {gzip_path}")
    if gzip_path.stat().st_size < MIN_FILE_SIZE:
        fail(f"GZIP file is unexpectedly small: {gzip_path.stat().st_size} bytes")

    try:
        with gzip.open(gzip_path, "rb") as handle:
            decompressed = handle.read()
    except (OSError, EOFError) as exc:
        fail(f"Cannot decompress GZIP: {exc}")

    original = xml_path.read_bytes()
    if decompressed != original:
        fail("guide.xml.gz does not decompress to the exact guide.xml content")


def validate_json(path: Path) -> None:
    if not path.is_file():
        fail(f"Missing JSON file: {path}")
    if path.stat().st_size < MIN_FILE_SIZE:
        fail(f"JSON file is unexpectedly small: {path.stat().st_size} bytes")

    try:
        with path.open("r", encoding="utf-8") as handle:
            data = json.load(handle)
    except (json.JSONDecodeError, UnicodeDecodeError, OSError) as exc:
        fail(f"Cannot parse JSON: {exc}")

    if data is None:
        fail("JSON output is null")

    if isinstance(data, (dict, list)) and len(data) == 0:
        fail("JSON output is empty")

    if not isinstance(data, (dict, list)):
        fail(f"Unexpected JSON top-level type: {type(data).__name__}")


def main() -> None:
    output_dir = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("epg")

    xml_path = output_dir / "guide.xml"
    gzip_path = output_dir / "guide.xml.gz"
    json_path = output_dir / "guide.json"

    channels, programmes = validate_xml(xml_path)
    validate_gzip(xml_path, gzip_path)
    validate_json(json_path)

    print("EPG validation passed")
    print(f"Channels: {channels:,}")
    print(f"Programmes: {programmes:,}")
    print(f"XML: {xml_path.stat().st_size:,} bytes")
    print(f"GZIP: {gzip_path.stat().st_size:,} bytes")
    print(f"JSON: {json_path.stat().st_size:,} bytes")


if __name__ == "__main__":
    main()
