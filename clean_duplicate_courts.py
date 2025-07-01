#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
清理重复场馆，保留每个场馆名称的第一个记录
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import SessionLocal
from app.models import TennisCourt, CourtDetail
from collections import defaultdict

def clean_duplicate_courts():
    """清理重复场馆，保留每个场馆名称的第一个记录"""
    db = SessionLocal()
    
    try:
        # 获取所有场馆
        all_courts = db.query(TennisCourt).all()
        
        print(f"🔍 开始清理重复场馆\\n")
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
            
            kept_courts.append(kept_court)
            to_delete_ids.extend([court.id for court in duplicate_courts])
            
            print(f"🏟️ {name}: 保留ID {kept_court.id}, 删除 {len(duplicate_courts)} 个重复记录")
        
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
    clean_duplicate_courts() 