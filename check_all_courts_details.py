#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import SessionLocal
from app.models import TennisCourt, CourtDetail
import json
from datetime import datetime

def check_all_courts_details():
    """检查所有场馆的详情数据爬取情况"""
    db = SessionLocal()
    
    try:
        # 获取所有场馆
        all_courts = db.query(TennisCourt).all()
        total_courts = len(all_courts)
        
        print(f"🏟️  场馆总数: {total_courts}")
        print("=" * 80)
        
        # 获取所有详情记录
        all_details = db.query(CourtDetail).all()
        total_details = len(all_details)
        
        print(f"📊 详情缓存总数: {total_details}")
        print(f"📈 详情覆盖率: {total_details/total_courts*100:.1f}%")
        print("=" * 80)
        
        # 统计有详情的场馆
        courts_with_details = []
        courts_without_details = []
        
        for court in all_courts:
            detail = db.query(CourtDetail).filter(CourtDetail.court_id == court.id).first()
            if detail:
                courts_with_details.append(court)
            else:
                courts_without_details.append(court)
        
        print(f"✅ 有详情缓存的场馆: {len(courts_with_details)}")
        print(f"❌ 无详情缓存的场馆: {len(courts_without_details)}")
        print("=" * 80)
        
        # 分析详情数据质量
        valid_details = 0
        invalid_details = 0
        
        for detail in all_details:
            # 检查是否有有效数据（不是"该数据不能获得"）
            has_valid_data = False
            
            if detail.merged_description and detail.merged_description != "该数据不能获得":
                has_valid_data = True
            elif detail.description and detail.description != "该数据不能获得":
                has_valid_data = True
            elif detail.merged_facilities and detail.merged_facilities != "该数据不能获得":
                has_valid_data = True
            elif detail.merged_business_hours and detail.merged_business_hours != "该数据不能获得":
                has_valid_data = True
            elif detail.merged_rating and detail.merged_rating > 0:
                has_valid_data = True
            
            if has_valid_data:
                valid_details += 1
            else:
                invalid_details += 1
        
        print(f"🎯 有效详情数据: {valid_details}")
        print(f"⚠️  无效详情数据: {invalid_details}")
        print(f"📊 数据有效率: {valid_details/total_details*100:.1f}%" if total_details > 0 else "📊 数据有效率: 0%")
        print("=" * 80)
        
        # 按区域统计
        print("📍 按区域统计:")
        area_stats = {}
        for court in all_courts:
            area = court.area or "未知"
            if area not in area_stats:
                area_stats[area] = {"total": 0, "with_details": 0, "without_details": 0}
            
            area_stats[area]["total"] += 1
            detail = db.query(CourtDetail).filter(CourtDetail.court_id == court.id).first()
            if detail:
                area_stats[area]["with_details"] += 1
            else:
                area_stats[area]["without_details"] += 1
        
        for area, stats in area_stats.items():
            coverage = stats["with_details"] / stats["total"] * 100 if stats["total"] > 0 else 0
            print(f"  {area}: {stats['total']}个场馆, {stats['with_details']}个有详情 ({coverage:.1f}%)")
        
        print("=" * 80)
        
        # 显示无详情的场馆列表（前10个）
        if courts_without_details:
            print(f"❌ 无详情缓存的场馆列表（前10个）:")
            for i, court in enumerate(courts_without_details[:10]):
                print(f"  {i+1}. {court.name} (ID: {court.id}, 区域: {court.area})")
            if len(courts_without_details) > 10:
                print(f"  ... 还有 {len(courts_without_details) - 10} 个场馆")
        
        print("=" * 80)
        
        # 检查最近更新的详情
        print("🕒 最近更新的详情:")
        recent_details = db.query(CourtDetail).order_by(CourtDetail.updated_at.desc()).limit(5).all()
        for detail in recent_details:
            court = db.query(TennisCourt).filter(TennisCourt.id == detail.court_id).first()
            print(f"  {court.name if court else detail.court_id}: {detail.updated_at}")
        
        print("=" * 80)
        
        # 总结
        print("📋 总结:")
        print(f"  • 总场馆数: {total_courts}")
        print(f"  • 有详情缓存: {len(courts_with_details)} ({len(courts_with_details)/total_courts*100:.1f}%)")
        print(f"  • 无详情缓存: {len(courts_without_details)} ({len(courts_without_details)/total_courts*100:.1f}%)")
        print(f"  • 有效详情数据: {valid_details} ({valid_details/total_details*100:.1f}%)" if total_details > 0 else "  • 有效详情数据: 0 (0%)")
        
        if len(courts_without_details) > 0:
            print(f"\n💡 建议: 还有 {len(courts_without_details)} 个场馆需要爬取详情数据")
        
    except Exception as e:
        print(f"❌ 检查失败: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    check_all_courts_details() 