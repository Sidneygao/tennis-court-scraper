#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
检查缓存数据脚本
"""

import os
import sys
import json
import sqlite3
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from app.database import get_db
from app.models import TennisCourt, CourtDetail

def check_cache_data():
    """检查缓存数据"""
    print("=== 缓存数据检查 ===")
    
    db = next(get_db())
    
    # 总场馆数
    total_courts = db.query(TennisCourt).count()
    print(f"总场馆数: {total_courts}")
    
    # 有详情表的场馆数
    courts_with_details = db.query(CourtDetail).count()
    print(f"有详情表的场馆: {courts_with_details}")
    
    # 检查各种缓存字段
    print("\n=== 缓存字段统计 ===")
    
    # 有评论数据的场馆
    courts_with_reviews = db.query(CourtDetail).filter(
        CourtDetail.dianping_reviews.isnot(None)
    ).count()
    print(f"有点评评论的场馆: {courts_with_reviews}")
    
    # 有图片数据的场馆
    courts_with_images = db.query(CourtDetail).filter(
        CourtDetail.dianping_images.isnot(None)
    ).count()
    print(f"有点评图片的场馆: {courts_with_images}")
    
    # 有评分数据的场馆
    courts_with_rating = db.query(CourtDetail).filter(
        CourtDetail.dianping_rating.isnot(None)
    ).count()
    print(f"有点评评分的场馆: {courts_with_rating}")
    
    # 有价格数据的场馆（检查所有价格字段）
    courts_with_dianping_prices = db.query(CourtDetail).filter(
        CourtDetail.dianping_prices.isnot(None) & (CourtDetail.dianping_prices != '')
    ).count()
    print(f"有点评价格的场馆: {courts_with_dianping_prices}")
    
    courts_with_meituan_prices = db.query(CourtDetail).filter(
        CourtDetail.meituan_prices.isnot(None) & (CourtDetail.meituan_prices != '')
    ).count()
    print(f"有美团价格的场馆: {courts_with_meituan_prices}")
    
    # 统计需要爬取价格的场馆
    print("\n=== 需要爬取价格的场馆统计 ===")
    
    # 没有真实价格数据的场馆
    courts_without_real_prices = db.query(CourtDetail).filter(
        (CourtDetail.dianping_prices.is_(None) | (CourtDetail.dianping_prices == '')) &
        (CourtDetail.meituan_prices.is_(None) | (CourtDetail.meituan_prices == ''))
    ).count()
    print(f"没有真实价格数据的场馆: {courts_without_real_prices}")
    
    # 有详情表但没有真实价格的场馆
    courts_with_details_no_prices = db.query(CourtDetail).filter(
        (CourtDetail.dianping_prices.is_(None) | (CourtDetail.dianping_prices == '')) &
        (CourtDetail.meituan_prices.is_(None) | (CourtDetail.meituan_prices == ''))
    ).all()
    
    print(f"有详情表但无真实价格的场馆: {len(courts_with_details_no_prices)}")
    
    # 完全没有详情表的场馆
    all_court_ids = set(c.id for c in db.query(TennisCourt).all())
    detail_court_ids = set(d.court_id for d in db.query(CourtDetail).all())
    courts_without_details = all_court_ids - detail_court_ids
    print(f"完全没有详情表的场馆: {len(courts_without_details)}")
    
    print(f"总计需要爬取价格的场馆: {len(courts_with_details_no_prices) + len(courts_without_details)}")
    
    # 检查前几个有评论的场馆
    print("\n=== 前3个有评论数据的场馆 ===")
    details_with_reviews = db.query(CourtDetail).filter(
        CourtDetail.dianping_reviews.isnot(None)
    ).limit(3).all()
    
    for detail in details_with_reviews:
        court = db.query(TennisCourt).filter(TennisCourt.id == detail.court_id).first()
        print(f"场馆: {court.name if court else 'Unknown'}")
        print(f"  点评评分: {detail.dianping_rating}")
        print(f"  美团评分: {detail.meituan_rating}")
        print(f"  融合评分: {detail.merged_rating}")
        print(f"  点评价格: {detail.dianping_prices[:200] if detail.dianping_prices else 'None'}...")
        print(f"  美团价格: {detail.meituan_prices[:200] if detail.meituan_prices else 'None'}...")
        print(f"  融合价格: {detail.merged_prices[:200] if detail.merged_prices else 'None'}...")
        print("-" * 50)
    
    db.close()

def main():
    conn = sqlite3.connect('data/courts.db')
    cursor = conn.cursor()
    cursor.execute('SELECT COUNT(*) FROM court_details WHERE bing_prices IS NOT NULL AND bing_prices != "[]" AND bing_prices != ""')
    count = cursor.fetchone()[0]
    print(f"有效BING价格场馆数: {count}")
    conn.close()

if __name__ == "__main__":
    check_cache_data()
    main() 