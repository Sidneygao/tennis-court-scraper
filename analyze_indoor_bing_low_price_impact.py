#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
统计全市各区域室内BING原始价格低于150元的分布、占比及其对merged均值和预测的影响。
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

def analyze_indoor_bing_low_price_impact():
    print("🔍 统计全市各区域室内BING原始低价分布及影响...")
    db = next(get_db())
    
    area_stats = defaultdict(lambda: {'bing': [], 'bing_low': [], 'merged': [], 'predict': []})
    
    courts = db.query(TennisCourt).all()
    for court in courts:
        if court.court_type != '室内' or not court.area:
            continue
        detail = db.query(CourtDetail).filter(CourtDetail.court_id == court.id).first()
        if not detail:
            continue
        # BING原始价格
        if detail.bing_prices:
            try:
                bing_data = json.loads(detail.bing_prices)
                if isinstance(bing_data, list):
                    for price in bing_data:
                        v = extract_price_value(price.get('price',''))
                        if v:
                            area_stats[court.area]['bing'].append(v)
                            if v < 150:
                                area_stats[court.area]['bing_low'].append(v)
            except: pass
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
    
    print(f"{'区域':<10}{'BING低价数':>8}{'BING总数':>8}{'低价占比%':>10}{'merged均值':>10}{'预测均值':>10}")
    for area, stat in sorted(area_stats.items(), key=lambda x: -len(x[1]['bing'])):
        bing = stat['bing']
        bing_low = stat['bing_low']
        merged = stat['merged']
        predict = stat['predict']
        if not bing or not merged or not predict:
            continue
        low_ratio = len(bing_low)/len(bing)*100 if bing else 0
        merged_mean = sum(merged)/len(merged)
        predict_mean = sum(predict)/len(predict)
        print(f"{area:<10}{len(bing_low):>8}{len(bing):>8}{low_ratio:>10.1f}{merged_mean:>10.0f}{predict_mean:>10.0f}")
    db.close()

if __name__ == "__main__":
    analyze_indoor_bing_low_price_impact() 