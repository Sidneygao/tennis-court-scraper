#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
import tempfile
import os
from app.scrapers.xiaohongshu_selenium import XiaohongshuSeleniumScraper

# 设置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def test_xiaohongshu_scraper():
    """测试小红书爬虫"""
    print("开始测试小红书爬虫...")
    
    scraper = None
    try:
        # 使用临时用户数据目录
        temp_dir = tempfile.mkdtemp(prefix='chrome_selenium_')
        print(f"使用临时用户数据目录: {temp_dir}")
        
        # 创建爬虫实例
        scraper = XiaohongshuSeleniumScraper(user_data_dir=temp_dir)
        
        # 设置浏览器驱动
        if not scraper.setup_driver():
            print("❌ 浏览器驱动设置失败")
            return
        
        # 测试爬取
        keyword = "网球"
        result = scraper.search_xiaohongshu(keyword)
        
        if result:
            print(f"\n✅ 爬取成功!")
            print(f"评分: {result.get('rating', 'N/A')}")
            print(f"评论数: {result.get('review_count', 'N/A')}")
            print(f"描述: {result.get('description', 'N/A')[:100]}...")
            print(f"设施: {result.get('facilities', 'N/A')}")
            print(f"营业时间: {result.get('business_hours', 'N/A')}")
            print(f"价格: {result.get('prices', [])}")
            print(f"图片: {len(result.get('images', []))} 张")
            
            if result.get('reviews'):
                print(f"\n评论:")
                for i, review in enumerate(result['reviews'][:3]):
                    print(f"  {i+1}. {review.get('user', 'N/A')} - {review.get('rating', 'N/A')}星")
                    print(f"     {review.get('content', 'N/A')[:50]}...")
        else:
            print("❌ 爬取失败，未获取到数据")
        
        print("\n测试完成!")
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
    finally:
        if scraper:
            scraper.close()
        # 清理临时目录
        try:
            import shutil
            shutil.rmtree(temp_dir, ignore_errors=True)
        except:
            pass

if __name__ == "__main__":
    test_xiaohongshu_scraper() 