# FileCloud 服务器部署指南

## 服务器环境准备

### 1. 服务器选择
- **推荐配置**：2核4G内存以上
- **系统**：Ubuntu 20.04 LTS 或 CentOS 7+
- **存储**：根据文件存储需求选择合适的磁盘空间
- **带宽**：根据用户数量和文件大小选择合适的带宽

### 2. 环境安装

#### Ubuntu 20.04 LTS
```bash
# 更新系统
apt update && apt upgrade -y

# 安装必要的依赖
apt install -y python3 python3-pip python3-venv nodejs npm git

# 安装 Node.js 16+
curl -fsSL https://deb.nodesource.com/setup_16.x | bash -
apt install -y nodejs
```

#### CentOS 7+
```bash
# 更新系统
yum update -y

# 安装 EPEL 源
yum install -y epel-release

# 安装必要的依赖
yum install -y python3 python3-pip git

# 安装 Node.js 16+
curl -fsSL https://rpm.nodesource.com/setup_16.x | bash -
yum install -y nodejs
```

---

## 项目部署

### 1. 克隆项目
```bash
# 创建项目目录
mkdir -p /opt/filecloud
cd /opt/filecloud

# 克隆项目（如果有Git仓库）
git clone <项目地址> .

# 或上传压缩包并解压
# unzip filecloud.zip
```

### 2. 安装依赖

#### 后端依赖
```bash
cd /opt/filecloud/backend

# 创建虚拟环境（推荐）
python3 -m venv venv
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt

# 退出虚拟环境
deactivate
```

#### 前端依赖
```bash
cd /opt/filecloud/frontend

# 安装依赖
npm install

# 构建生产版本
npm run build
```

---

## 服务配置

### 1. 配置 Nginx

#### 安装 Nginx
```bash
# Ubuntu
apt install -y nginx

# CentOS
yum install -y nginx
```

#### 配置 Nginx
```bash
# 创建 Nginx 配置文件
cat > /etc/nginx/sites-available/filecloud << 'EOF'
server {
    listen 80;
    server_name your-domain.com;  # 替换为您的域名或IP

    # 前端静态文件
    location / {
        root /opt/filecloud/frontend/dist;
        index index.html;
        try_files $uri $uri/ /index.html;
    }

    # 后端 API
    location /api {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
EOF

# 创建软链接
ln -s /etc/nginx/sites-available/filecloud /etc/nginx/sites-enabled/

# 测试配置
nginx -t

# 重启 Nginx
systemctl restart nginx
```

### 2. 配置 Supervisor

#### 安装 Supervisor
```bash
# Ubuntu
apt install -y supervisor

# CentOS
yum install -y supervisor

# 启动 Supervisor
systemctl start supervisor
systemctl enable supervisor
```

#### 配置 Supervisor
```bash
# 创建配置文件
cat > /etc/supervisor/conf.d/filecloud.conf << 'EOF'
[program:filecloud-backend]
command=/opt/filecloud/backend/venv/bin/python /opt/filecloud/backend/main.py
directory=/opt/filecloud/backend
autostart=true
autorestart=true
startsecs=5
startretries=3
user=www-data
stderr_logfile=/var/log/filecloud/backend.err.log
stdout_logfile=/var/log/filecloud/backend.out.log

# 环境变量
environment=PYTHONUNBUFFERED=1
EOF

# 创建日志目录
mkdir -p /var/log/filecloud

# 重新加载配置
supervisorctl reread
supervisorctl update
supervisorctl start filecloud-backend
```

---

## 安全设置

### 1. 防火墙配置
```bash
# Ubuntu (ufw)
ufw allow 80/tcp
ufw allow 443/tcp
ufw enable

# CentOS (firewalld)
firewall-cmd --permanent --add-service=http
firewall-cmd --permanent --add-service=https
firewall-cmd --reload
```

### 2. HTTPS 配置（推荐）

#### 安装 Certbot
```bash
# Ubuntu
apt install -y certbot python3-certbot-nginx

# CentOS
yum install -y certbot python3-certbot-nginx
```

#### 获取 SSL 证书
```bash
certbot --nginx -d your-domain.com

# 自动续期设置
crontab -e
# 添加以下行
0 12 * * * /usr/bin/certbot renew --quiet
```

### 3. 权限设置
```bash
# 设置文件权限
chown -R www-data:www-data /opt/filecloud
chmod -R 755 /opt/filecloud

# 确保 storage 目录可写
chmod -R 775 /opt/filecloud/backend/storage
```

---

## 性能优化

### 1. 系统优化

#### 增加文件描述符限制
```bash
cat >> /etc/security/limits.conf << 'EOF'
* soft nofile 65536
* hard nofile 65536
EOF

# 重启系统或重新登录
```

#### 优化网络设置
```bash
cat >> /etc/sysctl.conf << 'EOF'
# 网络优化
net.core.somaxconn = 65535
net.ipv4.tcp_max_syn_backlog = 4096
net.ipv4.tcp_fin_timeout = 30
net.ipv4.tcp_keepalive_time = 300
net.ipv4.tcp_keepalive_probes = 5
net.ipv4.tcp_keepalive_intvl = 15
EOF

# 应用设置
sysctl -p
```

### 2. Nginx 优化
```bash
cat >> /etc/nginx/nginx.conf << 'EOF'

http {
    # 优化配置
    worker_processes auto;
    worker_connections 1024;
    multi_accept on;
    sendfile on;
    tcp_nopush on;
    tcp_nodelay on;
    keepalive_timeout 65;
    keepalive_requests 10000;
    
    # 缓冲区设置
    client_body_buffer_size 16k;
    client_max_body_size 100M;  # 根据需要调整
    
    # Gzip 压缩
    gzip on;
    gzip_comp_level 5;
    gzip_types text/plain text/css application/json application/javascript text/xml application/xml application/xml+rss text/javascript;
}
EOF

# 重启 Nginx
systemctl restart nginx
```

---

## 监控和维护

### 1. 监控设置

#### 安装监控工具
```bash
# 安装 htop
apt install -y htop  # Ubuntu
yum install -y htop  # CentOS

# 安装 netdata（可选）
bash <(curl -Ss https://my-netdata.io/kickstart.sh)
```

### 2. 日志管理

#### 配置日志轮转
```bash
cat > /etc/logrotate.d/filecloud << 'EOF'
/var/log/filecloud/*.log {
    daily
    missingok
    rotate 7
    compress
    delaycompress
    notifempty
    create 644 www-data www-data
}
EOF
```

### 3. 定期备份

#### 创建备份脚本
```bash
cat > /opt/filecloud/backup.sh << 'EOF'
#!/bin/bash

# 备份目录
BACKUP_DIR="/backup/filecloud"
DATE=$(date +%Y%m%d)

# 创建备份目录
mkdir -p $BACKUP_DIR

# 备份数据库
cp /opt/filecloud/backend/filecloud.db $BACKUP_DIR/filecloud.db.$DATE

# 备份文件
rsync -av /opt/filecloud/backend/storage/ $BACKUP_DIR/storage/

# 清理 7 天前的备份
find $BACKUP_DIR -type f -mtime +7 -delete

echo "Backup completed: $DATE"
EOF

# 设置执行权限
chmod +x /opt/filecloud/backup.sh

# 添加到 crontab
crontab -e
# 添加以下行（每天凌晨 2 点备份）
0 2 * * * /opt/filecloud/backup.sh
```

---

## 常见问题

### 1. 服务启动失败
```bash
# 查看后端日志
tail -f /var/log/filecloud/backend.err.log

# 检查 Supervisor 状态
supervisorctl status

# 重启服务
supervisorctl restart filecloud-backend
```

### 2. 文件上传失败
```bash
# 检查权限
ls -la /opt/filecloud/backend/storage/

# 检查 Nginx 配置
nginx -t

# 检查客户端最大上传限制
# 修改 /etc/nginx/nginx.conf 中的 client_max_body_size
```

### 3. 访问速度慢
```bash
# 检查服务器负载
top

# 检查网络连接
netstat -tuln

# 优化 Nginx 配置
# 参考性能优化部分
```

---

## 升级指南

### 1. 备份数据
```bash
# 执行备份脚本
/opt/filecloud/backup.sh
```

### 2. 更新代码
```bash
cd /opt/filecloud

# 如果使用 Git
git pull

# 或上传新的代码包
# unzip -o filecloud.zip
```

### 3. 更新依赖
```bash
# 后端
source /opt/filecloud/backend/venv/bin/activate
pip install -r requirements.txt
deactivate

# 前端
cd /opt/filecloud/frontend
npm install
npm run build
```

### 4. 重启服务
```bash
# 重启后端
supervisorctl restart filecloud-backend

# 重启 Nginx
systemctl restart nginx
```

---

## 生产环境检查清单

- [ ] 服务器环境配置完成
- [ ] 项目部署完成
- [ ] Nginx 配置完成
- [ ] Supervisor 配置完成
- [ ] 防火墙设置完成
- [ ] HTTPS 配置完成（推荐）
- [ ] 权限设置完成
- [ ] 性能优化完成
- [ ] 监控设置完成
- [ ] 备份策略配置完成
- [ ] 测试所有功能正常

---

## 技术支持

### 故障排查
1. **检查后端日志**：`tail -f /var/log/filecloud/backend.err.log`
2. **检查 Nginx 日志**：`tail -f /var/log/nginx/error.log`
3. **检查网络连接**：`netstat -tuln`
4. **检查服务状态**：`supervisorctl status`

### 联系方式
- 查看 README.md 和 DEPLOY.md 文件
- 检查代码注释和文档
- 参考 FastAPI 和 Vue 官方文档

---

## 部署成功验证

1. **访问前端**：http://your-domain.com/ 或 http://your-server-ip/
2. **测试登录**：使用测试账号 test/123456
3. **测试上传**：上传一个文件
4. **测试下载**：下载上传的文件
5. **测试预览**：预览图片或视频文件
6. **测试分享**：生成分享链接

如果所有测试都通过，说明部署成功！
