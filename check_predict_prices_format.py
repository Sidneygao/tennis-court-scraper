#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
检查预测价格的数据格式
"""

import sys
import os
import json
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import get_db
from app.models import TennisCourt, CourtDetail

def check_predict_prices_format():
    """检查预测价格的数据格式"""
    print("🔍 检查预测价格的数据格式...")
    print("=" * 60)
    
    db = next(get_db())
    
    # 检查前5个场馆的预测价格格式
    courts = db.query(TennisCourt).limit(5).all()
    
    for court in courts:
        detail = db.query(CourtDetail).filter(CourtDetail.court_id == court.id).first()
        
        print(f"\n🏟️ 场馆: {court.name} (ID: {court.id})")
        print("-" * 40)
        
        if detail and detail.predict_prices:
            print(f"原始数据: {detail.predict_prices}")
            print(f"数据类型: {type(detail.predict_prices)}")
            
            try:
                parsed = json.loads(detail.predict_prices)
                print(f"解析后: {parsed}")
                print(f"解析后类型: {type(parsed)}")
                
                if isinstance(parsed, dict):
                    print("✅ 是对象格式")
                    if 'peak_price' in parsed:
                        print(f"  黄金时间价格: {parsed['peak_price']}")
                    if 'off_peak_price' in parsed:
                        print(f"  非黄金时间价格: {parsed['off_peak_price']}")
                elif isinstance(parsed, list):
                    print("❌ 是数组格式（前端期望对象格式）")
                else:
                    print(f"❓ 其他格式: {type(parsed)}")
                    
            except Exception as e:
                print(f"❌ JSON解析失败: {e}")
        else:
            print("❌ 无预测价格数据")
    
    db.close()
    print("\n✅ 检查完成!")

if __name__ == "__main__":
    check_predict_prices_format() 