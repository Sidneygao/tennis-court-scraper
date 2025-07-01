#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查缓存文件中的数据量
"""
import json

def main():
    print("🔍 检查缓存文件数据量...")
    
    try:
        with open('data/new_areas_cache.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        print(f"缓存文件时间戳: {data.get('timestamp', '未知')}")
        print(f"区域列表: {data.get('areas', [])}")
        
        amap_data = data.get('amap_data', {})
        print(f"\n📊 高德数据统计:")
        for area, records in amap_data.items():
            print(f"  {area}: {len(records)} 条记录")
        
        total_records = sum(len(records) for records in amap_data.values())
        print(f"\n总计: {total_records} 条记录")
        
        # 检查前几条记录的结构
        if amap_data:
            first_area = list(amap_data.keys())[0]
            if amap_data[first_area]:
                print(f"\n📋 {first_area} 区域第一条记录示例:")
                first_record = amap_data[first_area][0]
                if isinstance(first_record, str):
                    print(f"  记录格式: 字符串")
                    print(f"  内容预览: {first_record[:200]}...")
                else:
                    print(f"  名称: {first_record.get('name', 'N/A')}")
                    print(f"  地址: {first_record.get('address', 'N/A')}")
                    print(f"  坐标: {first_record.get('latitude', 'N/A')}, {first_record.get('longitude', 'N/A')}")
        
    except Exception as e:
        print(f"❌ 读取缓存文件失败: {e}")

if __name__ == "__main__":
    main() 