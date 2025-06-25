#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

def test_chrome_profile():
    """测试Chrome profile的使用"""
    print("🔍 开始测试Chrome profile...")
    
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
    
    # 检查是否有lock文件
    lock_files = ['lock', 'SingletonLock', 'SingletonCookie', 'SingletonSocket']
    for lock_file in lock_files:
        lock_path = os.path.join(user_data_dir, lock_file)
        if os.path.exists(lock_path):
            print(f"⚠️  发现lock文件: {lock_path}")
    
    # 设置Chrome选项 - 最简配置
    chrome_options = Options()
    
    # 基本设置
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    
    # 使用Profile 1
    chrome_options.add_argument(f'--user-data-dir={user_data_dir}')
    chrome_options.add_argument('--profile-directory=Profile 1')
    
    # 不要加--headless，不要加--remote-debugging-port
    # 不要加其他复杂参数
    
    print("🚀 启动Chrome...")
    print(f"Chrome选项: {chrome_options.arguments}")
    
    try:
        # 启动Chrome
        driver = webdriver.Chrome(options=chrome_options)
        
        print("✅ Chrome启动成功!")
        
        # 访问小红书
        print("🌐 访问小红书...")
        driver.get('https://www.xiaohongshu.com')
        
        # 等待页面加载
        time.sleep(3)
        
        # 获取页面标题
        title = driver.title
        print(f"页面标题: {title}")
        
        # 检查是否登录
        if "小红书" in title:
            print("✅ 成功访问小红书")
        else:
            print("⚠️  页面标题异常")
        
        # 等待用户确认
        input("按回车键关闭浏览器...")
        
        # 关闭浏览器
        driver.quit()
        print("✅ 测试完成")
        return True
        
    except Exception as e:
        print(f"❌ Chrome启动失败: {e}")
        return False

def test_without_profile():
    """测试不使用profile的情况"""
    print("\n🔍 测试不使用profile...")
    
    chrome_options = Options()
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    
    # 不使用任何profile参数
    
    try:
        driver = webdriver.Chrome(options=chrome_options)
        print("✅ 不使用profile启动成功!")
        
        driver.get('https://www.xiaohongshu.com')
        time.sleep(3)
        
        title = driver.title
        print(f"页面标题: {title}")
        
        input("按回车键关闭浏览器...")
        driver.quit()
        return True
        
    except Exception as e:
        print(f"❌ 不使用profile也启动失败: {e}")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("Chrome Profile 测试工具")
    print("=" * 60)
    
    # 测试使用Profile 1
    success1 = test_chrome_profile()
    
    if not success1:
        print("\n" + "=" * 60)
        print("Profile 1测试失败，尝试不使用profile...")
        print("=" * 60)
        success2 = test_without_profile()
        
        if success2:
            print("\n💡 结论: Profile 1目录有问题，建议:")
            print("1. 重启电脑彻底释放profile")
            print("2. 删除Profile 1目录下的lock文件")
            print("3. 备份Profile 1，让Chrome重新创建")
        else:
            print("\n💡 结论: Selenium环境有问题，建议:")
            print("1. 检查Chrome版本和ChromeDriver版本是否匹配")
            print("2. 重新安装selenium和webdriver-manager")
    else:
        print("\n💡 结论: Profile 1工作正常，问题可能在其他地方") 