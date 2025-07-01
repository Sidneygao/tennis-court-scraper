#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查/api/courts/areas/list返回的区域key和name
"""
import requests

def main():
    url = 'http://127.0.0.1:8000/api/courts/areas/list'
    resp = requests.get(url, timeout=5)
    print('API状态:', resp.status_code)
    data = resp.json()
    for area in data.get('areas', []):
        print(f"key: {area.get('key')}, name: {area.get('name')}")
    print(f"共{len(data.get('areas', []))}个区域")

if __name__ == "__main__":
    main() 