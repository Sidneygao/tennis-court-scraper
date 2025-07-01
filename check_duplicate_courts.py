#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查后台重复场馆情况
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import SessionLocal
from app.models import TennisCourt
from collections import defaultdict

def check_duplicate_courts():
    """检查后台重复场馆情况"""
    db = SessionLocal()
    
    try:
        # 获取所有场馆
        all_courts = db.query(TennisCourt).all()
        
        print(f"🔍 检查重复场馆情况\\n")
        print(f"总场馆数: {len(all_courts)}")
        
        # 按名称分组
        name_groups = defaultdict(list)
        for court in all_courts:
            name_groups[court.name].append(court)
        
        # 找出重复的场馆
        duplicates = {name: courts for name, courts in name_groups.items() if len(courts) > 1}
        
        print(f"\\n📊 重复场馆统计:")
        print(f"   有重复的场馆名称: {len(duplicates)}")
        
        total_duplicates = sum(len(courts) - 1 for courts in duplicates.values())
        print(f"   重复场馆总数: {total_duplicates}")
        
        # 显示重复场馆详情
        if duplicates:
            print(f"\\n🔍 重复场馆详情:")
            for name, courts in list(duplicates.items())[:10]:  # 只显示前10个
                print(f"\\n🏟️ 场馆名称: {name}")
                print(f"   重复次数: {len(courts)}")
                for i, court in enumerate(courts):
                    print(f"   {i+1}. ID: {court.id}, 地址: {court.address}, 类型: {court.court_type}")
        
        # 检查游泳池场馆
        print(f"\\n🏊 游泳池场馆详情:")
        swimming_pools = [court for court in all_courts if '游泳池' in court.name]
        for court in swimming_pools:
            print(f"   ID: {court.id}, 名称: {court.name}, 地址: {court.address}, 类型: {court.court_type}")
        
        # 统计各区域场馆数量
        print(f"\\n📊 各区域场馆数量:")
        area_counts = defaultdict(int)
        for court in all_courts:
            area_counts[court.area] += 1
        
        for area, count in sorted(area_counts.items()):
            print(f"   {area}: {count}")
        
    finally:
        db.close()

if __name__ == "__main__":
    check_duplicate_courts() 