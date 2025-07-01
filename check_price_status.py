#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
检查价格状态脚本
"""

import os
import sys
import json
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from app.database import get_db
from app.models import TennisCourt, CourtDetail

def check_price_status():
    """检查价格状态"""
    print("=== 价格状态检查 ===")
    
    db = next(get_db())
    
    # 总场馆数
    total_courts = db.query(TennisCourt).count()
    print(f"总场馆数: {total_courts}")
    
    # 有价格信息的场馆
    courts_with_prices = db.query(TennisCourt).filter(
        (TennisCourt.peak_price.isnot(None)) & 
        (TennisCourt.peak_price != '')
    ).count()
    print(f"有价格信息的场馆: {courts_with_prices}")
    
    # 没有价格信息的场馆
    courts_without_prices = total_courts - courts_with_prices
    print(f"没有价格信息的场馆: {courts_without_prices}")
    
    # 按场地类型统计
    print("\n=== 按场地类型统计 ===")
    court_types = db.query(TennisCourt.court_type).distinct().all()
    for court_type in court_types:
        if court_type[0]:
            type_count = db.query(TennisCourt).filter(TennisCourt.court_type == court_type[0]).count()
            type_with_prices = db.query(TennisCourt).filter(
                (TennisCourt.court_type == court_type[0]) &
                (TennisCourt.peak_price.isnot(None)) & 
                (TennisCourt.peak_price != '')
            ).count()
            print(f"{court_type[0]}: {type_with_prices}/{type_count}")
    
    # 检查前几个没有价格的场馆
    print("\n=== 前5个没有价格的场馆 ===")
    courts_no_price = db.query(TennisCourt).filter(
        (TennisCourt.peak_price.is_(None)) | 
        (TennisCourt.peak_price == '')
    ).limit(5).all()
    
    for court in courts_no_price:
        print(f"ID: {court.id}, 名称: {court.name}, 区域: {court.area}, 类型: {court.court_type}")
    
    db.close()

def check_price_cache_status():
    """检查价格缓存状态"""
    db = next(get_db())
    
    try:
        # 获取所有详情记录
        details = db.query(CourtDetail).all()
        
        total_details = len(details)
        with_price_cache = 0
        without_price_cache = 0
        empty_price_cache = 0
        
        for detail in details:
            # 检查是否有任何价格信息
            has_prices = False
            if detail.dianping_prices:
                try:
                    price_data = json.loads(detail.dianping_prices)
                    if price_data and len(price_data) > 0:
                        has_prices = True
                except:
                    pass
            
            if detail.meituan_prices:
                try:
                    price_data = json.loads(detail.meituan_prices)
                    if price_data and len(price_data) > 0:
                        has_prices = True
                except:
                    pass
            
            if detail.merged_prices:
                try:
                    price_data = json.loads(detail.merged_prices)
                    if price_data and len(price_data) > 0:
                        has_prices = True
                except:
                    pass
            
            if has_prices:
                with_price_cache += 1
            else:
                without_price_cache += 1
        
        print(f"=== 价格缓存状态统计 ===")
        print(f"总详情记录数: {total_details}")
        print(f"有价格缓存: {with_price_cache}")
        print(f"无价格缓存: {without_price_cache}")
        print(f"需要抓取价格的场馆: {without_price_cache}")
        
        # 显示没有价格缓存的场馆列表
        if without_price_cache > 0:
            print(f"\n=== 无价格缓存的场馆 ({without_price_cache}个) ===")
            for detail in details:
                has_prices = False
                if detail.dianping_prices or detail.meituan_prices or detail.merged_prices:
                    try:
                        if detail.dianping_prices:
                            price_data = json.loads(detail.dianping_prices)
                            if price_data and len(price_data) > 0:
                                has_prices = True
                        if detail.meituan_prices:
                            price_data = json.loads(detail.meituan_prices)
                            if price_data and len(price_data) > 0:
                                has_prices = True
                        if detail.merged_prices:
                            price_data = json.loads(detail.merged_prices)
                            if price_data and len(price_data) > 0:
                                has_prices = True
                    except:
                        pass
                
                if not has_prices:
                    print(f"- {detail.court_id}")
        
    finally:
        db.close()

if __name__ == "__main__":
    check_price_status()
    check_price_cache_status() 