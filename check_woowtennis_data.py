#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查WoowTennis网球俱乐部(国贸店)数据库中的实际价格字段
"""
from app.database import get_db
from app.models import TennisCourt, CourtDetail
import json

def check_woowtennis_data():
    """检查WoowTennis网球俱乐部(国贸店)数据库中的实际价格字段"""
    print("🔍 检查WoowTennis网球俱乐部(国贸店)数据库数据...")
    
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
    
    print("\n=== 数据库中的价格字段 ===")
    print(f"prices字段: {detail.prices}")
    print(f"bing_prices字段: {detail.bing_prices}")
    print(f"merged_prices字段: {detail.merged_prices}")
    print(f"predict_prices字段: {detail.predict_prices}")
    
    print("\n=== 解析后的价格数据 ===")
    
    # 解析prices字段
    if detail.prices:
        try:
            prices_data = json.loads(detail.prices) if isinstance(detail.prices, str) else detail.prices
            print(f"prices解析: {json.dumps(prices_data, ensure_ascii=False, indent=2)}")
        except Exception as e:
            print(f"prices解析失败: {e}")
    
    # 解析bing_prices字段
    if detail.bing_prices:
        try:
            bing_data = json.loads(detail.bing_prices) if isinstance(detail.bing_prices, str) else detail.bing_prices
            print(f"bing_prices解析: {json.dumps(bing_data, ensure_ascii=False, indent=2)}")
        except Exception as e:
            print(f"bing_prices解析失败: {e}")
    
    # 解析merged_prices字段
    if detail.merged_prices:
        try:
            merged_data = json.loads(detail.merged_prices) if isinstance(detail.merged_prices, str) else detail.merged_prices
            print(f"merged_prices解析: {json.dumps(merged_data, ensure_ascii=False, indent=2)}")
        except Exception as e:
            print(f"merged_prices解析失败: {e}")
    
    # 解析predict_prices字段
    if detail.predict_prices:
        try:
            predict_data = json.loads(detail.predict_prices) if isinstance(detail.predict_prices, str) else detail.predict_prices
            print(f"predict_prices解析: {json.dumps(predict_data, ensure_ascii=False, indent=2)}")
        except Exception as e:
            print(f"predict_prices解析失败: {e}")

if __name__ == "__main__":
    check_woowtennis_data() 