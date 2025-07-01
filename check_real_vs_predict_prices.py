#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
分析真实价格和预测价格的分布情况
"""

import json
import sqlite3
from collections import defaultdict, Counter
import numpy as np

def main():
    print("\n=== 国贸区域预测价格及依赖真实价格样本 ===\n")
    conn = sqlite3.connect('data/courts.db')
    cursor = conn.cursor()
    # 查找国贸区域所有场馆
    cursor.execute("""
        SELECT tc.id, tc.name, cd.predict_prices, cd.merged_prices
        FROM tennis_courts tc
        LEFT JOIN court_details cd ON tc.id = cd.court_id
        WHERE tc.area = 'guomao'
    """)
    results = cursor.fetchall()
    for cid, name, predict_prices, merged_prices in results:
        print(f"🏟️ {name} (ID: {cid})")
        # 预测价格
        if predict_prices:
            try:
                pred = json.loads(predict_prices)
                print(f"  预测黄金时间价格: {pred.get('peak_price', '无')} 元")
                print(f"  预测非黄金时间价格: {pred.get('off_peak_price', '无')} 元")
                print(f"  预测样本数量: {pred.get('data_count', '无')}")
                print(f"  预测样本来源:")
                for src in pred.get('source_courts', [])[:5]:
                    print(f"    - {src.get('name', '')} 距离: {src.get('distance', '无')}km")
                if len(pred.get('source_courts', [])) > 5:
                    print(f"    ...共{len(pred.get('source_courts', []))}个样本")
            except Exception as e:
                print(f"  预测价格解析失败: {e}")
        else:
            print("  无预测价格")
        # 依赖的真实价格样本
        if merged_prices:
            try:
                real = json.loads(merged_prices)
                real_samples = [p for p in real if not p.get('is_predicted', True)]
                print(f"  依赖真实价格样本（前5条）：")
                for p in real_samples[:5]:
                    print(f"    - {p.get('type', '')}: {p.get('price', '')} 来源: {p.get('source', '')} 置信度: {p.get('confidence', '')}")
                if len(real_samples) > 5:
                    print(f"    ...共{len(real_samples)}条真实价格")
            except Exception as e:
                print(f"  真实价格解析失败: {e}")
        else:
            print("  无真实价格样本")
        print()
    conn.close()

def extract_price_value(price_str: str) -> float:
    """提取价格数值"""
    import re
    if not price_str:
        return None
    
    # 匹配价格模式
    patterns = [
        r'¥?(\d+(?:\.\d+)?)',
        r'(\d+(?:\.\d+)?)元',
        r'(\d+(?:\.\d+)?)/小时',
        r'(\d+(?:\.\d+)?)元/小时'
    ]
    
    for pattern in patterns:
        match = re.search(pattern, price_str)
        if match:
            try:
                return float(match.group(1))
            except:
                continue
    
    return None

def is_indoor_court(court_type: str) -> bool:
    """判断是否为室内场馆"""
    if not court_type:
        return False
        
    indoor_keywords = ['室内', '气膜', 'indoor', '馆']
    outdoor_keywords = ['室外', 'outdoor', '场', '公园', '小区']
    
    court_type_lower = court_type.lower()
    
    for keyword in indoor_keywords:
        if keyword in court_type_lower:
            return True
    for keyword in outdoor_keywords:
        if keyword in court_type_lower:
            return False
    
    return '馆' in court_type_lower

def is_peak_time(price_type: str) -> bool:
    """判断是否为黄金时段"""
    peak_keywords = ['黄金', '高峰', 'peak', '黄金时间', '黄金时段']
    offpeak_keywords = ['非黄金', '非高峰', 'off', '非黄金时间', '非黄金时段']
    
    price_type_lower = price_type.lower()
    
    for keyword in peak_keywords:
        if keyword in price_type_lower:
            return True
    for keyword in offpeak_keywords:
        if keyword in price_type_lower:
            return False
    
    return False

if __name__ == "__main__":
    main() 