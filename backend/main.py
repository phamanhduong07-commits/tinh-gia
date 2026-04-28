from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from .config import settings
from .database import Base, engine, SessionLocal
from .routers import (
    auth, admin, config, prices, presets, terms,
    customers, products, orders, history, autocomplete, import_data,
)

# Tạo tất cả bảng khi khởi động
Base.metadata.create_all(bind=engine)

# Tự động tạo admin mặc định nếu chưa có user nào
def _create_default_admin():
    from .models import User
    from .auth import hash_password
    db = SessionLocal()
    try:
        if db.query(User).count() == 0:
            db.add(User(
                email="admin@namphuong.local",
                username="admin",
                hashed_password=hash_password("admin123"),
                full_name="Admin",
                role="admin",
                is_active=True,
            ))
            db.commit()
            print("\n" + "="*50)
            print("  TAI KHOAN ADMIN MAC DINH DA DUOC TAO:")
            print("  Username : admin")
            print("  Password : admin123")
            print("  --> Doi mat khau sau khi dang nhap!")
            print("="*50 + "\n")
    finally:
        db.close()

_create_default_admin()

app = FastAPI(
    title="Tính Giá Thùng Carton – Nam Phương API",
    description="Backend API cho ứng dụng tính giá thùng carton",
    version="1.0.0",
)

origins = [o.strip() for o in settings.ALLOWED_ORIGINS.split(",") if o.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router,         prefix="/api")
app.include_router(admin.router,        prefix="/api")
app.include_router(config.router,       prefix="/api")
app.include_router(prices.router,       prefix="/api")
app.include_router(presets.router,      prefix="/api")
app.include_router(terms.router,        prefix="/api")
app.include_router(customers.router,    prefix="/api")
app.include_router(products.router,     prefix="/api")
app.include_router(orders.router,       prefix="/api")
app.include_router(history.router,      prefix="/api")
app.include_router(autocomplete.router, prefix="/api")
app.include_router(import_data.router,  prefix="/api")


@app.get("/", include_in_schema=False)
def root():
    return JSONResponse({"status": "ok", "app": "Nam Phuong API v1.0"})

@app.get("/health", include_in_schema=False)
def health():
    return JSONResponse({"status": "healthy"})
