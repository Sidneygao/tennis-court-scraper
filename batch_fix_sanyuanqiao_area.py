#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
批量修正三元桥区域分区归属
将高德API返回的三元桥5公里范围内的场馆，area字段批量归属为sanyuanqiao
并将原分区信息保留到original_area字段
"""
import sqlite3
import json
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
    print("🔧 开始批量修正三元桥区域分区归属...")
    
    # 三元桥中心坐标
    SANYUANQIAO_CENTER = (39.9589, 116.4567)  # 三元桥地铁站坐标
    RADIUS_KM = 5.0  # 5公里半径
    
    conn = sqlite3.connect('data/courts.db')
    cursor = conn.cursor()
    
    # 1. 添加original_area字段（如果不存在）
    print("\n📝 检查并添加original_area字段...")
    cursor.execute("PRAGMA table_info(tennis_courts)")
    columns = cursor.fetchall()
    has_original_area = any(col[1] == 'original_area' for col in columns)
    
    if not has_original_area:
        print("  ➕ 添加original_area字段...")
        cursor.execute("ALTER TABLE tennis_courts ADD COLUMN original_area VARCHAR(50)")
        print("  ✅ original_area字段添加成功")
    else:
        print("  ✅ original_area字段已存在")
    
    # 2. 获取所有场馆数据
    print("\n📊 获取所有场馆数据...")
    cursor.execute("""
        SELECT id, name, area, latitude, longitude 
        FROM tennis_courts 
        WHERE latitude IS NOT NULL AND longitude IS NOT NULL
    """)
    all_courts = cursor.fetchall()
    print(f"  📍 找到 {len(all_courts)} 个有坐标的场馆")
    
    # 3. 筛选三元桥5公里范围内的场馆
    print(f"\n🎯 筛选三元桥{RADIUS_KM}公里范围内的场馆...")
    sanyuanqiao_courts = []
    
    for court_id, name, current_area, lat, lng in all_courts:
        if lat and lng:
            distance = calculate_distance(lat, lng, SANYUANQIAO_CENTER[0], SANYUANQIAO_CENTER[1])
            if distance <= RADIUS_KM:
                sanyuanqiao_courts.append({
                    'id': court_id,
                    'name': name,
                    'current_area': current_area,
                    'distance': distance
                })
    
    print(f"  🎯 找到 {len(sanyuanqiao_courts)} 个三元桥{RADIUS_KM}公里范围内的场馆")
    
    # 4. 显示需要调整的场馆列表
    print("\n📋 需要调整分区归属的场馆列表:")
    for i, court in enumerate(sanyuanqiao_courts, 1):
        print(f"  {i:2d}. {court['name']} (当前: {court['current_area']}, 距离: {court['distance']:.1f}km)")
    
    # 5. 批量更新分区归属
    print(f"\n🔄 开始批量更新分区归属...")
    updated_count = 0
    
    for court in sanyuanqiao_courts:
        if court['current_area'] != 'sanyuanqiao':
            try:
                # 更新area为sanyuanqiao，original_area为原分区
                cursor.execute("""
                    UPDATE tennis_courts 
                    SET area = 'sanyuanqiao', 
                        original_area = ?,
                        updated_at = ?
                    WHERE id = ?
                """, (court['current_area'], datetime.now(), court['id']))
                
                updated_count += 1
                print(f"  ✅ {court['name']}: {court['current_area']} → sanyuanqiao")
                
            except Exception as e:
                print(f"  ❌ {court['name']}: 更新失败 - {e}")
    
    # 6. 提交更改
    conn.commit()
    
    # 7. 验证结果
    print(f"\n📊 更新结果验证:")
    cursor.execute("SELECT COUNT(*) FROM tennis_courts WHERE area = 'sanyuanqiao'")
    final_count = cursor.fetchone()[0]
    print(f"  🎯 三元桥区域场馆数: {final_count}")
    
    cursor.execute("SELECT COUNT(*) FROM tennis_courts WHERE original_area IS NOT NULL")
    original_area_count = cursor.fetchone()[0]
    print(f"  📝 有original_area记录的场馆数: {original_area_count}")
    
    # 8. 生成变更日志
    log_data = {
        'timestamp': datetime.now().isoformat(),
        'operation': 'batch_fix_sanyuanqiao_area',
        'sanyuanqiao_center': SANYUANQIAO_CENTER,
        'radius_km': RADIUS_KM,
        'total_courts_in_range': len(sanyuanqiao_courts),
        'updated_count': updated_count,
        'final_sanyuanqiao_count': final_count,
        'updated_courts': [
            {
                'id': court['id'],
                'name': court['name'],
                'old_area': court['current_area'],
                'new_area': 'sanyuanqiao',
                'distance': court['distance']
            }
            for court in sanyuanqiao_courts if court['current_area'] != 'sanyuanqiao'
        ]
    }
    
    log_filename = f"sanyuanqiao_area_fix_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(log_filename, 'w', encoding='utf-8') as f:
        json.dump(log_data, f, ensure_ascii=False, indent=2)
    
    print(f"\n📄 变更日志已保存到: {log_filename}")
    
    conn.close()
    
    print(f"\n🎉 批量修正完成!")
    print(f"   📍 三元桥{RADIUS_KM}公里范围内场馆: {len(sanyuanqiao_courts)} 个")
    print(f"   🔄 实际更新场馆: {updated_count} 个")
    print(f"   🎯 最终三元桥区域场馆数: {final_count} 个")

if __name__ == "__main__":
    main() 