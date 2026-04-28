from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, EmailStr


# ── Auth ──────────────────────────────────────────────────────────────────────

class UserCreate(BaseModel):
    email: EmailStr
    username: str
    password: str
    company_name: Optional[str] = None


class UserLogin(BaseModel):
    username: str
    password: str


class UserOut(BaseModel):
    id: int
    email: str
    username: str
    company_name: Optional[str]
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str
    user: UserOut


# ── Config ────────────────────────────────────────────────────────────────────

class ConfigIn(BaseModel):
    print_cost: float = 0
    make_cost: float = 0
    profit: float = 0
    waste: float = 0


class ConfigOut(ConfigIn):
    id: int
    updated_at: datetime

    class Config:
        from_attributes = True


# ── Paper Prices ──────────────────────────────────────────────────────────────

class PaperPriceIn(BaseModel):
    code: str
    price_per_kg: float = 0
    active: bool = True


class PaperPriceOut(PaperPriceIn):
    id: int

    class Config:
        from_attributes = True


class PaperPricesBulk(BaseModel):
    """Bulk update từ object {code: price} của frontend"""
    prices: Dict[str, float]
    active_paper: Optional[str] = None


# ── Presets ───────────────────────────────────────────────────────────────────

class PresetIn(BaseModel):
    data: Dict[str, Any]


class PresetOut(PresetIn):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


class PresetsBulk(BaseModel):
    presets: List[Dict[str, Any]]


# ── Terms ─────────────────────────────────────────────────────────────────────

class TermIn(BaseModel):
    sort_order: int = 0
    data: Dict[str, Any]


class TermOut(TermIn):
    id: int

    class Config:
        from_attributes = True


class TermsBulk(BaseModel):
    terms: List[Dict[str, Any]]


# ── Customer ──────────────────────────────────────────────────────────────────

class CustomerIn(BaseModel):
    client_id: str
    mst: Optional[str] = None
    name: str
    short: Optional[str] = None
    code: Optional[str] = None
    addr: Optional[str] = None
    delivery_addr: Optional[str] = None
    rep_name: Optional[str] = None
    rep_title: Optional[str] = None
    rep_basis: Optional[str] = None
    rep_id: Optional[str] = None
    rep_id_date: Optional[str] = None
    rep_id_place: Optional[str] = None
    contact: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    company_phone: Optional[str] = None
    fax: Optional[str] = None
    web: Optional[str] = None
    bank_owner: Optional[str] = None
    bank_no: Optional[str] = None
    bank_name: Optional[str] = None
    bank_branch: Optional[str] = None
    sales: Optional[str] = None
    credit_limit: float = 0
    pay_term: Optional[str] = None
    note: Optional[str] = None


class CustomerOut(CustomerIn):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ── Product ───────────────────────────────────────────────────────────────────

class ProductIn(BaseModel):
    client_id: str
    client_cust_id: Optional[str] = None
    code: Optional[str] = None
    name: str
    box_type: str = "a1"
    dim_d: float = 0
    dim_r: float = 0
    dim_c: float = 0
    song_type: str = "C"
    num_layers: int = 3
    print_type: Optional[str] = None
    print_colors: int = 0
    chong_tham: Optional[str] = None
    can_mang: Optional[str] = None
    lan: Optional[str] = None
    ban_ve: Optional[str] = None
    sell_price: float = 0
    cost_price: float = 0
    moq: int = 0
    unit: str = "Thùng"
    note: Optional[str] = None
    ghim: bool = False
    boi: bool = False
    dan: bool = False
    dophu: bool = False
    paper_codes: Optional[Dict[str, str]] = None


class ProductOut(ProductIn):
    id: int
    customer_id: Optional[int] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ── Order ─────────────────────────────────────────────────────────────────────

class OrderIn(BaseModel):
    seq: int
    no: str
    date: Optional[str] = None
    delivery: Optional[str] = None
    cust: Optional[str] = None
    cust_phone: Optional[str] = None
    cust_addr: Optional[str] = None
    sales: Optional[str] = None
    approver: Optional[str] = None
    po_kh: Optional[str] = None
    from_quote: Optional[str] = None
    item_name: Optional[str] = None
    unit: str = "Thùng"
    qty_bg: int = 0
    qty_po: int = 0
    qty_lsx: int = 0
    layers: int = 3
    song: str = "C"
    box_type: str = "a1"
    dim_d: float = 0
    dim_r: float = 0
    dim_c: float = 0
    dai_tt: float = 0
    kho_tt: float = 0
    no_formula: bool = False
    print_type: Optional[str] = None
    print_colors: int = 0
    con_bi: int = 0
    dokho: bool = False
    ghim: bool = False
    chap_xa: bool = False
    dophu: bool = False
    dan: bool = False
    boi: bool = False
    chong_tham: Optional[str] = None
    can_mang: Optional[str] = None
    loai_lan: Optional[str] = None
    ban_ve: Optional[str] = None
    sell_price: float = 0
    extra_cost: float = 0
    discount: float = 0
    amis: Optional[str] = None
    note: Optional[str] = None
    priority: str = "normal"
    status: str = "new"
    layer_codes: Optional[Dict[str, str]] = None


class OrderOut(OrderIn):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ── Calc History ──────────────────────────────────────────────────────────────

class CalcHistoryIn(BaseModel):
    ts: float
    label: Optional[str] = None
    date: Optional[str] = None
    items: List[Dict[str, Any]] = []
    tot_rev: float = 0
    tot_cost: float = 0


class CalcHistoryOut(CalcHistoryIn):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


# ── AutoComplete ──────────────────────────────────────────────────────────────

class AutoCompleteIn(BaseModel):
    name: str
    data: Dict[str, Any]


class AutoCompleteOut(AutoCompleteIn):
    id: int

    class Config:
        from_attributes = True


class AutoCompleteBulk(BaseModel):
    """Bulk sync từ object {name: {...}} của frontend"""
    entries: Dict[str, Dict[str, Any]]


# ── Bulk Import (từ localStorage export) ─────────────────────────────────────

class BulkImport(BaseModel):
    """Toàn bộ dữ liệu từ 1 file export localStorage"""
    config: Optional[Dict[str, Any]] = None
    prices: Optional[Dict[str, Any]] = None
    presets: Optional[List[Dict[str, Any]]] = None
    terms: Optional[List[Dict[str, Any]]] = None
    customers: Optional[List[Dict[str, Any]]] = None
    products: Optional[List[Dict[str, Any]]] = None
    orders: Optional[List[Dict[str, Any]]] = None
    calc_history: Optional[List[Dict[str, Any]]] = None
    autocomplete: Optional[Dict[str, Dict[str, Any]]] = None


class BulkImportResult(BaseModel):
    imported: Dict[str, int]
    errors: List[str] = []
