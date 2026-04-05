# GitHub 部署指南

本指南将帮助您将 FileCloud 个人网盘系统部署到 GitHub 上。

## 准备工作

### 1. 创建 GitHub 仓库
1. 登录 GitHub 账号
2. 点击右上角的 "+", 选择 "New repository"
3. 输入仓库名称（例如：filecloud）
4. 选择仓库类型（公开或私有）
5. 点击 "Create repository"

### 2. 检查项目文件
确保项目中包含以下文件：
- `README.md` - 项目说明文件
- `.gitignore` - Git 忽略文件配置
- `backend/` - 后端代码目录
- `frontend/` - 前端代码目录
- `start.bat` - 启动脚本

## 部署步骤

### 1. 初始化 Git 仓库
在项目根目录打开命令行终端，执行以下命令：

```bash
# 初始化 Git 仓库
git init

# 配置 Git 用户名和邮箱
git config user.name "Your Name"
git config user.email "your.email@example.com"
```

### 2. 添加文件到 Git

```bash
# 添加所有文件到 Git
git add .

# 查看已添加的文件
git status
```

### 3. 提交文件

```bash
# 提交文件
git commit -m "Initial commit: FileCloud personal cloud storage system"
```

### 4. 关联 GitHub 仓库
复制 GitHub 仓库的 HTTPS 或 SSH 地址，然后执行：

```bash
# 关联 GitHub 仓库
git remote add origin https://github.com/your-username/filecloud.git

# 查看远程仓库信息
git remote -v
```

### 5. 推送代码到 GitHub

```bash
# 推送代码到 GitHub
git push -u origin master
```

如果您使用的是 main 分支而不是 master 分支，请执行：

```bash
git push -u origin main
```

## 后续操作

### 1. 克隆仓库
其他人可以通过以下命令克隆您的仓库：

```bash
git clone https://github.com/your-username/filecloud.git
cd filecloud
```

### 2. 安装依赖

```bash
# 安装后端依赖
cd backend
pip install -r requirements.txt

# 安装前端依赖
cd ../frontend
npm install
```

### 3. 启动服务

```bash
# 启动后端服务
cd ../backend
python main.py

# 启动前端开发服务器
cd ../frontend
npm run dev
```

## 注意事项

1. **敏感信息**：确保不要将敏感信息（如数据库密码、API 密钥等）上传到 GitHub
2. **存储目录**：`backend/storage/` 和 `backend/downloads/` 目录已在 `.gitignore` 中排除，不会被上传
3. **数据库文件**：`*.db` 文件已在 `.gitignore` 中排除，不会被上传
4. **依赖目录**：`node_modules/` 和 `.venv/` 目录已在 `.gitignore` 中排除，不会被上传

## 部署到生产环境

如果您想将项目部署到生产环境，请参考 `README.md` 中的生产环境部署部分。

## 常见问题

### 1. 推送失败
如果推送失败，可能是因为：
- GitHub 仓库不存在
- 权限不足
- 网络连接问题

请检查 GitHub 仓库地址是否正确，确保您有推送权限，并检查网络连接。

### 2. 文件被忽略
如果某些文件没有被上传，可能是因为它们被 `.gitignore` 文件排除了。请检查 `.gitignore` 文件的内容。

### 3. 依赖问题
如果安装依赖失败，请确保您的 Python 和 Node.js 版本符合要求：
- Python 3.7+
- Node.js 14+
- npm 6+

## 联系方式

如有问题或建议，请联系：
- GitHub: https://github.com/your-username/filecloud
