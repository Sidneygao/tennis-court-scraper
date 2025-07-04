#!/usr/bin/env python3
"""
检查详情页地图显示问题
"""

import sqlite3
import os
import requests

def check_map_display():
    """检查详情页地图显示问题"""
    db_path = "data/courts.db"
    
    print("🗺️ 检查详情页地图显示问题...")
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 查询有地图图片的记录
        cursor.execute("SELECT court_id, map_image FROM court_details WHERE map_image IS NOT NULL LIMIT 5")
        rows = cursor.fetchall()
        
        print(f"📊 检查前5条地图记录:")
        
        for court_id, map_image in rows:
            print(f"\n--- 场馆ID: {court_id} ---")
            print(f"  数据库路径: {map_image}")
            
            # 检查路径格式
            if map_image and map_image.startswith('/data/map_cache/'):
                print(f"  ✅ 路径格式正确")
                
                # 检查文件是否存在
                file_path = map_image[1:]  # 去掉开头的斜杠
                if os.path.exists(file_path):
                    print(f"  ✅ 文件存在: {file_path}")
                    
                    # 检查文件大小
                    file_size = os.path.getsize(file_path)
                    print(f"  📏 文件大小: {file_size} 字节")
                    
                    # 测试HTTP访问
                    try:
                        url = f"http://127.0.0.1:8000{map_image}"
                        response = requests.get(url, timeout=5)
                        if response.status_code == 200:
                            print(f"  ✅ HTTP访问成功: {url}")
                        else:
                            print(f"  ❌ HTTP访问失败: {response.status_code}")
                    except Exception as e:
                        print(f"  ❌ HTTP访问异常: {e}")
                else:
                    print(f"  ❌ 文件不存在: {file_path}")
            else:
                print(f"  ❌ 路径格式错误: {map_image}")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ 检查失败: {e}")

if __name__ == "__main__":
    check_map_display() 