#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查BING价格数据的实际结构
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import SessionLocal
from app.models import TennisCourt, CourtDetail
import json

def check_bing_price_structure():
    """检查BING价格数据的实际结构"""
    db = SessionLocal()
    
    try:
        # 获取前5个有merged_prices的详情
        details = db.query(CourtDetail).filter(CourtDetail.merged_prices.isnot(None)).limit(5).all()
        
        print(f"🔍 检查BING价格数据结构\\n")
        
        for detail in details:
            court = db.query(TennisCourt).filter(TennisCourt.id == detail.court_id).first()
            court_name = court.name if court else f"ID:{detail.court_id}"
            
            print(f"\\n🏟️ {court_name} (ID: {detail.court_id})")
            
            try:
                prices = json.loads(detail.merged_prices)
                print(f"   价格数据类型: {type(prices)}")
                print(f"   价格数据长度: {len(prices) if isinstance(prices, list) else 'N/A'}")
                
                if isinstance(prices, list) and len(prices) > 0:
                    print(f"   第一个价格数据:")
                    first_price = prices[0]
                    for key, value in first_price.items():
                        print(f"     {key}: {value}")
                    
                    # 检查source字段
                    sources = [p.get('source', 'NO_SOURCE') for p in prices[:3]]
                    print(f"   前3个价格来源: {sources}")
                    
                    # 检查是否有BING价格
                    bing_count = sum(1 for p in prices if p.get('source') == 'BING')
                    print(f"   BING价格数量: {bing_count}")
                    
            except Exception as e:
                print(f"   ❌ 解析失败: {e}")
        
    finally:
        db.close()

if __name__ == "__main__":
    check_bing_price_structure() 