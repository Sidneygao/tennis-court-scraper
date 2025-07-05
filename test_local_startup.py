#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试本地启动
"""

import sys
import os

def test_imports():
    """测试所有必要的导入"""
    print("测试导入...")
    
    try:
        print("1. 测试基础模块...")
        from app.config import settings
        print("   ✅ config 导入成功")
        
        print("2. 测试数据库...")
        from app.database import get_db, init_db
        print("   ✅ database 导入成功")
        
        print("3. 测试模型...")
        from app.models import TennisCourt
        print("   ✅ models 导入成功")
        
        print("4. 测试API...")
        from app.api import courts, details, scraper
        print("   ✅ API 导入成功")
        
        print("5. 测试主应用...")
        from app.main import app
        print("   ✅ main 导入成功")
        
        print("6. 测试价格预测器...")
        from app.scrapers.price_predictor import PricePredictor
        print("   ✅ price_predictor 导入成功")
        
        print("\n✅ 所有导入测试通过")
        return True
        
    except Exception as e:
        print(f"❌ 导入失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_database():
    """测试数据库连接"""
    print("\n测试数据库...")
    try:
        from app.database import get_db, init_db
        from app.models import TennisCourt
        
        # 初始化数据库
        init_db()
        print("   ✅ 数据库初始化成功")
        
        # 测试查询
        db = next(get_db())
        courts = db.query(TennisCourt).limit(5).all()
        print(f"   ✅ 数据库查询成功，找到 {len(courts)} 个场馆")
        
        return True
        
    except Exception as e:
        print(f"❌ 数据库测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主测试函数"""
    print("开始测试本地启动...")
    
    # 测试导入
    if not test_imports():
        return False
    
    # 测试数据库
    if not test_database():
        return False
    
    print("\n✅ 所有测试通过，本地启动应该正常")
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 