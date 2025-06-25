#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import SessionLocal
from app.models import TennisCourt
from app.config import settings

def check_all_areas():
    """检查所有区域的数据情况"""
    db = SessionLocal()
    
    try:
        print("🌍 目标区域列表:")
        for area in settings.target_areas:
            print(f"  - {area}")
        
        print("\n" + "=" * 80)
        
        # 检查每个区域的场馆数量
        print("📊 各区域场馆统计:")
        for area in settings.target_areas:
            count = db.query(TennisCourt).filter(TennisCourt.area == area).count()
            print(f"  {area}: {count}个场馆")
        
        print("\n" + "=" * 80)
        
        # 检查所有场馆
        all_courts = db.query(TennisCourt).all()
        print(f"🏟️  数据库总场馆数: {len(all_courts)}")
        
        # 按区域分组统计
        area_stats = {}
        for court in all_courts:
            area = court.area or "未知"
            if area not in area_stats:
                area_stats[area] = 0
            area_stats[area] += 1
        
        print("\n📍 实际数据分布:")
        for area, count in area_stats.items():
            print(f"  {area}: {count}个场馆")
        
        print("\n" + "=" * 80)
        
        # 检查是否有其他区域的数据
        print("🔍 检查是否有其他区域数据:")
        all_areas = db.query(TennisCourt.area).distinct().all()
        all_areas = [area[0] for area in all_areas if area[0]]
        
        print(f"数据库中的区域: {all_areas}")
        
        missing_areas = set(settings.target_areas) - set(all_areas)
        if missing_areas:
            print(f"❌ 缺少的区域: {list(missing_areas)}")
        else:
            print("✅ 所有目标区域都有数据")
        
        print("\n" + "=" * 80)
        
        # 分析原因
        print("🔍 分析:")
        print(f"  1. 目标区域数: {len(settings.target_areas)}")
        print(f"  2. 实际数据区域数: {len(all_areas)}")
        print(f"  3. 总场馆数: {len(all_courts)}")
        
        if len(all_courts) < 500:
            print(f"  4. ❌ 场馆数量不足500家，只有{len(all_courts)}家")
            print("  5. 可能原因:")
            print("     - 只抓取了部分区域的数据")
            print("     - 其他区域的数据还没有抓取")
            print("     - 需要运行完整的抓取流程")
        else:
            print(f"  4. ✅ 场馆数量充足: {len(all_courts)}家")
        
        print("\n💡 建议:")
        print("  1. 检查是否所有区域都已经抓取")
        print("  2. 运行完整的抓取流程")
        print("  3. 检查抓取日志，确认是否有错误")
        
    except Exception as e:
        print(f"❌ 检查失败: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    check_all_areas() 