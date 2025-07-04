#!/usr/bin/env python3
"""
用Selenium自动打开Bing地图网页版，定位到指定经纬度和缩放级别，截图地图区域并保存为本地图片。
"""
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time
import sys
import os
from PIL import Image, ImageDraw
import math

def screenshot_bing(lat, lng, zoom, out_file):
    url = f'https://www.bing.com/maps?cp={lat}~{lng}&lvl={zoom}'
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--window-size=1200,800')
    driver = webdriver.Chrome(options=chrome_options)
    try:
        driver.get(url)
        time.sleep(5)  # 等待地图加载
        # 自动点击公交图层按钮
        try:
            # 尝试查找并点击"图层"按钮
            layer_btn = driver.find_element('xpath', "//button[contains(@aria-label, '图层') or contains(@aria-label, 'Layers')]")
            layer_btn.click()
            time.sleep(1)
            # 查找公交/交通/Transit选项
            transit_btn = driver.find_element('xpath', "//button[contains(@aria-label, '公交') or contains(@aria-label, '交通') or contains(@aria-label, 'Transit')]")
            transit_btn.click()
            print('✅ 已切换公交图层')
            time.sleep(3)  # 等待公交线路渲染
        except Exception as e:
            print(f'⚠️ 未能自动切换公交图层: {e}')
        driver.save_screenshot('full_bing_before.png')
        driver.save_screenshot('full_bing.png')
        # 裁剪地图区域（Bing地图主区域大致在页面中间，1200x800下约[300,80,1100,700]）
        im = Image.open('full_bing.png')
        left, top, right, bottom = 300, 80, 1100, 700
        print(f'裁剪区域: left={left}, top={top}, right={right}, bottom={bottom}')
        im = im.crop((left, top, right, bottom))
        # 综合PIN偏移算法：
        # 1. 先整体向左上（西北）偏移50像素（经验修正，适配Bing地图UI）
        # 2. 再向西（左）偏移190米（约63像素，1像素≈3米）
        offset_ui = 50  # UI修正
        offset_west = 63  # 190米/3米每像素
        center_x = (right - left) // 2 - offset_ui - offset_west
        center_y = (bottom - top) // 2 - offset_ui
        print(f'PIN中心像素(综合修正): x={center_x}, y={center_y}')
        draw = ImageDraw.Draw(im)
        pin_radius = 10
        draw.ellipse([
            center_x - pin_radius, center_y - pin_radius,
            center_x + pin_radius, center_y + pin_radius
        ], fill=(255,0,0), outline=(255,0,0))
        im.save(out_file)
        os.remove('full_bing.png')
        print(f'✅ Bing地图截图已保存为 {out_file}')
    finally:
        driver.quit()

if __name__ == '__main__':
    if len(sys.argv) != 5:
        print('用法: python selenium_bing_map_screenshot.py <lat> <lng> <zoom> <output_file>')
        sys.exit(1)
    lat = float(sys.argv[1])
    lng = float(sys.argv[2])
    zoom = int(sys.argv[3])
    out_file = sys.argv[4]
    screenshot_bing(lat, lng, zoom, out_file) 