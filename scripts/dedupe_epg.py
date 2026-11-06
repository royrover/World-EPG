#!/usr/bin/env python3
"""Remove duplicate <channel> (by id) and duplicate <programme> from an XMLTV file.

Usage:
  python scripts/dedupe_epg.py epg/guide.xml            # edit in place
  python scripts/dedupe_epg.py epg                      # folder -> epg/guide.xml
  python scripts/dedupe_epg.py in.xml out.xml
"""

import sys
import xml.etree.ElementTree as ET
from pathlib import Path

src = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("epg")
if src.is_dir():
    src = src / "guide.xml"
dst = Path(sys.argv[2]) if len(sys.argv) > 2 else src

tree = ET.parse(src)
root = tree.getroot()

seen_ch, seen_pg = set(), set()
removed_ch = removed_pg = 0
for el in list(root):
    if el.tag == "channel":
        key, seen = el.get("id"), seen_ch
    elif el.tag == "programme":
        key, seen = (
            el.get("channel"),
            el.get("start"),
            el.get("stop"),
            el.findtext("title"),
        ), seen_pg
    else:
        continue
    if key in seen:
        root.remove(el)
        if el.tag == "channel":
            removed_ch += 1
        else:
            removed_pg += 1
    else:
        seen.add(key)

tree.write(dst, encoding="UTF-8", xml_declaration=True)
print(
    f"dedupe: channels={len(seen_ch)} (-{removed_ch}) programmes={len(seen_pg)} (-{removed_pg})"
)
