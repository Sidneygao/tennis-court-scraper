#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查数据库中所有场馆的实际分布情况
"""
import sqlite3
from collections import defaultdict

def main():
    print("🔍 检查数据库中所有场馆的实际分布...")
    
    conn = sqlite3.connect('data/courts.db')
    cursor = conn.cursor()
    
    # 1. 基本统计
    print("\n📊 基本统计:")
    cursor.execute("SELECT COUNT(*) FROM tennis_courts")
    total = cursor.fetchone()[0]
    print(f"  总场馆数: {total}")
    
    # 2. 检查经纬度范围分布
    print("\n🌍 经纬度范围分布:")
    cursor.execute("""
        SELECT 
            COUNT(*) as total,
            MIN(latitude) as min_lat,
            MAX(latitude) as max_lat,
            MIN(longitude) as min_lng,
            MAX(longitude) as max_lng
        FROM tennis_courts
        WHERE latitude IS NOT NULL AND longitude IS NOT NULL
    """)
    
    coords_stats = cursor.fetchone()
    print(f"  有经纬度的场馆: {coords_stats[0]}")
    print(f"  纬度范围: {coords_stats[1]:.6f} ~ {coords_stats[2]:.6f}")
    print(f"  经度范围: {coords_stats[3]:.6f} ~ {coords_stats[4]:.6f}")
    
    # 3. 按经纬度范围分组统计
    print("\n📈 按经纬度范围分组:")
    
    # 检查是否所有场馆都在丰台区和亦庄范围内
    cursor.execute("""
        SELECT 
            COUNT(*) as total,
            SUM(CASE WHEN longitude > 116.321 AND address LIKE '%丰台%' THEN 1 ELSE 0 END) as fengtai_east,
            SUM(CASE WHEN longitude <= 116.321 AND address LIKE '%丰台%' THEN 1 ELSE 0 END) as fengtai_west,
            SUM(CASE WHEN address LIKE '%亦庄%' THEN 1 ELSE 0 END) as yizhuang,
            SUM(CASE WHEN address NOT LIKE '%丰台%' AND address NOT LIKE '%亦庄%' THEN 1 ELSE 0 END) as other_areas
        FROM tennis_courts
    """)
    
    area_stats = cursor.fetchone()
    print(f"  丰台区东部: {area_stats[1]} 个")
    print(f"  丰台区西部: {area_stats[2]} 个")
    print(f"  亦庄: {area_stats[3]} 个")
    print(f"  其他区域: {area_stats[4]} 个")
    
    # 4. 检查场馆名称和地址
    print("\n🏟️ 场馆名称和地址样本:")
    cursor.execute("""
        SELECT id, name, address, latitude, longitude
        FROM tennis_courts
        ORDER BY id
        LIMIT 10
    """)
    
    samples = cursor.fetchall()
    for court_id, name, address, lat, lng in samples:
        print(f"  ID {court_id}: {name}")
        print(f"    地址: {address}")
        print(f"    坐标: ({lat}, {lng})")
        print()
    
    # 5. 检查是否有其他区域的场馆
    print("\n🔍 检查其他区域的场馆:")
    cursor.execute("""
        SELECT id, name, address, latitude, longitude
        FROM tennis_courts
        WHERE address NOT LIKE '%丰台%' AND address NOT LIKE '%亦庄%'
        ORDER BY id
        LIMIT 10
    """)
    
    other_areas = cursor.fetchall()
    print(f"  其他区域场馆数: {len(other_areas)}")
    
    for court_id, name, address, lat, lng in other_areas:
        print(f"  ID {court_id}: {name} - {address} - ({lat}, {lng})")
    
    # 6. 检查经纬度是否都在合理范围内
    print("\n✅ 检查经纬度合理性:")
    cursor.execute("""
        SELECT 
            COUNT(*) as total,
            SUM(CASE WHEN latitude < 39.4 OR latitude > 41.1 OR longitude < 115.7 OR longitude > 117.4 THEN 1 ELSE 0 END) as out_of_range,
            SUM(CASE WHEN latitude BETWEEN 39.4 AND 41.1 AND longitude BETWEEN 115.7 AND 117.4 THEN 1 ELSE 0 END) as in_range
        FROM tennis_courts
        WHERE latitude IS NOT NULL AND longitude IS NOT NULL
    """)
    
    range_stats = cursor.fetchone()
    print(f"  总场馆数: {range_stats[0]}")
    print(f"  超出北京范围: {range_stats[1]}")
    print(f"  在合理范围内: {range_stats[2]}")
    
    conn.close()
    print(f"\n✅ 检查完成！")

if __name__ == "__main__":
    main() 