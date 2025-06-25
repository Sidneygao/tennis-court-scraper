import requests

API_URL = 'http://127.0.0.1:8000/api/courts?limit=5'

if __name__ == '__main__':
    resp = requests.get(API_URL)
    resp.raise_for_status()
    courts = resp.json()
    print('前五个场馆名称：')
    for i, court in enumerate(courts, 1):
        print(f'{i}. {court["name"]}') 