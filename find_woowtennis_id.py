#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
查找WoowTennis网球俱乐部(国贸店)的正确ID
"""
from app.database import get_db
from app.models import TennisCourt, CourtDetail
import json

def find_woowtennis_id():
    """查找WoowTennis网球俱乐部(国贸店)的正确ID"""
    print("🔍 查找WoowTennis网球俱乐部(国贸店)...")
    
    db = next(get_db())
    
    # 查找所有包含WoowTennis的场馆
    courts = db.query(TennisCourt).filter(TennisCourt.name.like('%WoowTennis%')).all()
    
    print(f"找到 {len(courts)} 个WoowTennis相关场馆:")
    for court in courts:
        print(f"ID: {court.id}, Name: {court.name}")
        
        # 查找对应的详情
        detail = db.query(CourtDetail).filter(CourtDetail.court_id == court.id).first()
        if detail:
            print(f"  预测价格: {detail.predict_prices}")
            print(f"  真实价格: {detail.prices}")
            print(f"  BING价格: {detail.bing_prices}")
            print(f"  融合价格: {detail.merged_prices}")
        else:
            print("  无详情数据")
        print()

if __name__ == "__main__":
    find_woowtennis_id() 