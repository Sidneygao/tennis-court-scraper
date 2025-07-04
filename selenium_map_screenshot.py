#!/usr/bin/env python3
"""
用Selenium自动打开高德地图网页版，定位到指定经纬度，截图地图区域并保存为本地图片。
"""
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time
import sys
import os

def screenshot_amap(lat, lng, out_file):
    url = f'https://ditu.amap.com/'
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--window-size=1200,800')
    driver = webdriver.Chrome(options=chrome_options)
    try:
        driver.get(url)
        time.sleep(3)
        # 搜索框输入经纬度
        search_box = driver.find_element(By.ID, 'searchInput')
        search_box.clear()
        search_box.send_keys(f'{lng},{lat}')
        search_btn = driver.find_element(By.ID, 'searchButton')
        search_btn.click()
        time.sleep(4)
        # 关闭左侧面板，最大化地图
        try:
            close_btn = driver.find_element(By.CLASS_NAME, 'close')
            close_btn.click()
            time.sleep(1)
        except Exception:
            pass
        # 截图地图区域
        map_canvas = driver.find_element(By.ID, 'container')
        location = map_canvas.location
        size = map_canvas.size
        driver.save_screenshot('full.png')
        from PIL import Image
        im = Image.open('full.png')
        left = int(location['x'])
        top = int(location['y'])
        right = left + int(size['width'])
        bottom = top + int(size['height'])
        im = im.crop((left, top, right, bottom))
        im.save(out_file)
        os.remove('full.png')
        print(f'✅ 地图截图已保存为 {out_file}')
    finally:
        driver.quit()

if __name__ == '__main__':
    if len(sys.argv) != 4:
        print('用法: python selenium_map_screenshot.py <lat> <lng> <output_file>')
        sys.exit(1)
    lat = float(sys.argv[1])
    lng = float(sys.argv[2])
    out_file = sys.argv[3]
    screenshot_amap(lat, lng, out_file) 