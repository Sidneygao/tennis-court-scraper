#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
统计各area场馆数量，并查找created_at为None的记录，输出三区域相关数据
"""
import sqlite3
from collections import Counter

def main():
    conn = sqlite3.connect('data/courts.db')
    cursor = conn.cursor()

    print("\n📊 各area场馆数量:")
    cursor.execute("SELECT area FROM tennis_courts")
    areas = [row[0] for row in cursor.fetchall()]
    area_count = Counter(areas)
    for area, count in area_count.items():
        print(f"  {area}: {count}")

    print("\n🔍 created_at为None的记录:")
    cursor.execute("SELECT id, name, area FROM tennis_courts WHERE created_at IS NULL")
    rows = cursor.fetchall()
    if not rows:
        print("  无")
    else:
        for r in rows:
            print(f"  id={r[0]}, name={r[1]}, area={r[2]}")

    print("\n🟦 fengtai_east 场馆:")
    cursor.execute("SELECT id, name, created_at FROM tennis_courts WHERE area='fengtai_east'")
    for row in cursor.fetchall():
        print(row)

    print("\n🟧 fengtai_west 场馆:")
    cursor.execute("SELECT id, name, created_at FROM tennis_courts WHERE area='fengtai_west'")
    for row in cursor.fetchall():
        print(row)

    print("\n🟩 yizhuang 场馆:")
    cursor.execute("SELECT id, name, created_at FROM tennis_courts WHERE area='yizhuang'")
    for row in cursor.fetchall():
        print(row)

    conn.close()

if __name__ == "__main__":
    main() 