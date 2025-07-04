#!/usr/bin/env python3
"""
批量修正所有map_image字段为/开头，保证前端可正常访问地图图片
"""
import sqlite3

def main():
    conn = sqlite3.connect('data/courts.db')
    cursor = conn.cursor()
    cursor.execute("SELECT id, map_image FROM court_details WHERE map_image IS NOT NULL AND map_image NOT LIKE '/%'")
    rows = cursor.fetchall()
    count = 0
    for detail_id, old_path in rows:
        if old_path and not old_path.startswith('/'):
            new_path = '/' + old_path
            cursor.execute("UPDATE court_details SET map_image=? WHERE id=?", (new_path, detail_id))
            count += 1
    conn.commit()
    conn.close()
    print(f'✅ 已修正{count}条map_image路径为/开头')

if __name__ == '__main__':
    main() 