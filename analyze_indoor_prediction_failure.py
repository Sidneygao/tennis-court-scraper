#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
分析室内场馆预测失败原因
对比修复前后的差异
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import get_db
from app.models import TennisCourt, CourtDetail
from app.scrapers.price_predictor import PricePredictor
import json
from datetime import datetime

def analyze_indoor_prediction_failure():
    print("🔍 分析室内场馆预测失败原因...")
    print("📋 对比修复前后的差异")
    print("=" * 80)
    
    # 初始化预测器
    predictor = PricePredictor()
    
    # 获取所有室内场馆
    indoor_courts = []
    for court in predictor.db.query(TennisCourt).all():
        court_type = predictor.determine_court_type(court.name)
        if court_type == '室内':
            indoor_courts.append(court)
    
    print(f"📊 室内场馆总数: {len(indoor_courts)}")
    
    # 统计预测结果
    success_count = 0
    failed_count = 0
    failed_courts = []
    
    for court in indoor_courts:
        print(f"\n🏟️ 分析场馆: {court.name} ({getattr(court, 'area', 'unknown')})")
        
        # 检查当前预测结果
        detail = predictor.db.query(CourtDetail).filter(CourtDetail.court_id == court.id).first()
        current_prediction = None
        if detail and detail.predict_prices:
            try:
                current_prediction = json.loads(detail.predict_prices)
            except:
                pass
        
        if current_prediction and not current_prediction.get('predict_failed'):
            success_count += 1
            print(f"   ✅ 当前预测成功")
        else:
            failed_count += 1
            failed_courts.append(court)
            print(f"   ❌ 当前预测失败")
            
            # 分析失败原因
            try:
                # 模拟修复前的算法（不做类型过滤）
                print(f"   🔍 分析失败原因...")
                
                # 查找3KM内所有场馆（不区分类型）
                nearby_all = predictor.find_nearby_courts_with_prices(court, 3, filter_by_type=False)
                print(f"      3KM内总场馆数: {len(nearby_all)}")
                
                # 查找3KM内同类型场馆
                nearby_same_type = predictor.find_nearby_courts_with_prices(court, 3, filter_by_type=True)
                print(f"      3KM内同类型场馆数: {len(nearby_same_type)}")
                
                if len(nearby_all) >= 2 and len(nearby_same_type) < 2:
                    print(f"      💡 原因确认：修复前有{len(nearby_all)}个样本，修复后只有{len(nearby_same_type)}个同类型样本")
                    print(f"      📝 修复前依赖了不同类型场馆作为样本")
                    
                    # 显示依赖的场馆类型
                    type_count = {}
                    for nearby in nearby_all:
                        nearby_type = predictor.determine_court_type(nearby['court'].name)
                        type_count[nearby_type] = type_count.get(nearby_type, 0) + 1
                    
                    print(f"      📊 依赖样本类型分布: {type_count}")
                    
                elif len(nearby_same_type) < 2:
                    print(f"      💡 原因：3KM内确实没有足够的同类型样本")
                    
            except Exception as e:
                print(f"      ❌ 分析异常: {e}")
    
    # 统计结果
    print("\n" + "=" * 80)
    print("📊 室内场馆预测结果统计:")
    print(f"   总室内场馆数: {len(indoor_courts)}")
    print(f"   预测成功: {success_count}")
    print(f"   预测失败: {failed_count}")
    print(f"   成功率: {success_count/(len(indoor_courts) or 1)*100:.1f}%")
    
    # 按区域统计失败情况
    print(f"\n📋 按区域统计失败情况:")
    area_failures = {}
    for court in failed_courts:
        area = getattr(court, 'area', 'unknown')
        if area not in area_failures:
            area_failures[area] = []
        area_failures[area].append(court)
    
    for area, courts in area_failures.items():
        print(f"   {area}: {len(courts)}个失败")
    
    # 详细分析几个典型失败案例
    print(f"\n🔍 典型失败案例详细分析:")
    for i, court in enumerate(failed_courts[:5], 1):
        print(f"\n  [{i}] {court.name} ({getattr(court, 'area', 'unknown')})")
        
        # 查找1-3KM内的所有场馆
        for radius in [1, 2, 3]:
            nearby_all = predictor.find_nearby_courts_with_prices(court, radius, filter_by_type=False)
            nearby_same_type = predictor.find_nearby_courts_with_prices(court, radius, filter_by_type=True)
            
            print(f"     {radius}KM内: 总{len(nearby_all)}个, 同类型{len(nearby_same_type)}个")
            
            if len(nearby_all) >= 2 and len(nearby_same_type) < 2:
                # 显示依赖的场馆
                print(f"     依赖场馆:")
                for nearby in nearby_all[:3]:  # 只显示前3个
                    nearby_type = predictor.determine_court_type(nearby['court'].name)
                    distance = nearby['distance']
                    print(f"       - {nearby['court'].name} ({nearby_type}, {distance:.1f}KM)")
    
    predictor.db.close()
    print(f"\n✅ 分析完成!")

if __name__ == "__main__":
    analyze_indoor_prediction_failure() 