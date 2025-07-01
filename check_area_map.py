#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
导出所有场馆的area字段和名称
"""
import sqlite3

def main():
    conn = sqlite3.connect('data/courts.db')
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, area FROM tennis_courts ORDER BY area, name")
    rows = cursor.fetchall()
    area_map = {}
    for cid, name, area in rows:
        if area not in area_map:
            area_map[area] = []
        area_map[area].append(name)
    for area, names in area_map.items():
        print(f"区域: {area}  场馆数: {len(names)}")
        for n in names[:3]:
            print(f"  - {n}")
        if len(names) > 3:
            print(f"  ... 共{len(names)}家")
        print()
    print(f"共{len(area_map)}个不同area字段")

if __name__ == "__main__":
    main() 