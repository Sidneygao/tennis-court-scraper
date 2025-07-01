#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查数据库中真实价格的数量和分布
"""
import json
import sqlite3
from collections import defaultdict

def main():
    print("🔍 检查数据库中真实价格的数量和分布...")
    
    conn = sqlite3.connect('data/courts.db')
    cursor = conn.cursor()
    
    # 1. 统计有真实价格的场馆数量
    print("\n📊 真实价格统计:")
    cursor.execute("""
        SELECT COUNT(*) as total_courts
        FROM tennis_courts tc
        LEFT JOIN court_details cd ON tc.id = cd.court_id
        WHERE cd.merged_prices IS NOT NULL 
        AND cd.merged_prices != '' 
        AND cd.merged_prices != '[]'
        AND cd.merged_prices != 'null'
    """)
    
    total_with_prices = cursor.fetchone()[0]
    print(f"  有真实价格的场馆数: {total_with_prices}")
    
    # 2. 检查真实价格的具体内容
    print("\n🔍 检查真实价格内容:")
    cursor.execute("""
        SELECT tc.name, tc.latitude, tc.longitude, cd.merged_prices
        FROM tennis_courts tc
        LEFT JOIN court_details cd ON tc.id = cd.court_id
        WHERE cd.merged_prices IS NOT NULL 
        AND cd.merged_prices != '' 
        AND cd.merged_prices != '[]'
        AND cd.merged_prices != 'null'
        LIMIT 10
    """)
    
    samples = cursor.fetchall()
    print(f"  样本数量: {len(samples)}")
    
    real_price_count = 0
    predicted_price_count = 0
    
    for name, lat, lng, merged_prices in samples:
        print(f"\n🏟️ 场馆: {name}")
        print(f"  坐标: ({lat}, {lng})")
        
        try:
            prices = json.loads(merged_prices)
            if isinstance(prices, list):
                print(f"  价格项数: {len(prices)}")
                
                for i, item in enumerate(prices):
                    if isinstance(item, dict):
                        price_type = item.get('type', '')
                        price_value = item.get('price', '')
                        is_predicted = item.get('is_predicted', False)
                        confidence = item.get('confidence', 0)
                        
                        print(f"    {i+1}. {price_type}: {price_value}")
                        print(f"       预测: {is_predicted}, 置信度: {confidence}")
                        
                        if is_predicted:
                            predicted_price_count += 1
                        else:
                            real_price_count += 1
            else:
                print(f"  价格数据格式异常: {type(prices)}")
        except Exception as e:
            print(f"  解析失败: {e}")
    
    print(f"\n📈 价格类型统计:")
    print(f"  真实价格: {real_price_count} 个")
    print(f"  预测价格: {predicted_price_count} 个")
    
    # 3. 检查PricePredictor是否能正确识别真实价格
    print("\n🔍 测试PricePredictor的真实价格识别:")
    from app.scrapers.price_predictor import PricePredictor
    from app.database import get_db
    from app.models import TennisCourt, CourtDetail
    
    db = next(get_db())
    predictor = PricePredictor()
    
    # 获取几个样本场馆
    sample_courts = db.query(TennisCourt).join(
        CourtDetail, CourtDetail.court_id == TennisCourt.id
    ).filter(
        CourtDetail.merged_prices.isnot(None),
        CourtDetail.merged_prices != '[]',
        CourtDetail.merged_prices != 'null'
    ).limit(5).all()
    
    print(f"  测试样本数: {len(sample_courts)}")
    
    for court in sample_courts:
        print(f"\n🏟️ 测试场馆: {court.name}")
        
        # 获取详情
        detail = db.query(CourtDetail).filter(CourtDetail.court_id == court.id).first()
        if detail:
            real_prices = predictor._extract_real_prices(detail)
            print(f"  真实价格提取结果: {real_prices}")
            
            if real_prices:
                peak_price = real_prices.get('peak_price')
                off_peak_price = real_prices.get('off_peak_price')
                print(f"    黄金时段: {peak_price}")
                print(f"    非黄金时段: {off_peak_price}")
            else:
                print("    未提取到真实价格")
    
    conn.close()

if __name__ == "__main__":
    main() 