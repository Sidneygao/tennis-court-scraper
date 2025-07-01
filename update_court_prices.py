from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from app.database import get_db
from app.models import TennisCourt, CourtDetail
import json
import os

# 场馆名称列表
court_names = [
    '乾坤体育网球学练馆(望京SOHOT1商场店)',
    '合拍网球学练馆',
    '启晨体育酒仙桥UCP网球场',
    'PadelOne匹克球板式网球场',
    '酷迪网球(望京校区)',
]

# 预测结果文件路径（可根据实际情况修改）
PREDICT_FILE = 'geojson_predict_results_fixed_20250630_091014.json'

def close_popup(driver):
    # 关闭可能出现的弹窗
    try:
        # 关闭城市选择弹窗
        close_btn = driver.find_element(By.CSS_SELECTOR, '.city-close')
        close_btn.click()
        time.sleep(1)
    except:
        pass
    try:
        # 关闭登录弹窗
        login_close = driver.find_element(By.CSS_SELECTOR, '.close')
        login_close.click()
        time.sleep(1)
    except:
        pass

def get_dianping_price(keyword):
    options = Options()
    # options.add_argument('--headless')  # 如需无头模式可取消注释
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')
    # === 代理设置（请填写你的代理信息） ===
    proxy = "http://user:pass@ip:port"  # ← 这里填写你的代理
    options.add_argument(f'--proxy-server={proxy}')
    driver = webdriver.Chrome(options=options)
    driver.set_window_size(1200, 800)
    try:
        driver.get('https://www.dianping.com/')
        wait = WebDriverWait(driver, 15)
        time.sleep(2)
        close_popup(driver)
        # 尝试多种方式定位搜索框
        try:
            search_box = wait.until(EC.presence_of_element_located((By.ID, 'J-search-input')))
        except:
            try:
                search_box = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'input[type="search"]')))
            except:
                search_box = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'input')))
        search_box.clear()
        search_box.send_keys(keyword)
        search_box.send_keys(Keys.ENTER)
        time.sleep(3)
        # 进入第一个搜索结果
        links = driver.find_elements(By.CSS_SELECTOR, '.tit a, .shop-title a, .shop-name a')
        if not links:
            print(f'{keyword}: 未找到搜索结果')
            return None
        links[0].click()
        time.sleep(3)
        driver.switch_to.window(driver.window_handles[-1])
        # 等待价格元素出现
        try:
            price_elem = WebDriverWait(driver, 8).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, '.price, .shop-price, .shop-info .price'))
            )
            price = price_elem.text
        except Exception:
            price = None
        print(f'{keyword}: {price}')
        return price
    except Exception as e:
        print(f'{keyword}: 抓取失败 {e}')
        return None
    finally:
        driver.quit()

def update_price_in_db(name, price):
    db = next(get_db())
    court = db.query(TennisCourt).filter(TennisCourt.name == name).first()
    if court:
        court.peak_price = price
        db.commit()
        print(f'已更新数据库: {name} -> {price}')
    else:
        print(f'未找到数据库场馆: {name}')

def update_predict_prices(predict_file):
    if not os.path.exists(predict_file):
        print(f'文件不存在: {predict_file}')
        return
    with open(predict_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    results = data.get('results', [])
    print(f'共读取到 {len(results)} 条预测结果')
    db = next(get_db())
    update_count = 0
    for item in results:
        court_id = item.get('court_id')
        predict = item.get('prediction')
        if not court_id or not predict:
            continue
        detail = db.query(CourtDetail).filter(CourtDetail.court_id == court_id).first()
        if detail:
            detail.predict_prices = json.dumps(predict, ensure_ascii=False)
            db.commit()
            update_count += 1
            print(f'已更新 court_id={court_id} 的 predict_prices')
        else:
            print(f'未找到 court_id={court_id} 的 CourtDetail，跳过')
    print(f'批量同步完成，共更新 {update_count} 条记录')

if __name__ == '__main__':
    for name in court_names:
        price = get_dianping_price(name)
        if price:
            update_price_in_db(name, price)
    update_predict_prices(PREDICT_FILE) 