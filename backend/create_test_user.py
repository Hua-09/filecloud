from database import engine, SessionLocal
from models import Base, User

# 创建所有表
Base.metadata.create_all(bind=engine)

# 创建会话
db = SessionLocal()

# 检查是否已存在测试账号
test_user = db.query(User).filter(User.username == "test").first()

if not test_user:
    # 创建测试账号
    new_user = User(
        username="test",
        email="test@example.com",
        password_hash="test_password_hash"
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    print("测试账号创建成功：")
    print(f"用户名：test")
    print(f"密码：123456")
else:
    print("测试账号已存在：")
    print(f"用户名：test")
    print(f"密码：123456")

# 关闭会话
db.close()