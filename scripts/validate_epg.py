#!/usr/bin/env python3
"""Remove duplicate <channel> (by id) and duplicate <programme> from an XMLTV file.

Usage: python dedupe.py epg/guide.xml epg/guide.xml
Run it after guide.xml is generated and BEFORE guide.xml.gz / guide.json are built.
"""
import sys
import xml.etree.ElementTree as ET

src, dst = sys.argv[1], sys.argv[2]
tree = ET.parse(src)
root = tree.getroot()

seen_ch, seen_pg = set(), set()
for el in list(root):
    if el.tag == "channel":
        key, seen = el.get("id"), seen_ch
    elif el.tag == "programme":
        key, seen = (el.get("channel"), el.get("start"), el.get("stop"), el.findtext("title")), seen_pg
    else:
        continue
    if key in seen:
        root.remove(el)
    else:
        seen.add(key)

tree.write(dst, encoding="UTF-8", xml_declaration=True)
print(f"channels={len(seen_ch)} programmes={len(seen_pg)}")
