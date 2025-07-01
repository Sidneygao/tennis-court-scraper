import requests
from bs4 import BeautifulSoup
import re
import json
from difflib import SequenceMatcher
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

# 读取高德场馆库
with open('courts.json', 'r', encoding='utf-8') as f:
    gaode_courts = json.load(f)

def similar(a, b):
    return SequenceMatcher(None, a, b).ratio()

def baidu_search(query, page=0):
    url = f'https://www.baidu.com/s?wd={query}&pn={page*10}'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36'
    }
    resp = requests.get(url, headers=headers, timeout=10)
    resp.encoding = resp.apparent_encoding
    return resp.text

def extract_price(text):
    # 原始价格信息
    price_raw = []
    # 结构化价格信息
    price_struct = []
    # 匹配常见价格表达
    for m in re.finditer(r'(\d{2,4})\s*元/小时|包场\d{2,4}元|会员价\d{2,4}元', text):
        price_raw.append(m.group())
        # 结构化
        if '元/小时' in m.group():
            price_struct.append(f"{m.group(1)}元/小时")
        elif '包场' in m.group():
            price_struct.append(f"包场{re.search(r'\d+', m.group()).group()}元")
        elif '会员价' in m.group():
            price_struct.append(f"会员价{re.search(r'\d+', m.group()).group()}元")
    return '; '.join(price_raw), '; '.join(price_struct)

def parse_baidu_results(html):
    soup = BeautifulSoup(html, 'html.parser')
    results = []
    for item in soup.select('.result'):
        title = item.select_one('h3')
        if not title:
            continue
        name = title.get_text(strip=True)
        link = title.a['href'] if title.a else ''
        desc = item.get_text(separator=' ', strip=True)
        results.append({'name': name, 'desc': desc, 'link': link})
    return results

def get_real_url(baidu_url):
    try:
        resp = requests.get(baidu_url, timeout=10, allow_redirects=True)
        return resp.url
    except Exception:
        return baidu_url

def fetch_detail_page_selenium(url, driver):
    try:
        driver.get(url)
        time.sleep(2)
        return driver.page_source
    except Exception:
        return ''

def fetch_detail_page_requests(url):
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        resp = requests.get(url, headers=headers, timeout=10)
        resp.encoding = resp.apparent_encoding
        return resp.text
    except Exception:
        return ''

def fuzzy_match(baidu_name, gaode_courts):
    best = None
    best_score = 0
    for c in gaode_courts:
        score = similar(baidu_name, c['name'])
        if score > best_score:
            best = c
            best_score = score
    return best, best_score

if __name__ == '__main__':
    keywords = [
        '北京网球场盘点',
        '朝阳区网球场盘点',
        '丰台区网球场盘点',
        '亦庄网球场盘点'
    ]
    all_results = []
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--no-sandbox')
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    for kw in keywords:
        for page in range(3):
            html = baidu_search(kw, page)
            results = parse_baidu_results(html)
            for r in results:
                match, score = fuzzy_match(r['name'], gaode_courts)
                if match and score > 0.6:
                    real_url = get_real_url(r['link']) if r['link'] else ''
                    detail_html = ''
                    if real_url:
                        detail_html = fetch_detail_page_selenium(real_url, driver)
                        if not detail_html:
                            detail_html = fetch_detail_page_requests(real_url)
                    price_raw, price_struct = extract_price(detail_html)
                    if price_raw:
                        all_results.append({
                            '高德场馆名称': match['name'],
                            '高德地址': f"({match.get('latitude','')},{match.get('longitude','')})",
                            '百度爬取名称': r['name'],
                            '百度详情页原文价格': price_raw,
                            '百度加工后价格': price_struct,
                            '详情页链接': real_url,
                            '匹配分数': score
                        })
                    time.sleep(1)
    driver.quit()
    print('高德场馆名称 | 高德地址 | 百度爬取名称 | 百度详情页原文价格 | 百度加工后价格 | 详情页链接')
    for row in all_results:
        print(f"{row['高德场馆名称']} | {row['高德地址']} | {row['百度爬取名称']} | {row['百度详情页原文价格']} | {row['百度加工后价格']} | {row['详情页链接']}") 