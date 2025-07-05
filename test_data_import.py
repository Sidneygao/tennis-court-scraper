#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试数据导入功能
"""

import os
import shutil
from app.database import init_db, get_db
from app.models import TennisCourt

def test_data_import():
    """测试数据导入功能"""
    print("测试数据导入功能...")
    
    # 备份原数据库
    if os.path.exists("data/courts.db"):
        shutil.copy("data/courts.db", "data/courts.db.backup")
        print("已备份原数据库")
    
    # 删除原数据库，模拟空数据库
    if os.path.exists("data/courts.db"):
        os.remove("data/courts.db")
        print("已删除原数据库")
    
    # 初始化空数据库
    init_db()
    
    # 检查数据库是否为空
    db = next(get_db())
    court_count = db.query(TennisCourt).count()
    print(f"空数据库场馆数量: {court_count}")
    
    # 检查数据文件是否存在
    data_file = "courts_data.json"
    if os.path.exists(data_file):
        print(f"数据文件存在: {data_file}")
        
        # 模拟导入过程
        import json
        with open(data_file, 'r', encoding='utf-8') as f:
            courts_data = json.load(f)
        
        print(f"数据文件包含 {len(courts_data)} 个场馆")
        
        # 导入前几个场馆作为测试
        test_count = 5
        imported_count = 0
        
        for court_data in courts_data[:test_count]:
            try:
                court = TennisCourt(
                    name=court_data.get('name'),
                    address=court_data.get('address'),
                    area=court_data.get('area'),
                    court_type=court_data.get('court_type'),
                    phone=court_data.get('phone'),
                    latitude=court_data.get('latitude'),
                    longitude=court_data.get('longitude'),
                    data_source=court_data.get('data_source')
                )
                
                db.add(court)
                imported_count += 1
                print(f"  导入: {court.name}")
                
            except Exception as e:
                print(f"  导入失败: {e}")
        
        db.commit()
        print(f"✅ 测试导入完成: {imported_count} 个场馆")
        
        # 验证导入结果
        final_count = db.query(TennisCourt).count()
        print(f"数据库最终场馆数量: {final_count}")
        
    else:
        print(f"❌ 数据文件不存在: {data_file}")
    
    # 恢复原数据库
    if os.path.exists("data/courts.db.backup"):
        shutil.copy("data/courts.db.backup", "data/courts.db")
        print("已恢复原数据库")

if __name__ == "__main__":
    test_data_import() 