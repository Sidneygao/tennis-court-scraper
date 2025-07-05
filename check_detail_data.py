#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查本地详情数据
"""

from app.database import get_db, init_db
from app.models import TennisCourt, CourtDetail

def check_detail_data():
    """检查本地详情数据"""
    print("检查本地详情数据...")
    
    # 初始化数据库
    init_db()
    
    # 获取数据库会话
    db = next(get_db())
    
    # 查询场馆总数
    total_courts = db.query(TennisCourt).count()
    print(f"场馆总数: {total_courts}")
    
    # 查询详情总数
    total_details = db.query(CourtDetail).count()
    print(f"详情总数: {total_details}")
    
    # 查询有详情的场馆
    courts_with_details = db.query(TennisCourt).join(CourtDetail).count()
    print(f"有详情的场馆数: {courts_with_details}")
    
    # 显示前几个详情
    if total_details > 0:
        print("\n前3个详情:")
        details = db.query(CourtDetail).limit(3).all()
        for detail in details:
            court = db.query(TennisCourt).filter(TennisCourt.id == detail.court_id).first()
            print(f"  - {court.name if court else 'Unknown'} (ID: {detail.court_id})")
            print(f"    地图图片: {detail.map_image}")
            print(f"    评分: {detail.merged_rating}")
            print(f"    价格: {detail.merged_prices[:100] if detail.merged_prices else 'None'}...")
    else:
        print("\n没有详情数据")

if __name__ == "__main__":
    check_detail_data() 