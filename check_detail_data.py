#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import SessionLocal
from app.models import CourtDetail, TennisCourt
import json

def check_detail_data():
    """检查详情表中的数据"""
    db = SessionLocal()
    
    try:
        # 获取所有详情记录
        details = db.query(CourtDetail).all()
        
        print(f"详情表记录总数: {len(details)}")
        print("=" * 80)
        
        valid_count = 0
        invalid_count = 0
        
        for detail in details:
            # 查询对应的场馆信息
            court = db.query(TennisCourt).filter(TennisCourt.id == detail.court_id).first()
            
            print(f"场馆ID: {detail.court_id}")
            print(f"场馆名称: {court.name if court else 'N/A'}")
            print(f"场馆地址: {court.address if court else 'N/A'}")
            print(f"描述: {detail.merged_description}")
            print(f"设施: {detail.merged_facilities}")
            print(f"营业时间: {detail.merged_business_hours}")
            print(f"评分: {detail.merged_rating}")
            print(f"价格: {detail.merged_prices}")
            print(f"最后更新: {detail.updated_at}")
            print("-" * 40)
            
            # 判断是否有有效数据
            if detail.merged_description and detail.merged_description != "该数据不能获得":
                valid_count += 1
                print("✅ 有效数据")
            else:
                invalid_count += 1
                print("❌ 无效数据")
            print()
        
        print("=" * 80)
        print(f"有效数据场馆数: {valid_count}")
        print(f"无效数据场馆数: {invalid_count}")
        print(f"总计: {valid_count + invalid_count}")
        
        # 检查是否有真实的小红书数据
        print("\n检查是否有真实的小红书数据:")
        for detail in details:
            if detail.merged_description and "小红书" in detail.merged_description:
                court = db.query(TennisCourt).filter(TennisCourt.id == detail.court_id).first()
                print(f"✅ 场馆 {court.name if court else detail.court_id} 包含小红书数据")
                print(f"   描述: {detail.merged_description[:100]}...")
                print()
        
        # 检查是否有模拟数据
        print("\n检查是否有模拟数据:")
        for detail in details:
            if detail.merged_description and "该数据不能获得" in detail.merged_description:
                court = db.query(TennisCourt).filter(TennisCourt.id == detail.court_id).first()
                print(f"❌ 场馆 {court.name if court else detail.court_id} 使用模拟数据")
                print()
        
        detail = db.query(CourtDetail).filter(CourtDetail.court_id == 1).first()
        if detail:
            print("=== 详情数据检查 ===")
            print(f"ID: {detail.id}")
            print(f"Court ID: {detail.court_id}")
            print(f"Merged Description: {detail.merged_description}")
            print(f"Merged Facilities: {detail.merged_facilities}")
            print(f"Merged Business Hours: {detail.merged_business_hours}")
            print(f"Merged Rating: {detail.merged_rating}")
            
            print("\n=== JSON字段检查 ===")
            print(f"Merged Prices (raw): {detail.merged_prices}")
            print(f"Dianping Reviews (raw): {detail.dianping_reviews}")
            print(f"Dianping Images (raw): {detail.dianping_images}")
            
            print("\n=== JSON解析测试 ===")
            try:
                if detail.merged_prices:
                    prices = json.loads(detail.merged_prices)
                    print(f"Merged Prices (parsed): {prices}")
                else:
                    print("Merged Prices: None")
            except Exception as e:
                print(f"Merged Prices 解析失败: {e}")
            
            try:
                if detail.dianping_reviews:
                    reviews = json.loads(detail.dianping_reviews)
                    print(f"Dianping Reviews (parsed): {reviews}")
                else:
                    print("Dianping Reviews: None")
            except Exception as e:
                print(f"Dianping Reviews 解析失败: {e}")
            
            try:
                if detail.dianping_images:
                    images = json.loads(detail.dianping_images)
                    print(f"Dianping Images (parsed): {images}")
                else:
                    print("Dianping Images: None")
            except Exception as e:
                print(f"Dianping Images 解析失败: {e}")
                
        else:
            print("未找到详情数据")
        
    except Exception as e:
        print(f"查询出错: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    check_detail_data() 