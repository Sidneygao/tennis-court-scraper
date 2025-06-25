#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import asyncio
import logging
import json
import hashlib
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
    
    def generate_data_hash(self, data: Dict[str, Any]) -> str:
        """生成数据的哈希值用于比较"""
        # 对数据进行排序和序列化，确保哈希一致性
        def sort_dict(d):
            if isinstance(d, dict):
                return {k: sort_dict(v) for k, v in sorted(d.items())}
            elif isinstance(d, list):
                return [sort_dict(item) for item in sorted(d, key=lambda x: str(x))]
            else:
                return d
        
        sorted_data = sort_dict(data)
        data_str = json.dumps(sorted_data, ensure_ascii=False, sort_keys=True)
        return hashlib.md5(data_str.encode('utf-8')).hexdigest()
    
    def compare_data(self, old_data: Dict[str, Any], new_data: Dict[str, Any]) -> Dict[str, bool]:
        """比较新旧数据，返回哪些字段发生了变化"""
        changes = {
            'description': False,
            'facilities': False,
            'business_hours': False,
            'prices': False,
            'rating': False,
            'reviews': False,
            'images': False
        }
        
        # 比较各个字段
        if old_data.get('description') != new_data.get('description'):
            changes['description'] = True
            
        if old_data.get('facilities') != new_data.get('facilities'):
            changes['facilities'] = True
            
        if old_data.get('business_hours') != new_data.get('business_hours'):
            changes['business_hours'] = True
            
        # 比较价格（JSON格式）
        old_prices = old_data.get('prices', [])
        new_prices = new_data.get('prices', [])
        if self.generate_data_hash(old_prices) != self.generate_data_hash(new_prices):
            changes['prices'] = True
            
        if old_data.get('rating', 0) != new_data.get('rating', 0):
            changes['rating'] = True
            
        # 比较评论（JSON格式）
        old_reviews = old_data.get('reviews', [])
        new_reviews = new_data.get('reviews', [])
        if self.generate_data_hash(old_reviews) != self.generate_data_hash(new_reviews):
            changes['reviews'] = True
            
        # 比较图片（JSON格式）
        old_images = old_data.get('images', [])
        new_images = new_data.get('images', [])
        if self.generate_data_hash(old_images) != self.generate_data_hash(new_images):
            changes['images'] = True
            
        return changes
    
    def has_changes(self, changes: Dict[str, bool]) -> bool:
        """检查是否有任何变化"""
        return any(changes.values())
    
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