#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
恢复高德原始地理数据并修复经纬度倒置问题
"""
import json
import sqlite3
import sys
import os
from datetime import datetime

def main():
    print("🔄 开始恢复高德原始地理数据...")
    print(f"⏰ 开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 1. 读取高德原始数据
    print("\n📖 第一步：读取高德原始数据...")
    with open('real_courts_locations.json', 'r', encoding='utf-8') as f:
        amap_data = json.load(f)
    
    print(f"高德原始数据包含 {len(amap_data)} 个场馆")
    
    # 2. 修复经纬度倒置
    print("\n🔧 第二步：修复经纬度倒置...")
    fixed_data = []
    for court in amap_data:
        # 经纬度倒置：latitude和longitude字段内容互换
        fixed_court = {
            'court_id': court['court_id'],
            'name': court['name'],
            'latitude': court['longitude'],  # 原来的longitude值作为latitude
            'longitude': court['latitude']   # 原来的latitude值作为longitude
        }
        fixed_data.append(fixed_court)
    
    print(f"修复后数据包含 {len(fixed_data)} 个场馆")
    
    # 3. 验证修复结果
    print("\n✅ 第三步：验证修复结果...")
    sample_count = min(5, len(fixed_data))
    for i in range(sample_count):
        court = fixed_data[i]
        print(f"  {court['name']}: 经度{court['longitude']:.6f}, 纬度{court['latitude']:.6f}")
    
    # 4. 备份当前数据库
    print("\n💾 第四步：备份当前数据库...")
    if os.path.exists('data/courts.db'):
        backup_name = f"data/courts_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
        import shutil
        shutil.copy2('data/courts.db', backup_name)
        print(f"数据库已备份到: {backup_name}")
    
    # 5. 清空当前数据库并导入修复后的数据
    print("\n🗄️ 第五步：清空数据库并导入修复后的数据...")
    conn = sqlite3.connect('data/courts.db')
    cursor = conn.cursor()
    
    # 清空现有数据
    cursor.execute("DELETE FROM tennis_courts")
    cursor.execute("DELETE FROM court_details")
    
    # 重置自增ID（如果存在sqlite_sequence表）
    try:
        cursor.execute("DELETE FROM sqlite_sequence WHERE name='tennis_courts'")
        cursor.execute("DELETE FROM sqlite_sequence WHERE name='court_details'")
    except sqlite3.OperationalError:
        print("sqlite_sequence表不存在，跳过重置自增ID")
    
    # 导入修复后的数据
    for court in fixed_data:
        cursor.execute("""
            INSERT INTO tennis_courts (id, name, latitude, longitude, address, area, area_name, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            court['court_id'],
            court['name'],
            court['latitude'],
            court['longitude'],
            '',  # 地址暂时为空
            '未知',  # area默认未知
            '未知',  # area_name默认未知
            datetime.now(),
            datetime.now()
        ))
    
    conn.commit()
    conn.close()
    
    print(f"成功导入 {len(fixed_data)} 个场馆到数据库")
    
    # 6. 验证数据库导入结果
    print("\n🔍 第六步：验证数据库导入结果...")
    conn = sqlite3.connect('data/courts.db')
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM tennis_courts")
    total_count = cursor.fetchone()[0]
    print(f"数据库中共有 {total_count} 个场馆")
    
    # 检查经纬度范围
    cursor.execute("""
        SELECT MIN(longitude), MAX(longitude), MIN(latitude), MAX(latitude)
        FROM tennis_courts
    """)
    lon_min, lon_max, lat_min, lat_max = cursor.fetchone()
    print(f"经度范围: {lon_min:.6f} - {lon_max:.6f}")
    print(f"纬度范围: {lat_min:.6f} - {lat_max:.6f}")
    
    # 检查北京范围内的场馆数量
    cursor.execute("""
        SELECT COUNT(*) FROM tennis_courts 
        WHERE longitude BETWEEN 115.7 AND 117.4 
        AND latitude BETWEEN 39.4 AND 41.1
    """)
    beijing_count = cursor.fetchone()[0]
    print(f"北京范围内场馆: {beijing_count} 个")
    
    conn.close()
    
    print(f"\n✅ 高德原始地理数据恢复完成！")
    print(f"⏰ 完成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"📊 恢复场馆总数: {len(fixed_data)}")
    print(f"🗺️ 北京范围内场馆: {beijing_count}")

if __name__ == "__main__":
    main() 