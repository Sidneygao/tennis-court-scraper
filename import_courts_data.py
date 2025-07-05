#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
导入场馆数据到数据库
"""

import json
from datetime import datetime
from app.database import get_db, init_db
from app.models import TennisCourt

def import_courts_data():
    """导入场馆数据"""
    print("导入场馆数据...")
    
    # 检查数据文件是否存在
    data_file = "courts_data.json"
    try:
        with open(data_file, 'r', encoding='utf-8') as f:
            courts_data = json.load(f)
    except FileNotFoundError:
        print(f"❌ 数据文件 {data_file} 不存在")
        return
    except Exception as e:
        print(f"❌ 读取数据文件失败: {e}")
        return
    
    print(f"读取到 {len(courts_data)} 个场馆数据")
    
    # 初始化数据库
    init_db()
    
    # 获取数据库会话
    db = next(get_db())
    
    # 检查数据库是否已有数据
    existing_count = db.query(TennisCourt).count()
    if existing_count > 0:
        print(f"⚠️ 数据库已有 {existing_count} 个场馆")
        response = input("是否清空现有数据并重新导入？(y/N): ")
        if response.lower() != 'y':
            print("取消导入")
            return
        # 清空现有数据
        db.query(TennisCourt).delete()
        db.commit()
        print("已清空现有数据")
    
    # 导入数据
    print("开始导入数据...")
    imported_count = 0
    
    for court_data in courts_data:
        try:
            # 处理时间字段
            created_at = None
            updated_at = None
            if court_data.get('created_at'):
                created_at = datetime.fromisoformat(court_data['created_at'])
            if court_data.get('updated_at'):
                updated_at = datetime.fromisoformat(court_data['updated_at'])
            
            # 创建场馆对象
            court = TennisCourt(
                name=court_data.get('name'),
                address=court_data.get('address'),
                area=court_data.get('area'),
                area_name=court_data.get('area_name'),
                court_type=court_data.get('court_type'),
                phone=court_data.get('phone'),
                latitude=court_data.get('latitude'),
                longitude=court_data.get('longitude'),
                data_source=court_data.get('data_source'),
                created_at=created_at,
                updated_at=updated_at
            )
            
            db.add(court)
            imported_count += 1
            
            # 每100个提交一次
            if imported_count % 100 == 0:
                db.commit()
                print(f"已导入 {imported_count} 个场馆...")
                
        except Exception as e:
            print(f"❌ 导入场馆 {court_data.get('name', 'unknown')} 失败: {e}")
            continue
    
    # 最终提交
    db.commit()
    
    print(f"✅ 导入完成: {imported_count} 个场馆")
    
    # 显示统计
    final_count = db.query(TennisCourt).count()
    print(f"数据库总场馆数: {final_count}")
    
    # 按区域统计
    areas = {}
    for court in db.query(TennisCourt).all():
        area = court.area or '未知'
        if area not in areas:
            areas[area] = 0
        areas[area] += 1
    
    print("\n按区域统计:")
    for area, count in sorted(areas.items()):
        print(f"  {area}: {count} 个场馆")

if __name__ == "__main__":
    import_courts_data() 