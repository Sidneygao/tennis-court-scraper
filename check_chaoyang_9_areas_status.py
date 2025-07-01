#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查朝阳区9个区域场馆状态
"""
import sqlite3
import json
from datetime import datetime

def check_chaoyang_9_areas():
    """检查朝阳区9个区域场馆状态"""
    print("🔍 检查朝阳区9个区域场馆状态...")
    
    conn = sqlite3.connect('tennis_courts.db')
    cursor = conn.cursor()
    
    # 朝阳区9个区域
    chaoyang_areas = {
        'guomao': '国贸CBD核心区',
        'sanlitun': '三里屯-工体时尚区', 
        'wangjing': '望京科技商务区',
        'aoyuncun': '奥运村-亚运村文体区',
        'chaoyangpark': '朝阳公园-蓝色港湾生态区',
        'dawanglu': '大望路-华贸商业区',
        'shuangjing': '双井-富力城居住区',
        'gaobeidian': '高碑店-传媒文化区',
        'dongba': '东坝-第四使馆区'
    }
    
    print("\n📊 朝阳区9个区域场馆统计:")
    total_count = 0
    
    for area_code, area_name in chaoyang_areas.items():
        cursor.execute("""
            SELECT COUNT(*) FROM tennis_courts WHERE area = ?
        """, (area_code,))
        count = cursor.fetchone()[0]
        total_count += count
        print(f"  {area_name}: {count} 个场馆")
    
    print(f"\n总计: {total_count} 个场馆")
    
    # 检查数据来源
    print("\n📋 数据来源统计:")
    cursor.execute("""
        SELECT data_source, COUNT(*) FROM tennis_courts 
        WHERE area IN (?, ?, ?, ?, ?, ?, ?, ?)
        GROUP BY data_source
    """, tuple(chaoyang_areas.keys()))
    
    sources = cursor.fetchall()
    for source, count in sources:
        print(f"  {source}: {count} 个场馆")
    
    # 检查三元桥区域的情况
    print("\n🔍 三元桥区域详细检查:")
    cursor.execute("""
        SELECT id, name, address, latitude, longitude, area, area_name, data_source
        FROM tennis_courts WHERE area = 'sanyuanqiao'
        LIMIT 10
    """)
    
    sanyuanqiao_courts = cursor.fetchall()
    print(f"三元桥区域场馆数量: {len(sanyuanqiao_courts)}")
    
    for court in sanyuanqiao_courts:
        print(f"  ID: {court[0]}, 名称: {court[1]}")
        print(f"    地址: {court[2]}")
        print(f"    坐标: {court[3]}, {court[4]}")
        print(f"    区域: {court[5]} ({court[6]})")
        print(f"    来源: {court[7]}")
        print()
    
    # 检查是否有场馆应该属于三元桥但被错误分配
    print("🔍 检查可能应该属于三元桥的场馆:")
    cursor.execute("""
        SELECT id, name, address, latitude, longitude, area, area_name, data_source
        FROM tennis_courts 
        WHERE (latitude BETWEEN 116.45 AND 116.47) 
        AND (longitude BETWEEN 39.96 AND 39.98)
        AND area != 'sanyuanqiao'
        LIMIT 10
    """)
    
    nearby_courts = cursor.fetchall()
    print(f"三元桥附近但不在三元桥区域的场馆: {len(nearby_courts)}")
    
    for court in nearby_courts:
        print(f"  ID: {court[0]}, 名称: {court[1]}")
        print(f"    地址: {court[2]}")
        print(f"    坐标: {court[3]}, {court[4]}")
        print(f"    当前区域: {court[5]} ({court[6]})")
        print(f"    来源: {court[7]}")
        print()
    
    conn.close()
    
    print("✅ 检查完成")

if __name__ == "__main__":
    check_chaoyang_9_areas() 