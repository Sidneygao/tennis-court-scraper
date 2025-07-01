#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
调试场馆类型判定过程
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.scrapers.price_predictor import PricePredictor

def debug_court_type():
    predictor = PricePredictor()
    
    court_name = "得乐网球俱乐部(宏昌竣网球中心)"
    address = "来广营东路88号(宏昌竣体育公园内)"
    
    print(f"🔍 调试场馆类型判定")
    print(f"场馆名称: {court_name}")
    print(f"场馆地址: {address}")
    print()
    
    # 手动执行三层次判定过程
    court_name_lower = court_name.lower()
    address_lower = address.lower()
    
    print("📋 第一层：硬TAG判断")
    if '室内' in court_name_lower:
        print("  ✅ 包含'室内' → 判定为室内")
        return '室内'
    elif '室外' in court_name_lower:
        print("  ✅ 包含'室外' → 判定为室外")
        return '室外'
    else:
        print("  ❌ 无硬TAG")
    
    print("\n📋 第二层：直接关键字判断")
    if '网球场' in court_name_lower:
        print("  ✅ 包含'网球场' → 判定为室外")
        return '室外'
    elif '网球馆' in court_name_lower:
        print("  ✅ 包含'网球馆' → 判定为室内")
        return '室内'
    elif '气膜' in court_name_lower:
        print("  ✅ 包含'气膜' → 判定为气膜")
        return '气膜'
    else:
        print("  ❌ 无直接关键字")
    
    print("\n📋 第三层：间接关键字评分判断")
    indoor_score = 0
    outdoor_score = 0
    
    print(f"室内关键词: {predictor.indoor_keywords}")
    print(f"室外关键词: {predictor.outdoor_keywords}")
    print()
    
    # 室内关键词评分
    for keyword in predictor.indoor_keywords:
        if keyword in court_name_lower:
            indoor_score += 1
            print(f"  ✅ 室内关键词'{keyword}'匹配")
    
    # 室外关键词评分
    for keyword in predictor.outdoor_keywords:
        if keyword in court_name_lower:
            outdoor_score += 1
            print(f"  ✅ 室外关键词'{keyword}'匹配")
    
    # 检查地址中的"层"字
    import re
    if re.search(r'\d+层', court_name_lower) or re.search(r'\d+层', address_lower):
        indoor_score += 1
        print(f"  ✅ 地址或名称包含'[数字]层' → 室内+1")
    
    print(f"\n📊 评分结果:")
    print(f"  室内评分: {indoor_score}")
    print(f"  室外评分: {outdoor_score}")
    
    if indoor_score > outdoor_score:
        result = '室内'
        print(f"  🏆 室内评分更高 → 判定为室内")
    elif outdoor_score > indoor_score:
        result = '室外'
        print(f"  🏆 室外评分更高 → 判定为室外")
    else:
        result = '室外'  # 默认
        print(f"  🏆 评分相等 → 默认判定为室外")
    
    print(f"\n🎯 最终判定结果: {result}")
    return result

if __name__ == "__main__":
    debug_court_type() 