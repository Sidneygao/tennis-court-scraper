#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查之前9个区域的经纬度数据是否有问题
"""
import sqlite3
from collections import defaultdict

def main():
    print("🔍 检查之前9个区域的经纬度数据...")
    
    conn = sqlite3.connect('data/courts.db')
    cursor = conn.cursor()
    
    # 定义9个老区域
    old_areas = {
        'guomao': '国贸CBD核心区',
        'sanyuanqiao': '三元桥-太阳宫国际生活区', 
        'wangjing': '望京科技商务区',
        'aoyuncun': '奥运村-亚运村文体区',
        'chaoyanggongyuan': '朝阳公园-蓝色港湾生态区',
        'dawanglu': '大望路-华贸商业区',
        'shuangjing': '双井-富力城居住区',
        'gaobeidian': '高碑店-传媒文化区',
        'dongba': '东坝-第四使馆区',
        'changying': '常营-东坝边缘居住区'
    }
    
    print("\n📊 检查各区域场馆数量和经纬度问题:")
    
    total_courts = 0
    total_wrong_coords = 0
    
    for area_code, area_name in old_areas.items():
        # 根据区域代码查询场馆
        if area_code == 'guomao':
            # 国贸CBD核心区：经度 116.4-116.5，纬度 39.9-40.0
            cursor.execute("""
                SELECT id, name, latitude, longitude
                FROM tennis_courts
                WHERE longitude BETWEEN 116.4 AND 116.5 
                AND latitude BETWEEN 39.9 AND 40.0
                AND (name LIKE '%国贸%' OR name LIKE '%CBD%' OR name LIKE '%建外%' OR name LIKE '%永安里%')
            """)
        elif area_code == 'sanyuanqiao':
            # 三元桥-太阳宫国际生活区：经度 116.4-116.5，纬度 39.9-40.0
            cursor.execute("""
                SELECT id, name, latitude, longitude
                FROM tennis_courts
                WHERE longitude BETWEEN 116.4 AND 116.5 
                AND latitude BETWEEN 39.9 AND 40.0
                AND (name LIKE '%三元桥%' OR name LIKE '%太阳宫%' OR name LIKE '%朝阳门%' OR name LIKE '%东直门%')
            """)
        elif area_code == 'wangjing':
            # 望京科技商务区：经度 116.4-116.5，纬度 39.9-40.0
            cursor.execute("""
                SELECT id, name, latitude, longitude
                FROM tennis_courts
                WHERE longitude BETWEEN 116.4 AND 116.5 
                AND latitude BETWEEN 39.9 AND 40.0
                AND (name LIKE '%望京%' OR name LIKE '%酒仙桥%' OR name LIKE '%大山子%')
            """)
        elif area_code == 'aoyuncun':
            # 奥运村-亚运村文体区：经度 116.3-116.4，纬度 40.0-40.1
            cursor.execute("""
                SELECT id, name, latitude, longitude
                FROM tennis_courts
                WHERE longitude BETWEEN 116.3 AND 116.4 
                AND latitude BETWEEN 40.0 AND 40.1
                AND (name LIKE '%奥运%' OR name LIKE '%亚运%' OR name LIKE '%安立路%' OR name LIKE '%慧忠路%')
            """)
        elif area_code == 'chaoyanggongyuan':
            # 朝阳公园-蓝色港湾生态区：经度 116.4-116.5，纬度 39.9-40.0
            cursor.execute("""
                SELECT id, name, latitude, longitude
                FROM tennis_courts
                WHERE longitude BETWEEN 116.4 AND 116.5 
                AND latitude BETWEEN 39.9 AND 40.0
                AND (name LIKE '%朝阳公园%' OR name LIKE '%蓝色港湾%' OR name LIKE '%亮马桥%')
            """)
        elif area_code == 'dawanglu':
            # 大望路-华贸商业区：经度 116.4-116.5，纬度 39.9-40.0
            cursor.execute("""
                SELECT id, name, latitude, longitude
                FROM tennis_courts
                WHERE longitude BETWEEN 116.4 AND 116.5 
                AND latitude BETWEEN 39.9 AND 40.0
                AND (name LIKE '%大望路%' OR name LIKE '%华贸%' OR name LIKE '%百子湾%')
            """)
        elif area_code == 'shuangjing':
            # 双井-富力城居住区：经度 116.4-116.5，纬度 39.8-39.9
            cursor.execute("""
                SELECT id, name, latitude, longitude
                FROM tennis_courts
                WHERE longitude BETWEEN 116.4 AND 116.5 
                AND latitude BETWEEN 39.8 AND 39.9
                AND (name LIKE '%双井%' OR name LIKE '%富力%' OR name LIKE '%劲松%')
            """)
        elif area_code == 'gaobeidian':
            # 高碑店-传媒文化区：经度 116.5-116.6，纬度 39.8-39.9
            cursor.execute("""
                SELECT id, name, latitude, longitude
                FROM tennis_courts
                WHERE longitude BETWEEN 116.5 AND 116.6 
                AND latitude BETWEEN 39.8 AND 39.9
                AND (name LIKE '%高碑店%' OR name LIKE '%传媒%' OR name LIKE '%定福庄%')
            """)
        elif area_code == 'dongba':
            # 东坝-第四使馆区：经度 116.5-116.6，纬度 39.9-40.0
            cursor.execute("""
                SELECT id, name, latitude, longitude
                FROM tennis_courts
                WHERE longitude BETWEEN 116.5 AND 116.6 
                AND latitude BETWEEN 39.9 AND 40.0
                AND (name LIKE '%东坝%' OR name LIKE '%使馆%' OR name LIKE '%亮马桥%')
            """)
        elif area_code == 'changying':
            # 常营-东坝边缘居住区：经度 116.5-116.6，纬度 39.9-40.0
            cursor.execute("""
                SELECT id, name, latitude, longitude
                FROM tennis_courts
                WHERE longitude BETWEEN 116.5 AND 116.6 
                AND latitude BETWEEN 39.9 AND 40.0
                AND (name LIKE '%常营%' OR name LIKE '%管庄%' OR name LIKE '%双桥%')
            """)
        
        courts = cursor.fetchall()
        wrong_coords = []
        
        for court_id, name, lat, lng in courts:
            # 检查经纬度是否在合理范围内
            if not (39.4 <= lat <= 41.1 and 115.7 <= lng <= 117.4):
                wrong_coords.append((court_id, name, lat, lng))
        
        total_courts += len(courts)
        total_wrong_coords += len(wrong_coords)
        
        print(f"\n🏢 {area_name}:")
        print(f"  场馆数: {len(courts)}")
        print(f"  经纬度错误: {len(wrong_coords)}")
        
        if wrong_coords:
            print(f"  错误场馆:")
            for court_id, name, lat, lng in wrong_coords:
                print(f"    ID {court_id}: {name} - 坐标({lat}, {lng})")
    
    print(f"\n📈 总体统计:")
    print(f"  总场馆数: {total_courts}")
    print(f"  经纬度错误总数: {total_wrong_coords}")
    print(f"  错误率: {total_wrong_coords/total_courts*100:.1f}%" if total_courts > 0 else "错误率: 0%")
    
    # 检查所有场馆的经纬度分布
    print(f"\n🔍 检查所有场馆的经纬度分布:")
    cursor.execute("""
        SELECT 
            COUNT(*) as total,
            SUM(CASE WHEN latitude < 39.4 OR latitude > 41.1 OR longitude < 115.7 OR longitude > 117.4 THEN 1 ELSE 0 END) as out_of_range,
            SUM(CASE WHEN latitude IS NULL OR longitude IS NULL THEN 1 ELSE 0 END) as null_coords
        FROM tennis_courts
    """)
    
    stats = cursor.fetchone()
    print(f"  总场馆数: {stats[0]}")
    print(f"  超出北京范围: {stats[1]}")
    print(f"  经纬度为NULL: {stats[2]}")
    
    # 检查经纬度互换问题
    print(f"\n🔍 检查经纬度互换问题:")
    cursor.execute("""
        SELECT id, name, latitude, longitude
        FROM tennis_courts
        WHERE (latitude BETWEEN 115.7 AND 117.4) AND (longitude BETWEEN 39.4 AND 41.1)
        AND latitude IS NOT NULL AND longitude IS NOT NULL
        ORDER BY id
    """)
    
    swapped_coords = cursor.fetchall()
    print(f"  疑似经纬度互换的场馆: {len(swapped_coords)}")
    
    if swapped_coords:
        print(f"  前10个疑似互换的场馆:")
        for i, (court_id, name, lat, lng) in enumerate(swapped_coords[:10]):
            print(f"    {i+1}. ID {court_id}: {name} - 坐标({lat}, {lng})")
    
    conn.close()
    print(f"\n✅ 检查完成！")

if __name__ == "__main__":
    main() 