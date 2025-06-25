#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
重建数据库表结构脚本
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import engine, SessionLocal
from app.models import Base, TennisCourt, CourtDetail

def recreate_tables():
    """重建数据库表"""
    print("🗄️  重建数据库表结构...")
    
    # 删除所有表
    print("删除旧表...")
    Base.metadata.drop_all(bind=engine)
    
    # 创建新表
    print("创建新表...")
    Base.metadata.create_all(bind=engine)
    
    print("✅ 数据库表重建完成")

if __name__ == "__main__":
    recreate_tables() 