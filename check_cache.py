#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
检查详情数据缓存状态
"""

from app.database import SessionLocal
from app.models import CourtDetail, TennisCourt
from datetime import datetime

def check_cache_status():
    """检查缓存状态"""
    db = SessionLocal()
    
    try:
        # 获取所有详情记录
        details = db.query(CourtDetail).all()
        
        print("=" * 60)
        print("🎾 详情数据缓存状态检查")
        print("=" * 60)
        
        if not details:
            print("❌ 数据库中没有缓存任何详情数据")
            return
        
        print(f"✅ 当前缓存了 {len(details)} 条详情数据")
        print()
        
        # 统计缓存状态
        valid_cache = 0
        expired_cache = 0
        no_cache = 0
        
        for detail in details:
            # 获取场馆信息
            court = db.query(TennisCourt).filter(TennisCourt.id == detail.court_id).first()
            court_name = court.name if court else f"场馆ID:{detail.court_id}"
            
            # 检查缓存是否有效
            if detail.cache_expires_at:
                if detail.cache_expires_at > datetime.now():
                    valid_cache += 1
                    status = "✅ 有效"
                else:
                    expired_cache += 1
                    status = "⚠️ 已过期"
            else:
                no_cache += 1
                status = "❌ 无缓存"
            
            # 显示详细信息
            print(f"场馆: {court_name}")
            print(f"  状态: {status}")
            print(f"  最后更新: {detail.updated_at}")
            if detail.cache_expires_at:
                print(f"  缓存过期: {detail.cache_expires_at}")
            print(f"  描述: {detail.merged_description[:50] if detail.merged_description else '无'}...")
            print(f"  评分: {detail.merged_rating}")
            print("-" * 40)
        
        print("\n📊 缓存统计:")
        print(f"  有效缓存: {valid_cache} 条")
        print(f"  过期缓存: {expired_cache} 条")
        print(f"  无缓存: {no_cache} 条")
        print(f"  总计: {len(details)} 条")
        
        # 检查是否有"该数据不能获得"的记录
        unavailable_count = 0
        for detail in details:
            if detail.merged_description and "该数据不能获得" in detail.merged_description:
                unavailable_count += 1
        
        if unavailable_count > 0:
            print(f"\n⚠️ 发现 {unavailable_count} 条记录显示'该数据不能获得'")
        
    except Exception as e:
        print(f"❌ 检查缓存状态时出错: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    check_cache_status() 