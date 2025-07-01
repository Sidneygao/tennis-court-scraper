#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查丰台和亦庄区域分配情况
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

def check_fengtai_yizhuang():
    """检查丰台和亦庄区域"""
    print("🔍 检查丰台和亦庄区域分配...")
    
    # 区域中心点
    fengtai_east_center = (116.321, 39.858)
    fengtai_west_center = (116.247, 39.858)
    yizhuang_center = (116.493, 39.808)
    
    conn = sqlite3.connect('data/courts.db')
    cursor = conn.cursor()
    
    # 获取所有场馆
    cursor.execute("""
        SELECT id, name, address, latitude, longitude, area 
        FROM tennis_courts 
        WHERE latitude IS NOT NULL AND longitude IS NOT NULL
    """)
    courts = cursor.fetchall()
    
    print(f"总场馆数: {len(courts)}")
    
    # 检查丰台东部
    print("\n📊 丰台东部区域检查:")
    fengtai_east_courts = []
    for court_id, name, address, lat, lng, area in courts:
        dist = haversine(lng, lat, fengtai_east_center[0], fengtai_east_center[1])
        if dist <= 8000:  # 8公里内
            fengtai_east_courts.append((court_id, name, address, lat, lng, area, dist))
    
    print(f"丰台东部8公里内场馆数: {len(fengtai_east_courts)}")
    
    # 检查丰台西部
    print("\n📊 丰台西部区域检查:")
    fengtai_west_courts = []
    for court_id, name, address, lat, lng, area in courts:
        dist = haversine(lng, lat, fengtai_west_center[0], fengtai_west_center[1])
        if dist <= 8000:  # 8公里内
            fengtai_west_courts.append((court_id, name, address, lat, lng, area, dist))
    
    print(f"丰台西部8公里内场馆数: {len(fengtai_west_courts)}")
    
    # 检查亦庄
    print("\n📊 亦庄区域检查:")
    yizhuang_courts = []
    for court_id, name, address, lat, lng, area in courts:
        dist = haversine(lng, lat, yizhuang_center[0], yizhuang_center[1])
        if dist <= 8000:  # 8公里内
            yizhuang_courts.append((court_id, name, address, lat, lng, area, dist))
    
    print(f"亦庄8公里内场馆数: {len(yizhuang_courts)}")
    
    # 检查当前分配情况
    print("\n📋 当前分配情况:")
    cursor.execute("SELECT area, COUNT(*) FROM tennis_courts WHERE area IN ('fengtai_east', 'fengtai_west', 'yizhuang') GROUP BY area")
    current_assignments = cursor.fetchall()
    for area, count in current_assignments:
        print(f"  {area}: {count} 个场馆")
    
    # 调试最近的几个场馆
    print("\n🔍 调试最近的场馆:")
    
    # 丰台东部最近的场馆
    if fengtai_east_courts:
        print("\n丰台东部最近的场馆:")
        for i, (court_id, name, address, lat, lng, area, dist) in enumerate(sorted(fengtai_east_courts, key=lambda x: x[6])[:3]):
            print(f"  {i+1}. {name}")
            print(f"     地址: {address}")
            print(f"     坐标: {lat}, {lng}")
            print(f"     当前区域: {area}")
            print(f"     距离丰台东部: {dist:.0f}米")
            
            assigned_area, all_distances = assign_area_for_court(lat, lng)
            print(f"     应该分配区域: {assigned_area}")
            print()
    
    # 丰台西部最近的场馆
    if fengtai_west_courts:
        print("\n丰台西部最近的场馆:")
        for i, (court_id, name, address, lat, lng, area, dist) in enumerate(sorted(fengtai_west_courts, key=lambda x: x[6])[:3]):
            print(f"  {i+1}. {name}")
            print(f"     地址: {address}")
            print(f"     坐标: {lat}, {lng}")
            print(f"     当前区域: {area}")
            print(f"     距离丰台西部: {dist:.0f}米")
            
            assigned_area, all_distances = assign_area_for_court(lat, lng)
            print(f"     应该分配区域: {assigned_area}")
            print()
    
    # 亦庄最近的场馆
    if yizhuang_courts:
        print("\n亦庄最近的场馆:")
        for i, (court_id, name, address, lat, lng, area, dist) in enumerate(sorted(yizhuang_courts, key=lambda x: x[6])[:3]):
            print(f"  {i+1}. {name}")
            print(f"     地址: {address}")
            print(f"     坐标: {lat}, {lng}")
            print(f"     当前区域: {area}")
            print(f"     距离亦庄: {dist:.0f}米")
            
            assigned_area, all_distances = assign_area_for_court(lat, lng)
            print(f"     应该分配区域: {assigned_area}")
            print()
    
    conn.close()

if __name__ == "__main__":
    check_fengtai_yizhuang() 