#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Render数据库初始化脚本
用于在Render部署时导入场馆数据
"""

import os
import shutil
from app.database import init_db, get_db
from app.models import TennisCourt

def init_render_database():
    """初始化Render数据库"""
    print("开始初始化Render数据库...")
    
    # 确保数据目录存在
    os.makedirs("data", exist_ok=True)
    
    # 初始化数据库
    init_db()
    
    # 检查是否需要导入数据
    db = next(get_db())
    court_count = db.query(TennisCourt).count()
    
    print(f"当前数据库场馆数量: {court_count}")
    
    if court_count == 0:
        print("数据库为空，需要导入数据...")
        
        # 这里可以添加数据导入逻辑
        # 比如从JSON文件导入，或者从其他数据源导入
        print("请手动导入场馆数据")
        
        # 示例：创建一些测试数据
        print("创建测试数据...")
        test_courts = [
            {
                "name": "测试网球场1",
                "address": "北京市朝阳区测试地址1",
                "area": "guomao",
                "court_type": "室内",
                "phone": "010-12345678"
            },
            {
                "name": "测试网球场2", 
                "address": "北京市朝阳区测试地址2",
                "area": "wangjing",
                "court_type": "室外",
                "phone": "010-87654321"
            }
        ]
        
        for court_data in test_courts:
            court = TennisCourt(**court_data)
            db.add(court)
        
        db.commit()
        print("测试数据创建完成")
    else:
        print("数据库已有数据，无需初始化")
    
    # 显示最终统计
    final_count = db.query(TennisCourt).count()
    print(f"最终数据库场馆数量: {final_count}")

if __name__ == "__main__":
    init_render_database() 