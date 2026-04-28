/**
 * BƯỚC 1: EXPORT DỮ LIỆU TỪ TRÌNH DUYỆT
 * =========================================
 * Mở file HTML trong trình duyệt, mở DevTools (F12) → Console
 * Dán toàn bộ đoạn code này vào Console rồi nhấn Enter
 * File JSON sẽ được tải xuống tự động
 */

(function exportLocalStorage() {
  const keys = {
    config:       'np_cfg_v5',
    prices:       'np_prices_v5',
    presets:      'np_presets_v5',
    terms:        'np_terms_v1',
    customers:    'np_cust_v2',
    products:     'np_prod_v2',
    orders:       'np_orders_v2',
    calc_history: 'np_hist_v5',
    autocomplete: 'np_ac_v5',
  };

  const data = {};
  for (const [field, lsKey] of Object.entries(keys)) {
    try {
      const raw = localStorage.getItem(lsKey);
      if (raw) data[field] = JSON.parse(raw);
    } catch (e) {
      console.warn(`Không đọc được ${lsKey}:`, e);
    }
  }

  const json = JSON.stringify(data, null, 2);
  const blob = new Blob([json], { type: 'application/json' });
  const url  = URL.createObjectURL(blob);
  const a    = document.createElement('a');
  a.href     = url;
  a.download = `namphuong_backup_${new Date().toISOString().slice(0,10)}.json`;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  setTimeout(() => URL.revokeObjectURL(url), 3000);

  console.log('✅ Đã xuất dữ liệu:', Object.keys(data).map(k => `${k}: ${JSON.stringify(data[k])?.length} chars`).join('\n'));
  return data;
})();
