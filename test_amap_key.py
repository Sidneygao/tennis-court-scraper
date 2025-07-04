#!/usr/bin/env python3
"""
测试高德地图API Key是否有效
"""

import os
import requests
import sys

def test_amap_key(api_key=None):
    """测试高德地图API Key"""
    
    # 获取API Key
    if not api_key:
        api_key = os.getenv('AMAP_KEY')
    
    if not api_key:
        print("❌ 未找到高德地图API Key")
        print("请通过以下方式之一设置：")
        print("1. 环境变量: $env:AMAP_KEY='your_key'")
        print("2. .env文件: AMAP_KEY=your_key")
        print("3. 直接传入参数")
        return False
    
    print(f"🔑 使用API Key: {api_key[:8]}...")
    
    # 测试静态地图API
    test_url = f"https://restapi.amap.com/v3/staticmap"
    params = {
        'location': '116.397428,39.90923',  # 天安门坐标
        'zoom': 10,
        'size': '400*300',
        'key': api_key
    }
    
    try:
        print("🌍 正在测试高德地图静态API...")
        response = requests.get(test_url, params=params, timeout=10)
        
        print(f"📊 响应状态码: {response.status_code}")
        print(f"📋 响应头: {response.headers.get('content-type', '未知')}")
        
        if response.status_code == 200:
            content_type = response.headers.get('content-type', '')
            if 'image' in content_type or len(response.content) > 1000:
                print("✅ API Key配置成功！可以生成地图图片")
                return True
            else:
                print("⚠️ API返回成功，但可能不是图片数据")
                print(f"响应内容长度: {len(response.content)}")
                return False
        else:
            print(f"❌ API调用失败: {response.status_code}")
            try:
                error_info = response.json()
                print(f"错误信息: {error_info}")
            except:
                print(f"响应内容: {response.text[:200]}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ 网络请求失败: {e}")
        return False
    except Exception as e:
        print(f"❌ 测试过程中出现错误: {e}")
        return False

def main():
    """主函数"""
    print("🎾 高德地图API Key测试工具")
    print("=" * 50)
    
    # 检查命令行参数
    if len(sys.argv) > 1:
        api_key = sys.argv[1]
        print(f"🔑 使用命令行传入的API Key: {api_key[:8]}...")
        success = test_amap_key(api_key)
    else:
        success = test_amap_key()
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 测试完成！API Key配置正确，可以开始生成地图图片")
        print("\n下一步操作：")
        print("1. 重启后端服务")
        print("2. 访问场馆详情页面，地图图片会自动生成")
        print("3. 或运行批量地图生成脚本")
    else:
        print("💡 请检查API Key配置，然后重新测试")
        print("\n获取API Key步骤：")
        print("1. 访问 https://lbs.amap.com/")
        print("2. 注册/登录账号")
        print("3. 创建Web服务应用")
        print("4. 获取API Key并配置")

if __name__ == "__main__":
    main() 