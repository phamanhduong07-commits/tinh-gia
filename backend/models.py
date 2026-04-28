from sqlalchemy import (
    Boolean, Column, DateTime, Float, ForeignKey,
    Integer, JSON, String, Text, func,
)
from sqlalchemy.orm import relationship

from .database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    username = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    company_name = Column(String(255))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relations
    configs = relationship("Config", back_populates="user", cascade="all, delete-orphan")
    paper_prices = relationship("PaperPrice", back_populates="user", cascade="all, delete-orphan")
    presets = relationship("Preset", back_populates="user", cascade="all, delete-orphan")
    terms = relationship("Term", back_populates="user", cascade="all, delete-orphan")
    customers = relationship("Customer", back_populates="user", cascade="all, delete-orphan")
    products = relationship("Product", back_populates="user", cascade="all, delete-orphan")
    orders = relationship("Order", back_populates="user", cascade="all, delete-orphan")
    calc_histories = relationship("CalcHistory", back_populates="user", cascade="all, delete-orphan")
    autocomplete = relationship("AutoComplete", back_populates="user", cascade="all, delete-orphan")


class Config(Base):
    """Thông số gia công & lợi nhuận (LS_CFG)"""
    __tablename__ = "configs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    print_cost = Column(Float, default=0)   # gPrint
    make_cost = Column(Float, default=0)    # gMake
    profit = Column(Float, default=0)       # gProfit
    waste = Column(Float, default=0)        # gWaste
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())

    user = relationship("User", back_populates="configs")


class PaperPrice(Base):
    """Giá giấy theo mã (LS_PRICES)"""
    __tablename__ = "paper_prices"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    code = Column(String(20), nullable=False)       # mã giấy VD: GA, HB, 98
    price_per_kg = Column(Float, default=0)
    active = Column(Boolean, default=True)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())

    user = relationship("User", back_populates="paper_prices")


class Preset(Base):
    """Cấu trúc thùng preset (LS_PRESETS)"""
    __tablename__ = "presets"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    data = Column(JSON, nullable=False)     # toàn bộ preset object từ JS
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="presets")


class Term(Base):
    """Điều khoản báo giá (LS_TERMS)"""
    __tablename__ = "terms"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    sort_order = Column(Integer, default=0)
    data = Column(JSON, nullable=False)     # toàn bộ term object từ JS
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())

    user = relationship("User", back_populates="terms")


class Customer(Base):
    """Danh mục khách hàng (LS_CUST)"""
    __tablename__ = "customers"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    client_id = Column(String(50), nullable=False)  # ID từ frontend (uid())
    mst = Column(String(20))
    name = Column(String(255), nullable=False, index=True)
    short = Column(String(100))
    code = Column(String(50), index=True)
    addr = Column(Text)
    delivery_addr = Column(Text)
    rep_name = Column(String(255))
    rep_title = Column(String(100))
    rep_basis = Column(String(255))
    rep_id = Column(String(50))
    rep_id_date = Column(String(50))
    rep_id_place = Column(String(255))
    contact = Column(String(255))
    phone = Column(String(50))
    email = Column(String(255))
    company_phone = Column(String(50))
    fax = Column(String(50))
    web = Column(String(255))
    bank_owner = Column(String(255))
    bank_no = Column(String(50))
    bank_name = Column(String(255))
    bank_branch = Column(String(255))
    sales = Column(String(255))
    credit_limit = Column(Float, default=0)
    pay_term = Column(String(255))
    note = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())

    user = relationship("User", back_populates="customers")
    products = relationship("Product", back_populates="customer", cascade="all, delete-orphan")


class Product(Base):
    """Mã hàng (LS_PROD)"""
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=True, index=True)
    client_id = Column(String(50), nullable=False)
    client_cust_id = Column(String(50))    # custId từ JS
    code = Column(String(100), index=True)
    name = Column(String(255), nullable=False)
    box_type = Column(String(20), default="a1")
    dim_d = Column(Float, default=0)
    dim_r = Column(Float, default=0)
    dim_c = Column(Float, default=0)
    song_type = Column(String(10), default="C")
    num_layers = Column(Integer, default=3)
    print_type = Column(String(50))
    print_colors = Column(Integer, default=0)
    chong_tham = Column(String(50))
    can_mang = Column(String(50))
    lan = Column(String(50))
    ban_ve = Column(String(255))
    sell_price = Column(Float, default=0)
    cost_price = Column(Float, default=0)
    moq = Column(Integer, default=0)
    unit = Column(String(20), default="Thùng")
    note = Column(Text)
    ghim = Column(Boolean, default=False)
    boi = Column(Boolean, default=False)
    dan = Column(Boolean, default=False)
    dophu = Column(Boolean, default=False)
    paper_codes = Column(JSON)   # {l1, s1, l2, ...}
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())

    user = relationship("User", back_populates="products")
    customer = relationship("Customer", back_populates="products")


class Order(Base):
    """Lệnh sản xuất (LS_ORDERS)"""
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    seq = Column(Integer, nullable=False)
    no = Column(String(50), nullable=False, index=True)
    date = Column(String(20))
    delivery = Column(String(20))
    cust = Column(String(255))
    cust_phone = Column(String(50))
    cust_addr = Column(Text)
    sales = Column(String(255))
    approver = Column(String(255))
    po_kh = Column(String(100))
    from_quote = Column(String(100))
    item_name = Column(String(255))
    unit = Column(String(20), default="Thùng")
    qty_bg = Column(Integer, default=0)
    qty_po = Column(Integer, default=0)
    qty_lsx = Column(Integer, default=0)
    layers = Column(Integer, default=3)
    song = Column(String(10), default="C")
    box_type = Column(String(20), default="a1")
    dim_d = Column(Float, default=0)
    dim_r = Column(Float, default=0)
    dim_c = Column(Float, default=0)
    dai_tt = Column(Float, default=0)
    kho_tt = Column(Float, default=0)
    no_formula = Column(Boolean, default=False)
    print_type = Column(String(50))
    print_colors = Column(Integer, default=0)
    con_bi = Column(Integer, default=0)
    dokho = Column(Boolean, default=False)
    ghim = Column(Boolean, default=False)
    chap_xa = Column(Boolean, default=False)
    dophu = Column(Boolean, default=False)
    dan = Column(Boolean, default=False)
    boi = Column(Boolean, default=False)
    chong_tham = Column(String(50))
    can_mang = Column(String(50))
    loai_lan = Column(String(50))
    ban_ve = Column(String(255))
    sell_price = Column(Float, default=0)
    extra_cost = Column(Float, default=0)
    discount = Column(Float, default=0)
    amis = Column(String(100))
    note = Column(Text)
    priority = Column(String(20), default="normal")
    status = Column(String(20), default="new")
    layer_codes = Column(JSON)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())

    user = relationship("User", back_populates="orders")


class CalcHistory(Base):
    """Lịch sử tính giá (HIST_KEY)"""
    __tablename__ = "calc_histories"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    ts = Column(Float, nullable=False)       # timestamp milliseconds
    label = Column(String(50))
    date = Column(String(20))
    items = Column(JSON)                     # [{name,D,R,C,qty,costPB,sellPB,area}]
    tot_rev = Column(Float, default=0)
    tot_cost = Column(Float, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="calc_histories")


class AutoComplete(Base):
    """Lịch sử autocomplete tên thùng (AC_KEY)"""
    __tablename__ = "autocomplete"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    data = Column(JSON)                      # {D,R,C,songType,numLayers,gsm}
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())

    user = relationship("User", back_populates="autocomplete")
