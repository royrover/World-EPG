#!/usr/bin/env python3
"""Remove duplicate <channel> (by id) and duplicate <programme> from an XMLTV file.

Usage: python dedupe.py epg/guide.xml epg/guide.xml
Run it after guide.xml is generated and BEFORE guide.xml.gz / guide.json are built.
"""
import sys
import xml.etree.ElementTree as ET


def main():
  if len(sys.argv) < 3:
    print(f"Usage: python {sys.argv[0]} <input_file> <output_file>")
    sys.exit(1)

  src, dst = sys.argv[1], sys.argv[2]

  try:
    tree = ET.parse(src)
  except Exception as e:
    print(f"Error parsing XML file: {e}")
    sys.exit(1)

  root = tree.getroot()

  seen_ch = set()
  seen_pg = set()
  new_children = []

  total_channels = 0
  unique_channels = 0
  total_programmes = 0
  unique_programmes = 0

  # กรองข้อมูลและสร้างลิสต์ใหม่แบบ O(N) ประหยัดเวลาและแรมกว่าการใช้ root.remove()
  for el in root:
    if el.tag == "channel":
      total_channels += 1
      key = el.get("id")
      if key in seen_ch:
        continue  # ข้ามตัวซ้ำ
      seen_ch.add(key)
      unique_channels += 1
      new_children.append(el)

    elif el.tag == "programme":
      total_programmes += 1
      # ใช้ channel, start, stop และ title เป็น key ในการเช็คซ้ำ
      key = (
          el.get("channel"),
          el.get("start"),
          el.get("stop"),
          el.findtext("title"),
      )
      if key in seen_pg:
        continue  # ข้ามตัวซ้ำ
      seen_pg.add(key)
      unique_programmes += 1
      new_children.append(el)

    else:
      # เก็บ element อื่นๆ ที่ไม่ใช่ channel หรือ programme ไว้ตามเดิม (ถ้ามี)
      new_children.append(el)

  # แทนที่ลูกทั้งหมดใน root ทีเดียว (In-place update)
  root[:] = new_children

  # บันทึกไฟล์ผลลัพธ์
  try:
    tree.write(dst, encoding="UTF-8", xml_declaration=True)
  except Exception as e:
    print(f"Error writing output file: {e}")
    sys.exit(1)

  # สรุปผลการทำงาน
  ch_removed = total_channels - unique_channels
  pg_removed = total_programmes - unique_programmes
  print(f"Channels: {unique_channels} unique (removed {ch_removed} duplicates)")
  print(f"Programmes: {unique_programmes} unique (removed {pg_removed} duplicates)")


if __name__ == "__main__":
  main()
