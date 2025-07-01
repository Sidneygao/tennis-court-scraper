#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
重新计算所有场馆的类型，使用当前的三层次算法
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.scrapers.price_predictor import PricePredictor
from app.database import get_db
from app.models import TennisCourt

def recalculate_court_types():
    print("🔄 开始重新计算所有场馆类型...")
    
    predictor = PricePredictor()
    db = next(get_db())
    
    # 获取所有场馆
    courts = db.query(TennisCourt).all()
    print(f"📊 总共 {len(courts)} 个场馆")
    
    updated_count = 0
    unchanged_count = 0
    
    for i, court in enumerate(courts, 1):
        if i % 50 == 0:
            print(f"⏳ 进度: {i}/{len(courts)}")
        
        # 使用三层次算法重新判定类型
        new_type = predictor.determine_court_type(court.name, court.address)
        
        # 检查是否需要更新
        if court.court_type != new_type:
            old_type = court.court_type
            court.court_type = new_type
            updated_count += 1
            print(f"🔄 更新: {court.name}")
            print(f"    旧类型: {old_type} → 新类型: {new_type}")
        else:
            unchanged_count += 1
    
    # 提交更改
    db.commit()
    
    print(f"\n✅ 重新计算完成!")
    print(f"   更新场馆: {updated_count} 个")
    print(f"   未变化: {unchanged_count} 个")
    print(f"   总计: {len(courts)} 个")

if __name__ == "__main__":
    recalculate_court_types() 