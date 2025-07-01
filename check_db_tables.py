import sqlite3

def check_db_tables():
    try:
        conn = sqlite3.connect('data/courts.db')
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        print("data/courts.db 中的表:", tables)
        
        # 检查每个表的结构
        for table in tables:
            table_name = table[0]
            cursor.execute(f"PRAGMA table_info({table_name})")
            columns = cursor.fetchall()
            print(f"\n表 {table_name} 的列:")
            for col in columns:
                print(f"  {col[1]} ({col[2]})")
        
        conn.close()
    except Exception as e:
        print("data/courts.db 错误:", e)

if __name__ == "__main__":
    check_db_tables() 