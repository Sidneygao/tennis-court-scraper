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

def test_simple_profile():
    """简单测试Chrome profile设置"""
    
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
    
    try:
        # 设置Chrome选项
        chrome_options = Options()
        
        # 基本设置
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        
        # 强制使用Coding profile
        chrome_options.add_argument(f'--user-data-dir={user_data_dir}')
        chrome_options.add_argument('--profile-directory=Coding')
        
        # 添加更多强制参数
        chrome_options.add_argument('--force-profile=Coding')
        chrome_options.add_argument('--profile-directory-name=Coding')
        
        # 打印所有Chrome选项
        logger.info("Chrome启动参数:")
        for arg in chrome_options.arguments:
            logger.info(f"  {arg}")
        
        # 设置Chrome驱动
        service = Service(ChromeDriverManager().install())
        
        # 创建驱动
        driver = webdriver.Chrome(service=service, options=chrome_options)
        
        # 访问chrome://version/验证profile
        driver.get("chrome://version/")
        time.sleep(3)
        
        # 获取页面内容
        page_source = driver.page_source
        
        # 检查是否包含Coding
        if "Coding" in page_source:
            logger.info("✅ 成功使用Coding profile")
        else:
            logger.warning("⚠️ 可能未使用Coding profile")
            logger.info("页面内容片段:")
            logger.info(page_source[:500])
        
        # 关闭浏览器
        driver.quit()
        
    except Exception as e:
        logger.error(f"❌ 测试失败: {e}")

if __name__ == "__main__":
    test_simple_profile() 