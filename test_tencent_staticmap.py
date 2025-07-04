#!/usr/bin/env python3
"""
测试腾讯地图静态图片API，使用用户提供的KEY，下载指定经纬度的地图图片，支持自定义缩放。
"""
import requests

# 用户提供的腾讯地图Key
TENCENT_KEY = 'C6QBZ-QOFL3-XUX3E-RBQVQ-6S3Y2-NMFMJ'

def test_tencent_staticmap():
    latitude = 39.913837
    longitude = 116.458604
    zoom = 14  # 2KM地铁/1KM公交建议用14-15
    size = '600*300'
    markers = f'marker::{longitude},{latitude}'
    url = f'https://apis.map.qq.com/ws/staticmap/v2/?center={latitude},{longitude}&zoom={zoom}&size={size}&markers={markers}&key={TENCENT_KEY}'
    print(f'🔗 请求URL: {url}')
    try:
        response = requests.get(url, timeout=10)
        print(f'📊 响应状态码: {response.status_code}')
        print(f'📏 响应内容长度: {len(response.content)} 字节')
        print(f'📄 响应头: {dict(response.headers)}')
        content_type = response.headers.get('content-type', '')
        print(f'📋 内容类型: {content_type}')
        if response.status_code == 200 and 'image' in content_type:
            with open('test_tencent_map.png', 'wb') as f:
                f.write(response.content)
            print('✅ 图片已保存为 test_tencent_map.png')
        else:
            print('❌ 响应不是图片或API出错')
            print(response.text[:200])
    except Exception as e:
        print(f'❌ 请求失败: {e}')

if __name__ == '__main__':
    test_tencent_staticmap() 