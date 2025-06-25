#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from app.database import get_db
from app.models import CourtDetail

def check_details():
    """检查详情表数据"""
    db = next(get_db())
    
    try:
        # 获取所有详情记录
        details = db.query(CourtDetail).all()
        print(f"详情表记录总数: {len(details)}")
        
        if details:
            print("\n前5条记录:")
            for i, detail in enumerate(details[:5]):
                print(f"{i+1}. ID: {detail.id}, 场馆ID: {detail.court_id}")
                print(f"   描述: {detail.description[:100]}...")
                print(f"   评分: {detail.rating}")
                print(f"   更新时间: {detail.updated_at}")
                print()
        else:
            print("详情表中没有数据")
            
        # 统计有效数据
        valid_details = [d for d in details if d.description and d.description != "该数据不能获得"]
        print(f"有效数据记录数: {len(valid_details)}")
        
        # 统计无效数据
        invalid_details = [d for d in details if not d.description or d.description == "该数据不能获得"]
        print(f"无效数据记录数: {len(invalid_details)}")
        
    except Exception as e:
        print(f"查询出错: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    check_details() 