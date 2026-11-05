
#!/usr/bin/env python3
"""
Validate generated XMLTV, GZIP and JSON EPG files.

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


def validate_xml(xml_file):
    print("\n========== XMLTV VALIDATION ==========")

    if not xml_file.is_file():
        fail(f"XML file not found: {xml_file}")

    try:
        tree = ET.parse(xml_file)
    except Exception as e:
        fail(f"Cannot parse XML: {e}")

    root = tree.getroot()

    if root.tag != "tv":
        fail(f"Invalid XMLTV root element: {root.tag}")

    channels = root.findall("channel")
    programmes = root.findall("programme")

    if not channels:
        fail("No channels found in XMLTV.")

    if not programmes:
        fail("No programmes found in XMLTV.")

    channel_ids = set()

    for channel in channels:
        channel_id = channel.get("id")

        if not channel_id:
            fail("Channel found without id attribute.")

        if channel_id in channel_ids:
            fail(f"Duplicate channel ID found: {channel_id}")

        channel_ids.add(channel_id)

    datetime_pattern = re.compile(
        r"^\d{14}(?:\s*[+-]\d{4})?$"
    )

    for index, programme in enumerate(programmes, start=1):

        channel = programme.get("channel")
        start = programme.get("start")
        stop = programme.get("stop")

        if not channel:
            fail(f"Programme #{index} missing channel attribute.")

        if not start:
            fail(f"Programme #{index} missing start attribute.")

        if not stop:
            fail(f"Programme #{index} missing stop attribute.")

        if not datetime_pattern.match(start):
            fail(f"Invalid programme start time: {start}")

        if not datetime_pattern.match(stop):
            fail(f"Invalid programme stop time: {stop}")

        if channel not in channel_ids:
            fail(
                f"Programme #{index} references unknown channel: "
                f"{channel}"
            )

    print(f"Channels: {len(channels)}")
    print(f"Programmes: {len(programmes)}")
    print("XMLTV structure: OK")

    return len(channels), len(programmes)


def validate_gzip(gzip_file, xml_file):
    print("\n========== GZIP VALIDATION ==========")

    if not gzip_file.is_file():
        fail(f"GZIP file not found: {gzip_file}")

    try:
        with gzip.open(gzip_file, "rb") as f:
            gzip_data = f.read()

        xml_data = xml_file.read_bytes()

    except Exception as e:
        fail(f"Cannot read GZIP/XML: {e}")

    if not gzip_data:
        fail("GZIP file is empty.")

    if gzip_data != xml_data:
        fail("GZIP content does not match guide.xml.")

    print(f"GZIP size: {gzip_file.stat().st_size:,} bytes")
    print("GZIP content matches XML: OK")


def validate_json(json_file):
    print("\n========== JSON VALIDATION ==========")

    if not json_file.is_file():
        fail(f"JSON file not found: {json_file}")

    try:
        with json_file.open("r", encoding="utf-8") as f:
            data = json.load(f)

    except Exception as e:
        fail(f"Invalid JSON: {e}")

    if not data:
        fail("JSON file contains no data.")

    if not isinstance(data, (dict, list)):
        fail("JSON root must be an object or array.")

    print(f"JSON size: {json_file.stat().st_size:,} bytes")
    print(f"JSON root type: {type(data).__name__}")
    print("JSON syntax: OK")


def main():

    if len(sys.argv) != 2:
        print(f"Usage: python {sys.argv[0]} <epg_directory>")
        sys.exit(1)

    epg_dir = Path(sys.argv[1])

    if not epg_dir.is_dir():
        fail(f"EPG directory not found: {epg_dir}")

    xml_file = epg_dir / "guide.xml"
    gzip_file = epg_dir / "guide.xml.gz"
    json_file = epg_dir / "guide.json"

    print("======================================")
    print("       WORLD EPG FILE VALIDATOR")
    print("======================================")

    channels, programmes = validate_xml(xml_file)

    validate_gzip(gzip_file, xml_file)

    validate_json(json_file)

    print("\n======================================")
    print("       ALL VALIDATIONS PASSED")
    print("======================================")
    print(f"Channels: {channels}")
    print(f"Programmes: {programmes}")
    print("XML: OK")
    print("GZIP: OK")
    print("JSON: OK")


if __name__ == "__main__":
    main()
