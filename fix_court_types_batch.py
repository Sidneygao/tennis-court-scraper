#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
批量修复场馆类型：将英文indoor/outdoor改为中文室内/室外
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import SessionLocal
from app.models import TennisCourt

def fix_court_types():
    """批量修复场馆类型"""
    db = SessionLocal()
    
    try:
        # 获取所有场馆
        courts = db.query(TennisCourt).all()
        print(f"开始修复 {len(courts)} 家场馆的类型...")
        
        updated_count = 0
        indoor_count = 0
        outdoor_count = 0
        
        for court in courts:
            old_type = court.court_type
            new_type = None
            
            # 修复英文类型
            if old_type == 'indoor':
                new_type = '室内'
            elif old_type == 'outdoor':
                new_type = '室外'
            
            # 更新场馆类型
            if new_type and old_type != new_type:
                court.court_type = new_type
                updated_count += 1
                
                print(f"场馆: {court.name}")
                print(f"  类型: {old_type} -> {new_type}")
                print()
            
            # 统计
            if court.court_type == '室内':
                indoor_count += 1
            elif court.court_type == '室外':
                outdoor_count += 1
        
        # 提交更改
        db.commit()
        
        print(f"批量修复完成！")
        print(f"更新场馆数: {updated_count}")
        print(f"室内场馆: {indoor_count}")
        print(f"室外场馆: {outdoor_count}")
        print(f"总计: {len(courts)}")
        
    except Exception as e:
        print(f"批量修复出错: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    fix_court_types() 