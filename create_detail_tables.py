#!/usr/bin/env python3
"""
创建详情相关数据库表的脚本
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import engine, Base
from app.models import CourtDetail

def create_detail_tables():
    """创建详情相关的数据库表"""
    print("正在创建详情相关数据库表...")
    
    try:
        # 创建CourtDetail表
        CourtDetail.__table__.create(engine, checkfirst=True)
        print("✅ CourtDetail表创建成功")
        
        print("🎉 所有详情相关表创建完成！")
        
    except Exception as e:
        print(f"❌ 创建表失败: {e}")
        return False
    
    return True

if __name__ == "__main__":
    create_detail_tables() 