#!/usr/bin/env python3
"""
Validate per-source XMLTV, GZIP and JSON EPG files.

Usage:
    python scripts/validate_epg.py epg
"""

import sys
import gzip
import json
import re
import xml.etree.ElementTree as ET

from pathlib import Path


def fail(message):
    print(f"ERROR: {message}")
    sys.exit(1)


def warn(message):
    print(f"WARNING: {message}")


DATETIME_RE = re.compile(r"^\d{14}(?:\s*[+-]\d{4})?$")


def validate_xml(xml_file):
    try:
        root = ET.parse(xml_file).getroot()
    except Exception as e:
        fail(f"{xml_file.name}: cannot parse XML: {e}")

    if root.tag != "tv":
        fail(f"{xml_file.name}: invalid XMLTV root element: {root.tag}")

    channels = root.findall("channel")
    programmes = root.findall("programme")

    if not channels:
        fail(f"{xml_file.name}: no channels found.")
    if not programmes:
        fail(f"{xml_file.name}: no programmes found.")

    channel_ids = set()
    for channel in channels:
        channel_id = channel.get("id")
        if not channel_id:
            fail(f"{xml_file.name}: channel without id attribute.")
        if channel_id in channel_ids:
            warn(f"{xml_file.name}: duplicate channel id: {channel_id}")
        channel_ids.add(channel_id)

    for index, programme in enumerate(programmes, start=1):
        channel = programme.get("channel")
        start = programme.get("start")
        stop = programme.get("stop")

        if not channel or not start or not stop:
            fail(f"{xml_file.name}: programme #{index} missing channel/start/stop.")
        if not DATETIME_RE.match(start) or not DATETIME_RE.match(stop):
            fail(f"{xml_file.name}: programme #{index} invalid time: {start} / {stop}")
        if channel not in channel_ids:
            fail(f"{xml_file.name}: programme #{index} unknown channel: {channel}")

    print(f"  XML: OK (channels={len(channel_ids)}, programmes={len(programmes)})")
    return len(channel_ids), len(programmes)


def validate_gzip(gzip_file, xml_file):
    if not gzip_file.is_file():
        fail(f"GZIP file not found: {gzip_file.name}")

    try:
        with gzip.open(gzip_file, "rb") as f:
            gzip_data = f.read()
        xml_data = xml_file.read_bytes()
    except Exception as e:
        fail(f"{gzip_file.name}: cannot read GZIP/XML: {e}")

    if not gzip_data:
        fail(f"{gzip_file.name}: GZIP file is empty.")
    if gzip_data != xml_data:
        fail(f"{gzip_file.name}: content does not match {xml_file.name}.")

    print(f"  GZIP: OK ({gzip_file.stat().st_size:,} bytes)")


def validate_json(json_file):
    if not json_file.is_file():
        fail(f"JSON file not found: {json_file.name}")

    try:
        with json_file.open("r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:
        fail(f"{json_file.name}: invalid JSON: {e}")

    if not data:
        fail(f"{json_file.name}: no data.")
    if not isinstance(data, (dict, list)):
        fail(f"{json_file.name}: root must be an object or array.")

    print(f"  JSON: OK ({json_file.stat().st_size:,} bytes)")


def main():
    if len(sys.argv) != 2:
        print(f"Usage: python {sys.argv[0]} <epg_directory>")
        sys.exit(1)

    epg_dir = Path(sys.argv[1])
    if not epg_dir.is_dir():
        fail(f"EPG directory not found: {epg_dir}")

    xml_files = sorted(epg_dir.glob("*.xml"))
    if not xml_files:
        fail(f"No .xml files found in {epg_dir}")

    total_ch = total_pg = 0
    for xml_file in xml_files:
        print(f"\n##### {xml_file.name} #####")
        ch, pg = validate_xml(xml_file)
        validate_gzip(xml_file.with_name(xml_file.name + ".gz"), xml_file)
        validate_json(xml_file.with_suffix(".json"))
        total_ch += ch
        total_pg += pg

    print("\n======================================")
    print("      ALL VALIDATIONS PASSED")
    print("======================================")
    print(f"Sources: {len(xml_files)}")
    print(f"Channels: {total_ch}")
    print(f"Programmes: {total_pg}")


if __name__ == "__main__":
    main()
