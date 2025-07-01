import requests
from bs4 import BeautifulSoup
import json
import pandas as pd
from rapidfuzz import fuzz, process

# 1. 采集 gotennis 场馆列表
GOTENNIS_URL = 'http://gotennis.cn/hall/frontend/list'
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
}

resp = requests.get(GOTENNIS_URL, headers=headers, timeout=15)
soup = BeautifulSoup(resp.text, 'html.parser')

# 假设页面有 class="hall-item" 的div，每个div下有名称和地址
halls = []
for item in soup.find_all(class_='hall-item'):
    name = item.find(class_='hall-name')
    addr = item.find(class_='hall-address')
    name = name.get_text(strip=True) if name else ''
    addr = addr.get_text(strip=True) if addr else ''
    if name:
        halls.append({'gotennis_name': name, 'gotennis_addr': addr})

# 2. 读取本地 courts.json
with open('courts.json', encoding='utf-8') as f:
    courts = json.load(f)

local_courts = []
for c in courts:
    local_courts.append({
        'local_name': c.get('name', ''),
        'local_addr': c.get('address', '')
    })

# 3. 用 rapidfuzz 进行模糊匹配
results = []
for hall in halls:
    best = process.extractOne(
        hall['gotennis_name'],
        [lc['local_name'] for lc in local_courts],
        scorer=fuzz.token_sort_ratio
    )
    best_idx = [lc['local_name'] for lc in local_courts].index(best[0]) if best else -1
    best_local = local_courts[best_idx] if best_idx >= 0 else {'local_name': '', 'local_addr': ''}
    results.append({
        'gotennis_name': hall['gotennis_name'],
        'gotennis_addr': hall['gotennis_addr'],
        'local_name': best_local['local_name'],
        'local_addr': best_local['local_addr'],
        'name_score': best[1] if best else 0
    })

# 4. 输出结果
pd.DataFrame(results).to_csv('gotennis_vs_courts_match.csv', index=False, encoding='utf-8-sig')
print('匹配完成，结果已保存为 gotennis_vs_courts_match.csv') 