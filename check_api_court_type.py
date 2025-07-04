#!/usr/bin/env python3
import requests
import sys

def main():
    # 获取所有场馆，查找嘉里中心-网球场的ID
    url = 'http://127.0.0.1:8000/api/courts/'
    try:
        resp = requests.get(url)
        resp.raise_for_status()
        courts = resp.json()
        for court in courts:
            if '嘉里中心-网球场' in court['name']:
                print(f"场馆: {court['name']}")
                print(f"地址: {court['address']}")
                print(f"API返回类型: {court.get('court_type', '未找到')}")
                print(f"ID: {court['id']}")
                print(f"完整响应: {court}")
                return
        print('未找到嘉里中心-网球场')
    except Exception as e:
        print(f"API请求失败: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main() 