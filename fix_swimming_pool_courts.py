#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
直接修复包含"游泳池"字样的场馆类型为空
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import SessionLocal
from app.models import TennisCourt

def fix_swimming_pool_courts():
    """修复包含"游泳池"字样的场馆类型为空"""
    db = SessionLocal()
    
    try:
        # 查找包含"游泳池"字样的场馆
        swimming_pool_courts = db.query(TennisCourt).filter(
            (TennisCourt.name.like('%游泳池%')) |
            (TennisCourt.address.like('%游泳池%'))
        ).all()
        
        print(f"🔍 找到 {len(swimming_pool_courts)} 个包含'游泳池'字样的场馆")
        
        # 将这些场馆的类型设置为空
        for court in swimming_pool_courts:
            print(f"修复: {court.name} - 类型从 '{court.court_type}' 改为空")
            court.court_type = ''
        
        # 提交更改
        db.commit()
        print(f"✅ 成功修复 {len(swimming_pool_courts)} 个游泳池场馆的类型")
        
    except Exception as e:
        print(f"❌ 修复失败: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    fix_swimming_pool_courts() 