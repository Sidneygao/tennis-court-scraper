#!/usr/bin/env python3
"""
批量生成所有场馆的地图图片
"""

import os
import sys
import sqlite3
import time
from pathlib import Path

# 添加项目路径
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from app.scrapers.map_generator import MapGenerator

def batch_generate_maps(amap_key: str = None):
    """批量生成所有场馆的地图图片"""
    
    print("🎾 批量生成场馆地图图片")
    print("=" * 50)
    
    # 检查数据库
    db_path = "data/courts.db"
    if not os.path.exists(db_path):
        print(f"❌ 数据库文件不存在: {db_path}")
        return False
    
    # 初始化地图生成器，传入API Key
    try:
        map_generator = MapGenerator(amap_key=amap_key)
        print("✅ 地图生成器初始化成功")
        if amap_key:
            print(f"🔑 使用高德地图API Key: {amap_key[:8]}...")
        else:
            print("⚠️  未提供高德地图API Key，将使用OSM兜底")
    except Exception as e:
        print(f"❌ 地图生成器初始化失败: {e}")
        return False
    
    # 连接数据库
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        print("✅ 数据库连接成功")
    except Exception as e:
        print(f"❌ 数据库连接失败: {e}")
        return False
    
    # 获取所有场馆
    try:
        cursor.execute("""
            SELECT id, name, latitude, longitude 
            FROM tennis_courts 
            WHERE latitude IS NOT NULL AND longitude IS NOT NULL
        """)
        courts = cursor.fetchall()
        print(f"📊 找到 {len(courts)} 个有效场馆")
    except Exception as e:
        print(f"❌ 查询场馆失败: {e}")
        conn.close()
        return False
    
    # 批量生成地图
    success_count = 0
    fail_count = 0
    small_file_count = 0
    same_size_count = 0
    
    # 记录文件大小，用于检测重复
    file_sizes = {}
    
    for i, (court_id, name, lat, lng) in enumerate(courts, 1):
        print(f"\n[{i}/{len(courts)}] 处理场馆: {name}")
        print(f"   坐标: {lat}, {lng}")
        
        try:
            # 生成地图图片
            map_path = map_generator.generate_smart_map(name, lat, lng)
            
            if map_path:
                # 检查文件大小
                if os.path.exists(map_path):
                    file_size = os.path.getsize(map_path)
                    print(f"   文件大小: {file_size} 字节")
                    
                    # 检查文件是否太小（小于1KB）
                    if file_size < 1024:
                        print(f"   ⚠️  文件太小 ({file_size} 字节)，可能生成失败")
                        small_file_count += 1
                        fail_count += 1
                        continue
                    
                    # 检查文件大小是否重复
                    if file_size in file_sizes:
                        print(f"   ⚠️  文件大小重复 ({file_size} 字节)，与 {file_sizes[file_size]} 相同")
                        same_size_count += 1
                        if same_size_count >= 3:  # 如果连续3个文件大小相同，停止
                            print(f"   🛑 连续 {same_size_count} 个文件大小相同，停止生成并检查抓取逻辑")
                            break
                    else:
                        file_sizes[file_size] = name
                        same_size_count = 0  # 重置计数器
                    
                    # 更新数据库
                    cursor.execute("""
                        UPDATE court_details 
                        SET map_image = ? 
                        WHERE court_id = ?
                    """, (map_path, court_id))
                    conn.commit()
                    print(f"✅ 地图生成成功: {map_path}")
                    success_count += 1
                else:
                    print(f"❌ 生成的文件不存在: {map_path}")
                    fail_count += 1
            else:
                print(f"❌ 地图生成失败")
                fail_count += 1
                
        except Exception as e:
            print(f"❌ 处理失败: {e}")
            fail_count += 1
        
        # 控制频率，避免API限制
        time.sleep(0.5)
    
    # 输出结果
    print(f"\n🎉 批量生成完成!")
    print(f"✅ 成功: {success_count} 个")
    print(f"❌ 失败: {fail_count} 个")
    print(f"📊 总计: {len(courts)} 个")
    print(f"⚠️  文件太小: {small_file_count} 个")
    print(f"⚠️  文件大小重复: {same_size_count} 个")
    
    if small_file_count > 0 or same_size_count >= 3:
        print(f"\n🔍 建议检查:")
        print(f"1. 高德地图API Key是否有效")
        print(f"2. 网络连接是否正常")
        print(f"3. 地图生成器逻辑是否有问题")
    
    conn.close()
    return True

def fix_map_image_paths():
    """批量修正数据库中map_image字段为以/data/map_cache/开头"""
    db_path = "data/courts.db"
    if not os.path.exists(db_path):
        print(f"❌ 数据库文件不存在: {db_path}")
        return False
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT id, map_image FROM court_details WHERE map_image LIKE 'data/map_cache/%'")
        rows = cursor.fetchall()
        count = 0
        for detail_id, old_path in rows:
            if old_path and old_path.startswith('data/map_cache/'):
                new_path = '/' + old_path
                cursor.execute("UPDATE court_details SET map_image=? WHERE id=?", (new_path, detail_id))
                count += 1
        conn.commit()
        conn.close()
        print(f"✅ 已修正{count}条map_image路径为前端可访问格式")
        return True
    except Exception as e:
        print(f"❌ 修正map_image路径失败: {e}")
        return False

def main():
    """主函数"""
    print("🎾 网球场馆地图批量生成工具")
    print("=" * 50)
    
    # 修正map_image路径
    fix_map_image_paths()
    
    # 检查环境
    if not os.path.exists("data/courts.db"):
        print("❌ 数据库文件不存在，请先确保有场馆数据")
        return
    
    # 检查地图生成器依赖
    try:
        from app.scrapers.map_generator import MapGenerator
        print("✅ 地图生成器依赖检查通过")
    except ImportError as e:
        print(f"❌ 地图生成器依赖缺失: {e}")
        return
    
    # 使用您提供的API Key
    AMAP_KEY = "213dd87b21e5e3d8eab72f1a62da1a8e"
    
    if batch_generate_maps(AMAP_KEY):
        print("\n🎉 批量生成完成！")
        print("现在可以：")
        print("1. 重启后端服务")
        print("2. 访问场馆详情页面查看地图图片")
    else:
        print("\n💡 批量生成未完成，请检查：")
        print("1. 高德地图API Key是否配置正确")
        print("2. 网络连接是否正常")
        print("3. 场馆数据是否有效")

if __name__ == "__main__":
    main() 