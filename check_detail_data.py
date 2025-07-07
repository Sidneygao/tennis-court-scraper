#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查详情数据
"""

from app.database import get_db
from app.models import CourtDetail

def check_detail_data():
    print("🔍 检查详情数据...")
    
    db = next(get_db())
    
    # 检查有地图图片的详情
    details_with_map = db.query(CourtDetail).filter(
        CourtDetail.map_image.isnot(None),
        CourtDetail.map_image != ''
    ).limit(5).all()
    
    print(f"📊 有地图图片的详情数量: {len(details_with_map)}")
    for detail in details_with_map:
        print(f"  场馆ID: {detail.court_id}, 地图: {detail.map_image}")
    
    # 检查有手动价格的详情
    details_with_manual = db.query(CourtDetail).filter(
        CourtDetail.manual_prices.isnot(None),
        CourtDetail.manual_prices != ''
    ).limit(5).all()
    
    print(f"📊 有手动价格的详情数量: {len(details_with_manual)}")
    for detail in details_with_manual:
        print(f"  场馆ID: {detail.court_id}, 手动价格: {detail.manual_prices[:100] if detail.manual_prices else None}")
    
    # 检查有手动备注的详情
    details_with_remark = db.query(CourtDetail).filter(
        CourtDetail.manual_remark.isnot(None),
        CourtDetail.manual_remark != ''
    ).limit(5).all()
    
    print(f"📊 有手动备注的详情数量: {len(details_with_remark)}")
    for detail in details_with_remark:
        print(f"  场馆ID: {detail.court_id}, 手动备注: {detail.manual_remark[:100] if detail.manual_remark else None}")

if __name__ == "__main__":
    check_detail_data() 