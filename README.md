<div align="center">

# 💕 TwoSpace

**专属于两个人的私密恋爱空间**

一个为情侣打造的自托管私密网站——记录每一篇日记、珍藏每一张合照、铭记每一个纪念日、留下属于两个人的温柔足迹。

[![License: MIT](https://img.shields.io/badge/License-MIT-pink.svg)](LICENSE)
[![Vue 3](https://img.shields.io/badge/Vue-3-42b883?logo=vue.js)](https://vuejs.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?logo=fastapi)](https://fastapi.tiangolo.com)
[![Python 3.11+](https://img.shields.io/badge/Python-3.11+-3776ab?logo=python)](https://python.org)

</div>

---

## 💡 初心与设计理念

市面上的恋爱记录 App 大多依赖第三方平台：数据存在别人的服务器、隐私难以保证、服务随时可能停止。TwoSpace 的出发点很简单——**把这份珍贵的记录完全掌握在自己手里**。

- **完全私有**：部署在自己的服务器上，只有两个人能登录，没有广告、没有推荐算法、没有数据泄露风险
- **长期保存**：数据以 SQLite 单文件 + 图片目录的形式存储，10 年后打开一个压缩包就能还原全部回忆
- **轻量自托管**：一台最低配的云服务器（1 核 1G）即可流畅运行，Docker Compose 一条命令启动
- **专为两人设计**：没有多余的社交功能，界面干净，只为记录和回忆
- **移动端优先**：日常使用场景以手机为主，UI 针对移动端做了深度优化

如果你也想拥有一个只属于你们两个人的私密空间，TwoSpace 是一个开箱即用的选择。

---

## ✨ 功能一览

| 模块 | 功能 |
|------|------|
| 🏠 **首页** | 恋爱天数倒计时、合照展示、随机语录、最近日记预览 |
| 📖 **日记** | 全屏翻页浏览、日历侧边索引、心情标签、多图上传、补写历史日期 |
| 🖼 **相册** | 瀑布流展示全部图片，支持大图预览与下载 |
| 📊 **STATS** | 纪念日倒计时管理 + 「足迹」自定义统计卡片（记录拥抱次数等） |

## 🛠 技术栈

```
前端  Vue 3 + Vite + Vue Router 4 + Pinia + Axios
后端  FastAPI + SQLAlchemy 2.0 (async) + aiosqlite + PyJWT + bcrypt
部署  Docker Compose + Nginx + Let's Encrypt (HTTPS)
数据  SQLite 单文件，零运维
```

## 🚀 快速开始（本地开发）

### 前置条件

- Node.js 18+
- Python 3.11+

### 1. 克隆项目

```bash
git clone <your-repo-url> TwoSpace
cd TwoSpace
```

### 2. 配置环境变量

```bash
cp .env.example .env
```

生成密码哈希（两个用户分别执行）：

```bash
python3 -c "import bcrypt; print(bcrypt.hashpw(b'你的密码', bcrypt.gensalt()).decode())"
```

编辑 `.env`，填写所有字段：

| 变量 | 说明 | 示例 |
|------|------|------|
| `SECRET_KEY` | JWT 签名密钥，建议 64 位随机字符串 | `openssl rand -hex 32` |
| `USER1_NAME` / `USER2_NAME` | 两人昵称 | `小花` / `小明` |
| `USER1_AVATAR` / `USER2_AVATAR` | 头像路径（相对 uploads） | `/uploads/avatar1.jpg` |
| `USER1_PASSWORD_HASH` / `USER2_PASSWORD_HASH` | bcrypt 哈希密码 | `$2b$12$...` |
| `LOVE_START_DATE` | 恋爱开始日期 | `2024-01-01` |
| `COUPLE_PHOTO` | 首页合照路径 | `/uploads/couple.jpg` |
| `QUOTES` | 自定义语录，`\|` 分隔，留空用内置默认 | `你是我的小太阳\|爱你` |
| `UPLOAD_DIR` | 图片存储绝对路径 | `/opt/twospace/data/uploads` |
| `DOMAIN` | 你的域名（部署时使用） | `love.example.com` |

### 3. 启动后端

```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload
# API 文档：http://localhost:8000/docs
```

### 4. 启动前端

```bash
cd frontend
npm install
npm run dev
# 访问：http://localhost:5173
```

### 5. 上传初始图片

将头像和合照放入 `data/uploads/`（本地开发时对应 `.env` 中 `UPLOAD_DIR` 指向的目录）：

```bash
mkdir -p data/uploads
cp couple.jpg   data/uploads/
cp avatar1.jpg  data/uploads/
cp avatar2.jpg  data/uploads/
```

---

## ☁️ 部署到云服务器

详细的云服务器部署步骤请参阅 **[docs/deploy.md](docs/deploy.md)**，涵盖：

- 服务器初始化与安全加固
- Docker 环境安装
- Nginx + Let's Encrypt HTTPS 配置
- 一键部署脚本使用方法
- 数据备份与恢复
- 常见问题排查

---

## 📁 项目结构

```
TwoSpace/
├── backend/
│   ├── main.py              # FastAPI 入口，路由注册，静态文件挂载
│   ├── auth.py              # JWT 认证，硬编码双用户
│   ├── models.py            # SQLAlchemy ORM 模型
│   ├── schemas.py           # Pydantic 请求/响应模型
│   ├── database.py          # 异步 SQLite 连接
│   ├── requirements.txt
│   ├── Dockerfile
│   └── routers/
│       ├── auth.py          # 登录接口
│       ├── diary.py         # 日记 CRUD + 图片上传
│       ├── gallery.py       # 相册聚合查询
│       ├── anniversary.py   # 纪念日管理
│       ├── counter.py       # 足迹统计卡片
│       └── config.py        # 全局配置（天数、合照、语录）
├── frontend/
│   └── src/
│       ├── views/           # Login / Home / Diary / Gallery / Stats
│       ├── components/      # NavBar / AnniversaryBanner / ImageModal
│       ├── stores/          # Pinia auth store
│       ├── styles/          # global.css（主题变量、卡片、背景动效）
│       └── api/             # axios 封装（拦截器、401 跳转）
├── nginx/
│   └── twospace.conf        # Nginx 配置模板
├── docs/
│   └── deploy.md            # 云服务器部署详细文档
├── data/                    # 运行时数据（gitignore）
│   ├── uploads/             # 上传的图片
│   └── db/                  # SQLite 数据库文件
├── docker-compose.yml
├── deploy.sh                # 一键部署脚本
└── .env.example             # 环境变量模板
```

---

## 💾 数据备份

所有数据（数据库 + 图片）均存储在 `data/` 目录，备份只需打包该目录：

```bash
# 备份
tar czf twospace-backup-$(date +%Y%m%d).tar.gz /opt/twospace/data/

# 恢复
tar xzf twospace-backup-20240101.tar.gz -C /
docker compose restart
```

---

<div align="center">
Made with 💕 for two people only
</div>
