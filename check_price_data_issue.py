#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查后台价格数据问题，查看为什么所有场馆都显示为真实价格
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import SessionLocal
from app.models import TennisCourt, CourtDetail
import json

def check_price_data_issue():
    """检查后台价格数据问题"""
    db = SessionLocal()
    
    try:
        # 随机选择几个场馆检查
        courts = db.query(TennisCourt).limit(10).all()
        
        print("🔍 检查后台价格数据问题\\n")
        
        for court in courts:
            detail = db.query(CourtDetail).filter(CourtDetail.court_id == court.id).first()
            
            print(f"🏟️ 场馆: {court.name}")
            print(f"   类型: {court.court_type}")
            
            if detail:
                print(f"   merged_prices: {detail.merged_prices}")
                print(f"   predict_prices: {detail.predict_prices}")
                
                # 检查真实价格数据
                real_prices = []
                if detail.merged_prices:
                    try:
                        merged = json.loads(detail.merged_prices)
                        if merged and len(merged) > 0:
                            real_prices.extend(merged)
                    except:
                        pass
                
                if detail.bing_prices:
                    try:
                        bing = json.loads(detail.bing_prices)
                        if bing and len(bing) > 0:
                            real_prices.extend(bing)
                    except:
                        pass
                
                if detail.dianping_prices:
                    try:
                        dianping = json.loads(detail.dianping_prices)
                        if dianping and len(dianping) > 0:
                            real_prices.extend(dianping)
                    except:
                        pass
                
                if detail.meituan_prices:
                    try:
                        meituan = json.loads(detail.meituan_prices)
                        if meituan and len(meituan) > 0:
                            real_prices.extend(meituan)
                    except:
                        pass
                
                print(f"   真实价格数量: {len(real_prices)}")
                if real_prices:
                    print(f"   真实价格示例: {real_prices[:2]}")
                
                # 检查预测价格
                predict_prices = None
                if detail.predict_prices:
                    try:
                        predict_prices = json.loads(detail.predict_prices)
                        print(f"   预测价格: {predict_prices}")
                    except:
                        print(f"   预测价格解析失败")
                
                print()
            else:
                print(f"   无详情数据")
                print()
        
        # 统计整体情况
        print("\\n📊 整体统计:")
        
        total_courts = db.query(TennisCourt).count()
        courts_with_real_prices = 0
        courts_with_predict_prices = 0
        courts_with_both = 0
        
        all_courts = db.query(TennisCourt).all()
        
        for court in all_courts:
            detail = db.query(CourtDetail).filter(CourtDetail.court_id == court.id).first()
            if detail:
                has_real = False
                has_predict = False
                
                # 检查真实价格
                for field in [detail.merged_prices, detail.bing_prices, detail.dianping_prices, detail.meituan_prices]:
                    if field:
                        try:
                            data = json.loads(field)
                            if data and len(data) > 0:
                                has_real = True
                                break
                        except:
                            continue
                
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
                if has_real and has_predict:
                    courts_with_both += 1
        
        print(f"   总场馆数: {total_courts}")
        print(f"   有真实价格的场馆: {courts_with_real_prices}")
        print(f"   有预测价格的场馆: {courts_with_predict_prices}")
        print(f"   同时有真实和预测价格的场馆: {courts_with_both}")
        
    finally:
        db.close()

if __name__ == "__main__":
    check_price_data_issue() 