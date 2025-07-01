#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
检查各区域价格分布情况
"""

import sys
import os
import json
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import get_db
from app.models import TennisCourt, CourtDetail

def check_area_price_distribution():
    """检查各区域价格分布情况"""
    print("🔍 检查各区域价格分布情况...")
    print("=" * 60)
    
    db = next(get_db())
    
    # 检查的区域
    areas = ["sanyuanqiao", "guomao", "shuangjing", "sanlitun"]
    
    for area in areas:
        print(f"\n📍 区域: {area}")
        print("-" * 40)
        
        # 获取该区域的所有场馆
        courts = db.query(TennisCourt).filter(TennisCourt.area == area).all()
        print(f"场馆总数: {len(courts)}")
        
        real_price_count = 0
        predict_price_count = 0
        no_price_count = 0
        
        for court in courts:
            detail = db.query(CourtDetail).filter(CourtDetail.court_id == court.id).first()
            
            if detail:
                # 解析真实价格
                real_prices = []
                if detail.prices:
                    try:
                        real_prices = json.loads(detail.prices)
                    except Exception:
                        real_prices = []
                # 解析预测价格
                predict_prices = None
                if detail.predict_prices:
                    try:
                        predict_prices = json.loads(detail.predict_prices)
                    except Exception:
                        predict_prices = None
                has_real_price = real_prices and len(real_prices) > 0
                has_predict_price = predict_prices and predict_prices.get('avg_price')
                
                if has_real_price:
                    real_price_count += 1
                elif has_predict_price:
                    predict_price_count += 1
                else:
                    no_price_count += 1
                    
                # 显示前3个场馆的详细信息
                if real_price_count + predict_price_count + no_price_count <= 3:
                    print(f"  {court.name} (ID: {court.id})")
                    print(f"    真实价格: {'有' if has_real_price else '无'}")
                    print(f"    预测价格: {'有' if has_predict_price else '无'}")
                    if has_real_price:
                        print(f"    真实价格内容: {real_prices[:2]}...")  # 只显示前2个
                    if has_predict_price:
                        print(f"    预测价格: {predict_prices.get('avg_price')}元/小时")
        
        print(f"\n📊 {area}区域价格分布:")
        print(f"  真实价格: {real_price_count}个")
        print(f"  预测价格: {predict_price_count}个")
        print(f"  无价格: {no_price_count}个")
        
        if len(courts) > 0:
            real_percent = (real_price_count / len(courts)) * 100
            predict_percent = (predict_price_count / len(courts)) * 100
            print(f"  真实价格占比: {real_percent:.1f}%")
            print(f"  预测价格占比: {predict_percent:.1f}%")
    
    db.close()
    print("\n✅ 检查完成!")

if __name__ == "__main__":
    check_area_price_distribution() 