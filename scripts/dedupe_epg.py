#!/usr/bin/env python3
"""Remove duplicate <channel> (by id) and duplicate <programme> from an XMLTV file."""

import sys
import xml.etree.ElementTree as ET
from pathlib import Path

src = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("epg")
if src.is_dir():
    src = src / "guide.xml"
dst = Path(sys.argv[2]) if len(sys.argv) > 2 else src

tree = ET.parse(src)
root = tree.getroot()

seen_ch = set()
seen_pg = set()
removed_ch = removed_pg = 0

for el in list(root):
    if el.tag == "channel":
        ch_id = el.get("id")
        if ch_id in seen_ch:
            root.remove(el)
            removed_ch += 1
        else:
            seen_ch.add(ch_id)

    elif el.tag == "programme":
        # สร้างคีย์สำหรับเช็ครายการซ้ำจาก channel, start, stop และ title
        title_el = el.find("title")
        title_text = title_el.text if title_el is not None else ""
        key = (el.get("channel"), el.get("start"), el.get("stop"), title_text)

        if key in seen_pg:
            root.remove(el)
            removed_pg += 1
        else:
            seen_pg.add(key)

tree.write(dst, encoding="UTF-8", xml_declaration=True)
print(
    f"dedupe: channels={len(seen_ch)} (-{removed_ch}) programmes={len(seen_pg)} (-{removed_pg})"
)
