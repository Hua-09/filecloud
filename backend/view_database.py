import sqlite3
from datetime import datetime
import os

def view_database():
    db_path = 'filecloud.db'
    
    # 检查数据库文件是否存在
    if not os.path.exists(db_path):
        print("错误：数据库文件不存在！")
        return
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 获取所有表名
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    
    # 打印数据库信息
    print("=" * 80)
    print(" FileCloud 数据库可视化".center(80))
    print("=" * 80)
    print(f"数据库文件: {db_path}")
    print(f"当前时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"表数量: {len(tables)}")
    print("=" * 80)
    
    for table in tables:
        table_name = table[0]
        
        # 打印表标题
        print(f"\n{'-' * 80}")
        print(f" {table_name} 表 ".center(80, '='))
        print(f"{'-' * 80}")
        
        # 获取表结构
        cursor.execute(f"PRAGMA table_info({table_name});")
        columns = cursor.fetchall()
        
        # 打印表结构
        print("表结构:")
        print("{:<20} {:<15} {:<10} {:<10}".format("列名", "数据类型", "是否主键", "是否可为空"))
        print("-" * 80)
        
        for col in columns:
            col_id, col_name, col_type, not_null, default_value, primary_key = col
            is_primary = "*" if primary_key else ""
            is_nullable = "*" if not not_null else ""
            print("{:<20} {:<15} {:<10} {:<10}".format(col_name, col_type, is_primary, is_nullable))
        
        # 获取数据
        cursor.execute(f"SELECT * FROM {table_name};")
        rows = cursor.fetchall()
        
        print(f"\n数据记录: {len(rows)} 条")
        
        if rows:
            print("-" * 80)
            # 打印表头
            column_names = [col[1] for col in columns]
            header = " | ".join([name[:15].ljust(15) for name in column_names])
            print(f"| {header} |")
            print("-" * 80)
            
            # 打印数据
            for row in rows:
                formatted_row = []
                for i, value in enumerate(row):
                    if value is None:
                        formatted_row.append("NULL".ljust(15))
                    elif isinstance(value, str) and len(value) > 15:
                        formatted_row.append(f"{value[:12]}...".ljust(15))
                    elif isinstance(value, datetime):
                        formatted_row.append(value.strftime('%Y-%m-%d %H:%M').ljust(15))
                    else:
                        formatted_row.append(str(value).ljust(15))
                row_str = " | ".join(formatted_row)
                print(f"| {row_str} |")
            print("-" * 80)
        else:
            print("无数据")
    
    # 打印统计信息
    print("\n" + "=" * 80)
    print(" 数据库统计信息 ".center(80, '='))
    print("=" * 80)
    
    total_records = 0
    for table in tables:
        table_name = table[0]
        cursor.execute(f"SELECT COUNT(*) FROM {table_name};")
        count = cursor.fetchone()[0]
        total_records += count
        print(f"{table_name}: {count} 条记录")
    
    print(f"\n总计: {total_records} 条记录")
    print("=" * 80)
    
    conn.close()

if __name__ == "__main__":
    view_database()