#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查所有场馆预测状态
正确统计当前数据库中的预测结果
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import get_db
from app.models import TennisCourt, CourtDetail
from app.scrapers.price_predictor import PricePredictor
import json
from datetime import datetime

def check_all_courts_prediction_status():
    print("🔍 检查所有场馆预测状态...")
    print("📋 正确统计当前数据库中的预测结果")
    print("=" * 80)
    
    # 初始化预测器
    predictor = PricePredictor()
    
    # 获取所有场馆
    all_courts = predictor.db.query(TennisCourt).all()
    print(f"📊 总场馆数量: {len(all_courts)}")
    
    # 按区域分组
    areas = {}
    for court in all_courts:
        area = getattr(court, 'area', 'unknown')
        if area not in areas:
            areas[area] = []
        areas[area].append(court)
    
    # 统计变量
    total_count = 0
    success_count = 0
    failed_count = 0
    
    # 按类型统计
    type_stats = {'室内': {'total': 0, 'success': 0, 'failed': 0},
                  '室外': {'total': 0, 'success': 0, 'failed': 0},
                  '未知': {'total': 0, 'success': 0, 'failed': 0},
                  '': {'total': 0, 'success': 0, 'failed': 0}}  # 处理空字符串类型
    
    for area_name, courts in areas.items():
        print(f"\n🏘️ 区域: {area_name} ({len(courts)}个场馆)")
        
        area_success = 0
        area_failed = 0
        
        for court in courts:
            total_count += 1
            
            # 判断场馆类型
            court_type = predictor.determine_court_type(court.name)
            type_stats[court_type]['total'] += 1
            
            # 检查预测结果
            detail = predictor.db.query(CourtDetail).filter(CourtDetail.court_id == court.id).first()
            current_prediction = None
            if detail and detail.predict_prices:
                try:
                    current_prediction = json.loads(detail.predict_prices)
                except:
                    pass
            
            if current_prediction and not current_prediction.get('predict_failed'):
                success_count += 1
                area_success += 1
                type_stats[court_type]['success'] += 1
            else:
                failed_count += 1
                area_failed += 1
                type_stats[court_type]['failed'] += 1
        
        area_total = len(courts)
        area_rate = area_success/(area_total or 1)*100
        print(f"   成功: {area_success}/{area_total} ({area_rate:.1f}%)")
    
    # 总体统计
    print("\n" + "=" * 80)
    print("📊 总体预测结果统计:")
    print(f"   总场馆数: {total_count}")
    print(f"   预测成功: {success_count}")
    print(f"   预测失败: {failed_count}")
    print(f"   成功率: {success_count/(total_count or 1)*100:.1f}%")
    
    # 按类型统计
    print(f"\n📋 按场馆类型统计:")
    for court_type, stats in type_stats.items():
        if stats['total'] > 0:
            type_rate = stats['success']/(stats['total'] or 1)*100
            print(f"   {court_type}: {stats['success']}/{stats['total']} ({type_rate:.1f}%)")
    
    # 显示失败的场馆
    print(f"\n❌ 预测失败的场馆列表:")
    failed_courts = []
    for court in all_courts:
        detail = predictor.db.query(CourtDetail).filter(CourtDetail.court_id == court.id).first()
        current_prediction = None
        if detail and detail.predict_prices:
            try:
                current_prediction = json.loads(detail.predict_prices)
            except:
                pass
        
        if not (current_prediction and not current_prediction.get('predict_failed')):
            failed_courts.append(court)
    
    for i, court in enumerate(failed_courts, 1):
        court_type = predictor.determine_court_type(court.name)
        area = getattr(court, 'area', 'unknown')
        print(f"   [{i:2d}] {court.name} ({court_type}, {area})")
        
        # 检查失败原因
        detail = predictor.db.query(CourtDetail).filter(CourtDetail.court_id == court.id).first()
        if detail and detail.predict_prices:
            try:
                predict_data = json.loads(detail.predict_prices)
                if predict_data.get('predict_failed'):
                    reason = predict_data.get('reason', '未知原因')
                    print(f"       失败原因: {reason}")
            except:
                print(f"       预测数据解析失败")
        else:
            print(f"       无预测数据")
    
    predictor.db.close()
    print(f"\n✅ 检查完成!")

if __name__ == "__main__":
    check_all_courts_prediction_status() 