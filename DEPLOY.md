# FileCloud 部署说明

## 项目迁移指南

### 可以迁移的内容
✅ **源代码**：backend/ 和 frontend/ 目录下的所有代码文件  
✅ **配置文件**：package.json、vite.config.js、requirements.txt 等  
✅ **数据库**：filecloud.db（SQLite数据库文件）  
✅ **用户数据**：storage/ 目录下的所有文件  

### 需要重新安装的内容
❌ **依赖包**：node_modules/ 和 Python site-packages  
❌ **缓存文件**：__pycache__/ 等缓存目录  

---

## 迁移步骤

### 1. 打包项目
将以下文件和目录打包：
```
filecloud/
├── backend/
│   ├── auth.py
│   ├── create_test_user.py
│   ├── database.py
│   ├── filecloud.db          # 包含用户数据和文件记录
│   ├── main.py
│   ├── models.py
│   ├── requirements.txt
│   └── storage/              # 包含所有上传的文件
├── frontend/
│   ├── src/
│   │   ├── App.vue
│   │   ├── main.js
│   │   └── style.css
│   ├── index.html
│   ├── package.json
│   └── vite.config.js
├── README.md
├── DEPLOY.md
└── start.bat
```

### 2. 在新设备上部署

#### 环境要求
- Python 3.7+
- Node.js 14+
- npm 6+

#### 部署步骤

**步骤1：解压项目**
```bash
# 解压到任意目录，例如：
cd C:\Users\YourName\Documents
# 解压 filecloud.zip
```

**步骤2：安装后端依赖**
```bash
cd backend
pip install -r requirements.txt
```

**步骤3：安装前端依赖**
```bash
cd ../frontend
npm install
```

**步骤4：启动服务**

**Windows：**
```bash
# 方式1：使用启动脚本
cd ..
start.bat

# 方式2：手动启动
cd backend
python main.py

# 新开一个终端
cd frontend
npm run dev
```

**Linux/Mac：**
```bash
# 安装依赖
cd backend
pip3 install -r requirements.txt

cd ../frontend
npm install

# 启动服务
cd ../backend
python3 main.py &

cd ../frontend
npm run dev
```

---

## 注意事项

### 1. 数据库兼容性
- SQLite数据库是跨平台的，可以在Windows、Linux、Mac之间迁移
- 数据库文件 `filecloud.db` 包含所有用户信息和文件记录

### 2. 文件路径
- 存储的文件在 `backend/storage/` 目录下
- 文件路径在数据库中使用相对路径存储，迁移后仍然有效

### 3. 网络配置
- 默认监听 `0.0.0.0:8000`（后端）和 `0.0.0.0:3000`（前端）
- 支持局域网访问，手机可以通过IP地址访问
- 如果IP地址变化，需要更新访问地址

### 4. 防火墙设置
- Windows防火墙需要允许3000和8000端口
- 或者暂时关闭防火墙进行测试

### 5. 依赖版本
- 如果在新设备上遇到依赖问题，可以尝试更新版本
- Python依赖：`pip install --upgrade -r requirements.txt`
- Node依赖：`npm update`

---

## 快速启动命令

### Windows
```powershell
# 一键启动（自动安装依赖并启动）
.\start.bat

# 手动启动后端
cd backend
python main.py

# 手动启动前端
cd frontend
npm run dev
```

### Linux/Mac
```bash
# 手动启动后端
cd backend
python3 main.py

# 手动启动前端
cd frontend
npm run dev
```

---

## 访问地址

### 本机访问
- 前端：http://localhost:3000/
- 后端API：http://localhost:8000/

### 局域网访问（手机/其他设备）
- 获取本机IP：`ipconfig` (Windows) 或 `ifconfig` (Linux/Mac)
- 前端：http://[你的IP]:3000/
- 后端：http://[你的IP]:8000/

**示例：**
- 本机IP：192.168.0.176
- 访问地址：http://192.168.0.176:3000/

---

## 测试账号
- 用户名：test
- 密码：123456

---

## 常见问题

### Q1: 启动时报错 "ModuleNotFoundError"
**解决**：安装依赖
```bash
pip install -r requirements.txt  # 后端
npm install                       # 前端
```

### Q2: 无法通过IP访问
**解决**：检查防火墙设置，确保端口已开放

### Q3: 数据库文件损坏
**解决**：删除 filecloud.db，系统会自动重新创建

### Q4: 文件上传失败
**解决**：检查 storage/ 目录权限，确保可写

---

## 生产环境部署

### 使用Nginx反向代理
```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        root /path/to/filecloud/frontend/dist;
        index index.html;
        try_files $uri $uri/ /index.html;
    }

    location /api {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### 构建生产版本
```bash
cd frontend
npm run build
# 生成的 dist/ 目录可以用于生产部署
```

---

## 技术支持

如有问题，请查看：
- README.md - 项目基本说明
- DEPLOY.md - 部署说明（本文档）
- 后端日志：查看终端输出
- 浏览器控制台：F12 查看前端错误
