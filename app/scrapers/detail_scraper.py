#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import asyncio
import logging
from typing import Dict, List, Optional, Any
from .xiaohongshu_smart import XiaohongshuSmartScraper

logger = logging.getLogger(__name__)

class DetailScraper:
    """详情爬虫 - 融合多个平台的数据（集成智能小红书爬虫）"""
    
    def __init__(self):
        self.platforms = {
            'xiaohongshu': self._scrape_xiaohongshu
        }
        self.xiaohongshu_scraper = XiaohongshuSmartScraper()
    
    def is_cache_valid(self, last_update):
        from datetime import datetime, timedelta
        if not last_update:
            return False
        return (datetime.now() - last_update) < timedelta(hours=24)
    
    async def scrape_all_platforms(self, venue_name: str, venue_address: str = "") -> Dict[str, Any]:
        """爬取所有平台的数据"""
        logger.info(f"开始爬取场馆详情: {venue_name}")
        
        # 只用智能小红书爬虫
        keywords = [venue_name]
        all_data = {
            'venue_name': venue_name,
            'venue_address': venue_address,
            'platforms': {},
            'summary': {}
        }
        # 只跑小红书
        result = self._scrape_xiaohongshu(venue_name)
        if result:
            all_data['platforms']['xiaohongshu'] = {'status': 'success', 'data': result}
        else:
            all_data['platforms']['xiaohongshu'] = {'status': 'error', 'data': None}
        all_data['summary'] = self._generate_summary(all_data['platforms'])
        return all_data
    
    def _scrape_xiaohongshu(self, keyword: str) -> Optional[Dict[str, Any]]:
        """爬取小红书数据"""
        try:
            # 爬取数据 - 使用新的方法名和参数
            result = self.xiaohongshu_scraper.scrape_court_details(keyword)
            
            if not result:
                return None
            
            # 转换数据格式
            return {
                'rating': result.get('rating', 0),
                'review_count': result.get('review_count', 0),
                'reviews': result.get('reviews', []),
                'description': result.get('description', ''),
                'facilities': result.get('facilities', ''),
                'business_hours': result.get('business_hours', ''),
                'prices': result.get('prices', []),
                'images': result.get('images', [])
            }
            
        except Exception as e:
            logger.error(f"小红书爬取失败: {e}")
            return None
    
    def _generate_summary(self, platforms_data: Dict[str, Any]) -> Dict[str, Any]:
        """生成综合摘要"""
        summary = {
            'total_platforms': len(platforms_data),
            'successful_platforms': 0,
            'total_reviews': 0,
            'total_rating': 0.0,
            'avg_rating': 0.0,
            'best_platform': None,
            'best_rating': 0.0,
            'all_reviews': [],
            'all_prices': [],
            'all_facilities': set(),
            'all_images': []
        }
        
        successful_count = 0
        
        for platform_name, platform_data in platforms_data.items():
            if platform_data.get('status') == 'success' and platform_data.get('data'):
                successful_count += 1
                data = platform_data['data']
                
                # 统计评分
                rating = data.get('rating', 0)
                if rating > 0:
                    summary['total_rating'] += rating
                    if rating > summary['best_rating']:
                        summary['best_rating'] = rating
                        summary['best_platform'] = platform_name
                
                # 统计评论
                reviews = data.get('reviews', [])
                summary['total_reviews'] += len(reviews)
                summary['all_reviews'].extend(reviews)
                
                # 统计价格
                prices = data.get('prices', [])
                summary['all_prices'].extend(prices)
                
                # 统计设施
                facilities = data.get('facilities', '')
                if facilities:
                    summary['all_facilities'].add(facilities)
                
                # 统计图片
                images = data.get('images', [])
                summary['all_images'].extend(images)
        
        summary['successful_platforms'] = successful_count
        
        # 计算平均评分
        if successful_count > 0:
            summary['avg_rating'] = summary['total_rating'] / successful_count
        
        # 转换设施集合为列表
        summary['all_facilities'] = list(summary['all_facilities'])
        
        return summary
    
    def close(self):
        """关闭爬虫资源"""
        pass

async def scrape_venue_details(venue_name: str, venue_address: str = "") -> Dict[str, Any]:
    """爬取场馆详情的便捷函数"""
    scraper = DetailScraper()
    try:
        return await scraper.scrape_all_platforms(venue_name, venue_address)
    finally:
        scraper.close()

# 测试函数
async def test():
    """测试函数"""
    result = await scrape_venue_details("测试网球馆", "北京市朝阳区")
    print(result)

if __name__ == "__main__":
    asyncio.run(test()) 