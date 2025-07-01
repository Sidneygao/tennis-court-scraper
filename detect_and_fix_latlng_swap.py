#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
极简通用经纬度倒置检测与修复脚本
用法：
  python detect_and_fix_latlng_swap.py dbfile tablename latfield lngfield [--fix]
示例：
  python detect_and_fix_latlng_swap.py data/courts.db tennis_courts latitude longitude --fix
"""
import sys
import sqlite3

def detect_and_fix(dbfile, tablename, latfield, lngfield, do_fix=False):
    conn = sqlite3.connect(dbfile)
    cursor = conn.cursor()
    # 检查倒置：纬度>90或<-90
    sql = f"SELECT id, {latfield}, {lngfield} FROM {tablename} WHERE ABS({latfield}) > 90"
    rows = cursor.execute(sql).fetchall()
    if not rows:
        print(f"✅ {dbfile} {tablename} 未发现经纬度倒置")
        return
    print(f"❌ {dbfile} {tablename} 检测到 {len(rows)} 条经纬度倒置：")
    for rid, lat, lng in rows:
        print(f"  id={rid}  {latfield}={lat}  {lngfield}={lng}  建议修复: {latfield}={lng}, {lngfield}={lat}")
    if do_fix:
        print("\n🔧 自动修复中...")
        for rid, lat, lng in rows:
            cursor.execute(f"UPDATE {tablename} SET {latfield}=?, {lngfield}=? WHERE id=?", (lng, lat, rid))
        conn.commit()
        print(f"✅ 已修复 {len(rows)} 条记录")
    conn.close()

if __name__ == "__main__":
    if len(sys.argv) < 5:
        print("用法: python detect_and_fix_latlng_swap.py dbfile tablename latfield lngfield [--fix]")
        sys.exit(1)
    dbfile, tablename, latfield, lngfield = sys.argv[1:5]
    do_fix = '--fix' in sys.argv
    detect_and_fix(dbfile, tablename, latfield, lngfield, do_fix) 