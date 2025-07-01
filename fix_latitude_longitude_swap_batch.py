#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
批量修复数据库中经纬度倒置问题
将所有场馆的latitude和longitude进行交换
"""
import sqlite3
from datetime import datetime

def main():
    print("🔧 批量修复数据库中经纬度倒置问题...")
    print("=" * 60)
    
    conn = sqlite3.connect('data/courts.db')
    cursor = conn.cursor()
    
    # 1. 检查修复前的数据
    print("\n📊 修复前数据检查:")
    cursor.execute("""
        SELECT COUNT(*) as total_courts,
               SUM(CASE WHEN latitude IS NOT NULL AND longitude IS NOT NULL THEN 1 ELSE 0 END) as has_coords
        FROM tennis_courts
    """)
    
    stats = cursor.fetchone()
    total_courts = stats[0]
    has_coords = stats[1]
    
    print(f"  总场馆数: {total_courts}")
    print(f"  有经纬度: {has_coords}")
    
    # 2. 显示修复前的样本数据
    print("\n📋 修复前样本数据:")
    cursor.execute("""
        SELECT id, name, latitude, longitude
        FROM tennis_courts
        WHERE latitude IS NOT NULL AND longitude IS NOT NULL
        ORDER BY id
        LIMIT 5
    """)
    
    sample_courts = cursor.fetchall()
    for court_id, name, lat, lng in sample_courts:
        print(f"  ID {court_id}: {name}")
        print(f"    修复前: 纬度={lat}, 经度={lng}")
        print(f"    修复后: 纬度={lng}, 经度={lat}")
    
    # 3. 确认修复操作
    print(f"\n⚠️  即将修复 {has_coords} 个场馆的经纬度数据")
    print("   此操作将交换所有场馆的latitude和longitude字段")
    
    # 4. 执行批量修复
    print(f"\n🔧 开始批量修复...")
    
    # 交换latitude和longitude
    cursor.execute("""
        UPDATE tennis_courts 
        SET latitude = longitude, 
            longitude = latitude,
            updated_at = ?
        WHERE latitude IS NOT NULL AND longitude IS NOT NULL
    """, (datetime.now(),))
    
    updated_count = cursor.rowcount
    print(f"✅ 已修复 {updated_count} 个场馆的经纬度数据")
    
    # 5. 验证修复结果
    print("\n📊 修复后数据验证:")
    cursor.execute("""
        SELECT id, name, latitude, longitude
        FROM tennis_courts
        WHERE latitude IS NOT NULL AND longitude IS NOT NULL
        ORDER BY id
        LIMIT 5
    """)
    
    fixed_courts = cursor.fetchall()
    for court_id, name, lat, lng in fixed_courts:
        print(f"  ID {court_id}: {name}")
        print(f"    修复后: 纬度={lat}, 经度={lng}")
        
        # 检查是否在北京范围内
        if 39.4 <= lat <= 41.1 and 115.7 <= lng <= 117.4:
            print(f"    ✅ 坐标在北京范围内")
        else:
            print(f"    ⚠️  坐标可能不在北京范围内")
    
    # 6. 检查各区域的场馆分布
    print("\n🗺️  修复后各区域场馆分布:")
    
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
    
    # 7. 检查是否还有异常坐标
    print("\n🔍 检查修复后是否还有异常坐标:")
    
    # 检查纬度超过90度的记录
    cursor.execute("""
        SELECT COUNT(*)
        FROM tennis_courts
        WHERE latitude IS NOT NULL AND longitude IS NOT NULL
        AND (latitude > 90 OR latitude < -90)
    """)
    
    invalid_lat_count = cursor.fetchone()[0]
    print(f"  纬度超过90度的记录: {invalid_lat_count} 个")
    
    # 检查经度超过180度的记录
    cursor.execute("""
        SELECT COUNT(*)
        FROM tennis_courts
        WHERE latitude IS NOT NULL AND longitude IS NOT NULL
        AND (longitude > 180 OR longitude < -180)
    """)
    
    invalid_lng_count = cursor.fetchone()[0]
    print(f"  经度超过180度的记录: {invalid_lng_count} 个")
    
    # 检查零值坐标
    cursor.execute("""
        SELECT COUNT(*)
        FROM tennis_courts
        WHERE latitude IS NOT NULL AND longitude IS NOT NULL
        AND (ABS(latitude) < 0.001 OR ABS(longitude) < 0.001)
    """)
    
    zero_coords_count = cursor.fetchone()[0]
    print(f"  零值或接近零值的坐标: {zero_coords_count} 个")
    
    # 8. 提交更改
    conn.commit()
    
    # 9. 生成修复日志
    log_data = {
        'timestamp': datetime.now().isoformat(),
        'operation': 'batch_fix_latitude_longitude_swap',
        'total_courts': total_courts,
        'updated_count': updated_count,
        'invalid_latitude_after': invalid_lat_count,
        'invalid_longitude_after': invalid_lng_count,
        'zero_coords_after': zero_coords_count,
        'sample_fixed_courts': [
            {
                'id': court_id,
                'name': name,
                'latitude': lat,
                'longitude': lng
            }
            for court_id, name, lat, lng in fixed_courts
        ]
    }
    
    import json
    log_filename = f"latitude_longitude_swap_fix_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(log_filename, 'w', encoding='utf-8') as f:
        json.dump(log_data, f, ensure_ascii=False, indent=2)
    
    print(f"\n📄 修复日志已保存到: {log_filename}")
    
    conn.close()
    
    print(f"\n🎉 批量修复完成!")
    print(f"   📊 总场馆数: {total_courts}")
    print(f"   🔄 已修复场馆: {updated_count} 个")
    print(f"   ❌ 修复后异常坐标: {invalid_lat_count + invalid_lng_count} 个")
    print(f"   📋 零值坐标: {zero_coords_count} 个")
    
    if invalid_lat_count + invalid_lng_count == 0 and zero_coords_count == 0:
        print(f"   ✅ 所有坐标数据已修复完成!")
    else:
        print(f"   ⚠️  仍有部分坐标需要进一步检查")

if __name__ == "__main__":
    main() 