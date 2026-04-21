# TwoSpace 💕

仅限两人使用的私密恋爱记录网站。记录日常、相册、纪念日。

## 功能

- **首页** — 恋爱天数、合照、随机语录、最近日记
- **日记** — 时间轴，支持心情标签和图片上传
- **相册** — 瀑布流展示所有日记图片，支持预览和下载
- **纪念日** — 倒计时卡片，自动计算距今天数

## 技术栈

- 前端：Vue 3 + Vite + Vue Router + Pinia
- 后端：FastAPI + SQLite（aiosqlite）
- 部署：Docker + Nginx + Let's Encrypt

## 本地开发

### 前置条件

- Node.js 18+
- Python 3.11+

### 1. 配置环境变量

```bash
cp .env.example .env
```

编辑 `.env`，填写以下字段：

```bash
# 生成密码哈希
python3 -c "import bcrypt; print(bcrypt.hashpw(b'你的密码', bcrypt.gensalt()).decode())"
```

| 变量 | 说明 |
|------|------|
| `SECRET_KEY` | JWT 签名密钥，随机长字符串 |
| `USER1_NAME` / `USER2_NAME` | 两人的昵称 |
| `USER1_PASSWORD_HASH` / `USER2_PASSWORD_HASH` | bcrypt 哈希后的密码 |
| `LOVE_START_DATE` | 恋爱开始日期，格式 `YYYY-MM-DD` |
| `COUPLE_PHOTO` | 合照路径，如 `/uploads/couple.jpg` |
| `QUOTES` | 自定义语录，用 `\|` 分隔，留空使用内置默认值 |
| `DOMAIN` | 你的域名 |

### 2. 启动后端

```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload
```

API 文档：http://localhost:8000/docs

### 3. 启动前端

```bash
cd frontend
npm install
npm run dev
```

访问：http://localhost:5173

## 部署到 VPS

### 前置准备

```bash
# 服务器上安装 Docker 和 Nginx
apt install -y nginx
curl -fsSL https://get.docker.com | sh

# 申请 SSL 证书
apt install -y certbot python3-certbot-nginx
certbot --nginx -d your-domain.com
```

### 配置 Nginx

```bash
# 将 nginx/twospace.conf 复制到服务器，替换 YOUR_DOMAIN
cp nginx/twospace.conf /etc/nginx/sites-available/twospace
sed -i 's/YOUR_DOMAIN/your-domain.com/g' /etc/nginx/sites-available/twospace
ln -s /etc/nginx/sites-available/twospace /etc/nginx/sites-enabled/
nginx -t && systemctl reload nginx
```

### 一键部署

```bash
# 在服务器上创建目录和 .env
ssh user@server "mkdir -p /opt/twospace"
scp .env user@server:/opt/twospace/.env

# 本地执行部署脚本
./deploy.sh user@your-server-ip
```

脚本会自动构建前端、上传静态文件、重启后端容器。

### 上传头像和合照

```bash
# 将图片放到服务器的 data/uploads/ 目录
scp couple.jpg user@server:/opt/twospace/data/uploads/
scp avatar1.jpg user@server:/opt/twospace/data/uploads/
scp avatar2.jpg user@server:/opt/twospace/data/uploads/
```

## 项目结构

```
TwoSpace/
├── backend/
│   ├── main.py          # FastAPI 入口
│   ├── auth.py          # JWT 认证，硬编码用户
│   ├── models.py        # SQLAlchemy 数据模型
│   ├── schemas.py       # Pydantic 响应模型
│   ├── database.py      # SQLite 连接
│   └── routers/         # auth / diary / gallery / anniversary / config
├── frontend/
│   └── src/
│       ├── views/       # Login / Home / Diary / Gallery / Anniversary
│       ├── components/  # NavBar / ImageModal
│       ├── stores/      # Pinia auth store
│       └── api/         # axios 封装
├── nginx/
│   └── twospace.conf    # Nginx 配置模板
├── docker-compose.yml
├── deploy.sh            # 一键部署脚本
└── .env.example         # 环境变量模板
```

## 数据备份

数据全部存储在 `data/` 目录：

```bash
# 备份
tar czf twospace-backup-$(date +%Y%m%d).tar.gz /opt/twospace/data/

# 恢复
tar xzf twospace-backup-YYYYMMDD.tar.gz -C /
```
