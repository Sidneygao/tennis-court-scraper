#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
批量GeoJSON+2KM步进法预测所有无真实价格场馆的价格，类型计算严格按现有三层次模型
"""
import json
import sqlite3
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from app.scrapers.price_predictor import PricePredictor

def main():
    # 1. 读取所有场馆及其经纬度
    with open('real_courts_locations.geojson', 'r', encoding='utf-8') as f:
        geojson = json.load(f)
    
    courts = []
    for feature in geojson['features']:
        prop = feature['properties']
        courts.append({
            'court_id': prop['court_id'],
            'name': prop['name'],
            'lat': feature['geometry']['coordinates'][1],
            'lon': feature['geometry']['coordinates'][0],
        })
    
    # 2. 用三层次模型批量计算类型（不改逻辑）
    predictor = PricePredictor()
    for c in courts:
        c['court_type'] = predictor.judge_court_type(c['name'])
    
    # 3. 读取数据库，找出无真实价格的场馆
    conn = sqlite3.connect('data/courts.db')
    cursor = conn.cursor()
    cursor.execute("SELECT court_id FROM court_details WHERE merged_prices IS NULL")
    no_real_price_ids = set(row[0] for row in cursor.fetchall())
    
    # 4. 按类型分组，GeoJSON+2KM步进法预测
    results = []
    for c in courts:
        if c['court_id'] not in no_real_price_ids:
            continue
        pred = predictor.predict_price_for_court(c, courts)
        if pred:
            results.append({
                'court_id': c['court_id'],
                'court_type': c['court_type'],
                'peak_price_pred': pred['peak_price'],
                'offpeak_price_pred': pred['offpeak_price'],
                'neighbor_count': pred['neighbor_count'],
                'method': 'GeoJSON_2KM_Step'
            })
    
    # 5. 写入数据库predict_prices字段
    updated = 0
    for r in results:
        predict_prices = json.dumps({
            'peak_price': f"{r['peak_price_pred']}元/小时",
            'offpeak_price': f"{r['offpeak_price_pred']}元/小时",
            'prediction_method': r['method'],
            'neighbor_count': r['neighbor_count'],
            'court_type': r['court_type']
        }, ensure_ascii=False)
        cursor.execute("UPDATE court_details SET predict_prices=? WHERE court_id=?", (predict_prices, r['court_id']))
        updated += 1
    conn.commit()
    print(f"✅ 预测完成，已更新{updated}家场馆的predict_prices字段")

if __name__ == '__main__':
    main() 