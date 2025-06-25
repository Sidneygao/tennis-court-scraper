from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from app.database import get_db
from app.models import TennisCourt

# 场馆名称列表
court_names = [
    '乾坤体育网球学练馆(望京SOHOT1商场店)',
    '合拍网球学练馆',
    '启晨体育酒仙桥UCP网球场',
    'PadelOne匹克球板式网球场',
    '酷迪网球(望京校区)',
]

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

if __name__ == '__main__':
    for name in court_names:
        price = get_dianping_price(name)
        if price:
            update_price_in_db(name, price) 