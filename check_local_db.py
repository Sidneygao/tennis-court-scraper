#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查本地数据库场馆数据
"""

from app.database import get_db, init_db
from app.models import TennisCourt
from app.config import settings

def check_local_db():
    """检查本地数据库"""
    print("检查本地数据库...")
    
    # 初始化数据库
    init_db()
    
    # 获取数据库会话
    db = next(get_db())
    
    # 查询场馆总数
    total_courts = db.query(TennisCourt).count()
    print(f"本地数据库总场馆数: {total_courts}")
    
    # 按区域统计
    print("\n按区域统计:")
    areas = {}
    for court in db.query(TennisCourt).all():
        area = court.area or "未知"
        if area not in areas:
            areas[area] = 0
        areas[area] += 1
    
    for area, count in sorted(areas.items()):
        print(f"  {area}: {count} 个场馆")
    
    # 显示前5个场馆
    print("\n前5个场馆:")
    for court in db.query(TennisCourt).limit(5).all():
        print(f"  - {court.name} (区域: {court.area}, 类型: {court.court_type})")
    
    # 检查数据库文件大小
    import os
    db_path = "data/courts.db"
    if os.path.exists(db_path):
        size = os.path.getsize(db_path) / (1024 * 1024)  # MB
        print(f"\n数据库文件大小: {size:.2f} MB")
    else:
        print("\n数据库文件不存在")

if __name__ == "__main__":
    check_local_db() 