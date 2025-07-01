#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
调试区域分配逻辑
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

def assign_area_for_court(lat, lng):
    """区域分配逻辑"""
    area_defs = {
        'guomao':      (116.468, 39.914, 5000),
        'sanlitun':    (116.453, 39.933, 5000),
        'wangjing':    (116.4828, 39.9968, 5000),
        'aoyuncun':    (116.396, 40.008, 5000),
        'chaoyangpark':(116.478, 39.946, 5000),
        'dawanglu':    (116.489, 39.914, 5000),
        'shuangjing':  (116.468, 39.894, 5000),
        'gaobeidian':  (116.525, 39.908, 5000),
        'dongba':      (116.5607, 39.9582, 5000),
        'changying':   (116.601, 39.933, 5000),
        'sanyuanqiao': (116.456, 39.967, 5000),
        'fengtai_east':(116.321, 39.858, 8000),
        'fengtai_west':(116.247, 39.858, 8000),
        'yizhuang':    (116.493, 39.808, 8000),
    }
    
    min_dist = float('inf')
    best_area = None
    all_distances = []
    
    for area, (center_lng, center_lat, radius) in area_defs.items():
        dist = haversine(lng, lat, center_lng, center_lat)
        all_distances.append((area, dist, radius, dist < radius))
        if dist < radius and dist < min_dist:
            min_dist = dist
            best_area = area
    
    return best_area, all_distances

def debug_sanyuanqiao():
    """调试三元桥区域分配"""
    print("🔍 调试三元桥区域分配...")
    
    # 三元桥中心点
    sanyuanqiao_center = (116.456, 39.967)
    
    conn = sqlite3.connect('data/courts.db')
    cursor = conn.cursor()
    
    # 获取三元桥附近的场馆
    cursor.execute("""
        SELECT id, name, address, latitude, longitude, area 
        FROM tennis_courts 
        WHERE latitude IS NOT NULL AND longitude IS NOT NULL
    """)
    courts = cursor.fetchall()
    
    # 检查最近的几个场馆
    nearby_courts = []
    for court_id, name, address, lat, lng, area in courts:
        dist = haversine(lng, lat, sanyuanqiao_center[0], sanyuanqiao_center[1])
        if dist <= 2000:  # 2公里内
            nearby_courts.append((court_id, name, address, lat, lng, area, dist))
    
    print(f"三元桥2公里内场馆数: {len(nearby_courts)}")
    
    # 调试前5个最近的场馆
    for i, (court_id, name, address, lat, lng, area, dist) in enumerate(sorted(nearby_courts, key=lambda x: x[6])[:5]):
        print(f"\n{i+1}. {name}")
        print(f"   地址: {address}")
        print(f"   坐标: {lat}, {lng}")
        print(f"   当前区域: {area}")
        print(f"   距离三元桥: {dist:.0f}米")
        
        # 计算到所有区域的距离
        assigned_area, all_distances = assign_area_for_court(lat, lng)
        print(f"   应该分配区域: {assigned_area}")
        print(f"   到各区域距离:")
        for area_name, distance, radius, in_range in sorted(all_distances, key=lambda x: x[1]):
            status = "✅" if in_range else "❌"
            print(f"     {area_name}: {distance:.0f}m (半径{radius}m) {status}")
    
    conn.close()

if __name__ == "__main__":
    debug_sanyuanqiao() 