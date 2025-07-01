#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试"得乐网球(欢乐谷网球场)"的预测修复
验证修复后的算法是否正确进行类型过滤
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import get_db
from app.models import TennisCourt, CourtDetail
from app.scrapers.price_predictor import PricePredictor
import json
from datetime import datetime

def test_delai_tennis_prediction_fix():
    print("🧪 测试'得乐网球(欢乐谷网球场)'的预测修复...")
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
    
    # 重新进行预测
    print(f"\n🔄 重新进行预测...")
    try:
        prediction = predictor.predict_price_for_court(target_court)
        
        if prediction and not prediction.get('predict_failed'):
            print(f"✅ 预测成功:")
            print(f"   黄金价格: {prediction.get('peak_price')}元")
            print(f"   非黄金价格: {prediction.get('off_peak_price')}元")
            print(f"   搜索半径: {prediction.get('search_radius')}KM")
            print(f"   样本数量: {prediction.get('data_count')}个")
            print(f"   预测方法: {prediction.get('predict_method')}")
            
            # 显示依赖样本
            source_courts = prediction.get('source_courts', [])
            if source_courts:
                print(f"\n📋 预测依赖样本:")
                for i, source in enumerate(source_courts, 1):
                    print(f"   [{i}] {source['name']} (距离: {source['distance']}KM)")
                    
                    # 获取依赖场馆的类型
                    source_court = predictor.db.query(TennisCourt).filter(TennisCourt.id == source['id']).first()
                    if source_court:
                        source_type = predictor.determine_court_type(source_court.name)
                        print(f"       类型: {source_type}")
                        
                        # 获取依赖场馆的价格信息
                        source_detail = predictor.db.query(CourtDetail).filter(CourtDetail.court_id == source['id']).first()
                        if source_detail and source_detail.merged_prices:
                            try:
                                source_prices = json.loads(source_detail.merged_prices)
                                if isinstance(source_prices, list) and len(source_prices) > 0:
                                    print(f"       价格: {source_prices[0].get('price', 'N/A')} ({source_prices[0].get('type', 'N/A')})")
                            except:
                                print(f"       价格: 解析失败")
            
            # 保存预测结果
            detail = predictor.db.query(CourtDetail).filter(CourtDetail.court_id == target_court.id).first()
            if not detail:
                detail = CourtDetail(court_id=target_court.id)
                predictor.db.add(detail)
                predictor.db.commit()
                predictor.db.refresh(detail)
            
            detail.predict_prices = json.dumps(prediction, ensure_ascii=False)
            predictor.db.commit()
            print(f"\n💾 预测结果已保存到数据库")
            
        elif prediction and prediction.get('predict_failed'):
            print(f"❌ 预测失败: {prediction.get('reason', '未知原因')}")
            
            # 保存失败结果
            detail = predictor.db.query(CourtDetail).filter(CourtDetail.court_id == target_court.id).first()
            if not detail:
                detail = CourtDetail(court_id=target_court.id)
                predictor.db.add(detail)
                predictor.db.commit()
                predictor.db.refresh(detail)
            
            detail.predict_prices = json.dumps(prediction, ensure_ascii=False)
            predictor.db.commit()
            print(f"\n💾 失败结果已保存到数据库")
            
        else:
            print(f"❌ 预测失败: 无预测结果")
            
    except Exception as e:
        print(f"❌ 预测异常: {e}")
    
    predictor.db.close()
    print(f"\n✅ 测试完成!")

if __name__ == "__main__":
    test_delai_tennis_prediction_fix() 