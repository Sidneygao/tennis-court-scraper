#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查得乐网球(欢乐谷网球场)周边的室外场馆分布
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import get_db
from app.models import TennisCourt, CourtDetail
from app.scrapers.price_predictor import PricePredictor
import json

def check_nearby_outdoor_courts():
    print("🔍 检查得乐网球(欢乐谷网球场)周边室外场馆分布...")
    
    # 初始化预测器
    predictor = PricePredictor()
    
    # 目标场馆
    target_court_name = "得乐网球(欢乐谷网球场)"
    target_court = predictor.db.query(TennisCourt).filter(TennisCourt.name == target_court_name).first()
    
    if not target_court:
        print(f"❌ 未找到目标场馆: {target_court_name}")
        return
    
    print(f"\n🎯 目标场馆: {target_court.name}")
    print(f"   位置: {target_court.latitude}, {target_court.longitude}")
    print(f"   类型: {predictor.determine_court_type(target_court.name)}")
    
    # 查找周边所有场馆
    all_courts = predictor.db.query(TennisCourt).all()
    nearby_courts = []
    
    for court in all_courts:
        if court.id == target_court.id:
            continue
        
        if not court.latitude or not court.longitude:
            continue
        
        # 计算距离
        distance = predictor.calculate_distance(
            target_court.latitude, target_court.longitude,
            court.latitude, court.longitude
        )
        
        if distance <= 6:  # 检查6KM内所有场馆
            # 判断场馆类型
            court_type = predictor.determine_court_type(court.name)
            
            # 检查是否有真实价格
            detail = predictor.db.query(CourtDetail).filter(CourtDetail.court_id == court.id).first()
            has_real_price = False
            merged_prices = None
            if detail:
                real_prices = predictor._extract_real_prices(detail)
                has_real_price = bool(real_prices)
                merged_prices = detail.merged_prices
            
            nearby_courts.append({
                'court': court,
                'distance': distance,
                'type': court_type,
                'has_real_price': has_real_price,
                'merged_prices': merged_prices
            })
    
    # 按距离排序
    nearby_courts.sort(key=lambda x: x['distance'])
    
    print(f"\n📊 周边6KM内场馆分布:")
    
    # 统计室外场馆
    outdoor_courts = [c for c in nearby_courts if c['type'] == '室外']
    
    print(f"\n🌳 室外场馆 ({len(outdoor_courts)}个):")
    for court_info in outdoor_courts:
        court = court_info['court']
        distance = court_info['distance']
        has_price = court_info['has_real_price']
        merged_prices = court_info['merged_prices']
        price_status = "✅ 有真实价格" if has_price else "❌ 无真实价格"
        print(f"  {court.name} ({price_status}) 距离: {distance:.2f}KM")
        if merged_prices:
            print(f"    merged_prices: {merged_prices}")
        else:
            print(f"    merged_prices: 空")
    
    predictor.db.close()

if __name__ == "__main__":
    check_nearby_outdoor_courts() 