#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查merged_prices中的BING价格数据
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import SessionLocal
from app.models import TennisCourt, CourtDetail
import json

def check_bing_prices_in_merged():
    """检查merged_prices中的BING价格数据"""
    db = SessionLocal()
    
    try:
        # 查找有merged_prices的场馆
        details = db.query(CourtDetail).filter(CourtDetail.merged_prices.isnot(None)).limit(10).all()
        
        print("🔍 检查merged_prices中的BING价格数据\n")
        
        for detail in details:
            court = db.query(TennisCourt).filter(TennisCourt.id == detail.court_id).first()
            if not court:
                continue
                
            print(f"🏟️ 场馆: {court.name}")
            print(f"   merged_prices: {detail.merged_prices}")
            
            if detail.merged_prices:
                try:
                    merged_data = json.loads(detail.merged_prices)
                    if isinstance(merged_data, list) and len(merged_data) > 0:
                        print(f"   价格数量: {len(merged_data)}")
                        print(f"   价格来源: {[p.get('source', '未知') for p in merged_data[:3]]}")
                        print(f"   价格示例: {merged_data[:2]}")
                    else:
                        print(f"   merged_prices不是有效列表")
                except Exception as e:
                    print(f"   解析失败: {e}")
            
            print()
        
        # 统计BING价格在merged_prices中的情况
        print("\n📊 统计BING价格在merged_prices中的情况:")
        
        total_with_merged = 0
        total_with_bing = 0
        
        all_details = db.query(CourtDetail).filter(CourtDetail.merged_prices.isnot(None)).all()
        
        for detail in all_details:
            total_with_merged += 1
            
            if detail.merged_prices:
                try:
                    merged_data = json.loads(detail.merged_prices)
                    if isinstance(merged_data, list):
                        for price in merged_data:
                            if isinstance(price, dict) and price.get('source') == 'BING':
                                total_with_bing += 1
                                break
                except:
                    pass
        
        print(f"   有merged_prices的场馆: {total_with_merged}")
        print(f"   merged_prices中包含BING价格的场馆: {total_with_bing}")
        
    finally:
        db.close()

if __name__ == "__main__":
    check_bing_prices_in_merged() 