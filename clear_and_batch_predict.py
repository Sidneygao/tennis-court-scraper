#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
清空predict_prices字段，然后用GeoJSON+2KM步进法批量预测
"""
import json
import sqlite3
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from app.scrapers.price_predictor import PricePredictor

def main():
    print("🗑️ 开始清空predict_prices字段...")
    
    # 1. 清空所有predict_prices字段
    conn = sqlite3.connect('data/courts.db')
    cursor = conn.cursor()
    cursor.execute("UPDATE court_details SET predict_prices = NULL")
    conn.commit()
    print("✅ predict_prices字段已清空")
    
    # 2. 读取所有场馆及其经纬度
    print("📖 读取GeoJSON数据...")
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
    
    print(f"📊 读取到{len(courts)}家场馆")
    
    # 3. 用三层次模型批量计算类型（不改逻辑）
    print("🏸 批量计算场馆类型...")
    predictor = PricePredictor()
    for c in courts:
        c['court_type'] = predictor.judge_court_type(c['name'])
    
    # 4. 读取数据库，找出无真实价格的场馆
    cursor.execute("SELECT court_id FROM court_details WHERE merged_prices IS NULL")
    no_real_price_ids = set(row[0] for row in cursor.fetchall())
    print(f"📋 无真实价格的场馆数量: {len(no_real_price_ids)}")
    
    # 5. 按类型分组，GeoJSON+2KM步进法预测
    print("🔄 开始批量预测...")
    results = []
    success_count = 0
    failed_count = 0
    
    for c in courts:
        if c['court_id'] not in no_real_price_ids:
            continue
            
        try:
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
                success_count += 1
            else:
                failed_count += 1
        except Exception as e:
            print(f"❌ 预测失败 {c['name']}: {e}")
            failed_count += 1
    
    # 6. 写入数据库predict_prices字段
    print("💾 写入数据库...")
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
    
    print(f"\n✅ 批量预测完成!")
    print(f"成功预测: {success_count} 家")
    print(f"预测失败: {failed_count} 家")
    print(f"已更新数据库: {updated} 家")
    
    conn.close()

if __name__ == '__main__':
    main() 