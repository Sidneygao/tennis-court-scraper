#!/usr/bin/env python3
"""
检查预测价格数据
"""

from app.database import SessionLocal
from app.models import TennisCourt, CourtDetail
import json

def check_predict_prices():
    db = SessionLocal()
    try:
        # 查找动之光网球馆
        court = db.query(TennisCourt).filter(TennisCourt.name.like('%动之光%')).first()
        if court:
            print(f"场馆: {court.name}")
            print(f"场馆ID: {court.id}")
            
            detail = db.query(CourtDetail).filter(CourtDetail.court_id == court.id).first()
            if detail and detail.predict_prices:
                predict_prices = json.loads(detail.predict_prices)
                print(f"预测价格数据类型: {type(predict_prices)}")
                print(f"预测价格数据: {predict_prices}")
                
                # 检查是否是字典格式
                if isinstance(predict_prices, dict):
                    print("\n预测价格字段:")
                    for key, value in predict_prices.items():
                        print(f"  {key}: {value}")
                        
                    # 检查是否有实际价格字段
                    if 'peak_price' in predict_prices:
                        print(f"\n黄金时段价格: {predict_prices['peak_price']}")
                    if 'off_peak_price' in predict_prices:
                        print(f"非黄金时段价格: {predict_prices['off_peak_price']}")
                        
                elif isinstance(predict_prices, list):
                    print("\n预测价格列表:")
                    for i, item in enumerate(predict_prices):
                        print(f"  {i+1}. {item}")
            else:
                print("没有预测价格数据")
        
        # 检查几个场馆的预测价格结构
        print("\n=== 检查预测价格结构 ===")
        test_courts = db.query(TennisCourt).limit(3).all()
        for court in test_courts:
            detail = db.query(CourtDetail).filter(CourtDetail.court_id == court.id).first()
            if detail and detail.predict_prices:
                predict_prices = json.loads(detail.predict_prices)
                print(f"\n{court.name}:")
                print(f"  数据类型: {type(predict_prices)}")
                if isinstance(predict_prices, dict):
                    print(f"  字段: {list(predict_prices.keys())}")
                    if 'peak_price' in predict_prices:
                        print(f"  黄金时段: {predict_prices['peak_price']}")
                    if 'off_peak_price' in predict_prices:
                        print(f"  非黄金时段: {predict_prices['off_peak_price']}")
        
    finally:
        db.close()

if __name__ == "__main__":
    check_predict_prices() 