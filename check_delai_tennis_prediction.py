#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
查看"得乐网球(欢乐谷网球场)"的预测依赖
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import get_db
from app.models import TennisCourt, CourtDetail
from app.scrapers.price_predictor import PricePredictor
import json
from datetime import datetime

def check_delai_tennis_prediction():
    print("🔍 查看'得乐网球(欢乐谷网球场)'的预测依赖...")
    print("=" * 80)
    
    # 初始化预测器
    predictor = PricePredictor()
    
    # 查找目标场馆
    target_court = None
    for court in predictor.db.query(TennisCourt).all():
        if "得乐网球" in court.name and "欢乐谷" in court.name:
            target_court = court
            break
    
    if not target_court:
        print("❌ 未找到'得乐网球(欢乐谷网球场)'")
        return
    
    print(f"🏟️ 目标场馆: {target_court.name}")
    print(f"   区域: {getattr(target_court, 'area', 'unknown')}")
    print(f"   坐标: {target_court.latitude}, {target_court.longitude}")
    
    # 判断场馆类型
    court_type = predictor.determine_court_type(target_court.name)
    print(f"   类型: {court_type}")
    
    # 检查当前预测结果
    detail = predictor.db.query(CourtDetail).filter(CourtDetail.court_id == target_court.id).first()
    if detail and detail.predict_prices:
        try:
            predict_data = json.loads(detail.predict_prices)
            if predict_data and not predict_data.get('predict_failed'):
                print(f"\n📊 当前预测结果:")
                print(f"   黄金价格: {predict_data.get('peak_price')}元")
                print(f"   非黄金价格: {predict_data.get('off_peak_price')}元")
                print(f"   搜索半径: {predict_data.get('search_radius')}KM")
                print(f"   样本数量: {predict_data.get('data_count')}个")
                print(f"   预测方法: {predict_data.get('predict_method')}")
                
                # 显示依赖样本
                source_courts = predict_data.get('source_courts', [])
                if source_courts:
                    print(f"\n📋 预测依赖样本:")
                    for i, source in enumerate(source_courts, 1):
                        print(f"   [{i}] {source['name']} (距离: {source['distance']}KM)")
                        
                        # 获取依赖场馆的详细信息
                        source_detail = predictor.db.query(CourtDetail).filter(CourtDetail.court_id == source['id']).first()
                        if source_detail and source_detail.merged_prices:
                            try:
                                source_prices = json.loads(source_detail.merged_prices)
                                if isinstance(source_prices, list) and len(source_prices) > 0:
                                    print(f"       价格: {source_prices[0].get('price', 'N/A')} ({source_prices[0].get('type', 'N/A')})")
                            except:
                                print(f"       价格: 解析失败")
            else:
                print(f"\n❌ 预测失败: {predict_data.get('reason', '未知原因') if predict_data else '无预测数据'}")
        except Exception as e:
            print(f"\n❌ 预测数据解析失败: {e}")
    else:
        print(f"\n❌ 无预测数据")
    
    # 重新进行预测分析
    print(f"\n🔍 重新分析预测依赖:")
    
    # 查找1-6KM内的所有场馆（不区分类型）
    for radius in [1, 2, 3, 4, 5, 6]:
        nearby_all = predictor.find_nearby_courts_with_prices(target_court, radius, filter_by_type=False)
        nearby_same_type = predictor.find_nearby_courts_with_prices(target_court, radius, filter_by_type=True)
        
        print(f"\n   {radius}KM内:")
        print(f"     总场馆数: {len(nearby_all)}")
        print(f"     同类型({court_type})场馆数: {len(nearby_same_type)}")
        
        if len(nearby_all) > 0:
            print(f"     场馆列表:")
            for i, nearby in enumerate(nearby_all[:5], 1):  # 只显示前5个
                nearby_type = predictor.determine_court_type(nearby['court'].name)
                distance = nearby['distance']
                prices = nearby['prices']
                peak_price = prices.get('peak_price', 'N/A')
                off_peak_price = prices.get('off_peak_price', 'N/A')
                print(f"       [{i}] {nearby['court'].name} ({nearby_type}, {distance:.1f}KM)")
                print(f"           价格: 黄金{peak_price}元, 非黄金{off_peak_price}元")
        
        if len(nearby_same_type) >= 2:
            print(f"     ✅ 找到足够同类型样本，预测成功")
            break
        elif radius == 6 and len(nearby_same_type) < 2:
            print(f"     ❌ 6KM内同类型样本不足，无法预测")
    
    predictor.db.close()
    print(f"\n✅ 分析完成!")

if __name__ == "__main__":
    check_delai_tennis_prediction() 