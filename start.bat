@echo off

echo 启动 FileCloud 个人网盘系统...
echo ===============================

:: 检查 Python 是否安装
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo 错误: Python 未安装或未添加到环境变量
    pause
    exit /b 1
)

:: 检查 Node.js 是否安装
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo 错误: Node.js 未安装或未添加到环境变量
    pause
    exit /b 1
)

:: 安装后端依赖
echo 安装后端依赖...
cd backend
pip install --user -r requirements.txt
if %errorlevel% neq 0 (
    echo 错误: 安装后端依赖失败
    pause
    exit /b 1
)

:: 安装前端依赖
echo 安装前端依赖...
cd ../frontend
npm install
if %errorlevel% neq 0 (
    echo 错误: 安装前端依赖失败
    pause
    exit /b 1
)

:: 构建前端项目
echo 构建前端项目...
npm run build
if %errorlevel% neq 0 (
    echo 错误: 构建前端项目失败
    pause
    exit /b 1
)

:: 启动后端服务
echo 启动后端服务...
cd ../backend
start "FileCloud Backend" python main.py

:: 等待后端服务启动
timeout /t 3 /nobreak >nul

:: 启动前端开发服务器（可选）
echo 启动前端开发服务器...
cd ../frontend
start "FileCloud Frontend" npm run dev

echo ===============================
echo FileCloud 个人网盘系统已启动
 echo 后端服务: http://localhost:8000
echo 前端服务: http://localhost:3000
echo 按任意键退出...
pause >nul