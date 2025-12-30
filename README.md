# FastAPI二手交易网站项目

## 📁 项目结构

```
campus_trade/
├── app/
│   ├── __init__.py
│   ├── main.py              # 应用入口点，CORS配置，静态文件挂载
│   ├── database.py          # 数据库连接和会话管理
│   ├── models.py            # SQLAlchemy数据库模型
│   ├── schemas.py           # Pydantic数据模型（请求/响应）
│   ├── crud.py              # 数据库操作函数
│   ├── auth.py              # JWT认证逻辑，密码加密
│   └── routers/             # API路由模块
│       ├── __init__.py
│       ├── auth.py          # 认证相关接口
│       ├── items.py         # 商品相关接口
│       ├── orders.py        # 订单相关接口
│       └── messages.py      # 消息相关接口
├── static/                  # 前端静态资源
│   ├── css/
│   │   └── style.css        # 样式文件
│   ├── js/
│   │   ├── api.js           # API请求封装
│   │   ├── auth.js          # 认证逻辑
│   │   └── app.js           # 主应用逻辑
│   ├── index.html           # 首页
│   ├── login.html           # 登录页
│   ├── register.html        # 注册页
│   ├── dashboard.html       # 用户中心
│   ├── product.html         # 商品详情页
│   ├── post-item.html       # 发布商品页
│   └── chat.html            # 聊天页面
├── uploads/                 # 上传图片存储目录
├── requirements.txt         # Python依赖
└── README.md               # 项目说明文档
```

## 🚀 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 运行服务

```bash
cd app
uvicorn main:app --reload
```

### 3. 访问应用

打开浏览器访问：`http://localhost:8000`

## ✨ 功能特性

### 用户功能
- ✅ 用户注册和登录（JWT认证）
- ✅ 个人资料管理
- ✅ 密码修改

### 商品功能
- ✅ 发布二手商品
- ✅ 浏览所有商品
- ✅ 商品搜索和筛选
- ✅ 按分类浏览
- ✅ 商品详情查看
- ✅ 商品图片上传

### 交易功能
- ✅ 加入购物车
- ✅ 创建订单
- ✅ 订单历史记录
- ✅ 查看我发布的商品
- ✅ 查看我购买的商品

### 社交功能
- ✅ 站内消息系统
- ✅ 与卖家沟通

## 📚 API接口文档

### 认证接口
| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/auth/register` | 用户注册 |
| POST | `/auth/login` | 用户登录 |
| GET | `/auth/me` | 获取当前用户信息 |

### 商品接口
| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/items` | 获取商品列表 |
| POST | `/items` | 发布商品（需认证） |
| GET | `/items/{id}` | 获取商品详情 |
| PUT | `/items/{id}` | 更新商品（需认证） |
| DELETE | `/items/{id}` | 删除商品（需认证） |
| GET | `/items/my` | 获取我发布的商品 |

### 订单接口
| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/orders` | 创建订单 |
| GET | `/orders` | 获取我的订单 |
| GET | `/orders/{id}` | 获取订单详情 |

### 消息接口
| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/messages` | 获取消息列表 |
| POST | `/messages` | 发送消息 |

## 🎨 技术栈

- **后端**: FastAPI + SQLAlchemy + SQLite
- **认证**: OAuth2 + JWT (HS256)
- **前端**: 原生HTML/CSS/JavaScript
- **样式**: Tailwind CSS (CDN引入)
- **图片处理**: 异步文件上传

## 🔒 安全特性

- 密码bcrypt加密存储
- JWT Token认证
- 路由访问控制
- 输入数据验证
- CORS跨域配置

## 📱 响应式设计

- 完美支持手机、平板、电脑
- 移动端适配的导航菜单
- 自适应商品卡片布局

## 🛠️ 开发说明

### 添加新功能
1. 在 `models.py` 中定义数据模型
2. 在 `schemas.py` 中定义请求/响应模型
3. 在 `crud.py` 中实现数据库操作
4. 在 `routers/` 中创建新的路由模块
5. 在 `main.py` 中注册路由

### 修改样式
- 全局样式在 `static/css/style.css`
- 组件样式使用Tailwind CSS类

### 添加页面
1. 在 `static/` 目录创建HTML文件
2. 在JS文件中添加路由逻辑
3. 更新导航菜单

## 📄 许可证

MIT License
