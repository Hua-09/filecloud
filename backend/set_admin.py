import sqlite3

# 连接到数据库
conn = sqlite3.connect('filecloud.db')
cursor = conn.cursor()

# 添加role列（如果不存在）
try:
    cursor.execute("ALTER TABLE users ADD COLUMN role TEXT DEFAULT 'user'")
    conn.commit()
except sqlite3.OperationalError:
    # 列已存在，忽略错误
    pass

# 将test用户设置为admin
cursor.execute("UPDATE users SET role = 'admin' WHERE username = 'test'")
conn.commit()

# 查看结果
cursor.execute("SELECT id, username, role FROM users")
users = cursor.fetchall()
print("用户权限设置结果：")
for user in users:
    print(f"ID: {user[0]}, 用户名: {user[1]}, 角色: {user[2]}")

# 关闭连接
conn.close()

print("\n操作完成！test用户已设置为admin权限。")
