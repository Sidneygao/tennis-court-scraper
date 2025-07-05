#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试Render启动过程
"""

import os
import sys
import time

def test_startup():
    """测试启动过程"""
    print("测试Render启动过程...")
    
    # 设置环境变量模拟Render环境
    os.environ['PORT'] = '8000'
    os.environ['PYTHONUNBUFFERED'] = '1'
    
    try:
        print("1. 测试导入...")
        from app.config import settings
        print("   ✅ config 导入成功")
        
        from app.database import get_db, init_db
        print("   ✅ database 导入成功")
        
        from app.models import TennisCourt
        print("   ✅ models 导入成功")
        
        from app.api import courts, details, scraper
        print("   ✅ API 导入成功")
        
        from app.main import app
        print("   ✅ main 导入成功")
        
        print("2. 测试数据库初始化...")
        init_db()
        print("   ✅ 数据库初始化成功")
        
        print("3. 测试数据库查询...")
        db = next(get_db())
        courts_count = db.query(TennisCourt).count()
        print(f"   ✅ 数据库查询成功，共有 {courts_count} 个场馆")
        
        print("4. 测试区域配置...")
        areas_count = len(settings.target_areas)
        print(f"   ✅ 区域配置正常，共有 {areas_count} 个区域")
        
        print("5. 测试价格预测器...")
        from app.scrapers.price_predictor import PricePredictor
        predictor = PricePredictor()
        print("   ✅ 价格预测器初始化成功")
        
        print("6. 测试场馆类型判断...")
        # 测试几个场馆的类型判断
        test_courts = db.query(TennisCourt).limit(3).all()
        for court in test_courts:
            court_type = predictor.determine_court_type(court.name, court.address)
            print(f"   ✅ {court.name}: {court_type}")
        
        print("\n✅ 所有启动测试通过")
        return True
        
    except Exception as e:
        print(f"❌ 启动测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_startup()
    sys.exit(0 if success else 1) 