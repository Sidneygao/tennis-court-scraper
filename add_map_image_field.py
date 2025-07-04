#!/usr/bin/env python3
"""
添加map_image字段到court_details表
"""

import sqlite3
import os
from pathlib import Path

def add_map_image_field():
    """添加map_image字段到court_details表"""
    
    # 数据库路径
    db_path = "data/courts.db"
    
    if not os.path.exists(db_path):
        print(f"❌ 数据库文件不存在: {db_path}")
        return False
    
    try:
        # 连接数据库
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 检查字段是否已存在
        cursor.execute("PRAGMA table_info(court_details)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'map_image' in columns:
            print("✅ map_image字段已存在")
            return True
        
        # 添加map_image字段
        cursor.execute("""
            ALTER TABLE court_details 
            ADD COLUMN map_image VARCHAR(500)
        """)
        
        # 提交更改
        conn.commit()
        print("✅ 成功添加map_image字段到court_details表")
        
        # 验证字段是否添加成功
        cursor.execute("PRAGMA table_info(court_details)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'map_image' in columns:
            print("✅ 字段添加验证成功")
            return True
        else:
            print("❌ 字段添加验证失败")
            return False
            
    except Exception as e:
        print(f"❌ 添加字段失败: {e}")
        return False
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    print("🔧 开始添加map_image字段...")
    success = add_map_image_field()
    if success:
        print("🎉 数据库更新完成！")
    else:
        print("💥 数据库更新失败！")

    # ====== 批量生成地图图片并写入字段 ======
    import sys
    sys.path.append(os.path.abspath(os.path.dirname(__file__)))
    from app.scrapers.map_generator import MapGenerator
    import json

    db_path = "data/courts.db"
    if not os.path.exists(db_path):
        print(f"❌ 数据库文件不存在: {db_path}")
        sys.exit(1)
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT court_id, id FROM court_details")
        detail_rows = cursor.fetchall()
        print(f"共{len(detail_rows)}条详情记录待处理...")
        # 获取场馆经纬度
        for court_id, detail_id in detail_rows:
            cursor.execute("SELECT latitude, longitude, name FROM tennis_courts WHERE id=?", (court_id,))
            row = cursor.fetchone()
            if not row:
                print(f"court_id={court_id} 无主表数据，跳过")
                continue
            lat, lng, name = row
            if not lat or not lng:
                print(f"court_id={court_id} 缺少经纬度，跳过")
                continue
            mg = MapGenerator()
            img_path = mg.generate_smart_map(name, lat, lng)
            if img_path:
                cursor.execute("UPDATE court_details SET map_image=? WHERE id=?", (img_path, detail_id))
                print(f"court_id={court_id} 地图生成并写入成功: {img_path}")
            else:
                print(f"court_id={court_id} 地图生成失败")
        conn.commit()
        conn.close()
        print("✅ 所有地图图片已批量生成并写入")
    except Exception as e:
        print(f"❌ 批量生成地图图片失败: {e}") 