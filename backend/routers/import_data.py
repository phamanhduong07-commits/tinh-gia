"""
Endpoint để import toàn bộ dữ liệu từ localStorage export một lần.
Frontend sẽ gọi POST /import với JSON chứa tất cả dữ liệu cũ.

Lưu ý phân quyền:
  - config & prices: chỉ admin mới được import (dữ liệu chung toàn hệ thống)
  - phần còn lại: mọi user được import (dữ liệu riêng của họ)
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from .. import models, schemas
from ..auth import get_current_user
from ..database import get_db

router = APIRouter(prefix="/import", tags=["Import"])


@router.post("", response_model=schemas.BulkImportResult)
def bulk_import(
    body: schemas.BulkImport,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    imported: dict = {}
    errors: list = []

    # ── Config (global, chỉ admin) ──
    if body.config:
        if current_user.role != "admin":
            errors.append("config: chỉ Admin mới được import cấu hình chi phí")
        else:
            try:
                cfg = db.query(models.Config).first()
                if not cfg:
                    cfg = models.Config()
                    db.add(cfg)
                cfg.print_cost = float(body.config.get("print", 0))
                cfg.make_cost  = float(body.config.get("make", 0))
                cfg.profit     = float(body.config.get("profit", 0))
                cfg.waste      = float(body.config.get("waste", 0))
                cfg.updated_by = current_user.id
                imported["config"] = 1
            except Exception as e:
                errors.append(f"config: {e}")

    # ── Paper Prices (global, chỉ admin) ──
    if body.prices:
        if current_user.role != "admin":
            errors.append("prices: chỉ Admin mới được import giá giấy")
        else:
            try:
                db.query(models.PaperPrice).delete()
                prices = body.prices.get("prices", {})
                active = body.prices.get("active", None)
                for code, price in prices.items():
                    db.add(models.PaperPrice(
                        code=code,
                        price_per_kg=float(price),
                        active=(code == active),
                        updated_by=current_user.id,
                    ))
                imported["prices"] = len(prices)
            except Exception as e:
                errors.append(f"prices: {e}")

    # ── Presets ──
    if body.presets:
        try:
            db.query(models.Preset).filter_by(user_id=current_user.id).delete()
            for p in body.presets:
                db.add(models.Preset(user_id=current_user.id, data=p))
            imported["presets"] = len(body.presets)
        except Exception as e:
            errors.append(f"presets: {e}")

    # ── Terms ──
    if body.terms:
        try:
            db.query(models.Term).filter_by(user_id=current_user.id).delete()
            for i, t in enumerate(body.terms):
                db.add(models.Term(user_id=current_user.id, sort_order=i, data=t))
            imported["terms"] = len(body.terms)
        except Exception as e:
            errors.append(f"terms: {e}")

    # ── Customers ──
    cust_map: dict = {}
    if body.customers:
        try:
            db.query(models.Customer).filter_by(user_id=current_user.id).delete()
            for cu_data in body.customers:
                cu = models.Customer(
                    user_id=current_user.id,
                    client_id=cu_data.get("id", ""),
                    mst=cu_data.get("mst"),
                    name=cu_data.get("name", ""),
                    short=cu_data.get("short"),
                    code=cu_data.get("code"),
                    addr=cu_data.get("addr"),
                    delivery_addr=cu_data.get("deliveryAddr"),
                    rep_name=cu_data.get("repName"),
                    rep_title=cu_data.get("repTitle"),
                    rep_basis=cu_data.get("repBasis"),
                    rep_id=cu_data.get("repID"),
                    rep_id_date=cu_data.get("repIDDate"),
                    rep_id_place=cu_data.get("repIDPlace"),
                    contact=cu_data.get("contact"),
                    phone=cu_data.get("phone"),
                    email=cu_data.get("email"),
                    company_phone=cu_data.get("companyPhone"),
                    fax=cu_data.get("fax"),
                    web=cu_data.get("web"),
                    bank_owner=cu_data.get("bankOwner"),
                    bank_no=cu_data.get("bankNo"),
                    bank_name=cu_data.get("bankName"),
                    bank_branch=cu_data.get("bankBranch"),
                    sales=cu_data.get("sales"),
                    credit_limit=float(cu_data.get("creditLimit", 0)),
                    pay_term=cu_data.get("payTerm"),
                    note=cu_data.get("note"),
                )
                db.add(cu)
                db.flush()
                cust_map[cu_data.get("id", "")] = cu.id
            imported["customers"] = len(body.customers)
        except Exception as e:
            errors.append(f"customers: {e}")

    # ── Products ──
    if body.products:
        try:
            db.query(models.Product).filter_by(user_id=current_user.id).delete()
            for p_data in body.products:
                client_cust_id = p_data.get("custId", "")
                customer_id = cust_map.get(client_cust_id)
                db.add(models.Product(
                    user_id=current_user.id,
                    customer_id=customer_id,
                    client_id=p_data.get("id", ""),
                    client_cust_id=client_cust_id,
                    code=p_data.get("code"),
                    name=p_data.get("name", ""),
                    box_type=p_data.get("boxType", "a1"),
                    dim_d=float(p_data.get("D", 0)),
                    dim_r=float(p_data.get("R", 0)),
                    dim_c=float(p_data.get("C", 0)),
                    song_type=p_data.get("songType", "C"),
                    num_layers=int(p_data.get("numLayers", 3)),
                    print_type=p_data.get("printType"),
                    print_colors=int(p_data.get("printColors", 0)),
                    chong_tham=p_data.get("chongTham"),
                    can_mang=p_data.get("canMang"),
                    lan=p_data.get("lan"),
                    ban_ve=p_data.get("banVe"),
                    sell_price=float(p_data.get("sellPrice", 0)),
                    cost_price=float(p_data.get("costPrice", 0)),
                    moq=int(p_data.get("moq", 0)),
                    unit=p_data.get("unit", "Thùng"),
                    note=p_data.get("note"),
                    ghim=bool(p_data.get("ghim")),
                    boi=bool(p_data.get("boi")),
                    dan=bool(p_data.get("dan")),
                    dophu=bool(p_data.get("dophu")),
                    paper_codes=p_data.get("paperCode"),
                ))
            imported["products"] = len(body.products)
        except Exception as e:
            errors.append(f"products: {e}")

    # ── Orders ──
    if body.orders:
        try:
            db.query(models.Order).filter_by(user_id=current_user.id).delete()
            for o_data in body.orders:
                db.add(models.Order(
                    user_id=current_user.id,
                    seq=int(o_data.get("seq", 0)),
                    no=o_data.get("no", ""),
                    date=o_data.get("date"),
                    delivery=o_data.get("delivery"),
                    cust=o_data.get("cust"),
                    cust_phone=o_data.get("custPhone"),
                    cust_addr=o_data.get("custAddr"),
                    sales=o_data.get("sales"),
                    approver=o_data.get("approver"),
                    po_kh=o_data.get("poKH"),
                    from_quote=o_data.get("fromQuote"),
                    item_name=o_data.get("itemName"),
                    unit=o_data.get("unit", "Thùng"),
                    qty_bg=int(o_data.get("qtyBG", 0)),
                    qty_po=int(o_data.get("qtyPO", 0)),
                    qty_lsx=int(o_data.get("qtyLSX", 0)),
                    layers=int(o_data.get("layers", 3)),
                    song=o_data.get("song", "C"),
                    box_type=o_data.get("boxType", "a1"),
                    dim_d=float(o_data.get("D", 0)),
                    dim_r=float(o_data.get("R", 0)),
                    dim_c=float(o_data.get("C", 0)),
                    dai_tt=float(o_data.get("daiTT", 0)),
                    kho_tt=float(o_data.get("khoTT", 0)),
                    no_formula=bool(o_data.get("noFormula")),
                    print_type=o_data.get("printType"),
                    print_colors=int(o_data.get("printColors", 0)),
                    con_bi=int(o_data.get("conBi", 0)),
                    dokho=bool(o_data.get("dokho")),
                    ghim=bool(o_data.get("ghim")),
                    chap_xa=bool(o_data.get("chapXa")),
                    dophu=bool(o_data.get("dophu")),
                    dan=bool(o_data.get("dan")),
                    boi=bool(o_data.get("boi")),
                    chong_tham=o_data.get("chongTham"),
                    can_mang=o_data.get("canMang"),
                    loai_lan=o_data.get("loaiLan"),
                    ban_ve=o_data.get("banVe"),
                    sell_price=float(o_data.get("sellPrice", 0)),
                    extra_cost=float(o_data.get("extraCost", 0)),
                    discount=float(o_data.get("discount", 0)),
                    amis=o_data.get("amis"),
                    note=o_data.get("note"),
                    priority=o_data.get("priority", "normal"),
                    status=o_data.get("status", "new"),
                    layer_codes=o_data.get("layerCodes"),
                ))
            imported["orders"] = len(body.orders)
        except Exception as e:
            errors.append(f"orders: {e}")

    # ── Calc History ──
    if body.calc_history:
        try:
            db.query(models.CalcHistory).filter_by(user_id=current_user.id).delete()
            for h_data in body.calc_history[:50]:
                db.add(models.CalcHistory(
                    user_id=current_user.id,
                    ts=float(h_data.get("ts", 0)),
                    label=h_data.get("label"),
                    date=h_data.get("date"),
                    items=h_data.get("items", []),
                    tot_rev=float(h_data.get("totRev", 0)),
                    tot_cost=float(h_data.get("totCost", 0)),
                ))
            imported["calc_history"] = len(body.calc_history)
        except Exception as e:
            errors.append(f"calc_history: {e}")

    # ── AutoComplete ──
    if body.autocomplete:
        try:
            db.query(models.AutoComplete).filter_by(user_id=current_user.id).delete()
            for name, data in list(body.autocomplete.items())[:200]:
                db.add(models.AutoComplete(user_id=current_user.id, name=name, data=data))
            imported["autocomplete"] = len(body.autocomplete)
        except Exception as e:
            errors.append(f"autocomplete: {e}")

    db.commit()
    return schemas.BulkImportResult(imported=imported, errors=errors)
