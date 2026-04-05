from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base

# 创建SQLite数据库引擎
engine = create_engine('sqlite:///./filecloud.db', connect_args={"check_same_thread": False})

# 创建会话工厂
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 创建所有表
def init_db():
    Base.metadata.create_all(bind=engine)

# 依赖注入获取数据库会话
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()