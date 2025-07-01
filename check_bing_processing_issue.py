#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查BING价格加工为什么都是综合报价而不是分开的价格
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import get_db
from app.models import TennisCourt, CourtDetail
import json
import re
from collections import defaultdict

def extract_price_value(price_str):
    """从价格字符串中提取数值"""
    if not price_str:
        return None
    try:
        matches = re.findall(r'(\d+)', price_str)
        if matches:
            return int(matches[0])
    except:
        pass
    return None

def check_bing_processing_issue():
    """检查BING价格加工问题"""
    print("🔍 检查BING价格加工为什么都是综合报价而不是分开的价格")
    
    db = next(get_db())
    
    # 获取双井区域所有场馆
    courts = db.query(TennisCourt).filter(TennisCourt.area == 'shuangjing').all()
    
    for court in courts:
        detail = db.query(CourtDetail).filter(CourtDetail.court_id == court.id).first()
        if not detail or not detail.bing_prices:
            continue
            
        print(f"\n🏟️ {court.name} (ID: {court.id})")
        
        # 分析原始BING价格
        try:
            bing_data = json.loads(detail.bing_prices)
            if isinstance(bing_data, list):
                print(f"  原始BING价格数量: {len(bing_data)}")
                
                # 按类型分组
                type_groups = defaultdict(list)
                for price in bing_data:
                    price_type = price.get('type', '未知')
                    price_value = extract_price_value(price.get('price', ''))
                    if price_value:
                        type_groups[price_type].append(price_value)
                
                print(f"  价格类型分布:")
                for price_type, values in type_groups.items():
                    if values:
                        print(f"    {price_type}: {len(values)}个, 范围{min(values)}-{max(values)}元, 平均{sum(values)/len(values):.0f}元")
                
                # 检查是否有足够的不同类型来分开
                valid_types = [t for t, v in type_groups.items() if len(v) >= 2]
                print(f"  有效类型数(≥2个样本): {len(valid_types)}")
                
                if len(valid_types) >= 3:
                    print(f"  ✅ 可以分开为多个价格类型")
                else:
                    print(f"  ❌ 样本不足，只能综合报价")
                    
        except Exception as e:
            print(f"  解析BING价格失败: {e}")
    
    db.close()

if __name__ == "__main__":
    check_bing_processing_issue() 