#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import SessionLocal
from app.models import TennisCourt, CourtDetail
import json

def check_detail_quality():
    """详细分析详情数据质量"""
    db = SessionLocal()
    
    try:
        # 获取所有详情记录
        all_details = db.query(CourtDetail).all()
        
        print(f"📊 详情记录总数: {len(all_details)}")
        print("=" * 80)
        
        # 分析各个字段的数据质量
        field_stats = {
            "merged_description": {"total": 0, "valid": 0, "invalid": 0, "empty": 0},
            "merged_facilities": {"total": 0, "valid": 0, "invalid": 0, "empty": 0},
            "merged_business_hours": {"total": 0, "valid": 0, "invalid": 0, "empty": 0},
            "merged_rating": {"total": 0, "valid": 0, "invalid": 0, "empty": 0},
            "merged_prices": {"total": 0, "valid": 0, "invalid": 0, "empty": 0},
            "dianping_reviews": {"total": 0, "valid": 0, "invalid": 0, "empty": 0},
            "dianping_images": {"total": 0, "valid": 0, "invalid": 0, "empty": 0}
        }
        
        for detail in all_details:
            # 分析 merged_description
            field_stats["merged_description"]["total"] += 1
            if not detail.merged_description:
                field_stats["merged_description"]["empty"] += 1
            elif detail.merged_description == "该数据不能获得":
                field_stats["merged_description"]["invalid"] += 1
            else:
                field_stats["merged_description"]["valid"] += 1
            
            # 分析 merged_facilities
            field_stats["merged_facilities"]["total"] += 1
            if not detail.merged_facilities:
                field_stats["merged_facilities"]["empty"] += 1
            elif detail.merged_facilities == "该数据不能获得":
                field_stats["merged_facilities"]["invalid"] += 1
            else:
                field_stats["merged_facilities"]["valid"] += 1
            
            # 分析 merged_business_hours
            field_stats["merged_business_hours"]["total"] += 1
            if not detail.merged_business_hours:
                field_stats["merged_business_hours"]["empty"] += 1
            elif detail.merged_business_hours == "该数据不能获得":
                field_stats["merged_business_hours"]["invalid"] += 1
            else:
                field_stats["merged_business_hours"]["valid"] += 1
            
            # 分析 merged_rating
            field_stats["merged_rating"]["total"] += 1
            if not detail.merged_rating or detail.merged_rating == 0:
                field_stats["merged_rating"]["empty"] += 1
            elif detail.merged_rating == -1:
                field_stats["merged_rating"]["invalid"] += 1
            else:
                field_stats["merged_rating"]["valid"] += 1
            
            # 分析 merged_prices
            field_stats["merged_prices"]["total"] += 1
            if not detail.merged_prices:
                field_stats["merged_prices"]["empty"] += 1
            else:
                try:
                    prices = json.loads(detail.merged_prices)
                    if prices and len(prices) > 0:
                        # 检查是否有真实价格
                        has_real_price = False
                        for price in prices:
                            if isinstance(price, dict) and price.get("type") == "真实价格":
                                has_real_price = True
                                break
                        if has_real_price:
                            field_stats["merged_prices"]["valid"] += 1
                        else:
                            field_stats["merged_prices"]["invalid"] += 1
                    else:
                        field_stats["merged_prices"]["invalid"] += 1
                except:
                    field_stats["merged_prices"]["invalid"] += 1
            
            # 分析 dianping_reviews
            field_stats["dianping_reviews"]["total"] += 1
            if not detail.dianping_reviews:
                field_stats["dianping_reviews"]["empty"] += 1
            else:
                try:
                    reviews = json.loads(detail.dianping_reviews)
                    if reviews and len(reviews) > 0:
                        # 检查是否有真实评论
                        has_real_review = False
                        for review in reviews:
                            if isinstance(review, dict) and review.get("content") and review.get("content") != "该数据不能获得":
                                has_real_review = True
                                break
                        if has_real_review:
                            field_stats["dianping_reviews"]["valid"] += 1
                        else:
                            field_stats["dianping_reviews"]["invalid"] += 1
                    else:
                        field_stats["dianping_reviews"]["invalid"] += 1
                except:
                    field_stats["dianping_reviews"]["invalid"] += 1
            
            # 分析 dianping_images
            field_stats["dianping_images"]["total"] += 1
            if not detail.dianping_images:
                field_stats["dianping_images"]["empty"] += 1
            else:
                try:
                    images = json.loads(detail.dianping_images)
                    if images and len(images) > 0:
                        field_stats["dianping_images"]["valid"] += 1
                    else:
                        field_stats["dianping_images"]["invalid"] += 1
                except:
                    field_stats["dianping_images"]["invalid"] += 1
        
        # 打印字段统计
        print("📋 各字段数据质量统计:")
        for field, stats in field_stats.items():
            valid_rate = stats["valid"] / stats["total"] * 100 if stats["total"] > 0 else 0
            print(f"  {field}:")
            print(f"    总数: {stats['total']}")
            print(f"    有效: {stats['valid']} ({valid_rate:.1f}%)")
            print(f"    无效: {stats['invalid']}")
            print(f"    空值: {stats['empty']}")
            print()
        
        print("=" * 80)
        
        # 显示一些有效数据的例子
        print("✅ 有效数据示例:")
        valid_count = 0
        for detail in all_details:
            if detail.merged_description and detail.merged_description != "该数据不能获得":
                court = db.query(TennisCourt).filter(TennisCourt.id == detail.court_id).first()
                print(f"  {court.name if court else detail.court_id}:")
                print(f"    描述: {detail.merged_description[:100]}...")
                print(f"    设施: {detail.merged_facilities}")
                print(f"    评分: {detail.merged_rating}")
                print()
                valid_count += 1
                if valid_count >= 5:
                    break
        
        print("=" * 80)
        
        # 显示一些无效数据的例子
        print("❌ 无效数据示例:")
        invalid_count = 0
        for detail in all_details:
            if detail.merged_description == "该数据不能获得":
                court = db.query(TennisCourt).filter(TennisCourt.id == detail.court_id).first()
                print(f"  {court.name if court else detail.court_id}:")
                print(f"    描述: {detail.merged_description}")
                print(f"    设施: {detail.merged_facilities}")
                print(f"    评分: {detail.merged_rating}")
                print()
                invalid_count += 1
                if invalid_count >= 5:
                    break
        
        print("=" * 80)
        
        # 分析原因
        print("🔍 数据质量分析:")
        print("  1. 大部分详情数据都是'该数据不能获得'，说明爬虫没有成功获取到真实数据")
        print("  2. 这可能是因为:")
        print("     - 大众点评/美团的反爬虫机制")
        print("     - 网络连接问题")
        print("     - 场馆在这些平台上确实没有信息")
        print("     - 爬虫逻辑需要优化")
        print("  3. 建议:")
        print("     - 检查爬虫是否正常工作")
        print("     - 优化爬虫策略")
        print("     - 考虑使用其他数据源")
        
    except Exception as e:
        print(f"❌ 分析失败: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    check_detail_quality() 