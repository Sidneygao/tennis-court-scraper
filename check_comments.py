#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
检查评论数据缓存情况
"""

import sys
import os
import json
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import get_db
from app.models import TennisCourt, CourtDetail

def check_comments_cache():
    """检查评论数据缓存情况"""
    print("🔍 检查评论数据缓存情况...")
    print("=" * 60)
    
    db = next(get_db())
    
    # 检查所有场馆的评论数据
    courts = db.query(TennisCourt).all()
    
    total_courts = len(courts)
    dianping_comments_count = 0
    meituan_comments_count = 0
    no_comments_count = 0
    
    print(f"总场馆数: {total_courts}")
    print("\n📊 评论数据统计:")
    print("-" * 40)
    
    for court in courts:
        detail = db.query(CourtDetail).filter(CourtDetail.court_id == court.id).first()
        
        has_dianping = False
        has_meituan = False
        
        if detail:
            # 检查点评评论
            if detail.dianping_reviews:
                try:
                    dianping_data = json.loads(detail.dianping_reviews)
                    if dianping_data and len(dianping_data) > 0:
                        has_dianping = True
                        dianping_comments_count += 1
                except:
                    pass
            
            # 检查美团评论
            if detail.meituan_reviews:
                try:
                    meituan_data = json.loads(detail.meituan_reviews)
                    if meituan_data and len(meituan_data) > 0:
                        has_meituan = True
                        meituan_comments_count += 1
                except:
                    pass
        
        if not has_dianping and not has_meituan:
            no_comments_count += 1
            
        # 显示前5个场馆的详细信息
        if court.id <= 5:
            print(f"场馆 {court.id}: {court.name}")
            print(f"  点评评论: {'有' if has_dianping else '无'}")
            print(f"  美团评论: {'有' if has_meituan else '无'}")
            if has_dianping:
                try:
                    dianping_data = json.loads(detail.dianping_reviews)
                    print(f"  点评评论数: {len(dianping_data)}")
                except:
                    pass
            if has_meituan:
                try:
                    meituan_data = json.loads(detail.meituan_reviews)
                    print(f"  美团评论数: {len(meituan_data)}")
                except:
                    pass
            print()
    
    print(f"📈 评论数据分布:")
    print(f"  有点评评论: {dianping_comments_count}个 ({dianping_comments_count/total_courts*100:.1f}%)")
    print(f"  有美团评论: {meituan_comments_count}个 ({meituan_comments_count/total_courts*100:.1f}%)")
    print(f"  无任何评论: {no_comments_count}个 ({no_comments_count/total_courts*100:.1f}%)")
    
    # 检查评论爬取状态
    print(f"\n🔍 评论爬取状态检查:")
    print("-" * 40)
    
    # 检查是否有评论爬虫相关的文件
    comment_files = [
        "app/scrapers/dianping_scraper.py",
        "app/scrapers/meituan_scraper.py", 
        "app/scrapers/xiaohongshu_smart.py"
    ]
    
    for file_path in comment_files:
        if os.path.exists(file_path):
            print(f"✅ 找到评论爬虫: {file_path}")
        else:
            print(f"❌ 缺少评论爬虫: {file_path}")
    
    db.close()
    print("\n✅ 检查完成!")

if __name__ == "__main__":
    check_comments_cache() 