#!/usr/bin/env python3
"""
检查场馆类型判断
"""

from app.database import SessionLocal
from app.models import TennisCourt
from app.scrapers.price_predictor import PricePredictor

def check_court_type():
    db = SessionLocal()
    try:
        # 查找嘉里中心网球场
        court = db.query(TennisCourt).filter(TennisCourt.name.like('%嘉里中心%')).first()
        if court:
            print(f"场馆: {court.name}")
            print(f"地址: {court.address}")
            print(f"当前类型: {court.court_type}")
            
            # 手动执行判断逻辑
            name_lower = court.name.lower()
            address_lower = court.address.lower()
            full_text = name_lower + " " + address_lower
            
            print(f"\n=== 判断过程 ===")
            print(f"名称: {name_lower}")
            print(f"地址: {address_lower}")
            print(f"完整文本: {full_text}")
            
            # 第一层：硬TAG判断
            print(f"\n第一层：硬TAG判断")
            if "室内" in name_lower or "气膜" in name_lower:
                print("✓ 匹配室内硬TAG")
                return "室内"
            if "室外" in name_lower:
                print("✓ 匹配室外硬TAG")
                return "室外"
            print("✗ 无硬TAG匹配")
            
            # 第二层：直接关键字判断
            print(f"\n第二层：直接关键字判断")
            outdoor_keywords = ["网球场", "网球公园", "网球基地"]
            for keyword in outdoor_keywords:
                if keyword in name_lower or keyword in address_lower:
                    print(f"✓ 匹配室外关键字: {keyword}")
                    return "室外"
            
            indoor_keywords = ["网球馆", "网球汇", "网球学练馆", "网球训练馆", "体育馆"]
            for keyword in indoor_keywords:
                if keyword in name_lower or keyword in address_lower:
                    print(f"✓ 匹配室内关键字: {keyword}")
                    return "室内"
            print("✗ 无直接关键字匹配")
            
            # 第三层：间接关键字判断
            print(f"\n第三层：间接关键字判断")
            indoor_indirect = ['层', '楼', '地下', 'b1', 'b2', 'f1', 'f2', 'f3', 'f4', 'f5', '电梯', '馆内']
            for keyword in indoor_indirect:
                if keyword in full_text:
                    print(f"✓ 匹配室内间接关键字: {keyword}")
                    return "室内"
            
            # 检查数字+层模式
            import re
            if re.search(r'\d+层', full_text):
                print("✓ 匹配数字+层模式")
                return "室内"
            print("✗ 无数字+层模式匹配")
            
            outdoor_indirect = ['网球场', '室外', '露天', '户外']
            for keyword in outdoor_indirect:
                if keyword in full_text:
                    print(f"✓ 匹配室外间接关键字: {keyword}")
                    return "室外"
            
            print("✗ 无间接关键字匹配")
            return "未知"
            
        else:
            print("未找到嘉里中心网球场")
            
    finally:
        db.close()

if __name__ == "__main__":
    result = check_court_type()
    print(f"\n最终结果: {result}") 