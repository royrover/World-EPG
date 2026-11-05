
#!/usr/bin/env python3
"""
Remove duplicate XMLTV channels and programmes.

Channel identity:
    channel id

Programme identity:
    channel + start + stop + title

Usage:
    python scripts/dedupe.py epg/guide.xml epg/guide.xml
"""

import sys
import xml.etree.ElementTree as ET
from pathlib import Path


def main():
    if len(sys.argv) < 3:
        print(
            f"Usage: python {sys.argv[0]} "
            "<input_file> <output_file>"
        )
        sys.exit(1)

    src = Path(sys.argv[1])
    dst = Path(sys.argv[2])

    if not src.is_file():
        print(f"Error: Input file not found: {src}")
        sys.exit(1)

    try:
        tree = ET.parse(src)
    except Exception as e:
        print(f"Error parsing XML file: {e}")
        sys.exit(1)

    root = tree.getroot()

    if root.tag != "tv":
        print(f"Error: Invalid XMLTV root element: {root.tag}")
        sys.exit(1)

    seen_ch = set()
    seen_pg = set()

    new_children = []

    total_channels = 0
    unique_channels = 0

    total_programmes = 0
    unique_programmes = 0

    # Process all XMLTV elements in one pass.
    for el in root:

        if el.tag == "channel":

            total_channels += 1

            channel_id = el.get("id")

            # Keep elements without an ID.
            if not channel_id:
                unique_channels += 1
                new_children.append(el)
                continue

            if channel_id in seen_ch:
                continue

            seen_ch.add(channel_id)

            unique_channels += 1
            new_children.append(el)

        elif el.tag == "programme":

            total_programmes += 1

            key = (
                el.get("channel"),
                el.get("start"),
                el.get("stop"),
                el.findtext("title"),
            )

            # Keep incomplete programme records.
            if not all(key):
                unique_programmes += 1
                new_children.append(el)
                continue

            if key in seen_pg:
                continue

            seen_pg.add(key)

            unique_programmes += 1
            new_children.append(el)

        else:

            # Preserve all other XMLTV elements.
            new_children.append(el)

    # Replace XMLTV root children in one operation.
    root[:] = new_children

    try:
        dst.parent.mkdir(parents=True, exist_ok=True)

        tree.write(
            dst,
            encoding="UTF-8",
            xml_declaration=True
        )

    except Exception as e:
        print(f"Error writing XML file: {e}")
        sys.exit(1)

    # Summary.
    ch_removed = total_channels - unique_channels
    pg_removed = total_programmes - unique_programmes

    print("")
    print("========== XMLTV DEDUPLICATION ==========")

    print(
        f"Channels: {unique_channels} unique "
        f"(removed {ch_removed} duplicates)"
    )

    print(
        f"Programmes: {unique_programmes} unique "
        f"(removed {pg_removed} duplicates)"
    )

    print(f"Input:  {src}")
    print(f"Output: {dst}")

    print("=========================================")


if __name__ == "__main__":
    main()
  
