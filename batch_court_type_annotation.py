#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
批量场馆类型标注 - 三层次判断法
1. 硬TAG
2. 直接关键字（顺序：第一级室内/气膜/室外，第二级网球馆/网球场）
3. 间接关键字地址智能解析（排除中心这样的中性词）
"""

import sys
import os
import re
import json
import sqlite3
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import SessionLocal
from app.models import TennisCourt, CourtDetail

# 第三层间接关键字
INDIRECT_INDOOR_KEYWORDS = ['层', '楼', '地下', 'b1', 'b2', 'f1', 'f2', 'f3', 'f4', 'f5', '电梯']
INDIRECT_OUTDOOR_KEYWORDS = ['网球场', '室外', '露天', '户外']

def annotate_court_type(court_name, address=None):
    """
    使用三层判断法确定场馆类型
    1. 硬TAG判断
    2. 直接关键字判断
    3. 间接关键字判断
    如果都无法确定，返回"未知"
    """
    if not court_name:
        return "未知"
    
    name_lower = court_name.lower()
    address_lower = (address or "").lower()
    full_text = name_lower + " " + address_lower
    
    # 第一层：硬TAG判断
    if "室内" in name_lower or "气膜" in name_lower:
        return "室内"
    if "室外" in name_lower:
        return "室外"
    
    # 第二层：直接关键字判断
    # 室内关键字
    indoor_keywords = ["网球馆", "网球中心", "网球俱乐部", "网球汇", "网球学练馆", "网球训练馆"]
    for keyword in indoor_keywords:
        if keyword in name_lower:
            return "室内"
    
    # 室外关键字
    outdoor_keywords = ["网球场", "网球公园", "网球基地"]
    for keyword in outdoor_keywords:
        if keyword in name_lower or keyword in address_lower:
            return "室外"
    
    # 第三层：间接关键字判断
    # 室内间接关键字
    indoor_indirect = ['层', '楼', '地下', 'b1', 'b2', 'f1', 'f2', 'f3', 'f4', 'f5', '电梯']
    for keyword in indoor_indirect:
        if keyword in full_text:
            return "室内"
    
    # 室外间接关键字
    outdoor_indirect = ['网球场', '室外', '露天', '户外']
    for keyword in outdoor_indirect:
        if keyword in full_text:
            return "室外"
    
    # 如果三层判断都无法确定，返回"未知"
    return "未知"

def batch_annotate_court_types():
    """批量标注场馆类型"""
    conn = sqlite3.connect('data/courts.db')
    cursor = conn.cursor()
    
    try:
        # 获取所有场馆
        cursor.execute("SELECT id, name, address, court_type FROM tennis_courts")
        courts = cursor.fetchall()
        print(f"开始批量标注 {len(courts)} 家场馆的类型...")
        
        updated_count = 0
        indoor_count = 0
        outdoor_count = 0
        modified = []
        
        for cid, name, address, old_type in courts:
            # 标注类型
            court_type = annotate_court_type(name, address)
            
            # 更新场馆类型
            if court_type != old_type:
                cursor.execute("UPDATE tennis_courts SET court_type=? WHERE id=?", (court_type, cid))
                updated_count += 1
                
                print(f"场馆: {name}")
                print(f"  地址: {address}")
                print(f"  类型: {old_type} -> {court_type}")
                print()
            
            # 统计
            if court_type == '室内':
                indoor_count += 1
            else:
                outdoor_count += 1
            
            # 记录修改
            modified.append((name, old_type, court_type))
        
        # 提交更改
        conn.commit()
        
        print(f"批量标注完成！")
        print(f"更新场馆数: {updated_count}")
        print(f"室内场馆: {indoor_count}")
        print(f"室外场馆: {outdoor_count}")
        print(f"总计: {len(courts)}")
        
        print(f"共修正{len(modified)}个场馆：")
        for name, old_type, new_type in modified:
            print(f"{name}：{old_type} → {new_type}")
        
    except Exception as e:
        print(f"批量标注出错: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    batch_annotate_court_types() 