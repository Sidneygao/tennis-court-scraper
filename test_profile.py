#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import time
import logging
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

# 设置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_chrome_profile():
    """测试Chrome profile设置"""
    
    # 获取用户数据目录
    user_data_dir = os.path.expanduser("~/AppData/Local/Google/Chrome/User Data")
    coding_profile_path = os.path.join(user_data_dir, "Coding")
    
    logger.info(f"用户数据目录: {user_data_dir}")
    logger.info(f"Coding profile路径: {coding_profile_path}")
    
    # 检查profile是否存在
    if os.path.exists(coding_profile_path):
        logger.info("✅ Coding profile存在")
    else:
        logger.error("❌ Coding profile不存在")
        return
    
    # 设置Chrome选项
    chrome_options = Options()
    
    # 强制使用Coding profile
    chrome_options.add_argument(f'--user-data-dir={user_data_dir}')
    chrome_options.add_argument('--profile-directory=Coding')
    chrome_options.add_argument('--force-profile-directory=Coding')
    
    # 禁用默认profile
    chrome_options.add_argument('--disable-default-apps')
    chrome_options.add_argument('--disable-extensions-except')
    chrome_options.add_argument('--load-extension')
    
    # 其他设置
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-blink-features=AutomationControlled')
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    
    # 添加远程调试端口
    chrome_options.add_argument('--remote-debugging-port=9223')
    
    # 打印所有选项
    logger.info("Chrome选项:")
    for arg in chrome_options.arguments:
        logger.info(f"  {arg}")
    
    driver = None
    try:
        # 创建WebDriver
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        
        # 执行反检测脚本
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        # 访问chrome://version/检查profile
        logger.info("访问chrome://version/检查profile信息...")
        driver.get("chrome://version/")
        time.sleep(5)
        
        # 获取页面内容
        version_page = driver.page_source
        logger.info("Chrome版本页面内容:")
        logger.info(version_page[:2000])
        
        # 检查是否包含Coding
        if "Coding" in version_page:
            logger.info("✅ 确认使用了Coding profile")
        else:
            logger.warning("⚠️ 可能未使用Coding profile")
            
            # 尝试访问chrome://settings/
            logger.info("尝试访问chrome://settings/...")
            driver.get("chrome://settings/")
            time.sleep(3)
            
            # 检查settings页面
            settings_page = driver.page_source
            logger.info("Settings页面内容:")
            logger.info(settings_page[:1000])
        
        # 尝试访问小红书
        logger.info("尝试访问小红书...")
        driver.get("https://www.xiaohongshu.com")
        time.sleep(5)
        
        # 检查是否已登录
        current_url = driver.current_url
        logger.info(f"当前URL: {current_url}")
        
        if "login" not in current_url.lower():
            logger.info("✅ 可能已登录小红书")
        else:
            logger.info("⚠️ 可能需要登录小红书")
        
        # 获取页面标题
        title = driver.title
        logger.info(f"页面标题: {title}")
        
        # 检查页面内容
        page_source = driver.page_source
        if "小红书" in page_source:
            logger.info("✅ 成功访问小红书")
        else:
            logger.warning("⚠️ 可能未成功访问小红书")
        
    except Exception as e:
        logger.error(f"测试失败: {e}")
    
    finally:
        if driver:
            try:
                driver.quit()
                logger.info("浏览器已关闭")
            except Exception as e:
                logger.error(f"关闭浏览器失败: {e}")

if __name__ == "__main__":
    test_chrome_profile() 