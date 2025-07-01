#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
双井区域BING价格加工脚本：将BING爬取的价格进行置信度过滤和区间过滤后覆盖merged_prices
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import get_db
from app.models import TennisCourt, CourtDetail
from app.scrapers.price_confidence_model import PriceConfidenceModel
import json
import re
import numpy as np
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

def process_bing_prices_shuangjing():
    """加工双井区域BING价格并覆盖merged_prices"""
    print("🔄 开始加工双井区域BING价格...")
    
    db = next(get_db())
    confidence_model = PriceConfidenceModel()
    
    # 获取双井区域所有场馆
    courts = db.query(TennisCourt).filter(TennisCourt.area == 'shuangjing').all()
    
    processed_count = 0
    skipped_count = 0
    
    for court in courts:
        detail = db.query(CourtDetail).filter(CourtDetail.court_id == court.id).first()
        if not detail or not detail.bing_prices:
            skipped_count += 1
            continue
        
        try:
            bing_data = json.loads(detail.bing_prices)
            if not isinstance(bing_data, list) or len(bing_data) == 0:
                skipped_count += 1
                continue
            
            # 提取有效价格
            valid_prices = []
            for price in bing_data:
                price_value = extract_price_value(price.get('price', ''))
                if price_value:
                    # 区间过滤
                    if court.court_type == '室内':
                        if 60 <= price_value <= 600:
                            valid_prices.append(price_value)
                    elif court.court_type == '室外':
                        if 50 <= price_value <= 300:
                            valid_prices.append(price_value)
            
            if len(valid_prices) == 0:
                print(f"❌ {court.name}: 无有效价格数据")
                skipped_count += 1
                continue
            
            # 计算置信度权重（自定义规则覆盖）
            weights = []
            for price in valid_prices:
                if court.court_type == '室内':
                    if price == 100:
                        weights.append(0.1)
                    elif price == 150:
                        # 判断时段类型
                        # 这里只能用标准价，因为BING数据没有时段区分
                        weights.append(0.15)
                    else:
                        # 其它价格仍用原模型
                        weights.append(confidence_model.calculate_confidence(price, '室内', court.name))
                else:
                    weights.append(confidence_model.calculate_confidence(price, '室外', court.name))
            
            # 加权平均
            weighted_sum = sum(price * weight for price, weight in zip(valid_prices, weights))
            total_weight = sum(weights)
            
            if total_weight == 0:
                # 如果权重都为0，使用简单平均
                final_price = int(sum(valid_prices) / len(valid_prices))
                confidence = 0.5
            else:
                final_price = int(weighted_sum / total_weight)
                confidence = total_weight / len(weights)
            
            # 构建加工后的价格数据
            processed_price = {
                'type': '综合报价',
                'price': f'{final_price}元/小时',
                'confidence': round(confidence, 2),
                'sample_count': len(valid_prices),
                'source': 'BING_PROCESSED'
            }
            
            # 更新merged_prices
            detail.merged_prices = json.dumps([processed_price])
            db.commit()
            
            print(f"✅ {court.name}: {len(valid_prices)}个价格 → {final_price}元/小时 (置信度: {confidence:.2f})")
            processed_count += 1
            
        except Exception as e:
            print(f"❌ {court.name}: 处理失败 - {e}")
            skipped_count += 1
            continue
    
    print(f"\n📊 处理完成:")
    print(f"  成功处理: {processed_count} 个场馆")
    print(f"  跳过: {skipped_count} 个场馆")
    
    db.close()

if __name__ == "__main__":
    process_bing_prices_shuangjing() 