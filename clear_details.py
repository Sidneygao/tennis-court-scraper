from app.database import SessionLocal
from app.models import CourtDetail

def clear_details():
    session = SessionLocal()
    session.query(CourtDetail).delete()
    session.commit()
    session.close()
    print("已清空court_details表")

if __name__ == "__main__":
    clear_details()

import requests

proxies = {
    "http": "socks5h://127.0.0.1:1086",
    "https": "socks5h://127.0.0.1:1086"
}

try:
    r = requests.get("https://www.google.com", proxies=proxies, timeout=10)
    print("状态码:", r.status_code)
    print("内容片段:", r.text[:200])
except Exception as e:
    print("连接失败:", e) 