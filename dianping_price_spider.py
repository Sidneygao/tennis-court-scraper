from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
import time

# 场馆名称列表（可根据实际情况替换）
court_names = [
    '乾坤体育网球学练馆(望京SOHOT1商场店)',
    '合拍网球学练馆',
    '启晨体育酒仙桥UCP网球场',
    'PadelOne匹克球板式网球场',
    '酷迪网球(望京校区)',
    # 可补充真实场馆名
]

def get_dianping_price(keyword):
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')
    driver = webdriver.Chrome(options=options)
    driver.set_window_size(1200, 800)
    try:
        # 1. 打开大众点评首页
        driver.get('https://www.dianping.com/')
        time.sleep(2)
        # 2. 搜索场馆
        search_box = driver.find_element(By.ID, 'J-search-input')
        search_box.clear()
        search_box.send_keys(keyword)
        search_box.send_keys(Keys.ENTER)
        time.sleep(3)
        # 3. 进入第一个搜索结果
        links = driver.find_elements(By.CSS_SELECTOR, '.tit a')
        if not links:
            print(f'{keyword}: 未找到搜索结果')
            return None
        links[0].click()
        time.sleep(3)
        # 切换到新窗口
        driver.switch_to.window(driver.window_handles[-1])
        # 4. 抓取价格信息
        try:
            price_elem = driver.find_element(By.CSS_SELECTOR, '.price')
            price = price_elem.text
        except Exception:
            price = '未找到价格'
        print(f'{keyword}: {price}')
        return price
    except Exception as e:
        print(f'{keyword}: 抓取失败 {e}')
        return None
    finally:
        driver.quit()

if __name__ == '__main__':
    for name in court_names:
        get_dianping_price(name) 