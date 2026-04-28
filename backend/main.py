from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from .config import settings
from .database import Base, engine
from .routers import (
    auth, admin, config, prices, presets, terms,
    customers, products, orders, history, autocomplete, import_data,
)

# Tạo tất cả bảng khi khởi động
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Tính Giá Thùng Carton – Nam Phương API",
    description="Backend API cho ứng dụng tính giá thùng carton",
    version="1.0.0",
)

# CORS — cho phép frontend gọi API
origins = [o.strip() for o in settings.ALLOWED_ORIGINS.split(",") if o.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Đăng ký tất cả routers
app.include_router(auth.router, prefix="/api")
app.include_router(admin.router, prefix="/api")
app.include_router(config.router, prefix="/api")
app.include_router(prices.router, prefix="/api")
app.include_router(presets.router, prefix="/api")
app.include_router(terms.router, prefix="/api")
app.include_router(customers.router, prefix="/api")
app.include_router(products.router, prefix="/api")
app.include_router(orders.router, prefix="/api")
app.include_router(history.router, prefix="/api")
app.include_router(autocomplete.router, prefix="/api")
app.include_router(import_data.router, prefix="/api")


@app.get("/", include_in_schema=False)
def root():
    return JSONResponse({"status": "ok", "app": "Nam Phương API v1.0"})


@app.get("/health", include_in_schema=False)
def health():
    return JSONResponse({"status": "healthy"})
