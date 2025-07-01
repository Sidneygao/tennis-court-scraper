#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
价格预测器测试脚本
"""

import os
import sys
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from app.database import get_db
from app.models import TennisCourt
from app.scrapers.price_predictor import PricePredictor

def test_price_predictor():
    """测试价格预测器"""
    print("=== 价格预测器测试 ===")
    
    # 创建预测器
    predictor = PricePredictor()
    
    # 获取数据库连接
    db = next(get_db())
    
    # 获取前5个场馆进行测试
    courts = db.query(TennisCourt).limit(5).all()
    
    print(f"测试场馆数量: {len(courts)}")
    print()
    
    for i, court in enumerate(courts, 1):
        print(f"场馆 {i}: {court.name}")
        print(f"  区域: {court.area}")
        print(f"  类型: {court.court_type}")
        print(f"  设施: {court.facilities}")
        
        # 预测价格
        prediction = predictor.predict_price(court)
        
        print(f"  预测价格:")
        print(f"    黄金时间: {prediction['peak_price']}")
        print(f"    非黄金时间: {prediction['off_peak_price']}")
        print(f"    会员价格: {prediction['member_price']}")
        print(f"    置信度: {prediction['prediction_confidence']}")
        print(f"    预测因素: {prediction['prediction_factors']}")
        print()
    
    print("=== 测试完成 ===")

if __name__ == "__main__":
    test_price_predictor() 