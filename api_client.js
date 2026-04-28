/**
 * API CLIENT — Thêm đoạn này vào <script> đầu file HTML
 * =========================================================
 * Thay thế localStorage bằng các lời gọi API.
 * Tất cả hàm đều bất đồng bộ (async), trả về Promise.
 *
 * Cách dùng:
 *   1. Thêm <script src="api_client.js"></script> trước </body>
 *   2. Đặt API_BASE_URL trỏ đúng server của bạn
 *   3. Gọi await API.auth.login(username, password) khi khởi động
 */

const API_BASE_URL = 'http://localhost:8000/api';  // ← Đổi thành URL thực của bạn

/* ── Token storage ── */
const TokenStore = {
  get:    () => localStorage.getItem('np_api_token'),
  set:    (t) => localStorage.setItem('np_api_token', t),
  clear:  () => localStorage.removeItem('np_api_token'),
};

/* ── Core fetch wrapper ── */
async function apiFetch(path, options = {}) {
  const token = TokenStore.get();
  const headers = {
    'Content-Type': 'application/json',
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
    ...(options.headers || {}),
  };

  const res = await fetch(`${API_BASE_URL}${path}`, {
    ...options,
    headers,
    body: options.body ? JSON.stringify(options.body) : undefined,
  });

  if (res.status === 401) {
    TokenStore.clear();
    showLoginModal();
    throw new Error('Phiên đăng nhập hết hạn. Vui lòng đăng nhập lại.');
  }

  const data = await res.json().catch(() => ({}));
  if (!res.ok) throw new Error(data.detail || `Lỗi ${res.status}`);
  return data;
}

const get  = (path)         => apiFetch(path, { method: 'GET' });
const post = (path, body)   => apiFetch(path, { method: 'POST', body });
const put  = (path, body)   => apiFetch(path, { method: 'PUT',  body });
const del  = (path)         => apiFetch(path, { method: 'DELETE' });
const patch = (path, body)  => apiFetch(path, { method: 'PATCH', body });

/* ════════════════════════════════════════════════════════
   API METHODS — dùng thay cho localStorage
   ════════════════════════════════════════════════════════ */

const API = {

  /* ── Auth ── */
  auth: {
    register: (email, username, password, companyName) =>
      post('/auth/register', { email, username, password, company_name: companyName }),

    login: async (username, password) => {
      const res = await post('/auth/login', { username, password });
      TokenStore.set(res.access_token);
      return res.user;
    },

    logout: () => { TokenStore.clear(); showLoginModal(); },

    me: () => get('/auth/me'),

    isLoggedIn: () => !!TokenStore.get(),
  },

  /* ── Config (thay saveState / loadState) ── */
  config: {
    get: () => get('/config'),
    save: (printCost, makeCost, profit, waste) =>
      put('/config', { print_cost: printCost, make_cost: makeCost, profit, waste }),
  },

  /* ── Paper Prices (thay savePrices / loadPrices) ── */
  prices: {
    get: () => get('/prices'),
    save: (prices, activePaper) => put('/prices', { prices, active_paper: activePaper }),
  },

  /* ── Presets (thay savePresetsLS / loadPresets) ── */
  presets: {
    list:    () => get('/presets'),
    saveAll: (presets) => put('/presets', { presets }),
  },

  /* ── Terms (thay saveTermsLS / loadTerms) ── */
  terms: {
    list:    () => get('/terms'),
    saveAll: (terms) => put('/terms', { terms }),
  },

  /* ── Customers (thay saveCatalog / loadCatalog) ── */
  customers: {
    list:   (q) => get(`/customers${q ? `?q=${encodeURIComponent(q)}` : ''}`),
    create: (cu) => post('/customers', _mapCustomerToApi(cu)),
    update: (clientId, cu) => put(`/customers/${clientId}`, _mapCustomerToApi(cu)),
    delete: (clientId) => del(`/customers/${clientId}`),
  },

  /* ── Products ── */
  products: {
    list:   (custId) => get(`/products${custId ? `?cust_id=${custId}` : ''}`),
    create: (p) => post('/products', _mapProductToApi(p)),
    update: (clientId, p) => put(`/products/${clientId}`, _mapProductToApi(p)),
    delete: (clientId) => del(`/products/${clientId}`),
  },

  /* ── Orders (thay saveOrders / loadOrders) ── */
  orders: {
    list:   (status, q) => get(`/orders${_qs({ status, q })}`),
    save:   (o) => post('/orders', _mapOrderToApi(o)),    // upsert theo order.no
    update: (no, o) => put(`/orders/${no}`, _mapOrderToApi(o)),
    setStatus: (no, status) => patch(`/orders/${no}/status?status=${status}`),
    delete: (no) => del(`/orders/${no}`),
  },

  /* ── Calc History (thay HIST_KEY localStorage) ── */
  history: {
    list:   () => get('/history'),
    add:    (h) => post('/history', {
      ts: h.ts, label: h.label, date: h.date,
      items: h.items, tot_rev: h.totRev, tot_cost: h.totCost,
    }),
    delete:      (id) => del(`/history/${id}`),
    clearAll:    () => del('/history'),
  },

  /* ── AutoComplete ── */
  autocomplete: {
    get:  () => get('/autocomplete'),
    sync: (entries) => put('/autocomplete', { entries }),
  },

  /* ── Bulk Import (dùng 1 lần khi chuyển từ localStorage) ── */
  importAll: (data) => post('/import', data),
};

/* ── Helper: map frontend object → API snake_case ── */
function _mapCustomerToApi(cu) {
  return {
    client_id:      cu.id,
    mst:            cu.mst,
    name:           cu.name,
    short:          cu.short,
    code:           cu.code,
    addr:           cu.addr,
    delivery_addr:  cu.deliveryAddr,
    rep_name:       cu.repName,
    rep_title:      cu.repTitle,
    rep_basis:      cu.repBasis,
    rep_id:         cu.repID,
    rep_id_date:    cu.repIDDate,
    rep_id_place:   cu.repIDPlace,
    contact:        cu.contact,
    phone:          cu.phone,
    email:          cu.email,
    company_phone:  cu.companyPhone,
    fax:            cu.fax,
    web:            cu.web,
    bank_owner:     cu.bankOwner,
    bank_no:        cu.bankNo,
    bank_name:      cu.bankName,
    bank_branch:    cu.bankBranch,
    sales:          cu.sales,
    credit_limit:   cu.creditLimit || 0,
    pay_term:       cu.payTerm,
    note:           cu.note,
  };
}

function _mapProductToApi(p) {
  return {
    client_id:      p.id,
    client_cust_id: p.custId,
    code:           p.code,
    name:           p.name,
    box_type:       p.boxType || 'a1',
    dim_d:          p.D || 0,
    dim_r:          p.R || 0,
    dim_c:          p.C || 0,
    song_type:      p.songType || 'C',
    num_layers:     p.numLayers || 3,
    print_type:     p.printType,
    print_colors:   p.printColors || 0,
    chong_tham:     p.chongTham,
    can_mang:       p.canMang,
    lan:            p.lan,
    ban_ve:         p.banVe,
    sell_price:     p.sellPrice || 0,
    cost_price:     p.costPrice || 0,
    moq:            p.moq || 0,
    unit:           p.unit || 'Thùng',
    note:           p.note,
    ghim:           !!p.ghim,
    boi:            !!p.boi,
    dan:            !!p.dan,
    dophu:          !!p.dophu,
    paper_codes:    p.paperCode,
  };
}

function _mapOrderToApi(o) {
  return {
    seq:          o.seq,
    no:           o.no,
    date:         o.date,
    delivery:     o.delivery,
    cust:         o.cust,
    cust_phone:   o.custPhone,
    cust_addr:    o.custAddr,
    sales:        o.sales,
    approver:     o.approver,
    po_kh:        o.poKH,
    from_quote:   o.fromQuote,
    item_name:    o.itemName,
    unit:         o.unit || 'Thùng',
    qty_bg:       o.qtyBG || 0,
    qty_po:       o.qtyPO || 0,
    qty_lsx:      o.qtyLSX || 0,
    layers:       o.layers || 3,
    song:         o.song || 'C',
    box_type:     o.boxType || 'a1',
    dim_d:        o.D || 0,
    dim_r:        o.R || 0,
    dim_c:        o.C || 0,
    dai_tt:       o.daiTT || 0,
    kho_tt:       o.khoTT || 0,
    no_formula:   !!o.noFormula,
    print_type:   o.printType,
    print_colors: o.printColors || 0,
    con_bi:       o.conBi || 0,
    dokho:        !!o.dokho,
    ghim:         !!o.ghim,
    chap_xa:      !!o.chapXa,
    dophu:        !!o.dophu,
    dan:          !!o.dan,
    boi:          !!o.boi,
    chong_tham:   o.chongTham,
    can_mang:     o.canMang,
    loai_lan:     o.loaiLan,
    ban_ve:       o.banVe,
    sell_price:   o.sellPrice || 0,
    extra_cost:   o.extraCost || 0,
    discount:     o.discount || 0,
    amis:         o.amis,
    note:         o.note,
    priority:     o.priority || 'normal',
    status:       o.status || 'new',
    layer_codes:  o.layerCodes,
  };
}

function _qs(params) {
  const q = Object.entries(params)
    .filter(([, v]) => v != null && v !== '')
    .map(([k, v]) => `${k}=${encodeURIComponent(v)}`)
    .join('&');
  return q ? `?${q}` : '';
}

/* ── Login Modal (hiển thị khi token hết hạn) ── */
function showLoginModal() {
  const existing = document.getElementById('_apiLoginModal');
  if (existing) { existing.style.display = 'flex'; return; }

  const modal = document.createElement('div');
  modal.id = '_apiLoginModal';
  modal.innerHTML = `
    <div style="position:fixed;inset:0;background:rgba(0,0,0,.6);z-index:9999;
      display:flex;align-items:center;justify-content:center;font-family:sans-serif">
      <div style="background:#fff;border-radius:14px;padding:32px;width:340px;box-shadow:0 20px 60px rgba(0,0,0,.3)">
        <div style="font-size:18px;font-weight:800;color:#1C2A8C;margin-bottom:20px">
          🔐 Đăng nhập
        </div>
        <div style="margin-bottom:12px">
          <label style="font-size:11px;font-weight:600;color:#6b7194">USERNAME</label>
          <input id="_lgUser" type="text" style="width:100%;border:1.5px solid #d0d5e8;
            border-radius:7px;padding:8px 10px;margin-top:4px;font-size:13px;outline:none">
        </div>
        <div style="margin-bottom:20px">
          <label style="font-size:11px;font-weight:600;color:#6b7194">MẬT KHẨU</label>
          <input id="_lgPass" type="password" style="width:100%;border:1.5px solid #d0d5e8;
            border-radius:7px;padding:8px 10px;margin-top:4px;font-size:13px;outline:none">
        </div>
        <div id="_lgErr" style="color:#d63030;font-size:12px;margin-bottom:10px;display:none"></div>
        <button id="_lgBtn" onclick="window._doLogin()" style="width:100%;background:#E8830A;
          color:#fff;border:none;border-radius:8px;padding:12px;font-size:14px;
          font-weight:700;cursor:pointer">Đăng nhập</button>
        <div style="font-size:10px;color:#9095b0;text-align:center;margin-top:14px">
          Server: ${API_BASE_URL}
        </div>
      </div>
    </div>`;
  document.body.appendChild(modal);

  document.getElementById('_lgPass').addEventListener('keydown', e => {
    if (e.key === 'Enter') window._doLogin();
  });
}

window._doLogin = async function () {
  const u = document.getElementById('_lgUser').value.trim();
  const p = document.getElementById('_lgPass').value;
  const err = document.getElementById('_lgErr');
  const btn = document.getElementById('_lgBtn');
  if (!u || !p) { err.textContent = 'Nhập đầy đủ username và mật khẩu'; err.style.display=''; return; }
  btn.textContent = 'Đang đăng nhập...'; btn.disabled = true;
  try {
    await API.auth.login(u, p);
    document.getElementById('_apiLoginModal').remove();
    location.reload();
  } catch (e) {
    err.textContent = e.message || 'Sai thông tin đăng nhập';
    err.style.display = '';
    btn.textContent = 'Đăng nhập'; btn.disabled = false;
  }
};

/* ── Auto-init: kiểm tra token khi trang tải ── */
(async function init() {
  if (!API.auth.isLoggedIn()) {
    showLoginModal();
    return;
  }
  try {
    await API.auth.me();
  } catch {
    showLoginModal();
  }
})();
