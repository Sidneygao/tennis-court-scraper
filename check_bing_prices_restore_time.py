import sqlite3
import json
import csv

conn = sqlite3.connect('data/courts.db')
cursor = conn.cursor()

results = cursor.execute('SELECT court_id, bing_prices FROM court_details WHERE bing_prices IS NOT NULL AND bing_prices != ""').fetchall()

rows = []
for court_id, bp in results:
    try:
        bp_json = json.loads(bp)
        restore_time = bp_json.get('restored_at', '无时间')
    except Exception:
        restore_time = '无时间'
    rows.append({'court_id': court_id, 'restore_time': restore_time})

# 获取场馆名
court_names = {}
for row in rows:
    cursor.execute('SELECT name FROM tennis_courts WHERE id = ?', (row['court_id'],))
    res = cursor.fetchone()
    row['court_name'] = res[0] if res else '未知'

# 输出到csv
with open('bing_prices_restore_time.csv', 'w', newline='', encoding='utf-8') as f:
    writer = csv.DictWriter(f, fieldnames=['court_id', 'court_name', 'restore_time'])
    writer.writeheader()
    writer.writerows(rows)

# 屏幕输出
for row in rows:
    print(f"{row['court_id']}	{row['court_name']}	{row['restore_time']}")

conn.close()
print(f"\n共导出{len(rows)}条记录，已保存到bing_prices_restore_time.csv") 