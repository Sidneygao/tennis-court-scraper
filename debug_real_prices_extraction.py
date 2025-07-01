#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
调试真实价格提取逻辑
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import get_db
from app.models import TennisCourt, CourtDetail
from app.scrapers.price_predictor import PricePredictor
import json

def debug_real_prices_extraction():
    print("🔧 调试真实价格提取逻辑...")
    
    predictor = PricePredictor()
    
    # 测试场馆：中体一方百子湾室外网球场
    court_name = "中体一方百子湾室外网球场"
    court = predictor.db.query(TennisCourt).filter(TennisCourt.name == court_name).first()
    
    if not court:
        print(f"❌ 未找到场馆: {court_name}")
        return
    
    detail = predictor.db.query(CourtDetail).filter(CourtDetail.court_id == court.id).first()
    
    print(f"\n🏟️ {court.name} (ID: {court.id})")
    
    if detail:
        print(f"   详情记录: 存在")
        
        # 检查merged_prices
        if detail.merged_prices:
            print(f"\n📊 merged_prices 原始数据:")
            print(f"   {detail.merged_prices}")
            
            try:
                merged_data = json.loads(detail.merged_prices)
                print(f"   解析成功: {type(merged_data)}")
                print(f"   内容: {merged_data}")
                
                # 测试价格提取
                real_prices = predictor._extract_real_prices(detail)
                print(f"\n🔍 提取的真实价格:")
                print(f"   {real_prices}")
                
                if real_prices:
                    print(f"   ✅ 成功提取真实价格")
                else:
                    print(f"   ❌ 提取失败")
                    
            except Exception as e:
                print(f"   解析失败: {e}")
        else:
            print(f"   merged_prices: 空")
        
        # 检查其他价格字段
        for field_name in ['bing_prices', 'dianping_prices', 'meituan_prices']:
            field_value = getattr(detail, field_name)
            if field_value:
                print(f"\n📊 {field_name}:")
                print(f"   {field_value}")
            else:
                print(f"\n📊 {field_name}: 空")
    else:
        print(f"   详情记录: 不存在")
    
    predictor.db.close()

if __name__ == "__main__":
    debug_real_prices_extraction() 