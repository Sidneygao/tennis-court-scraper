#!/usr/bin/env python3
"""
测试Bing静态地图API，支持自定义经纬度、缩放级别和地铁/公交标记
"""
import requests
import os

def test_bing_staticmap():
    # 需替换为您的Bing Maps Key（可用免费Key测试）
    BING_KEY = os.getenv('BING_MAPS_KEY', '')
    if not BING_KEY:
        print('❌ 未设置Bing Maps Key，请设置环境变量BING_MAPS_KEY')
        return
    
    # 测试参数
    latitude = 39.913837
    longitude = 116.458604
    zoom = 14  # 2KM地铁/1KM公交建议用14-15
    map_size = '600,300'
    pushpins = f'{latitude},{longitude};66;场馆'
    
    # Bing静态地图API
    url = f'https://dev.virtualearth.net/REST/v1/Imagery/Map/Road/{latitude},{longitude}/{zoom}?mapSize={map_size}&pushpin={latitude},{longitude};66;场馆&key={BING_KEY}'
    print(f'🔗 请求URL: {url}')
    try:
        response = requests.get(url, timeout=10)
        print(f'📊 响应状态码: {response.status_code}')
        print(f'📏 响应内容长度: {len(response.content)} 字节')
        print(f'📄 响应头: {dict(response.headers)}')
        content_type = response.headers.get('content-type', '')
        print(f'📋 内容类型: {content_type}')
        if response.status_code == 200 and 'image' in content_type:
            with open('test_bing_map.png', 'wb') as f:
                f.write(response.content)
            print('✅ 图片已保存为 test_bing_map.png')
        else:
            print('❌ 响应不是图片或API出错')
            print(response.text[:200])
    except Exception as e:
        print(f'❌ 请求失败: {e}')

if __name__ == '__main__':
    test_bing_staticmap() 