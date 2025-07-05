#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
导出场馆数据为JSON格式
"""

import json
from app.database import get_db, init_db
from app.models import TennisCourt

def export_courts_data():
    """导出场馆数据"""
    print("导出场馆数据...")
    
    # 初始化数据库
    init_db()
    
    # 获取数据库会话
    db = next(get_db())
    
    # 查询所有场馆
    courts = db.query(TennisCourt).all()
    print(f"查询到 {len(courts)} 个场馆")
    
    # 转换为字典格式
    courts_data = []
    for court in courts:
        court_dict = {
            "name": court.name,
            "address": court.address,
            "area": court.area,
            "area_name": court.area_name,
            "court_type": court.court_type,
            "phone": court.phone,
            "latitude": court.latitude,
            "longitude": court.longitude,
            "data_source": court.data_source,
            "created_at": court.created_at.isoformat() if court.created_at else None,
            "updated_at": court.updated_at.isoformat() if court.updated_at else None
        }
        courts_data.append(court_dict)
    
    # 保存到JSON文件
    output_file = "courts_data.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(courts_data, f, ensure_ascii=False, indent=2)
    
    print(f"导出完成: {len(courts_data)} 个场馆")
    print(f"数据文件: {output_file}")
    
    # 显示统计信息
    areas = {}
    for court in courts_data:
        area = court.get('area') or '未知'
        if area not in areas:
            areas[area] = 0
        areas[area] += 1
    
    print("\n按区域统计:")
    for area, count in sorted(areas.items()):
        print(f"  {area}: {count} 个场馆")

if __name__ == "__main__":
    export_courts_data() 