#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试修复后的1KM步进法算法
验证场馆类型过滤是否正确工作
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import get_db
from app.models import TennisCourt, CourtDetail
from app.scrapers.price_predictor import PricePredictor
import json

def test_fixed_prediction_algorithm():
    print("🔧 测试修复后的1KM步进法算法...")
    
    # 初始化预测器
    predictor = PricePredictor()
    
    # 测试场馆：得乐网球(欢乐谷网球场)
    target_court_name = "得乐网球(欢乐谷网球场)"
    
    # 查找目标场馆
    target_court = predictor.db.query(TennisCourt).filter(TennisCourt.name == target_court_name).first()
    if not target_court:
        print(f"❌ 未找到目标场馆: {target_court_name}")
        return
    
    print(f"\n🎯 目标场馆: {target_court.name}")
    print(f"   位置: {target_court.latitude}, {target_court.longitude}")
    
    # 判断场馆类型
    court_type = predictor.determine_court_type(target_court.name)
    print(f"   类型: {court_type}")
    
    # 测试1KM步进法
    print(f"\n📊 1KM步进法测试:")
    
    for radius in [1, 2, 3]:
        print(f"\n  🔍 搜索半径: {radius}KM")
        nearby_courts = predictor.find_nearby_courts_with_prices(target_court, radius)
        
        print(f"    找到 {len(nearby_courts)} 个同类型邻域样本:")
        
        for i, nearby in enumerate(nearby_courts[:5]):  # 只显示前5个
            court = nearby['court']
            distance = nearby['distance']
            prices = nearby['prices']
            
            # 验证类型是否匹配
            nearby_type = predictor.determine_court_type(court.name)
            type_match = "✅" if nearby_type == court_type else "❌"
            
            print(f"      {i+1}. {court.name} ({type_match} {nearby_type})")
            print(f"         距离: {distance:.1f}KM")
            print(f"         价格: 黄金{prices.get('peak_price')}元, 非黄金{prices.get('off_peak_price')}元")
        
        if len(nearby_courts) > 5:
            print(f"      ... 还有 {len(nearby_courts) - 5} 个样本")
        
        if len(nearby_courts) >= 2:
            print(f"    ✅ 半径{radius}KM内找到足够样本，停止搜索")
            break
        else:
            print(f"    ⚠️ 半径{radius}KM内样本不足，继续扩大搜索")
    
    # 测试预测
    print(f"\n🎯 价格预测测试:")
    prediction = predictor.predict_price_for_court(target_court)
    
    if prediction and not prediction.get('predict_failed'):
        print(f"  ✅ 预测成功:")
        print(f"     黄金时段: {prediction.get('peak_price')}元")
        print(f"     非黄金时段: {prediction.get('off_peak_price')}元")
        print(f"     搜索半径: {prediction.get('search_radius')}KM")
        print(f"     样本数量: {prediction.get('data_count')}个")
        print(f"     预测方法: {prediction.get('predict_method')}")
        
        print(f"\n     依赖样本:")
        for i, source in enumerate(prediction.get('source_courts', [])):
            print(f"       {i+1}. {source['name']} (距离: {source['distance']}KM)")
    else:
        print(f"  ❌ 预测失败: {prediction.get('reason', '未知原因')}")
    
    predictor.db.close()

if __name__ == "__main__":
    test_fixed_prediction_algorithm() 