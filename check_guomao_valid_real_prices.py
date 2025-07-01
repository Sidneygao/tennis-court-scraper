#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
统计并展示国贸地区当前符合新价格范围的真实价格样本数量和分布
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import SessionLocal
from app.models import TennisCourt, CourtDetail
import json

def check_guomao_valid_real_prices():
    """统计国贸地区符合新价格范围的真实价格样本"""
    db = SessionLocal()
    try:
        courts = db.query(TennisCourt).filter(TennisCourt.area == 'guomao').all()
        print("\n🔍 国贸地区真实价格样本分布（新规则）\n")
        indoor_prices = []
        outdoor_prices = []
        for court in courts:
            detail = db.query(CourtDetail).filter(CourtDetail.court_id == court.id).first()
            if detail and detail.merged_prices:
                try:
                    merged = json.loads(detail.merged_prices)
                    for item in merged:
                        if not item.get('is_predicted', True):
                            price_str = item.get('price', '')
                            try:
                                price = float(str(price_str).replace('¥','').replace('/小时',''))
                                if court.court_type == '室内' and 60 <= price <= 600:
                                    indoor_prices.append(price)
                                elif court.court_type == '室外' and 50 <= price <= 300:
                                    outdoor_prices.append(price)
                            except:
                                continue
                except:
                    continue
        print(f"🏠 室内真实价格样本（60-600元）: {len(indoor_prices)}个")
        if indoor_prices:
            print(f"  范围: {min(indoor_prices):.0f}-{max(indoor_prices):.0f}元")
            print(f"  分布: {sorted(indoor_prices)}")
        else:
            print("  无")
        print(f"\n🌳 室外真实价格样本（50-300元）: {len(outdoor_prices)}个")
        if outdoor_prices:
            print(f"  范围: {min(outdoor_prices):.0f}-{max(outdoor_prices):.0f}元")
            print(f"  分布: {sorted(outdoor_prices)}")
        else:
            print("  无")
    finally:
        db.close()

if __name__ == "__main__":
    check_guomao_valid_real_prices() 