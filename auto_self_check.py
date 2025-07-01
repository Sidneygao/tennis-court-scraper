#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
自动自检脚本：当连续4次全局通用算法时，自动分析案例并改进数据和算法
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.scrapers.price_predictor import PricePredictor
from app.database import get_db
from app.models import TennisCourt, CourtDetail
import json
import sqlite3

def auto_self_check():
    print("🔍 自动自检：分析连续4次全局通用算法案例...")
    
    db = next(get_db())
    predictor = PricePredictor()
    
    # 获取所有场馆
    courts = db.query(TennisCourt).all()
    
    # 找到连续4次全局通用算法的案例
    consecutive_global_cases = []
    consecutive_count = 0
    
    for court in courts:
        detail = db.query(CourtDetail).filter(CourtDetail.court_id == court.id).first()
        if detail and detail.predict_prices:
            try:
                predict_data = json.loads(detail.predict_prices)
                if predict_data.get('source_courts') == '全局同类型均值预测':
                    consecutive_count += 1
                    consecutive_global_cases.append({
                        'court': court,
                        'predict_data': predict_data
                    })
                else:
                    consecutive_count = 0
                    consecutive_global_cases = []
                
                if consecutive_count >= 4:
                    break
            except:
                consecutive_count = 0
                consecutive_global_cases = []
    
    if len(consecutive_global_cases) < 4:
        print("❌ 未找到连续4次全局通用算法案例")
        return
    
    print(f"✅ 找到连续{len(consecutive_global_cases)}个全局通用算法案例")
    
    # 分析这4个案例
    for i, case in enumerate(consecutive_global_cases, 1):
        court = case['court']
        predict_data = case['predict_data']
        
        print(f"\n📊 案例{i}: {court.name} (ID: {court.id})")
        print(f"  场馆类型: {court.court_type}")
        print(f"  地址: {court.address}")
        print(f"  坐标: {court.latitude}, {court.longitude}")
        print(f"  预测价格: 黄金{predict_data.get('peak_price')}元, 非黄金{predict_data.get('off_peak_price')}元")
        
        # 检查附近是否有真实价格数据
        nearby_courts = predictor.find_nearby_courts_with_prices(court, 16.0)
        print(f"  16KM内有效数据场馆数: {len(nearby_courts)}")
        
        if len(nearby_courts) > 0:
            print("  附近有价格数据的场馆:")
            for nearby in nearby_courts[:3]:  # 只显示前3个
                nearby_court = nearby['court']
                distance = nearby['distance']
                print(f"    - {nearby_court.name} (距离: {distance:.1f}KM)")
        else:
            print("  ⚠️ 16KM内无有效价格数据")
    
    # 自动改进建议
    print(f"\n🔧 自动改进建议:")
    
    # 1. 检查是否需要补充BING价格数据
    print("1. 数据覆盖改进:")
    for case in consecutive_global_cases:
        court = case['court']
        detail = db.query(CourtDetail).filter(CourtDetail.court_id == court.id).first()
        
        if detail:
            bing_prices = detail.bing_prices
            merged_prices = detail.merged_prices
            
            if not bing_prices or bing_prices == '[]':
                print(f"   - {court.name}: 缺少BING价格数据，建议补充爬取")
            else:
                print(f"   - {court.name}: 已有BING价格数据")
    
    # 2. 检查邻域样本问题
    print("\n2. 邻域样本改进:")
    total_nearby = 0
    for case in consecutive_global_cases:
        court = case['court']
        nearby_courts = predictor.find_nearby_courts_with_prices(court, 16.0)
        total_nearby += len(nearby_courts)
        
        if len(nearby_courts) == 0:
            print(f"   - {court.name}: 16KM内无有效邻域样本，建议:")
            print(f"     * 检查附近场馆是否有真实价格数据")
            print(f"     * 考虑扩大搜索半径或降低数据质量要求")
    
    avg_nearby = total_nearby / len(consecutive_global_cases)
    print(f"   平均邻域样本数: {avg_nearby:.1f}")
    
    # 3. 算法参数调整建议
    print("\n3. 算法参数调整建议:")
    if avg_nearby < 2:
        print("   - 当前最小数据量要求(2家)过高，建议降低到1家")
        print("   - 或扩大最大搜索半径(当前16KM)")
    else:
        print("   - 邻域样本充足，问题可能在于数据质量或类型匹配")
    
    # 4. 自动执行改进措施
    print(f"\n🚀 自动执行改进措施:")
    
    # 检查是否需要补充BING价格
    need_bing_scrape = False
    for case in consecutive_global_cases:
        court = case['court']
        detail = db.query(CourtDetail).filter(CourtDetail.court_id == court.id).first()
        if detail and (not detail.bing_prices or detail.bing_prices == '[]'):
            need_bing_scrape = True
            break
    
    if need_bing_scrape:
        print("   - 检测到缺少BING价格数据，建议执行BING价格爬取")
        print("   - 执行命令: python bing_price_spider.py")
    
    # 检查是否需要调整算法参数
    if avg_nearby < 2:
        print("   - 建议调整预测算法参数:")
        print("     * 降低最小数据量要求")
        print("     * 或扩大搜索半径")
    
    print(f"\n✅ 自检完成！请根据建议执行相应改进措施。")

if __name__ == "__main__":
    auto_self_check() 