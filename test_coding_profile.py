#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

def test_coding_profile():
    """测试Profile 1的使用"""
    print("🔍 测试Profile 1使用...")
    
    # 获取用户数据目录
    user_data_dir = os.path.expanduser("~/AppData/Local/Google/Chrome/User Data")
    user_data_dir = os.path.abspath(user_data_dir)
    profile_path = os.path.join(user_data_dir, "Profile 1")
    
    print(f"用户数据目录: {user_data_dir}")
    print(f"Profile 1路径: {profile_path}")
    
    # 检查profile是否存在
    if not os.path.exists(profile_path):
        print(f"❌ Profile 1不存在: {profile_path}")
        return False
    
    print("✅ Profile 1存在")
    
    # 设置Chrome选项
    chrome_options = Options()
    
    # 基本设置
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-blink-features=AutomationControlled')
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    
    # 强制使用Profile 1
    chrome_options.add_argument(f'--user-data-dir={user_data_dir}')
    chrome_options.add_argument('--profile-directory=Profile 1')
    
    # 禁用其他功能
    chrome_options.add_argument('--disable-default-apps')
    chrome_options.add_argument('--disable-extensions')
    
    print("Chrome启动参数:")
    for arg in chrome_options.arguments:
        print(f"  {arg}")
    
    try:
        # 创建驱动
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        
        print("✅ Chrome驱动创建成功")
        
        # 访问chrome://version/验证profile
        print("访问chrome://version/验证profile...")
        driver.get("chrome://version/")
        time.sleep(3)
        
        # 获取页面内容
        page_source = driver.page_source
        
        # 检查是否包含Profile 1相关信息
        if "Profile 1" in page_source:
            print("✅ 页面包含Profile 1信息")
        else:
            print("⚠️ 页面未包含Profile 1信息")
        
        # 打印页面标题
        print(f"页面标题: {driver.title}")
        
        # 访问小红书测试
        print("访问小红书测试...")
        driver.get("https://www.xiaohongshu.com")
        time.sleep(5)
        
        print(f"小红书页面标题: {driver.title}")
        
        # 检查是否已登录
        if "登录" not in driver.page_source and "login" not in driver.page_source.lower():
            print("✅ 可能已登录小红书")
        else:
            print("⚠️ 可能需要登录小红书")
        
        driver.quit()
        print("✅ 测试完成")
        return True
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return False

if __name__ == "__main__":
    test_coding_profile() 