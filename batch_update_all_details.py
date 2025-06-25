#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
批量更新所有场馆的详情数据（带缓存比较功能）
只有在发现数据发生变化时才更新数据库对应字段
"""

import asyncio
import requests
import json
import time
import sys
import os
from typing import List, Dict, Any

# 添加项目路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# API基础URL
BASE_URL = "http://localhost:8000"

def get_all_courts() -> List[Dict[str, Any]]:
    """获取所有场馆列表"""
    try:
        response = requests.get(f"{BASE_URL}/api/courts/")
        if response.status_code == 200:
            return response.json()
        else:
            print(f"❌ 获取场馆列表失败: {response.status_code}")
            return []
    except Exception as e:
        print(f"❌ 获取场馆列表异常: {str(e)}")
        return []

def update_court_detail(court_id: int) -> bool:
    """更新单个场馆的详情数据"""
    try:
        response = requests.post(f"{BASE_URL}/api/details/{court_id}/update")
        if response.status_code == 200:
            print(f"✅ 场馆 {court_id} 详情更新成功")
            return True
        else:
            print(f"❌ 场馆 {court_id} 详情更新失败: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 场馆 {court_id} 详情更新异常: {str(e)}")
        return False

def preview_court_detail(court_id: int) -> Dict[str, Any]:
    """预览场馆详情"""
    try:
        response = requests.get(f"{BASE_URL}/api/details/{court_id}/preview")
        if response.status_code == 200:
            return response.json()
        else:
            return {"error": f"预览失败: {response.status_code}", "court_id": court_id}
    except Exception as e:
        return {"error": f"预览异常: {e}", "court_id": court_id}

async def batch_update_details():
    """批量更新所有场馆详情"""
    print("🔄 开始批量更新所有场馆详情...")
    
    # 获取所有场馆
    courts = get_all_courts()
    if not courts:
        print("❌ 没有找到场馆数据")
        return
    
    print(f"📊 找到 {len(courts)} 个场馆")
    
    # 统计信息
    total_courts = len(courts)
    updated_count = 0
    no_change_count = 0
    error_count = 0
    updated_fields_stats = {}
    
    for i, court in enumerate(courts, 1):
        court_id = court['id']
        court_name = court['name']
        
        print(f"\n[{i}/{total_courts}] 处理场馆: {court_name} (ID: {court_id})")
        
        # 先预览当前状态
        preview = preview_court_detail(court_id)
        if "error" in preview:
            print(f"  预览失败: {preview['error']}")
            error_count += 1
            continue
        
        has_detail = preview.get('has_detail', False)
        if has_detail:
            print(f"  当前状态: 已有详情数据")
        else:
            print(f"  当前状态: 无详情数据")
        
        # 更新详情
        if update_court_detail(court_id):
            updated_count += 1
        else:
            error_count += 1
        
        # 添加延迟避免请求过快
        time.sleep(0.5)
    
    # 输出统计结果
    print(f"\n📈 批量更新完成!")
    print(f"总场馆数: {total_courts}")
    print(f"成功更新: {updated_count}")
    print(f"失败: {error_count}")
    
    if updated_fields_stats:
        print(f"\n字段更新统计:")
        for field, count in sorted(updated_fields_stats.items(), key=lambda x: x[1], reverse=True):
            print(f"  {field}: {count} 次")
    
    print(f"📊 总计: {total_courts} 个")

if __name__ == "__main__":
    # 检查后端是否运行
    try:
        response = requests.get(f"{BASE_URL}/api/courts")
        if response.status_code != 200:
            print("错误: 后端服务未运行或无法访问")
            print("请先启动后端服务: python run.py")
            exit(1)
    except Exception as e:
        print(f"错误: 无法连接到后端服务: {e}")
        print("请先启动后端服务: python run.py")
        exit(1)
    
    # 运行批量更新
    asyncio.run(batch_update_details()) 