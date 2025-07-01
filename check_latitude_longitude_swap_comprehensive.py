#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
全面检查数据库中经纬度倒置问题
使用合理性原则：纬度不可能超过90度
"""
import sqlite3
import math
from datetime import datetime

def calculate_distance(lat1, lng1, lat2, lng2):
    """计算两点间距离（公里）"""
    R = 6371  # 地球半径（公里）
    
    lat1, lng1, lat2, lng2 = map(math.radians, [lat1, lng1, lat2, lng2])
    dlat = lat2 - lat1
    dlng = lng2 - lng1
    
    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlng/2)**2
    c = 2 * math.asin(math.sqrt(a))
    
    return R * c

def main():
    print("🔍 全面检查数据库中经纬度倒置问题...")
    print("=" * 60)
    
    conn = sqlite3.connect('data/courts.db')
    cursor = conn.cursor()
    
    # 1. 基本统计
    print("\n📊 基本数据统计:")
    cursor.execute("""
        SELECT 
            COUNT(*) as total_courts,
            SUM(CASE WHEN latitude IS NOT NULL AND longitude IS NOT NULL THEN 1 ELSE 0 END) as has_coords,
            SUM(CASE WHEN latitude IS NULL OR longitude IS NULL THEN 1 ELSE 0 END) as missing_coords
        FROM tennis_courts
    """)
    
    basic_stats = cursor.fetchone()
    print(f"  总场馆数: {basic_stats[0]}")
    print(f"  有经纬度: {basic_stats[1]}")
    print(f"  缺失经纬度: {basic_stats[2]}")
    
    # 2. 检查纬度超过90度的记录（绝对错误）
    print("\n❌ 检查纬度超过90度的记录（绝对错误）:")
    cursor.execute("""
        SELECT id, name, latitude, longitude
        FROM tennis_courts
        WHERE latitude IS NOT NULL AND longitude IS NOT NULL
        AND (latitude > 90 OR latitude < -90)
        ORDER BY id
    """)
    
    invalid_lat_courts = cursor.fetchall()
    print(f"  找到 {len(invalid_lat_courts)} 个纬度超过90度的记录:")
    
    for court_id, name, lat, lng in invalid_lat_courts:
        print(f"    ID {court_id}: {name}")
        print(f"      错误坐标: ({lat}, {lng})")
        print(f"      正确坐标: ({lng}, {lat})")
    
    # 3. 检查经度超过180度的记录（绝对错误）
    print("\n❌ 检查经度超过180度的记录（绝对错误）:")
    cursor.execute("""
        SELECT id, name, latitude, longitude
        FROM tennis_courts
        WHERE latitude IS NOT NULL AND longitude IS NOT NULL
        AND (longitude > 180 OR longitude < -180)
        ORDER BY id
    """)
    
    invalid_lng_courts = cursor.fetchall()
    print(f"  找到 {len(invalid_lng_courts)} 个经度超过180度的记录:")
    
    for court_id, name, lat, lng in invalid_lng_courts:
        print(f"    ID {court_id}: {name}")
        print(f"      错误坐标: ({lat}, {lng})")
        print(f"      正确坐标: ({lng}, {lat})")
    
    # 4. 检查疑似经纬度倒置的记录（北京地区合理性检查）
    print("\n🔄 检查疑似经纬度倒置的记录（北京地区合理性检查）:")
    
    # 北京地区的合理范围：
    # 纬度: 39.4 ~ 41.1
    # 经度: 115.7 ~ 117.4
    
    cursor.execute("""
        SELECT id, name, latitude, longitude
        FROM tennis_courts
        WHERE latitude IS NOT NULL AND longitude IS NOT NULL
        AND (
            -- 当前坐标不在北京范围内，但交换后可能在范围内
            (latitude BETWEEN 115.7 AND 117.4 AND longitude BETWEEN 39.4 AND 41.1)
            OR
            -- 当前坐标完全超出合理范围
            (latitude < 39.4 OR latitude > 41.1 OR longitude < 115.7 OR longitude > 117.4)
        )
        ORDER BY id
    """)
    
    suspected_swap_courts = cursor.fetchall()
    print(f"  找到 {len(suspected_swap_courts)} 个疑似经纬度倒置的记录:")
    
    definitely_swapped = []
    possibly_swapped = []
    
    for court_id, name, lat, lng in suspected_swap_courts:
        # 检查交换后的坐标是否在北京范围内
        swapped_lat, swapped_lng = lng, lat
        
        is_current_in_beijing = (39.4 <= lat <= 41.1 and 115.7 <= lng <= 117.4)
        is_swapped_in_beijing = (39.4 <= swapped_lat <= 41.1 and 115.7 <= swapped_lng <= 117.4)
        
        print(f"    ID {court_id}: {name}")
        print(f"      当前坐标: ({lat}, {lng})")
        print(f"      交换后坐标: ({swapped_lat}, {swapped_lng})")
        
        if is_current_in_beijing and not is_swapped_in_beijing:
            print(f"      ✅ 当前坐标在北京范围内，无需交换")
        elif not is_current_in_beijing and is_swapped_in_beijing:
            print(f"      🔄 交换后坐标在北京范围内，建议交换")
            definitely_swapped.append((court_id, name, lat, lng, swapped_lat, swapped_lng))
        elif not is_current_in_beijing and not is_swapped_in_beijing:
            print(f"      ⚠️  交换前后都不在北京范围内，需要进一步检查")
            possibly_swapped.append((court_id, name, lat, lng, swapped_lat, swapped_lng))
        else:
            print(f"      ✅ 当前坐标在北京范围内，无需交换")
    
    # 5. 检查零值或接近零值的坐标
    print("\n❌ 检查零值或接近零值的坐标:")
    cursor.execute("""
        SELECT id, name, latitude, longitude
        FROM tennis_courts
        WHERE latitude IS NOT NULL AND longitude IS NOT NULL
        AND (ABS(latitude) < 0.001 OR ABS(longitude) < 0.001)
        ORDER BY id
    """)
    
    zero_coords = cursor.fetchall()
    print(f"  找到 {len(zero_coords)} 个零值或接近零值的坐标:")
    
    for court_id, name, lat, lng in zero_coords:
        print(f"    ID {court_id}: {name}")
        print(f"      坐标: ({lat}, {lng})")
    
    # 6. 检查重复的坐标组合
    print("\n📋 检查重复的坐标组合:")
    cursor.execute("""
        SELECT latitude, longitude, COUNT(*) as count, GROUP_CONCAT(id) as ids
        FROM tennis_courts
        WHERE latitude IS NOT NULL AND longitude IS NOT NULL
        GROUP BY latitude, longitude
        HAVING COUNT(*) > 1
        ORDER BY count DESC
    """)
    
    duplicate_coords = cursor.fetchall()
    print(f"  找到 {len(duplicate_coords)} 组重复的坐标:")
    
    for lat, lng, count, ids in duplicate_coords:
        id_list = [int(x) for x in ids.split(',')]
        print(f"    坐标 ({lat}, {lng}): {count} 个场馆")
        print(f"      场馆ID: {id_list}")
        
        # 显示具体场馆名称
        cursor.execute("""
            SELECT id, name
            FROM tennis_courts
            WHERE id IN ({})
            ORDER BY id
        """.format(','.join(map(str, id_list))))
        
        courts = cursor.fetchall()
        for court_id, name in courts:
            print(f"        - ID {court_id}: {name}")
    
    # 7. 统计各区域的场馆分布
    print("\n🗺️  检查各区域的场馆分布:")
    
    # 定义主要区域范围
    areas = {
        '朝阳区': {'lat_min': 39.8, 'lat_max': 40.1, 'lng_min': 116.3, 'lng_max': 116.7},
        '丰台区': {'lat_min': 39.8, 'lat_max': 40.0, 'lng_min': 116.0, 'lng_max': 116.5},
        '海淀区': {'lat_min': 39.9, 'lat_max': 40.1, 'lng_min': 116.2, 'lng_max': 116.4},
        '西城区': {'lat_min': 39.9, 'lat_max': 40.0, 'lng_min': 116.3, 'lng_max': 116.4},
        '东城区': {'lat_min': 39.9, 'lat_max': 40.0, 'lng_min': 116.4, 'lng_max': 116.5},
        '亦庄': {'lat_min': 39.7, 'lat_max': 39.9, 'lng_min': 116.4, 'lng_max': 116.9}
    }
    
    for area_name, bounds in areas.items():
        cursor.execute("""
            SELECT COUNT(*)
            FROM tennis_courts
            WHERE latitude IS NOT NULL AND longitude IS NOT NULL
            AND latitude BETWEEN ? AND ?
            AND longitude BETWEEN ? AND ?
        """, (bounds['lat_min'], bounds['lat_max'], bounds['lng_min'], bounds['lng_max']))
        
        count = cursor.fetchone()[0]
        print(f"  {area_name}: {count} 个场馆")
    
    # 8. 生成修复建议
    print("\n🔧 修复建议:")
    print("=" * 60)
    
    if invalid_lat_courts or invalid_lng_courts:
        print("❌ 发现绝对错误的坐标（纬度>90度或经度>180度）:")
        print("   这些记录必须修复，建议交换经纬度")
    
    if definitely_swapped:
        print(f"\n🔄 发现 {len(definitely_swapped)} 个确定需要交换经纬度的记录:")
        for court_id, name, lat, lng, swapped_lat, swapped_lng in definitely_swapped:
            print(f"    ID {court_id}: {name}")
            print(f"      当前: ({lat}, {lng}) → 修复后: ({swapped_lat}, {swapped_lng})")
    
    if possibly_swapped:
        print(f"\n⚠️  发现 {len(possibly_swapped)} 个需要进一步检查的记录:")
        for court_id, name, lat, lng, swapped_lat, swapped_lng in possibly_swapped:
            print(f"    ID {court_id}: {name}")
            print(f"      当前: ({lat}, {lng})")
            print(f"      交换后: ({swapped_lat}, {swapped_lng})")
    
    if zero_coords:
        print(f"\n❌ 发现 {len(zero_coords)} 个零值坐标，需要重新获取")
    
    # 9. 生成修复SQL语句
    if definitely_swapped:
        print(f"\n📝 修复SQL语句:")
        print("-- 交换经纬度")
        for court_id, name, lat, lng, swapped_lat, swapped_lng in definitely_swapped:
            print(f"UPDATE tennis_courts SET latitude = {swapped_lat}, longitude = {swapped_lng} WHERE id = {court_id}; -- {name}")
    
    # 10. 保存检查结果
    result_data = {
        'timestamp': datetime.now().isoformat(),
        'total_courts': basic_stats[0],
        'has_coords': basic_stats[1],
        'missing_coords': basic_stats[2],
        'invalid_latitude_count': len(invalid_lat_courts),
        'invalid_longitude_count': len(invalid_lng_courts),
        'definitely_swapped': len(definitely_swapped),
        'possibly_swapped': len(possibly_swapped),
        'zero_coords_count': len(zero_coords),
        'duplicate_coords_count': len(duplicate_coords),
        'definitely_swapped_courts': [
            {
                'id': court_id,
                'name': name,
                'current_lat': lat,
                'current_lng': lng,
                'correct_lat': swapped_lat,
                'correct_lng': swapped_lng
            }
            for court_id, name, lat, lng, swapped_lat, swapped_lng in definitely_swapped
        ],
        'possibly_swapped_courts': [
            {
                'id': court_id,
                'name': name,
                'current_lat': lat,
                'current_lng': lng,
                'swapped_lat': swapped_lat,
                'swapped_lng': swapped_lng
            }
            for court_id, name, lat, lng, swapped_lat, swapped_lng in possibly_swapped
        ]
    }
    
    import json
    result_file = f'latitude_longitude_swap_check_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
    with open(result_file, 'w', encoding='utf-8') as f:
        json.dump(result_data, f, ensure_ascii=False, indent=2)
    
    print(f"\n📄 检查结果已保存到: {result_file}")
    
    conn.close()
    
    print(f"\n✅ 全面检查完成!")
    print(f"   📊 总场馆数: {basic_stats[0]}")
    print(f"   ❌ 绝对错误坐标: {len(invalid_lat_courts) + len(invalid_lng_courts)} 个")
    print(f"   🔄 确定需要交换: {len(definitely_swapped)} 个")
    print(f"   ⚠️  需要进一步检查: {len(possibly_swapped)} 个")
    print(f"   📋 重复坐标组合: {len(duplicate_coords)} 组")

if __name__ == "__main__":
    main() 