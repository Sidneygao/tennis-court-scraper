#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
批量清洗所有BING价格：
1. 只保留区间内价格，格式统一"xxx元/小时"
2. 置信度按正态分布中心距离赋值，异常价格置信度为0
3. 覆盖写回bing_prices和merged_prices。
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import get_db
from app.models import TennisCourt, CourtDetail
import json
import re
import numpy as np

def extract_price_value(price_str):
    if price_str is None:
        return None
    if isinstance(price_str, (int, float)):
        return int(price_str)
    try:
        matches = re.findall(r'(\d+)', str(price_str))
        if matches:
            return int(matches[0])
    except:
        pass
    return None

def calc_confidence(price, mean, std):
    # 距离均值越近置信度越高，超出2倍std置信度为0
    if std == 0:
        return 1.0 if price == mean else 0.0
    z = abs(price - mean) / std
    if z > 2:
        return 0.0
    return float(np.exp(-0.5 * z * z))  # 高斯分布核

def clean_all_bing_prices():
    print("🧹 批量清洗所有BING价格...")
    db = next(get_db())
    courts = db.query(TennisCourt).all()
    details = db.query(CourtDetail).all()
    
    # 统计全库室内/室外BING价格分布
    indoor_prices = []
    outdoor_prices = []
    for detail in details:
        if not detail.bing_prices:
            continue
        try:
            prices = json.loads(detail.bing_prices)
            if not isinstance(prices, list):
                continue
            court = next((c for c in courts if c.id == detail.court_id), None)
            if not court:
                continue
            for item in prices:
                v = extract_price_value(item.get('price'))
                if v is None:
                    continue
                if court.court_type == '室内':
                    if 60 <= v <= 600:
                        indoor_prices.append(v)
                elif court.court_type == '室外':
                    if 50 <= v <= 300:
                        outdoor_prices.append(v)
        except: pass
    # 计算均值和标准差
    indoor_mean = np.mean(indoor_prices) if indoor_prices else 200
    indoor_std = np.std(indoor_prices) if indoor_prices else 50
    outdoor_mean = np.mean(outdoor_prices) if outdoor_prices else 100
    outdoor_std = np.std(outdoor_prices) if outdoor_prices else 30
    print(f"室内均值: {indoor_mean:.1f}, std: {indoor_std:.1f} | 室外均值: {outdoor_mean:.1f}, std: {outdoor_std:.1f}")
    
    update_count = 0
    for detail in details:
        court = next((c for c in courts if c.id == detail.court_id), None)
        if not court or not detail.bing_prices:
            continue
        try:
            prices = json.loads(detail.bing_prices)
            if not isinstance(prices, list):
                continue
            new_prices = []
            for item in prices:
                v = extract_price_value(item.get('price'))
                if v is None:
                    continue
                # 区间过滤
                if court.court_type == '室内':
                    if not (60 <= v <= 600):
                        continue
                    mean, std = indoor_mean, indoor_std
                elif court.court_type == '室外':
                    if not (50 <= v <= 300):
                        continue
                    mean, std = outdoor_mean, outdoor_std
                else:
                    if not (60 <= v <= 600):
                        continue
                    mean, std = indoor_mean, indoor_std
                # 格式标准化
                item['price'] = f'{v}元/小时'
                # 置信度赋值
                item['confidence'] = round(calc_confidence(v, mean, std), 3)
                new_prices.append(item)
            # 更新bing_prices
            detail.bing_prices = json.dumps(new_prices, ensure_ascii=False)
            # merged_prices同步处理BING来源
            if detail.merged_prices:
                try:
                    merged = json.loads(detail.merged_prices)
                    changed = False
                    for m in merged:
                        if m.get('source', '').upper().startswith('BING'):
                            v = extract_price_value(m.get('price'))
                            if v is None:
                                continue
                            if court.court_type == '室内' and not (60 <= v <= 600):
                                m['price'] = ''
                                m['confidence'] = 0.0
                                changed = True
                                continue
                            if court.court_type == '室外' and not (50 <= v <= 300):
                                m['price'] = ''
                                m['confidence'] = 0.0
                                changed = True
                                continue
                            # 格式标准化
                            m['price'] = f'{v}元/小时'
                            m['confidence'] = round(calc_confidence(v, mean, std), 3)
                            changed = True
                    if changed:
                        # 只保留有效BING价格
                        merged = [m for m in merged if m.get('price')]
                        detail.merged_prices = json.dumps(merged, ensure_ascii=False)
                except: pass
            db.commit()
            update_count += 1
        except Exception as e:
            print(f"❌ 处理court_id={detail.court_id}失败: {e}")
    print(f"\n✅ 清洗完成，更新 {update_count} 条记录")

if __name__ == '__main__':
    clean_all_bing_prices() 