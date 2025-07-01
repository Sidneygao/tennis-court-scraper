#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
从new_areas_cache.json中提取高德场馆数据，修复经纬度倒置，并更新到数据库
"""
import json
import sqlite3
import sys
import os
from datetime import datetime
import re

def main():
    print("🔄 开始从new_areas_cache.json恢复高德场馆数据...")
    print(f"⏰ 开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 1. 读取new_areas_cache.json数据
    print("\n📖 第一步：读取new_areas_cache.json数据...")
    with open('data/new_areas_cache.json', 'r', encoding='utf-8') as f:
        cache_data = json.load(f)
    
    # 2. 提取场馆数据并修复经纬度倒置
    print("\n🔧 第二步：提取场馆数据并修复经纬度倒置...")
    courts_data = []
    
    # 处理丰台区数据
    for court_str in cache_data['amap_data']['fengtai']:
        court = parse_court_string(court_str)
        if court:
            courts_data.append(court)
    
    # 处理亦庄区数据
    for court_str in cache_data['amap_data']['yizhuang']:
        court = parse_court_string(court_str)
        if court:
            courts_data.append(court)
    
    print(f"提取到 {len(courts_data)} 个场馆数据")
    
    # 3. 检查经纬度倒置并修复
    print("\n🔧 第三步：检查并修复经纬度倒置...")
    fixed_count = 0
    for court in courts_data:
        if is_coordinate_swapped(court['latitude'], court['longitude']):
            # 经纬度倒置，需要互换
            court['latitude'], court['longitude'] = court['longitude'], court['latitude']
            fixed_count += 1
    
    print(f"修复了 {fixed_count} 个场馆的经纬度倒置")
    
    # 4. 更新数据库
    print("\n🗄️ 第四步：更新数据库...")
    conn = sqlite3.connect('data/courts.db')
    cursor = conn.cursor()
    
    updated_count = 0
    for court in courts_data:
        try:
            # 检查场馆是否已存在
            cursor.execute("SELECT id FROM tennis_courts WHERE name = ?", (court['name'],))
            existing = cursor.fetchone()
            
            if existing:
                # 更新现有场馆的经纬度
                cursor.execute("""
                    UPDATE tennis_courts 
                    SET latitude = ?, longitude = ?, address = ?, updated_at = ?
                    WHERE name = ?
                """, (
                    court['latitude'],
                    court['longitude'],
                    court['address'],
                    datetime.now(),
                    court['name']
                ))
                updated_count += 1
            else:
                # 插入新场馆
                cursor.execute("""
                    INSERT INTO tennis_courts (name, latitude, longitude, address, area, area_name, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    court['name'],
                    court['latitude'],
                    court['longitude'],
                    court['address'],
                    '未知',
                    '未知',
                    datetime.now(),
                    datetime.now()
                ))
                updated_count += 1
                
        except Exception as e:
            print(f"处理场馆 {court['name']} 时出错: {e}")
            continue
    
    conn.commit()
    conn.close()
    
    print(f"成功更新/插入 {updated_count} 个场馆")
    
    # 5. 检查结果
    print("\n🔍 第五步：检查更新结果...")
    conn = sqlite3.connect('data/courts.db')
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM tennis_courts")
    total_count = cursor.fetchone()[0]
    conn.close()
    
    print(f"数据库总场馆数: {total_count}")
    
    print(f"\n✅ 高德场馆数据恢复完成！")
    print(f"⏰ 完成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

def parse_court_string(court_str):
    """解析场馆字符串，提取场馆信息"""
    try:
        # 使用正则表达式提取信息
        name_match = re.search(r"name='([^']*)'", court_str)
        address_match = re.search(r"address='([^']*)'", court_str)
        latitude_match = re.search(r"latitude=([\d.]+)", court_str)
        longitude_match = re.search(r"longitude=([\d.]+)", court_str)
        
        if name_match and latitude_match and longitude_match:
            return {
                'name': name_match.group(1),
                'address': address_match.group(1) if address_match else '',
                'latitude': float(latitude_match.group(1)),
                'longitude': float(longitude_match.group(1))
            }
    except Exception as e:
        print(f"解析场馆字符串时出错: {e}")
    
    return None

def is_coordinate_swapped(lat, lng):
    """检查经纬度是否倒置"""
    # 北京地区：经度应该在115-118之间，纬度应该在39-42之间
    # 如果经度小于100或纬度大于100，说明可能倒置了
    return lng < 100 or lat > 100

if __name__ == "__main__":
    main() 