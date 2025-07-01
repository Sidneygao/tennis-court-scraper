#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
验证清理结果并检查价格显示问题
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import SessionLocal
from app.models import TennisCourt, CourtDetail
import json

def verify_cleanup_results():
    """验证清理结果并检查价格显示问题"""
    db = SessionLocal()
    
    try:
        # 获取清理后的场馆
        all_courts = db.query(TennisCourt).all()
        
        print(f"🔍 验证清理结果\\n")
        print(f"清理后总场馆数: {len(all_courts)}")
        
        # 检查是否还有重复
        court_names = [court.name for court in all_courts]
        unique_names = set(court_names)
        print(f"唯一场馆名称数: {len(unique_names)}")
        print(f"是否还有重复: {'是' if len(court_names) != len(unique_names) else '否'}")
        
        # 检查游泳池场馆
        swimming_pools = [court for court in all_courts if '游泳池' in court.name]
        print(f"\\n🏊 游泳池场馆:")
        for court in swimming_pools:
            print(f"   ID: {court.id}, 名称: {court.name}, 类型: {court.court_type}")
        
        # 检查价格数据情况
        print(f"\\n💰 价格数据检查:")
        
        courts_with_real_prices = 0
        courts_with_predict_prices = 0
        courts_with_bing_only = 0
        
        for court in all_courts:
            detail = db.query(CourtDetail).filter(CourtDetail.court_id == court.id).first()
            if detail:
                has_real = False
                has_predict = False
                has_bing_only = False
                
                # 检查真实价格（非BING）
                if detail.merged_prices:
                    try:
                        prices = json.loads(detail.merged_prices)
                        if prices and len(prices) > 0:
                            # 检查是否有非BING的价格
                            non_bing_prices = [p for p in prices if p.get('source') != 'BING']
                            if non_bing_prices:
                                has_real = True
                            else:
                                has_bing_only = True
                    except:
                        pass
                
                # 检查预测价格
                if detail.predict_prices:
                    try:
                        predict_data = json.loads(detail.predict_prices)
                        if predict_data and (predict_data.get('peak_price') or predict_data.get('off_peak_price')):
                            has_predict = True
                    except:
                        pass
                
                if has_real:
                    courts_with_real_prices += 1
                if has_predict:
                    courts_with_predict_prices += 1
                if has_bing_only:
                    courts_with_bing_only += 1
        
        print(f"   有真实价格（非BING）的场馆: {courts_with_real_prices}")
        print(f"   只有BING价格的场馆: {courts_with_bing_only}")
        print(f"   有预测价格的场馆: {courts_with_predict_prices}")
        
        # 检查几个具体场馆的价格数据
        print(f"\\n🔍 具体场馆价格数据示例:")
        sample_courts = all_courts[:5]
        
        for court in sample_courts:
            detail = db.query(CourtDetail).filter(CourtDetail.court_id == court.id).first()
            print(f"\\n🏟️ {court.name} (ID: {court.id})")
            print(f"   类型: {court.court_type}")
            
            if detail:
                if detail.merged_prices:
                    try:
                        prices = json.loads(detail.merged_prices)
                        if prices and len(prices) > 0:
                            sources = [p.get('source', '未知') for p in prices[:3]]
                            print(f"   价格来源: {sources}")
                            print(f"   价格数量: {len(prices)}")
                    except:
                        print(f"   价格数据解析失败")
                
                if detail.predict_prices:
                    try:
                        predict_data = json.loads(detail.predict_prices)
                        if predict_data:
                            print(f"   预测价格: 黄金{predict_data.get('peak_price')}元, 非黄金{predict_data.get('off_peak_price')}元")
                    except:
                        print(f"   预测价格解析失败")
            else:
                print(f"   无详情数据")
        
    finally:
        db.close()

if __name__ == "__main__":
    verify_cleanup_results() 