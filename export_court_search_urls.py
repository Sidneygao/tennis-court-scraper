import csv
from urllib.parse import quote
from app.database import get_db
from app.models import TennisCourt

def make_dianping_url(name):
    return f"https://www.dianping.com/search/keyword/2_0_{quote(name)}"

def make_meituan_url(name):
    return f"https://www.meituan.com/s/%s/" % quote(name)

def main():
    db = next(get_db())
    courts = db.query(TennisCourt).all()
    with open('courts_search_urls.csv', 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['name', 'dianping_url', 'meituan_url'])
        for c in courts:
            writer.writerow([
                c.name,
                make_dianping_url(c.name),
                make_meituan_url(c.name)
            ])
    print('已导出 courts_search_urls.csv')

if __name__ == '__main__':
    main() 