from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from contextlib import asynccontextmanager
import os
import sys

# 获取项目根目录路径
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATIC_DIR = os.path.join(PROJECT_ROOT, "static")
UPLOAD_DIR = os.path.join(STATIC_DIR, "uploads")

# 导入路由
from routers import auth, items, orders, messages
from database import engine, Base

# 创建数据库表
Base.metadata.create_all(bind=engine)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时执行
    # 确保上传目录存在
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    yield
    # 关闭时执行

# 创建FastAPI应用
app = FastAPI(
    title="校园二手交易平台",
    description="帮助同学们买卖二手物品的平台",
    version="1.0.0",
    lifespan=lifespan
)

# CORS配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 挂载静态文件目录
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

# 注册路由
app.include_router(auth.router, prefix="/api")
app.include_router(items.router, prefix="/api")
app.include_router(orders.router, prefix="/api")
app.include_router(messages.router, prefix="/api")

# HTML页面路由
HTML_PAGES = [
    "index", "login", "register", "dashboard", "product", "post-item", "chat", "help"
]

for page in HTML_PAGES:
    @app.get(f"/{page}.html")
    async def serve_html(page_name: str = page):
        """提供HTML页面"""
        file_path = os.path.join(STATIC_DIR, f"{page_name}.html")
        if os.path.exists(file_path):
            return FileResponse(file_path)
        return {"error": "Page not found"}

# 根路径重定向到首页
@app.get("/")
async def root():
    """根路径"""
    index_path = os.path.join(STATIC_DIR, "index.html")
    return FileResponse(index_path)

@app.get("/health")
async def health_check():
    """健康检查"""
    return {"status": "ok", "message": "服务运行正常"}

@app.get("/favicon.ico")
async def favicon():
    """返回空 favicon 避免 404"""
    from fastapi.responses import Response
    return Response(content="", media_type="image/x-icon")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
