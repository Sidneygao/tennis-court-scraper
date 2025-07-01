#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
清理重复场馆时合并有效数据，保留每个场馆名称的第一个记录
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import SessionLocal
from app.models import TennisCourt, CourtDetail
from collections import defaultdict
import json

def merge_court_data(kept_court, duplicate_courts):
    """合并场馆数据，将重复场馆的有效数据合并到保留的场馆中"""
    # 合并基本信息
    for duplicate in duplicate_courts:
        # 如果保留的场馆缺少某些信息，从重复场馆中补充
        if not kept_court.phone and duplicate.phone:
            kept_court.phone = duplicate.phone
        if not kept_court.address and duplicate.address:
            kept_court.address = duplicate.address
        if not kept_court.court_type and duplicate.court_type:
            kept_court.court_type = duplicate.court_type
        if not kept_court.area and duplicate.area:
            kept_court.area = duplicate.area
        if not kept_court.latitude and duplicate.latitude:
            kept_court.latitude = duplicate.latitude
        if not kept_court.longitude and duplicate.longitude:
            kept_court.longitude = duplicate.longitude

def merge_detail_data(kept_detail, duplicate_details):
    """合并详情数据，将重复场馆详情中的有效数据合并到保留的详情中"""
    for duplicate in duplicate_details:
        if not duplicate:
            continue
            
        # 合并价格数据 - 优先保留非BING的价格数据
        if not kept_detail.merged_prices and duplicate.merged_prices:
            kept_detail.merged_prices = duplicate.merged_prices
        elif kept_detail.merged_prices and duplicate.merged_prices:
            # 如果两者都有价格数据，检查是否有非BING的价格
            try:
                kept_prices = json.loads(kept_detail.merged_prices) if kept_detail.merged_prices else []
                dup_prices = json.loads(duplicate.merged_prices) if duplicate.merged_prices else []
                
                # 检查是否有非BING的价格数据
                kept_has_non_bing = any(p.get('source') != 'BING' for p in kept_prices)
                dup_has_non_bing = any(p.get('source') != 'BING' for p in dup_prices)
                
                # 如果保留的记录只有BING价格，而重复记录有非BING价格，则使用重复记录
                if not kept_has_non_bing and dup_has_non_bing:
                    kept_detail.merged_prices = duplicate.merged_prices
            except:
                pass
        
        # 合并其他详情字段
        if not kept_detail.dianping_prices and duplicate.dianping_prices:
            kept_detail.dianping_prices = duplicate.dianping_prices
        if not kept_detail.meituan_prices and duplicate.meituan_prices:
            kept_detail.meituan_prices = duplicate.meituan_prices
        if not kept_detail.bing_prices and duplicate.bing_prices:
            kept_detail.bing_prices = duplicate.bing_prices
        if not kept_detail.predict_prices and duplicate.predict_prices:
            kept_detail.predict_prices = duplicate.predict_prices
        
        # 合并评分和评论
        if not kept_detail.dianping_rating and duplicate.dianping_rating:
            kept_detail.dianping_rating = duplicate.dianping_rating
        if not kept_detail.meituan_rating and duplicate.meituan_rating:
            kept_detail.meituan_rating = duplicate.meituan_rating
        if not kept_detail.merged_rating and duplicate.merged_rating:
            kept_detail.merged_rating = duplicate.merged_rating
        
        if not kept_detail.dianping_reviews and duplicate.dianping_reviews:
            kept_detail.dianping_reviews = duplicate.dianping_reviews
        if not kept_detail.meituan_reviews and duplicate.meituan_reviews:
            kept_detail.meituan_reviews = duplicate.meituan_reviews
        
        # 合并描述信息
        if not kept_detail.merged_description and duplicate.merged_description:
            kept_detail.merged_description = duplicate.merged_description
        if not kept_detail.merged_facilities and duplicate.merged_facilities:
            kept_detail.merged_facilities = duplicate.merged_facilities
        if not kept_detail.merged_business_hours and duplicate.merged_business_hours:
            kept_detail.merged_business_hours = duplicate.merged_business_hours

def clean_duplicate_courts_with_merge():
    """清理重复场馆，合并有效数据"""
    db = SessionLocal()
    
    try:
        # 获取所有场馆
        all_courts = db.query(TennisCourt).all()
        
        print(f"🔍 开始清理重复场馆（合并有效数据）\\n")
        print(f"清理前总场馆数: {len(all_courts)}")
        
        # 按名称分组
        name_groups = defaultdict(list)
        for court in all_courts:
            name_groups[court.name].append(court)
        
        # 找出重复的场馆
        duplicates = {name: courts for name, courts in name_groups.items() if len(courts) > 1}
        
        print(f"有重复的场馆名称: {len(duplicates)}")
        
        # 记录要删除的场馆ID
        to_delete_ids = []
        kept_courts = []
        
        for name, courts in duplicates.items():
            # 按ID排序，保留第一个（ID最小的）
            courts.sort(key=lambda x: x.id)
            kept_court = courts[0]
            duplicate_courts = courts[1:]
            
            print(f"\\n🏟️ {name}: 保留ID {kept_court.id}, 删除 {len(duplicate_courts)} 个重复记录")
            
            # 合并场馆基本信息
            merge_court_data(kept_court, duplicate_courts)
            
            # 获取详情记录
            kept_detail = db.query(CourtDetail).filter(CourtDetail.court_id == kept_court.id).first()
            if not kept_detail:
                kept_detail = CourtDetail(court_id=kept_court.id)
                db.add(kept_detail)
            
            # 获取重复场馆的详情记录
            duplicate_details = []
            for dup_court in duplicate_courts:
                dup_detail = db.query(CourtDetail).filter(CourtDetail.court_id == dup_court.id).first()
                if dup_detail:
                    duplicate_details.append(dup_detail)
            
            # 合并详情数据
            if duplicate_details:
                merge_detail_data(kept_detail, duplicate_details)
                print(f"   ✅ 已合并 {len(duplicate_details)} 个详情记录的有效数据")
            
            kept_courts.append(kept_court)
            to_delete_ids.extend([court.id for court in duplicate_courts])
        
        print(f"\\n📊 清理统计:")
        print(f"   要删除的重复场馆数: {len(to_delete_ids)}")
        print(f"   要保留的场馆数: {len(kept_courts)}")
        
        # 确认是否执行删除
        confirm = input("\\n确认要删除这些重复场馆吗？(y/N): ")
        if confirm.lower() != 'y':
            print("取消删除操作")
            return
        
        # 删除重复场馆的详情记录
        print("\\n🗑️ 删除重复场馆的详情记录...")
        deleted_details = db.query(CourtDetail).filter(CourtDetail.court_id.in_(to_delete_ids)).delete()
        print(f"   删除了 {deleted_details} 个详情记录")
        
        # 删除重复场馆
        print("🗑️ 删除重复场馆...")
        deleted_courts = db.query(TennisCourt).filter(TennisCourt.id.in_(to_delete_ids)).delete()
        print(f"   删除了 {deleted_courts} 个重复场馆")
        
        # 提交更改
        db.commit()
        
        # 验证清理结果
        remaining_courts = db.query(TennisCourt).all()
        print(f"\\n✅ 清理完成!")
        print(f"   清理后总场馆数: {len(remaining_courts)}")
        print(f"   实际删除场馆数: {len(all_courts) - len(remaining_courts)}")
        
        # 检查是否还有重复
        remaining_names = [court.name for court in remaining_courts]
        unique_names = set(remaining_names)
        print(f"   唯一场馆名称数: {len(unique_names)}")
        print(f"   是否还有重复: {'是' if len(remaining_names) != len(unique_names) else '否'}")
        
    except Exception as e:
        print(f"❌ 清理失败: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    clean_duplicate_courts_with_merge() 