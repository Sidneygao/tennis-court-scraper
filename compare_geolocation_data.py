#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
比较地理信息：下载高德新数据与现有数据对比
"""
import json
import sqlite3
import requests
import time
from collections import defaultdict
import os

def get_amap_geocode(address, name):
    """从高德API获取地理编码"""
    try:
        # 使用高德API进行地理编码
        url = "https://restapi.amap.com/v3/geocode/geo"
        params = {
            'key': 'your_amap_key',  # 需要替换为实际的API key
            'address': f"{name} {address}",
            'city': '北京'
        }
        
        response = requests.get(url, params=params, timeout=10)
        data = response.json()
        
        if data['status'] == '1' and data['geocodes']:
            location = data['geocodes'][0]['location'].split(',')
            return {
                'longitude': float(location[0]),
                'latitude': float(location[1]),
                'formatted_address': data['geocodes'][0]['formatted_address'],
                'level': data['geocodes'][0]['level']
            }
        else:
            return None
    except Exception as e:
        print(f"获取地理编码失败: {e}")
        return None

def create_comparison_database():
    """创建对比数据库"""
    conn = sqlite3.connect('data/geolocation_comparison.db')
    cursor = conn.cursor()
    
    # 创建对比表
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS geolocation_comparison (
            id INTEGER PRIMARY KEY,
            court_id INTEGER,
            name TEXT,
            address TEXT,
            current_longitude REAL,
            current_latitude REAL,
            amap_longitude REAL,
            amap_latitude REAL,
            amap_address TEXT,
            amap_level TEXT,
            distance_diff REAL,
            status TEXT
        )
    """)
    
    conn.commit()
    return conn

def load_existing_data():
    """加载现有数据"""
    conn = sqlite3.connect('data/courts.db')
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT id, name, address, longitude, latitude
        FROM tennis_courts
        WHERE longitude IS NOT NULL AND latitude IS NOT NULL
        ORDER BY id
    """)
    
    existing_data = cursor.fetchall()
    conn.close()
    
    return existing_data

def calculate_distance(lat1, lon1, lat2, lon2):
    """计算两点间距离（米）"""
    from math import radians, cos, sin, asin, sqrt
    
    # 转换为弧度
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    
    # 计算差值
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    
    # 使用Haversine公式
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a))
    r = 6371000  # 地球半径（米）
    
    return c * r

def main():
    print("🔍 开始地理信息对比分析...")
    
    # 1. 创建对比数据库
    print("\n📊 创建对比数据库...")
    comp_conn = create_comparison_database()
    comp_cursor = comp_conn.cursor()
    
    # 2. 加载现有数据
    print("📥 加载现有数据...")
    existing_data = load_existing_data()
    print(f"找到 {len(existing_data)} 个场馆的现有地理数据")
    
    # 3. 检查是否有高德API key
    amap_key = os.getenv('AMAP_KEY')
    if not amap_key:
        print("⚠️  警告: 未找到高德API key，将使用模拟数据进行对比")
        print("请设置环境变量 AMAP_KEY 来获取真实的高德数据")
        
        # 使用模拟数据进行演示
        for i, (court_id, name, address, curr_lon, curr_lat) in enumerate(existing_data[:10]):
            # 模拟高德返回的数据（稍微偏移一点）
            amap_lon = curr_lon + 0.001 * (i % 3 - 1)  # 随机偏移
            amap_lat = curr_lat + 0.001 * (i % 3 - 1)
            
            distance = calculate_distance(curr_lat, curr_lon, amap_lat, amap_lon)
            
            comp_cursor.execute("""
                INSERT INTO geolocation_comparison 
                (court_id, name, address, current_longitude, current_latitude,
                 amap_longitude, amap_latitude, amap_address, amap_level, 
                 distance_diff, status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (court_id, name, address, curr_lon, curr_lat, 
                  amap_lon, amap_lat, f"模拟地址_{i}", "POI", distance, "模拟数据"))
        
        comp_conn.commit()
        
        # 分析结果
        comp_cursor.execute("""
            SELECT 
                COUNT(*) as total,
                AVG(distance_diff) as avg_distance,
                MAX(distance_diff) as max_distance,
                MIN(distance_diff) as min_distance,
                SUM(CASE WHEN distance_diff > 1000 THEN 1 ELSE 0 END) as large_diff_count
            FROM geolocation_comparison
        """)
        
        stats = comp_cursor.fetchone()
        print(f"\n📈 对比结果统计:")
        print(f"  总场馆数: {stats[0]}")
        print(f"  平均距离差: {stats[1]:.2f} 米")
        print(f"  最大距离差: {stats[2]:.2f} 米")
        print(f"  最小距离差: {stats[3]:.2f} 米")
        print(f"  距离差>1km的场馆: {stats[4]} 个")
        
        # 显示具体差异
        comp_cursor.execute("""
            SELECT name, current_longitude, current_latitude, 
                   amap_longitude, amap_latitude, distance_diff
            FROM geolocation_comparison
            ORDER BY distance_diff DESC
            LIMIT 10
        """)
        
        print(f"\n🔍 距离差异最大的10个场馆:")
        for row in comp_cursor.fetchall():
            name, curr_lon, curr_lat, amap_lon, amap_lat, distance = row
            print(f"  {name}: {distance:.2f}米")
            print(f"    现有: ({curr_lon:.6f}, {curr_lat:.6f})")
            print(f"    高德: ({amap_lon:.6f}, {amap_lat:.6f})")
        
        comp_conn.close()
        return
    
    # 4. 如果有API key，获取真实的高德数据
    print("🌐 开始获取高德地理编码数据...")
    
    for i, (court_id, name, address, curr_lon, curr_lat) in enumerate(existing_data):
        print(f"处理 {i+1}/{len(existing_data)}: {name}")
        
        # 获取高德地理编码
        amap_result = get_amap_geocode(address, name)
        
        if amap_result:
            distance = calculate_distance(curr_lat, curr_lon, 
                                       amap_result['latitude'], amap_result['longitude'])
            
            comp_cursor.execute("""
                INSERT INTO geolocation_comparison 
                (court_id, name, address, current_longitude, current_latitude,
                 amap_longitude, amap_latitude, amap_address, amap_level, 
                 distance_diff, status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (court_id, name, address, curr_lon, curr_lat, 
                  amap_result['longitude'], amap_result['latitude'], 
                  amap_result['formatted_address'], amap_result['level'], 
                  distance, "成功"))
        else:
            comp_cursor.execute("""
                INSERT INTO geolocation_comparison 
                (court_id, name, address, current_longitude, current_latitude,
                 amap_longitude, amap_latitude, amap_address, amap_level, 
                 distance_diff, status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (court_id, name, address, curr_lon, curr_lat, 
                  None, None, None, None, None, "获取失败"))
        
        # 避免API调用过于频繁
        time.sleep(0.1)
        
        if (i + 1) % 10 == 0:
            comp_conn.commit()
            print(f"已处理 {i+1} 个场馆...")
    
    comp_conn.commit()
    
    # 5. 分析结果
    comp_cursor.execute("""
        SELECT 
            COUNT(*) as total,
            SUM(CASE WHEN status = '成功' THEN 1 ELSE 0 END) as success_count,
            SUM(CASE WHEN status = '获取失败' THEN 1 ELSE 0 END) as fail_count,
            AVG(distance_diff) as avg_distance,
            MAX(distance_diff) as max_distance,
            MIN(distance_diff) as min_distance,
            SUM(CASE WHEN distance_diff > 1000 THEN 1 ELSE 0 END) as large_diff_count
        FROM geolocation_comparison
        WHERE status = '成功'
    """)
    
    stats = comp_cursor.fetchone()
    print(f"\n📈 对比结果统计:")
    print(f"  总场馆数: {stats[0]}")
    print(f"  成功获取: {stats[1]}")
    print(f"  获取失败: {stats[2]}")
    print(f"  平均距离差: {stats[3]:.2f} 米")
    print(f"  最大距离差: {stats[4]:.2f} 米")
    print(f"  最小距离差: {stats[5]:.2f} 米")
    print(f"  距离差>1km的场馆: {stats[6]} 个")
    
    # 显示具体差异
    comp_cursor.execute("""
        SELECT name, current_longitude, current_latitude, 
               amap_longitude, amap_latitude, distance_diff
        FROM geolocation_comparison
        WHERE status = '成功'
        ORDER BY distance_diff DESC
        LIMIT 10
    """)
    
    print(f"\n🔍 距离差异最大的10个场馆:")
    for row in comp_cursor.fetchall():
        name, curr_lon, curr_lat, amap_lon, amap_lat, distance = row
        print(f"  {name}: {distance:.2f}米")
        print(f"    现有: ({curr_lon:.6f}, {curr_lat:.6f})")
        print(f"    高德: ({amap_lon:.6f}, {amap_lat:.6f})")
    
    comp_conn.close()
    print(f"\n✅ 对比完成！结果保存在 data/geolocation_comparison.db")

if __name__ == "__main__":
    main() 