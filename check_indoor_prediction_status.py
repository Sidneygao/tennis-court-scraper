#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查室内场馆预测状态
对比分析结果和批量重新计算结果的差异
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import get_db
from app.models import TennisCourt, CourtDetail
from app.scrapers.price_predictor import PricePredictor
import json
from datetime import datetime

def check_indoor_prediction_status():
    print("🔍 检查室内场馆预测状态...")
    print("📋 对比分析结果和批量重新计算结果的差异")
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
        else:
            failed_count += 1
            failed_courts.append(court)
    
    print(f"\n📊 当前数据库中的预测状态:")
    print(f"   预测成功: {success_count}")
    print(f"   预测失败: {failed_count}")
    print(f"   成功率: {success_count/(len(indoor_courts) or 1)*100:.1f}%")
    
    # 显示失败的场馆
    if failed_courts:
        print(f"\n❌ 预测失败的室内场馆:")
        for i, court in enumerate(failed_courts, 1):
            print(f"   [{i}] {court.name} ({getattr(court, 'area', 'unknown')})")
            
            # 检查预测结果
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
    
    # 重新测试几个场馆的预测
    print(f"\n🧪 重新测试几个场馆的预测:")
    test_courts = indoor_courts[:5]  # 测试前5个
    
    for i, court in enumerate(test_courts, 1):
        print(f"\n  [{i}] 测试场馆: {court.name}")
        
        try:
            prediction = predictor.predict_price_for_court(court)
            if prediction and not prediction.get('predict_failed'):
                peak_price = prediction.get('peak_price')
                off_peak_price = prediction.get('off_peak_price')
                search_radius = prediction.get('search_radius')
                data_count = prediction.get('data_count')
                print(f"     ✅ 预测成功: 黄金{peak_price}元, 非黄金{off_peak_price}元")
                print(f"        搜索半径: {search_radius}KM, 样本数: {data_count}个")
            else:
                reason = prediction.get('reason', '未知原因') if prediction else '无预测结果'
                print(f"     ❌ 预测失败: {reason}")
        except Exception as e:
            print(f"     ❌ 预测异常: {e}")
    
    predictor.db.close()
    print(f"\n✅ 检查完成!")

if __name__ == "__main__":
    check_indoor_prediction_status() 