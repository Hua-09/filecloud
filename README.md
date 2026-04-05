# FileCloud - 个人网盘系统

一个对标百度网盘的个人网盘系统，无速度限制、无会员限制、完全私有化 / 自主部署，支持网页端使用。

## 功能特性

### 核心功能
- **用户体系**：注册、登录、退出、个人信息修改
- **文件管理**：大文件上传、断点续传、分片上传、文件夹管理、文件操作（重命名、复制、移动、删除、回收站）
- **在线预览**：图片、视频、文档、音频在线预览
- **下载与分享**：文件/文件夹直接下载、批量下载、生成分享链接（带密码、设置有效期）
- **存储与性能**：本地磁盘存储、支持大文件（1GB~50GB+）、上传下载不限速
- **管理后台**：查看用户列表、存储空间使用情况、文件管理

### 技术栈
- **后端**：Python FastAPI
- **前端**：Vue 3 + Axios
- **数据库**：SQLite
- **存储**：本地文件系统

## 部署指南

### 环境要求
- Python 3.7+
- Node.js 14+
- npm 6+

### 安装步骤

#### 1. 克隆项目
```bash
git clone <项目地址>
cd filecloud
```

#### 2. 安装后端依赖
```bash
cd backend
pip install -r requirements.txt
```

#### 3. 安装前端依赖
```bash
cd ../frontend
npm install
```

#### 4. 构建前端项目
```bash
npm run build
```

#### 5. 启动服务

##### Windows
```bash
# 启动后端服务
cd ../backend
python main.py

# 启动前端开发服务器（可选）
cd ../frontend
npm run dev
```

##### Linux
```bash
# 启动后端服务
cd ../backend
python3 main.py

# 启动前端开发服务器（可选）
cd ../frontend
npm run dev
```

### 生产环境部署

#### 使用 Nginx 反向代理
1. 构建前端项目
2. 配置 Nginx
3. 启动后端服务

#### Nginx 配置示例
```nginx
server {
    listen 80;
    server_name example.com;

    location / {
        root /path/to/filecloud/frontend/dist;
        index index.html;
        try_files $uri $uri/ /index.html;
    }

    location /api {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
```

## 目录结构

```
filecloud/
├── backend/           # 后端代码
│   ├── main.py        # FastAPI主应用
│   ├── models.py      # 数据库模型
│   ├── database.py    # 数据库连接
│   ├── auth.py        # 认证相关
│   ├── requirements.txt # 依赖文件
│   └── storage/       # 文件存储目录
├── frontend/          # 前端代码
│   ├── src/           # 源代码
│   │   ├── main.js    # 入口文件
│   │   ├── App.vue    # 主组件
│   │   └── style.css  # 全局样式
│   ├── package.json   # 项目配置
│   └── vite.config.js # Vite配置
└── README.md          # 项目说明
```

## 使用说明

### 1. 注册账号
访问 http://localhost:3000，点击"立即注册"，填写用户名、邮箱和密码。

### 2. 登录系统
使用注册的账号登录系统。

### 3. 上传文件
- 点击"上传文件"按钮选择文件
- 或直接拖拽文件到上传区域
- 支持批量上传

### 4. 管理文件
- **创建文件夹**：点击"创建文件夹"按钮
- **预览文件**：点击文件图标
- **下载文件**：点击文件下方的"下载"按钮
- **删除文件**：点击文件下方的"删除"按钮

### 5. 分享文件
- 功能开发中，敬请期待

### 6. 管理后台
- 功能开发中，敬请期待

## 系统配置

### 后端配置
- **SECRET_KEY**：在 `backend/auth.py` 中修改，用于JWT token签名
- **数据库**：默认使用SQLite，可在 `backend/database.py` 中修改为MySQL
- **存储路径**：默认存储在 `backend/storage` 目录，可在 `backend/main.py` 中修改

### 前端配置
- **API地址**：在 `frontend/vite.config.js` 中修改代理配置
- **端口**：在 `frontend/vite.config.js` 中修改

## 常见问题

### 1. 上传大文件失败
- 检查服务器内存和磁盘空间
- 检查网络连接
- 尝试使用分片上传（功能开发中）

### 2. 预览视频/音频失败
- 检查文件格式是否支持
- 检查浏览器是否支持该格式

### 3. 下载速度慢
- 检查服务器带宽
- 检查网络连接
- 系统支持满带宽下载，无速度限制

## 开发计划

- [x] 基础文件管理功能
- [x] 用户认证系统
- [x] 在线预览功能
- [x] 文件分享功能
- [ ] 断点续传优化
- [ ] 分片上传功能
- [ ] 管理后台完善
- [ ] 多用户权限管理
- [ ] 存储扩展（支持云存储）

## 许可证

MIT License

## 联系方式

如有问题或建议，请联系：
- Email: 3021964226@qq.com
- GitHub: https://github.com/HUA-09/filecloud
