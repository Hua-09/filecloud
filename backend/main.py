from fastapi import FastAPI, Depends, HTTPException, status, UploadFile, File, Form, Query
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.responses import FileResponse, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta
import os
import shutil
import zipfile
import uuid
import json
from typing import List, Optional

from database import get_db, init_db
from models import User, File, Folder, Share
from auth import verify_password, get_password_hash, create_access_token, verify_token, Token, TokenData

# 初始化数据库
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    # 启动时执行
    init_db()
    yield
    # 关闭时执行

# 创建FastAPI应用
app = FastAPI(lifespan=lifespan)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 在生产环境中应该设置具体的前端域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# OAuth2密码承载令牌
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

# 确保存储目录存在
os.makedirs("./storage", exist_ok=True)

# 依赖项：获取当前用户
def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    token_data = verify_token(token, credentials_exception)
    user = db.query(User).filter(User.username == token_data.username).first()
    if user is None:
        raise credentials_exception
    return user

# 依赖项：获取管理员用户
def get_admin_user(current_user: User = Depends(get_current_user)):
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="权限不足"
        )
    return current_user

# 健康检查
@app.get("/health")
def health_check():
    return {"status": "ok"}

# 认证相关路由
@app.post("/api/auth/register", response_model=dict)
def register(
    username: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    # 检查用户名是否已存在
    if db.query(User).filter(User.username == username).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )
    # 检查邮箱是否已存在
    if db.query(User).filter(User.email == email).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    # 创建新用户
    hashed_password = get_password_hash(password)
    new_user = User(
        username=username,
        email=email,
        password_hash=hashed_password
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"message": "User registered successfully"}

@app.post("/api/auth/login", response_model=Token)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.username == form_data.username).first()
    if not user or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=30)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

# 用户信息路由
@app.get("/api/user/me", response_model=dict)
def get_current_user_info(current_user: User = Depends(get_current_user)):
    return {
        "id": current_user.id,
        "username": current_user.username,
        "email": current_user.email,
        "role": current_user.role
    }

# 文件夹管理路由
@app.post("/api/folders", response_model=dict)
def create_folder(
    name: str = Form(...),
    parent_id: Optional[int] = Form(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # 检查父文件夹是否存在且属于当前用户
    if parent_id:
        parent_folder = db.query(Folder).filter(
            Folder.id == parent_id,
            Folder.user_id == current_user.id
        ).first()
        if not parent_folder:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Parent folder not found"
            )
    # 创建新文件夹
    new_folder = Folder(
        name=name,
        parent_id=parent_id,
        user_id=current_user.id
    )
    db.add(new_folder)
    db.commit()
    db.refresh(new_folder)
    return {
        "id": new_folder.id,
        "name": new_folder.name,
        "parent_id": new_folder.parent_id,
        "created_at": new_folder.created_at
    }

@app.get("/api/folders", response_model=List[dict])
def get_folders(
    parent_id: Optional[int] = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    folders = db.query(Folder).filter(
        Folder.user_id == current_user.id,
        Folder.parent_id == parent_id
    ).all()
    return [{
        "id": folder.id,
        "name": folder.name,
        "parent_id": folder.parent_id,
        "created_at": folder.created_at
    } for folder in folders]

# 文件管理路由
@app.post("/api/files/upload", response_model=dict)
async def upload_file(
    file: UploadFile = File(),
    folder_id: Optional[int] = Form(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # 检查文件夹是否存在且属于当前用户
    if folder_id:
        folder = db.query(Folder).filter(
            Folder.id == folder_id,
            Folder.user_id == current_user.id
        ).first()
        if not folder:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Folder not found"
            )
    
    # 生成唯一文件名
    unique_id = str(uuid.uuid4())
    filename = f"{unique_id}_{file.filename}"
    file_path = os.path.join("./storage", filename)
    
    # 保存文件
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    # 获取文件大小
    file_size = os.path.getsize(file_path)
    
    # 确定文件类型
    file_type = file.filename.split(".")[-1].lower() if "." in file.filename else ""    
    # 创建文件记录
    new_file = File(
        name=file.filename,
        size=file_size,
        path=file_path,
        type=file_type,
        folder_id=folder_id,
        user_id=current_user.id
    )
    db.add(new_file)
    db.commit()
    db.refresh(new_file)
    
    return {
        "id": new_file.id,
        "name": new_file.name,
        "size": new_file.size,
        "type": new_file.type,
        "folder_id": new_file.folder_id,
        "created_at": new_file.created_at
    }

@app.get("/api/files", response_model=List[dict])
def get_files(
    folder_id: Optional[int] = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    files = db.query(File).filter(
        File.user_id == current_user.id,
        File.folder_id == folder_id,
        File.is_deleted == False
    ).all()
    return [{
        "id": file.id,
        "name": file.name,
        "size": file.size,
        "type": file.type,
        "folder_id": file.folder_id,
        "created_at": file.created_at
    } for file in files]

@app.get("/api/files/{file_id}/download")
def download_file(
    file_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    file = db.query(File).filter(
        File.id == file_id,
        File.user_id == current_user.id,
        File.is_deleted == False
    ).first()
    if not file:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found"
        )
    return FileResponse(
        path=file.path,
        filename=file.name,
        media_type="application/octet-stream"
    )

@app.delete("/api/files/{file_id}", response_model=dict)
def delete_file(
    file_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    file = db.query(File).filter(
        File.id == file_id,
        File.user_id == current_user.id
    ).first()
    if not file:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found"
        )
    file.is_deleted = True
    file.deleted_at = datetime.utcnow()
    db.commit()
    return {"message": "File deleted successfully"}

# 分享功能路由
@app.post("/api/shares", response_model=dict)
def create_share(
    file_id: Optional[int] = Form(None),
    folder_id: Optional[int] = Form(None),
    password: Optional[str] = Form(None),
    expires_in: Optional[int] = Form(None),  # 过期时间（小时）
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # 验证文件或文件夹是否存在且属于当前用户
    if file_id:
        item = db.query(File).filter(
            File.id == file_id,
            File.user_id == current_user.id
        ).first()
    elif folder_id:
        item = db.query(Folder).filter(
            Folder.id == folder_id,
            Folder.user_id == current_user.id
        ).first()
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Either file_id or folder_id must be provided"
        )
    
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File or folder not found"
        )
    
    # 生成分享ID
    share_id = str(uuid.uuid4())[:8]
    
    # 计算过期时间
    expires_at = None
    if expires_in:
        expires_at = datetime.utcnow() + timedelta(hours=expires_in)
    
    # 创建分享记录
    new_share = Share(
        share_id=share_id,
        user_id=current_user.id,
        file_id=file_id,
        folder_id=folder_id,
        password=password,
        expires_at=expires_at
    )
    db.add(new_share)
    db.commit()
    db.refresh(new_share)
    
    return {
        "share_id": share_id,
        "url": f"/share/{share_id}",
        "expires_at": expires_at
    }

@app.get("/api/shares/{share_id}", response_model=dict)
def get_share(
    share_id: str,
    password: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    share = db.query(Share).filter(Share.share_id == share_id).first()
    if not share:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Share not found"
        )
    
    # 检查是否过期
    if share.expires_at and share.expires_at < datetime.utcnow():
        raise HTTPException(
            status_code=status.HTTP_410_GONE,
            detail="Share has expired"
        )
    
    # 检查密码
    if share.password and share.password != password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect password"
        )
    
    # 返回分享内容
    if share.file_id:
        file = share.file
        return {
            "type": "file",
            "name": file.name,
            "size": file.size,
            "type": file.type,
            "path": file.path
        }
    elif share.folder_id:
        folder = share.folder
        return {
            "type": "folder",
            "name": folder.name
        }

# 管理后台路由
@app.get("/api/admin/users", response_model=List[dict])
def get_users(
    current_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    users = db.query(User).all()
    return [{
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "password_hash": user.password_hash,  # 只有admin可以看到密码哈希
        "role": user.role,
        "created_at": user.created_at
    } for user in users]

# 数据库网盘资源下载功能
@app.get("/api/admin/download-all")
def download_all_resources(
    current_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    
    # 创建临时zip文件
    import tempfile
    import os
    
    with tempfile.NamedTemporaryFile(suffix='.zip', delete=False) as temp_zip:
        zip_filename = temp_zip.name
    
    # 创建zip文件
    with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
        # 添加用户数据
        users = db.query(User).all()
        users_data = [{"id": user.id, "username": user.username, "email": user.email, "role": user.role} for user in users]
        zipf.writestr('users.json', json.dumps(users_data, indent=2, ensure_ascii=False))
        
        # 添加文件数据
        files = db.query(File).all()
        files_data = [{"id": file.id, "name": file.name, "size": file.size, "type": file.type, "user_id": file.user_id, "created_at": str(file.created_at)} for file in files]
        zipf.writestr('files.json', json.dumps(files_data, indent=2, ensure_ascii=False))
        
        # 添加实际文件
        for file in files:
            if not file.is_deleted and os.path.exists(file.path):
                try:
                    # 创建用户目录结构
                    user_dir = f"files/user_{file.user_id}"
                    zipf.write(file.path, os.path.join(user_dir, file.name))
                except Exception as e:
                    print(f"Error adding file {file.name}: {e}")
    
    # 提供下载
    return FileResponse(
        path=zip_filename,
        filename="filecloud_resources.zip",
        media_type="application/zip"
    )

# 统计接口
@app.get("/api/admin/stats", response_model=dict)
def get_stats(
    current_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    # 获取用户数量
    user_count = db.query(User).count()
    
    # 获取文件数量
    file_count = db.query(File).filter(File.is_deleted == False).count()
    
    # 获取总文件大小
    total_file_size = db.query(func.sum(File.size)).filter(File.is_deleted == False).scalar() or 0
    
    # 获取每个用户的文件数量和大小
    user_stats = db.query(
        User.id,
        User.username,
        func.count(File.id).label('file_count'),
        func.sum(File.size).label('total_size')
    ).outerjoin(
        File, User.id == File.user_id
    ).filter(
        File.is_deleted == False
    ).group_by(
        User.id, User.username
    ).all()
    
    user_stats_list = [
        {
            "user_id": stat.id,
            "username": stat.username,
            "file_count": stat.file_count,
            "total_size": stat.total_size or 0
        }
        for stat in user_stats
    ]
    
    return {
        "user_count": user_count,
        "file_count": file_count,
        "total_file_size": total_file_size,
        "user_stats": user_stats_list
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)