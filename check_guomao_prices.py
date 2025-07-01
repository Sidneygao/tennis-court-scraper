#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
查看国贸地区当前的室内外预测价格范围
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import SessionLocal
from app.models import TennisCourt, CourtDetail
import json

def check_guomao_prices():
    """查看国贸地区的预测价格范围"""
    db = SessionLocal()
    
    try:
        # 查找国贸地区的场馆
        courts = db.query(TennisCourt).filter(
            TennisCourt.area == 'guomao'
        ).all()
        
        print(f"🔍 国贸地区场馆分析\n")
        print(f"📊 找到 {len(courts)} 个国贸地区场馆")
        
        indoor_courts = []
        outdoor_courts = []
        
        for court in courts:
            if court.court_type == '室内':
                indoor_courts.append(court)
            elif court.court_type == '室外':
                outdoor_courts.append(court)
        
        print(f"  🏠 室内场馆: {len(indoor_courts)}个")
        print(f"  🌳 室外场馆: {len(outdoor_courts)}个")
        
        # 分析室内场馆预测价格
        if indoor_courts:
            print(f"\n🏠 室内场馆预测价格分析:")
            indoor_predictions = []
            
            for court in indoor_courts:
                detail = db.query(CourtDetail).filter(CourtDetail.court_id == court.id).first()
                if detail and detail.predict_prices:
                    try:
                        predict_data = json.loads(detail.predict_prices)
                        if isinstance(predict_data, dict) and 'price' in predict_data:
                            price = predict_data['price']
                            if isinstance(price, (int, float)) and price > 0:
                                indoor_predictions.append(price)
                    except:
                        continue
            
            if indoor_predictions:
                indoor_predictions.sort()
                print(f"  📈 预测价格范围: {min(indoor_predictions):.0f}-{max(indoor_predictions):.0f}元/小时")
                print(f"  📊 预测价格分布:")
                print(f"    • 最低价: {min(indoor_predictions):.0f}元")
                print(f"    • 最高价: {max(indoor_predictions):.0f}元")
                print(f"    • 中位数: {sorted(indoor_predictions)[len(indoor_predictions)//2]:.0f}元")
                
                # 价格区间统计
                price_ranges = {
                    '60-100': 0, '100-150': 0, '150-200': 0, 
                    '200-250': 0, '250-300': 0, '300-400': 0, '400-600': 0
                }
                
                for price in indoor_predictions:
                    if 60 <= price < 100:
                        price_ranges['60-100'] += 1
                    elif 100 <= price < 150:
                        price_ranges['100-150'] += 1
                    elif 150 <= price < 200:
                        price_ranges['150-200'] += 1
                    elif 200 <= price < 250:
                        price_ranges['200-250'] += 1
                    elif 250 <= price < 300:
                        price_ranges['250-300'] += 1
                    elif 300 <= price < 400:
                        price_ranges['300-400'] += 1
                    elif 400 <= price <= 600:
                        price_ranges['400-600'] += 1
                
                print(f"  📋 价格区间分布:")
                for range_name, count in price_ranges.items():
                    if count > 0:
                        percentage = count / len(indoor_predictions) * 100
                        print(f"    • {range_name}元: {count}个 ({percentage:.1f}%)")
            else:
                print(f"  ❌ 没有找到有效的预测价格数据")
        
        # 分析室外场馆预测价格
        if outdoor_courts:
            print(f"\n🌳 室外场馆预测价格分析:")
            outdoor_predictions = []
            
            for court in outdoor_courts:
                detail = db.query(CourtDetail).filter(CourtDetail.court_id == court.id).first()
                if detail and detail.predict_prices:
                    try:
                        predict_data = json.loads(detail.predict_prices)
                        if isinstance(predict_data, dict) and 'price' in predict_data:
                            price = predict_data['price']
                            if isinstance(price, (int, float)) and price > 0:
                                outdoor_predictions.append(price)
                    except:
                        continue
            
            if outdoor_predictions:
                outdoor_predictions.sort()
                print(f"  📈 预测价格范围: {min(outdoor_predictions):.0f}-{max(outdoor_predictions):.0f}元/小时")
                print(f"  📊 预测价格分布:")
                print(f"    • 最低价: {min(outdoor_predictions):.0f}元")
                print(f"    • 最高价: {max(outdoor_predictions):.0f}元")
                print(f"    • 中位数: {sorted(outdoor_predictions)[len(outdoor_predictions)//2]:.0f}元")
                
                # 价格区间统计
                price_ranges = {
                    '50-80': 0, '80-120': 0, '120-150': 0, 
                    '150-200': 0, '200-250': 0, '250-300': 0
                }
                
                for price in outdoor_predictions:
                    if 50 <= price < 80:
                        price_ranges['50-80'] += 1
                    elif 80 <= price < 120:
                        price_ranges['80-120'] += 1
                    elif 120 <= price < 150:
                        price_ranges['120-150'] += 1
                    elif 150 <= price < 200:
                        price_ranges['150-200'] += 1
                    elif 200 <= price < 250:
                        price_ranges['200-250'] += 1
                    elif 250 <= price <= 300:
                        price_ranges['250-300'] += 1
                
                print(f"  📋 价格区间分布:")
                for range_name, count in price_ranges.items():
                    if count > 0:
                        percentage = count / len(outdoor_predictions) * 100
                        print(f"    • {range_name}元: {count}个 ({percentage:.1f}%)")
            else:
                print(f"  ❌ 没有找到有效的预测价格数据")
        
        # 检查真实价格数据
        print(f"\n💰 真实价格数据检查:")
        real_indoor_prices = []
        real_outdoor_prices = []
        
        for court in courts:
            detail = db.query(CourtDetail).filter(CourtDetail.court_id == court.id).first()
            if detail and detail.merged_prices:
                try:
                    merged_data = json.loads(detail.merged_prices)
                    if isinstance(merged_data, list):
                        for price_item in merged_data:
                            if isinstance(price_item, dict) and 'price' in price_item:
                                price_str = price_item['price']
                                try:
                                    price = float(price_str.replace('¥', '').replace('/小时', ''))
                                    if court.court_type == '室内':
                                        real_indoor_prices.append(price)
                                    elif court.court_type == '室外':
                                        real_outdoor_prices.append(price)
                                except:
                                    continue
                except:
                    continue
        
        if real_indoor_prices:
            print(f"  🏠 室内真实价格: {len(real_indoor_prices)}个")
            print(f"    范围: {min(real_indoor_prices):.0f}-{max(real_indoor_prices):.0f}元")
        else:
            print(f"  🏠 室内真实价格: 无")
            
        if real_outdoor_prices:
            print(f"  🌳 室外真实价格: {len(real_outdoor_prices)}个")
            print(f"    范围: {min(real_outdoor_prices):.0f}-{max(real_outdoor_prices):.0f}元")
        else:
            print(f"  🌳 室外真实价格: 无")
    
    finally:
        db.close()

if __name__ == "__main__":
    check_guomao_prices() 