#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
批量重新计算所有场馆预测
使用修复后的6KM步进法算法（室外6KM，室内3-4KM）
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import get_db
from app.models import TennisCourt, CourtDetail
from app.scrapers.price_predictor import PricePredictor
import json
from datetime import datetime

def batch_recalculate_all_predictions():
    print("🔄 批量重新计算所有场馆预测...")
    print("📋 使用修复后的6KM步进法算法")
    print("   - 室外场馆：最大半径6KM，步进[1,2,3,4,5,6]")
    print("   - 室内场馆：核心区3KM，非核心区4KM")
    print("   - 严格同类型过滤")
    print("   - 支持综合报价类型")
    print("=" * 80)
    
    # 初始化预测器
    predictor = PricePredictor()
    
    # 获取所有场馆
    all_courts = predictor.db.query(TennisCourt).all()
    print(f"📊 总场馆数量: {len(all_courts)}")
    
    # 统计变量
    total_count = 0
    success_count = 0
    failed_count = 0
    no_data_count = 0
    
    # 按区域分组处理
    areas = {}
    for court in all_courts:
        area = getattr(court, 'area', 'unknown')
        if area not in areas:
            areas[area] = []
        areas[area].append(court)
    
    print(f"📋 按区域分组: {list(areas.keys())}")
    print("=" * 80)
    
    for area_name, courts in areas.items():
        print(f"\n🏘️ 处理区域: {area_name} ({len(courts)}个场馆)")
        
        for i, court in enumerate(courts, 1):
            total_count += 1
            
            print(f"\n  [{i}/{len(courts)}] {court.name}")
            
            # 判断场馆类型
            court_type = predictor.determine_court_type(court.name)
            print(f"    类型: {court_type}")
            
            # 预测价格
            try:
                prediction = predictor.predict_price_for_court(court)
                
                if prediction and not prediction.get('predict_failed'):
                    # 预测成功
                    success_count += 1
                    peak_price = prediction.get('peak_price')
                    off_peak_price = prediction.get('off_peak_price')
                    search_radius = prediction.get('search_radius')
                    data_count = prediction.get('data_count')
                    
                    print(f"    ✅ 预测成功: 黄金{peak_price}元, 非黄金{off_peak_price}元")
                    print(f"       搜索半径: {search_radius}KM, 样本数: {data_count}个")
                    
                    # 保存预测结果
                    detail = predictor.db.query(CourtDetail).filter(CourtDetail.court_id == court.id).first()
                    if not detail:
                        detail = CourtDetail(court_id=court.id)
                        predictor.db.add(detail)
                        predictor.db.commit()
                        predictor.db.refresh(detail)
                    
                    detail.predict_prices = json.dumps(prediction, ensure_ascii=False)
                    predictor.db.commit()
                    
                elif prediction and prediction.get('predict_failed'):
                    # 预测失败 - 数据不足
                    failed_count += 1
                    reason = prediction.get('reason', '未知原因')
                    print(f"    ❌ 预测失败: {reason}")
                    
                else:
                    # 其他原因失败
                    failed_count += 1
                    print(f"    ❌ 预测失败: 未知原因")
                    
            except Exception as e:
                failed_count += 1
                print(f"    ❌ 预测异常: {e}")
                try:
                    predictor.db.rollback()
                except:
                    pass
    
    # 统计结果
    print("\n" + "=" * 80)
    print("📊 批量预测完成统计:")
    print(f"   总场馆数: {total_count}")
    print(f"   预测成功: {success_count}")
    print(f"   预测失败: {failed_count}")
    print(f"   成功率: {success_count/(total_count or 1)*100:.1f}%")
    
    # 按区域统计
    print(f"\n📋 按区域统计:")
    for area_name, courts in areas.items():
        area_success = 0
        area_failed = 0
        for court in courts:
            detail = predictor.db.query(CourtDetail).filter(CourtDetail.court_id == court.id).first()
            if detail and detail.predict_prices:
                try:
                    predict_data = json.loads(detail.predict_prices)
                    if predict_data and not predict_data.get('predict_failed'):
                        area_success += 1
                    else:
                        area_failed += 1
                except:
                    area_failed += 1
            else:
                area_failed += 1
        
        area_total = len(courts)
        area_rate = area_success/(area_total or 1)*100
        print(f"   {area_name}: {area_success}/{area_total} ({area_rate:.1f}%)")
    
    predictor.db.close()
    print(f"\n✅ 批量重新计算完成!")

if __name__ == "__main__":
    batch_recalculate_all_predictions() 