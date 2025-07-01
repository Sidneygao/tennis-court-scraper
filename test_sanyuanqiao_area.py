#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试三元桥区域场馆分布
"""
import sqlite3
from math import radians, cos, sin, sqrt, atan2

def haversine(lon1, lat1, lon2, lat2):
    """计算两点间距离，单位米"""
    R = 6371000
    phi1, phi2 = radians(lat1), radians(lat2)
    dphi = radians(lat2 - lat1)
    dlambda = radians(lon2 - lon1)
    a = sin(dphi/2)**2 + cos(phi1)*cos(phi2)*sin(dlambda/2)**2
    return 2*R*atan2(sqrt(a), sqrt(1-a))

def test_sanyuanqiao():
    """测试三元桥区域"""
    print("🔍 测试三元桥区域场馆分布...")
    
    # 三元桥中心点
    sanyuanqiao_center = (116.456, 39.967)
    radius = 5000  # 5公里
    
    conn = sqlite3.connect('data/courts.db')
    cursor = conn.cursor()
    
    # 获取所有场馆
    cursor.execute("SELECT id, name, address, latitude, longitude, area FROM tennis_courts")
    courts = cursor.fetchall()
    
    print(f"总场馆数: {len(courts)}")
    
    # 检查三元桥附近的场馆
    nearby_courts = []
    for court_id, name, address, lat, lng, area in courts:
        if lat is None or lng is None:
            continue
            
        dist = haversine(lng, lat, sanyuanqiao_center[0], sanyuanqiao_center[1])
        if dist <= radius:
            nearby_courts.append({
                'id': court_id,
                'name': name,
                'address': address,
                'lat': lat,
                'lng': lng,
                'area': area,
                'distance': dist
            })
    
    print(f"\n三元桥5公里范围内场馆数: {len(nearby_courts)}")
    
    if nearby_courts:
        print("\n三元桥附近的场馆:")
        for court in sorted(nearby_courts, key=lambda x: x['distance']):
            print(f"  {court['name']}")
            print(f"    地址: {court['address']}")
            print(f"    坐标: {court['lat']}, {court['lng']}")
            print(f"    当前区域: {court['area']}")
            print(f"    距离三元桥: {court['distance']:.0f}米")
            print()
    else:
        print("❌ 三元桥5公里范围内没有找到场馆")
        
        # 检查最近的场馆
        print("\n检查最近的场馆:")
        all_distances = []
        for court_id, name, address, lat, lng, area in courts:
            if lat is None or lng is None:
                continue
            dist = haversine(lng, lat, sanyuanqiao_center[0], sanyuanqiao_center[1])
            all_distances.append((name, address, lat, lng, area, dist))
        
        # 显示最近的10个场馆
        nearest = sorted(all_distances, key=lambda x: x[5])[:10]
        for name, address, lat, lng, area, dist in nearest:
            print(f"  {name}")
            print(f"    地址: {address}")
            print(f"    坐标: {lat}, {lng}")
            print(f"    当前区域: {area}")
            print(f"    距离三元桥: {dist:.0f}米")
            print()
    
    conn.close()

if __name__ == "__main__":
    test_sanyuanqiao() 