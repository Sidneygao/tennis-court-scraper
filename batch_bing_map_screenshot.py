#!/usr/bin/env python3
"""
批量为三元桥区域所有场馆生成Bing地图截图，并写入数据库
"""
import os
import sqlite3
import subprocess
from pathlib import Path

BING_SHOT_SCRIPT = 'selenium_bing_map_screenshot.py'
DB_PATH = 'data/courts.db'
MAP_CACHE = 'data/map_cache'
ZOOM = 16  # 可调整，地铁/公交站建议14-17

os.makedirs(MAP_CACHE, exist_ok=True)

def is_valid_image(path):
    return os.path.exists(path) and os.path.getsize(path) > 1024

def main():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    # 查询所有场馆，join tennis_courts获取名称和坐标
    cursor.execute("""
        SELECT cd.court_id, tc.name, tc.latitude, tc.longitude
        FROM court_details cd
        JOIN tennis_courts tc ON cd.court_id = tc.id
        WHERE tc.latitude IS NOT NULL AND tc.longitude IS NOT NULL
    """)
    courts = cursor.fetchall()
    print(f"共{len(courts)}个场馆")
    for court_id, name, lat, lng in courts:
        if not lat or not lng:
            print(f"跳过无坐标: {name}")
            continue
        safe_name = name.replace('/', '_').replace(' ', '_')
        out_file = f"{MAP_CACHE}/{safe_name}_{lat}_{lng}_bing.png"
        # 强制覆盖：无论图片是否存在都重新生成
        print(f"生成: {name} ({lat},{lng}) -> {out_file}")
        # 调用截图脚本
        cmd = [
            'python', BING_SHOT_SCRIPT,
            str(lat), str(lng), str(ZOOM), out_file
        ]
        try:
            subprocess.run(cmd, check=True)
        except Exception as e:
            print(f"截图失败: {e}")
            continue
        if is_valid_image(out_file):
            # 写入数据库
            cursor.execute(
                "UPDATE court_details SET map_image=? WHERE court_id=?",
                (out_file, court_id)
            )
            conn.commit()
            print(f"✅ 已写入数据库: {out_file}")
        else:
            print(f"❌ 截图无效: {out_file}")
    conn.close()
    print("全部完成！")

if __name__ == '__main__':
    main() 