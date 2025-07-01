#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
输出shuangjing区域所有场馆的predict_prices依赖样本及其最新merged价格，验证依赖链和数据是否同步刷新。
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import get_db
from app.models import TennisCourt, CourtDetail
import json

def extract_price_value(price_str):
    if not price_str:
        return None
    try:
        return int(float(str(price_str).replace('元','').replace('/小时','').replace('￥','').replace('¥','')))
    except:
        return None

def debug_shuangjing_prediction_chain():
    print("🔍 检查shuangjing区域预测依赖链和样本merged价格...")
    db = next(get_db())
    courts = db.query(TennisCourt).filter(TennisCourt.area == 'shuangjing').all()
    for court in courts:
        detail = db.query(CourtDetail).filter(CourtDetail.court_id == court.id).first()
        if not detail or not detail.predict_prices:
            continue
        try:
            predict_data = json.loads(detail.predict_prices)
        except:
            continue
        print(f"\n🏟️ {court.name} (ID: {court.id})")
        print(f"  预测价格: 黄金{predict_data.get('peak_price')}元, 非黄金{predict_data.get('off_peak_price')}元")
        print(f"  依赖样本:")
        source_courts = predict_data.get('source_courts', [])
        for i, source in enumerate(source_courts):
            name = source.get('name','')
            distance = source.get('distance','')
            # 查找依赖样本的merged价格
            sample_court = db.query(TennisCourt).filter(TennisCourt.name == name).first()
            merged_price = None
            if sample_court:
                sample_detail = db.query(CourtDetail).filter(CourtDetail.court_id == sample_court.id).first()
                if sample_detail and sample_detail.merged_prices:
                    try:
                        merged_data = json.loads(sample_detail.merged_prices)
                        if isinstance(merged_data, list):
                            for price in merged_data:
                                if price.get('source') == 'BING_PROCESSED':
                                    merged_price = extract_price_value(price.get('price',''))
                                    break
                    except: pass
            print(f"    {i+1}. {name} (距离: {distance}KM) merged价格: {merged_price if merged_price else '无'}")
    db.close()

if __name__ == "__main__":
    debug_shuangjing_prediction_chain() 