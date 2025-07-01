#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
临时数据库状态检查脚本
"""

import os
import sys
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from app.database import get_db, init_db
from app.models import TennisCourt
from app.config import settings
from sqlalchemy import text

def main():
    print("=== 数据库状态检查 ===")
    
    # 初始化数据库
    print("1. 初始化数据库...")
    init_db()
    
    # 检查数据库连接
    print("2. 检查数据库连接...")
    db = next(get_db())
    
    try:
        # 检查表是否存在
        print("3. 检查表结构...")
        result = db.execute(text("SELECT name FROM sqlite_master WHERE type='table' AND name='tennis_courts'"))
        if result.fetchone():
            print("✅ tennis_courts 表存在")
        else:
            print("❌ tennis_courts 表不存在")
            return
        
        # 检查数据数量
        print("4. 检查数据数量...")
        count = db.query(TennisCourt).count()
        print(f"数据库中共有 {count} 条场地记录")
        
        if count == 0:
            print("⚠️ 数据库中没有场地数据，这可能是导致加载卡死的原因")
            print("建议运行数据抓取脚本添加测试数据")
        else:
            # 显示前几条数据
            print("5. 显示前3条数据...")
            courts = db.query(TennisCourt).limit(3).all()
            for i, court in enumerate(courts, 1):
                print(f"  {i}. {court.name} - {court.area} - {court.data_source}")
        
        # 检查区域统计
        print("6. 检查区域统计...")
        for area_key in settings.target_areas.keys():
            count = db.query(TennisCourt).filter(TennisCourt.area == area_key).count()
            print(f"  {settings.target_areas[area_key]['name']}: {count} 条")
        
    except Exception as e:
        print(f"❌ 检查过程中出现错误: {e}")
    finally:
        db.close()
    
    print("\n=== 检查完成 ===")

if __name__ == "__main__":
    main() 