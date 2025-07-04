#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
清理WoowTennis网球俱乐部(国贸店)的merged_prices字段中的错误BING价格
"""
from app.database import get_db
from app.models import TennisCourt, CourtDetail
import json

def clean_woowtennis_merged_prices():
    """清理WoowTennis网球俱乐部(国贸店)的merged_prices字段中的错误BING价格"""
    print("🧹 清理WoowTennis网球俱乐部(国贸店)的merged_prices字段...")
    
    db = next(get_db())
    
    # 查找WoowTennis网球俱乐部(国贸店)
    court = db.query(TennisCourt).filter(TennisCourt.id == 9).first()
    if not court:
        print("❌ 未找到WoowTennis网球俱乐部(国贸店)")
        return
    
    print(f"场馆: {court.name} (ID: {court.id})")
    
    # 查找对应的详情
    detail = db.query(CourtDetail).filter(CourtDetail.court_id == court.id).first()
    if not detail:
        print("❌ 未找到详情数据")
        return
    
    print(f"清理前的merged_prices: {detail.merged_prices}")
    
    # 清理merged_prices字段，只保留真实价格（非BING来源）
    if detail.prices:
        try:
            # 使用prices字段作为merged_prices（真实价格）
            detail.merged_prices = detail.prices
            db.commit()
            print(f"✅ 已清理merged_prices字段，使用真实价格")
            print(f"清理后的merged_prices: {detail.merged_prices}")
        except Exception as e:
            print(f"❌ 清理失败: {e}")
            db.rollback()
    else:
        print("❌ 没有真实价格数据，无法清理")

if __name__ == "__main__":
    clean_woowtennis_merged_prices() 