#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
import time
import re
import json
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import SessionLocal
from app.models import TennisCourt, CourtDetail
from app.scrapers.bing_price_scraper import BingPriceScraper
from sqlalchemy import or_

# 多关键词模板
KEYWORD_TEMPLATES = [
    '{name} 网球价格',
    '{name} 网球场 价格',
    '{name} 网球场 预订',
    '{name} 网球收费',
    '{name} 网球场 收费',
    '{name} 网球场 场地费',
]

# 价格正则
PRICE_REGEX = re.compile(r'(\d{2,4})\s*[-~到至]?\s*(\d{2,4})?\s*[元块]?(/小时|/h|/场)?')


def extract_prices(text):
    """从文本中提取价格区间"""
    results = []
    for match in PRICE_REGEX.finditer(text):
        min_p = match.group(1)
        max_p = match.group(2) or ''
        unit = match.group(3) or ''
        if max_p:
            results.append({'min': int(min_p), 'max': int(max_p), 'unit': unit or '元/小时'})
        else:
            results.append({'min': int(min_p), 'max': int(min_p), 'unit': unit or '元/小时'})
    return results

def is_valid_price(price):
    # 价格合理性判断
    try:
        pmin = int(price['min'])
        pmax = int(price['max'])
        return 30 <= pmin <= 800 and 30 <= pmax <= 800
    except Exception:
        return False

def main():
    db = SessionLocal()
    scraper = BingPriceScraper()
    # 1. 找到所有无价格或价格异常的场馆
    courts = db.query(TennisCourt).join(CourtDetail, CourtDetail.court_id == TennisCourt.id)\
        .filter(
            or_(
                CourtDetail.merged_prices == None,
                CourtDetail.merged_prices == '',
                CourtDetail.merged_prices.like('%该数据不能获得%'),
                CourtDetail.merged_prices.like('%peak_price%'),
                CourtDetail.merged_prices.like('%off_peak_price%')
            )
        ).all()
    # 进一步筛选：已存价格字段小于30或大于800也纳入
    filtered_courts = []
    for court in courts:
        detail = db.query(CourtDetail).filter(CourtDetail.court_id == court.id).first()
        try:
            if detail and detail.merged_prices:
                try:
                    price_obj = json.loads(detail.merged_prices)
                    # 兼容列表和字典两种格式
                    if isinstance(price_obj, dict):
                        prices = [price_obj.get('peak_price'), price_obj.get('off_peak_price')]
                    elif isinstance(price_obj, list):
                        prices = []
                        for p in price_obj:
                            if isinstance(p, dict):
                                prices.extend([p.get('min'), p.get('max')])
                    else:
                        prices = []
                    # 判断是否有异常价格
                    if any(p is not None and (p == '' or int(p) < 30 or int(p) > 800) for p in prices if p not in [None, '']):
                        filtered_courts.append(court)
                        continue
                except Exception:
                    filtered_courts.append(court)
                    continue
            else:
                filtered_courts.append(court)
        except Exception:
            filtered_courts.append(court)
    print(f'共需深入爬取 {len(filtered_courts)} 家场馆...')
    for court in filtered_courts:
        detail = db.query(CourtDetail).filter(CourtDetail.court_id == court.id).first()
        print(f'\n==== 场馆: {court.name} (ID: {court.id}) ===')
        try:
            result = scraper.scrape_court_prices(court.name, court.address)
            peak = result.get('peak_price')
            off_peak = result.get('off_peak_price')
            # 价格过滤
            def valid(p):
                try:
                    return p is not None and 30 <= int(p) <= 800
                except Exception:
                    return False
            valid_peak = valid(peak)
            valid_off_peak = valid(off_peak)
            if valid_peak or valid_off_peak:
                merged = json.dumps({
                    'peak_price': int(peak) if valid_peak else None,
                    'off_peak_price': int(off_peak) if valid_off_peak else None,
                    'unit': '元/小时',
                    'source': 'bing_search'
                }, ensure_ascii=False)
                detail.merged_prices = merged
                db.commit()
                print(f'  ✅ 抓取到有效价格: 高峰 {peak if valid_peak else "(无效)"}，低谷 {off_peak if valid_off_peak else "(无效)"}')
            else:
                print(f'  ⚠️  价格无效，已忽略。高峰: {peak}，低谷: {off_peak}')
        except Exception as e:
            print(f'  [ERROR] 抓取失败: {e}')
        time.sleep(2)
    print('\n全部深入爬取完成。')

if __name__ == '__main__':
    main() 