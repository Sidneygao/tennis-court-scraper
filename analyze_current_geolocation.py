#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
分析现有经纬度数据分布和异常情况
"""
import sqlite3
from collections import defaultdict

def main():
    print("🔍 分析现有经纬度数据分布...")
    
    conn = sqlite3.connect('data/courts.db')
    cursor = conn.cursor()
    
    # 1. 基本统计
    cursor.execute("""
        SELECT 
            COUNT(*) as total_courts,
            SUM(CASE WHEN longitude IS NOT NULL AND latitude IS NOT NULL THEN 1 ELSE 0 END) as has_coords,
            SUM(CASE WHEN longitude IS NULL OR latitude IS NULL THEN 1 ELSE 0 END) as missing_coords
        FROM tennis_courts
    """)
    
    basic_stats = cursor.fetchone()
    print(f"\n📊 基本统计:")
    print(f"  总场馆数: {basic_stats[0]}")
    print(f"  有经纬度: {basic_stats[1]}")
    print(f"  缺失经纬度: {basic_stats[2]}")
    
    # 2. 经纬度范围分析
    cursor.execute("""
        SELECT 
            MIN(longitude) as min_lon,
            MAX(longitude) as max_lon,
            MIN(latitude) as min_lat,
            MAX(latitude) as max_lat,
            AVG(longitude) as avg_lon,
            AVG(latitude) as avg_lat
        FROM tennis_courts
        WHERE longitude IS NOT NULL AND latitude IS NOT NULL
    """)
    
    range_stats = cursor.fetchone()
    print(f"\n🌍 经纬度范围:")
    print(f"  经度范围: {range_stats[0]:.6f} ~ {range_stats[1]:.6f}")
    print(f"  纬度范围: {range_stats[2]:.6f} ~ {range_stats[3]:.6f}")
    print(f"  平均经度: {range_stats[4]:.6f}")
    print(f"  平均纬度: {range_stats[5]:.6f}")
    
    # 3. 检查异常值（北京范围外的数据）
    cursor.execute("""
        SELECT id, name, longitude, latitude
        FROM tennis_courts
        WHERE longitude IS NOT NULL AND latitude IS NOT NULL
        AND (longitude < 115 OR longitude > 118 OR latitude < 39 OR latitude > 42)
        ORDER BY id
    """)
    
    abnormal_courts = cursor.fetchall()
    print(f"\n⚠️  北京范围外的异常数据 ({len(abnormal_courts)} 个):")
    for court in abnormal_courts:
        print(f"  ID: {court[0]}, 名称: {court[1]}")
        print(f"    经纬度: ({court[2]:.6f}, {court[3]:.6f})")
    
    # 4. 检查经纬度互换的情况
    cursor.execute("""
        SELECT id, name, longitude, latitude
        FROM tennis_courts
        WHERE longitude IS NOT NULL AND latitude IS NOT NULL
        AND (longitude BETWEEN 39 AND 42 AND latitude BETWEEN 115 AND 118)
        ORDER BY id
    """)
    
    swapped_courts = cursor.fetchall()
    print(f"\n🔄 疑似经纬度互换的数据 ({len(swapped_courts)} 个):")
    for court in swapped_courts:
        print(f"  ID: {court[0]}, 名称: {court[1]}")
        print(f"    当前: ({court[2]:.6f}, {court[3]:.6f})")
        print(f"    正确: ({court[3]:.6f}, {court[2]:.6f})")
    
    # 5. 检查重复的经纬度
    cursor.execute("""
        SELECT longitude, latitude, COUNT(*) as count
        FROM tennis_courts
        WHERE longitude IS NOT NULL AND latitude IS NOT NULL
        GROUP BY longitude, latitude
        HAVING COUNT(*) > 1
        ORDER BY count DESC
    """)
    
    duplicate_coords = cursor.fetchall()
    print(f"\n📋 重复的经纬度组合 ({len(duplicate_coords)} 组):")
    for coord in duplicate_coords:
        print(f"  ({coord[0]:.6f}, {coord[1]:.6f}): {coord[2]} 个场馆")
        
        # 显示具体场馆
        cursor.execute("""
            SELECT id, name
            FROM tennis_courts
            WHERE longitude = ? AND latitude = ?
            ORDER BY id
        """, (coord[0], coord[1]))
        
        courts = cursor.fetchall()
        for court in courts:
            print(f"    - ID: {court[0]}, 名称: {court[1]}")
    
    # 6. 检查零值或接近零值
    cursor.execute("""
        SELECT id, name, longitude, latitude
        FROM tennis_courts
        WHERE longitude IS NOT NULL AND latitude IS NOT NULL
        AND (ABS(longitude) < 0.001 OR ABS(latitude) < 0.001)
        ORDER BY id
    """)
    
    zero_coords = cursor.fetchall()
    print(f"\n❌ 零值或接近零值的经纬度 ({len(zero_coords)} 个):")
    for court in zero_coords:
        print(f"  ID: {court[0]}, 名称: {court[1]}")
        print(f"    经纬度: ({court[2]:.6f}, {court[3]:.6f})")
    
    # 7. 统计各区域的场馆数量
    cursor.execute("""
        SELECT 
            SUM(CASE WHEN longitude BETWEEN 116.0 AND 116.5 AND latitude BETWEEN 39.8 AND 40.0 THEN 1 ELSE 0 END) as fengtai_east,
            SUM(CASE WHEN longitude BETWEEN 116.2 AND 116.7 AND latitude BETWEEN 39.8 AND 40.0 THEN 1 ELSE 0 END) as fengtai_west,
            SUM(CASE WHEN longitude BETWEEN 116.4 AND 116.9 AND latitude BETWEEN 39.7 AND 39.9 THEN 1 ELSE 0 END) as yizhuang
        FROM tennis_courts
        WHERE longitude IS NOT NULL AND latitude IS NOT NULL
    """)
    
    area_stats = cursor.fetchone()
    print(f"\n🗺️  各区域场馆数量:")
    print(f"  丰台东部: {area_stats[0]} 个")
    print(f"  丰台西部: {area_stats[1]} 个")
    print(f"  亦庄: {area_stats[2]} 个")
    
    conn.close()

if __name__ == "__main__":
    main() 