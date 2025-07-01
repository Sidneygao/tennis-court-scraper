#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
将现有的BING价格数据转换为预测价格格式（严格按室内60~600元、室外50~300元区间过滤，输出所有BING价格场馆调试信息）
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import SessionLocal
from app.models import TennisCourt, CourtDetail
import json
import re

def extract_price_from_string(price_str):
    """从价格字符串中提取数字价格"""
    if not price_str:
        return None
    match = re.search(r'¥?(\d+(?:\.\d+)?)', str(price_str))
    if match:
        return float(match.group(1))
    return None

def is_indoor(court_type):
    """判断是否为室内场馆"""
    if not court_type:
        return False
    return any(key in court_type for key in ['室内', '气膜'])

def is_outdoor(court_type):
    """判断是否为室外场馆"""
    if not court_type:
        return False
    return '室外' in court_type

def convert_bing_to_predict_prices():
    """将现有的BING价格数据转换为预测价格格式（区间过滤+调试）"""
    db = SessionLocal()
    try:
        details = db.query(CourtDetail).filter(CourtDetail.merged_prices.isnot(None)).all()
        print(f"🔍 检查所有有BING价格的场馆（区间过滤+调试）\n")
        print(f"总详情记录数: {len(details)}")
        for detail in details:
            try:
                prices = json.loads(detail.merged_prices)
                if not prices or not isinstance(prices, list):
                    continue
                bing_prices = []
                for price in prices:
                    if price.get('source') == 'BING':
                        bing_prices.append(price)
                if bing_prices:
                    court = db.query(TennisCourt).filter(TennisCourt.id == detail.court_id).first()
                    court_name = court.name if court else f"ID:{detail.court_id}"
                    court_type = court.court_type if court else ''
                    # 原始BING价格
                    all_bing_raw = []
                    for price_data in bing_prices:
                        price_str = price_data.get('price')
                        price_num = extract_price_from_string(price_str)
                        if price_num:
                            all_bing_raw.append(price_num)
                    # 区间过滤
                    all_prices = []
                    for price_num in all_bing_raw:
                        if is_indoor(court_type):
                            if 60 <= price_num <= 600:
                                all_prices.append(price_num)
                        elif is_outdoor(court_type):
                            if 50 <= price_num <= 300:
                                all_prices.append(price_num)
                        else:
                            # 类型未知时，全部丢弃
                            pass
                    print(f"\n🏟️ {court_name}")
                    print(f"   类型: {court_type}")
                    print(f"   原始BING价格: {all_bing_raw}")
                    print(f"   区间内采纳价格: {all_prices}")
            except Exception as e:
                print(f"❌ 处理详情ID {detail.id} 失败: {e}")
    except Exception as e:
        print(f"❌ 转换过程失败: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    convert_bing_to_predict_prices() 