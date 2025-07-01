#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
统计全市各区域室内场馆的merged_prices均值/中位数/分布、预测价格均值/中位数/分布，并分析预测与样本均值的偏差。
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import get_db
from app.models import TennisCourt, CourtDetail
import json
from collections import defaultdict

def extract_price_value(price_str):
    if not price_str:
        return None
    try:
        return int(float(str(price_str).replace('元','').replace('/小时','').replace('￥','').replace('¥','')))
    except:
        return None

def analyze_all_area_indoor_prediction():
    print("🔍 统计全市各区域室内场馆价格分布与预测偏差...")
    db = next(get_db())
    
    # 统计结构
    area_stats = defaultdict(lambda: {'merged': [], 'predict': []})
    
    courts = db.query(TennisCourt).all()
    for court in courts:
        if court.court_type != '室内' or not court.area:
            continue
        detail = db.query(CourtDetail).filter(CourtDetail.court_id == court.id).first()
        if not detail:
            continue
        # merged_prices
        if detail.merged_prices:
            try:
                merged_data = json.loads(detail.merged_prices)
                if isinstance(merged_data, list):
                    for price in merged_data:
                        if price.get('source') == 'BING_PROCESSED':
                            v = extract_price_value(price.get('price',''))
                            if v: area_stats[court.area]['merged'].append(v)
            except: pass
        # predict_prices
        if detail.predict_prices:
            try:
                predict_data = json.loads(detail.predict_prices)
                v = predict_data.get('peak_price')
                if v: area_stats[court.area]['predict'].append(v)
            except: pass
    
    # 输出统计
    print(f"{'区域':<10}{'样本数':>6}{'merged均值':>10}{'merged中位':>10}{'预测均值':>10}{'预测中位':>10}{'偏差(%)':>10}")
    for area, stat in sorted(area_stats.items(), key=lambda x: -len(x[1]['merged'])):
        merged = stat['merged']
        predict = stat['predict']
        if not merged or not predict:
            continue
        merged_mean = sum(merged)/len(merged)
        merged_median = sorted(merged)[len(merged)//2]
        predict_mean = sum(predict)/len(predict)
        predict_median = sorted(predict)[len(predict)//2]
        bias = (predict_mean-merged_mean)/merged_mean*100
        print(f"{area:<10}{len(merged):>6}{merged_mean:>10.0f}{merged_median:>10}{predict_mean:>10.0f}{predict_median:>10}{bias:>10.1f}")
    db.close()

if __name__ == "__main__":
    analyze_all_area_indoor_prediction() 