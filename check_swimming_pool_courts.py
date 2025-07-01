#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查包含"游泳池"字样的场馆是否被正确排除出前后端
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import SessionLocal
from app.models import TennisCourt, CourtDetail
import json

def check_swimming_pool_courts():
    """检查包含"游泳池"字样的场馆"""
    db = SessionLocal()
    
    try:
        # 查找包含"游泳池"字样的场馆
        swimming_pool_courts = db.query(TennisCourt).filter(
            (TennisCourt.name.like('%游泳池%')) |
            (TennisCourt.address.like('%游泳池%'))
        ).all()
        
        print(f"🔍 包含'游泳池'字样的场馆检查\\n")
        print(f"📊 找到 {len(swimming_pool_courts)} 个包含'游泳池'字样的场馆:\\n")
        
        for court in swimming_pool_courts:
            print(f"🏟️ 场馆ID: {court.id}")
            print(f"   名称: {court.name}")
            print(f"   地址: {court.address}")
            print(f"   类型: {court.court_type}")
            print(f"   区域: {court.area}")
            print(f"   数据来源: {court.data_source}")
            print()
        
        # 检查这些场馆是否还在API接口中返回
        print("\\n🔍 检查这些场馆是否还在API接口中返回...")
        
        for court in swimming_pool_courts:
            # 检查场馆类型是否为空
            if court.court_type == '' or court.court_type is None:
                print(f"✅ {court.name} - 类型已正确设置为空")
            else:
                print(f"❌ {court.name} - 类型未设置为空: {court.court_type}")
        
        # 检查API接口是否还会返回这些场馆
        print("\\n🔍 检查API接口过滤逻辑...")
        
        # 模拟API接口的过滤逻辑
        filtered_courts = db.query(TennisCourt).filter(
            TennisCourt.court_type != '',
            TennisCourt.court_type.isnot(None)
        ).all()
        
        swimming_pool_in_api = [c for c in swimming_pool_courts if c in filtered_courts]
        
        if swimming_pool_in_api:
            print(f"❌ 发现 {len(swimming_pool_in_api)} 个游泳池场馆仍在API接口中:")
            for court in swimming_pool_in_api:
                print(f"   - {court.name} (类型: {court.court_type})")
        else:
            print("✅ 所有游泳池场馆已正确从API接口中排除")
            
    finally:
        db.close()

if __name__ == "__main__":
    check_swimming_pool_courts() 