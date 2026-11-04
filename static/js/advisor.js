/**
 * advisor.js —— 模块1：新机选购
 * - 预算：填写最低价 / 最高价
 * - 品牌：参照京东筛选，下拉多选
 * 表单提交 -> 后端 -> 渲染推荐清单 + 记录管理。
 */

// 不同品类的常见品牌（可按需增删）
const BRANDS_BY_CATEGORY = {
  '手机': ['苹果', '华为', '小米', '荣耀', 'OPPO', 'vivo', '三星', '一加', 'realme'],
  '耳机': ['苹果', '华为', '小米', '索尼', '漫步者', 'Bose', 'JBL', 'OPPO', '倍思'],
  '笔记本': ['联想', '戴尔', '惠普', '苹果', '华硕', '华为', '小米', '宏碁'],
  '平板': ['苹果', '华为', '小米', '三星', '联想', '荣耀'],
  '相机': ['索尼', '佳能', '尼康', '富士', '松下', '大疆'],
};

const advisorPage = {
  clearForm() {
    document.getElementById('notes').value = '';
    document.getElementById('minPrice').value = '';
    document.getElementById('maxPrice').value = '';
    clearBrands();
    document.getElementById('advResult').hidden = true;
  },
};

// ---------- 品牌筛选状态 ----------
let selectedBrands = new Set();

function currentCategory() {
  return document.getElementById('category').value;
}

function renderBrandOptions() {
  const box = document.getElementById('brandOptions');
  const brands = BRANDS_BY_CATEGORY[currentCategory()] || [];
  box.innerHTML = '';
  brands.forEach(b => {
    const label = document.createElement('label');
    label.className = 'brand-option';
    const cb = document.createElement('input');
    cb.type = 'checkbox';
    cb.value = b;
    cb.checked = selectedBrands.has(b);
    cb.addEventListener('change', () => {
      if (cb.checked) selectedBrands.add(b); else selectedBrands.delete(b);
    });
    label.appendChild(cb);
    label.appendChild(document.createTextNode(' ' + b));
    box.appendChild(label);
  });
}

function updateBrandTrigger() {
  const trigger = document.getElementById('brandTrigger');
  const txt = selectedBrands.size ? Array.from(selectedBrands).join(' / ') : '全部品牌';
  trigger.textContent = selectedBrands.size ? (txt + ' ▾') : '全部品牌 ▾';
}

function clearBrands() {
  selectedBrands.clear();
  if (document.getElementById('brandOptions')) renderBrandOptions();
  updateBrandTrigger();
}

function getSelectedBrands() {
  return Array.from(selectedBrands);
}

// ---------- 预算 ----------
function buildBudgetText() {
  const min = parseFloat(document.getElementById('minPrice').value) || 0;
  const max = parseFloat(document.getElementById('maxPrice').value) || 0;
  if (min && max && min > max) {
    showToast('最低价不能大于最高价', 'error');
    return '';
  }
  if (min && max) return min + '元~' + max + '元';
  if (min) return min + '元以上';
  if (max) return max + '元以内';
  showToast('请填写预算（最低价或最高价，至少填一个）', 'error');
  return '';
}

// ---------- 表单 ----------
async function renderAdvisor() {
  const form = document.getElementById('advisorForm');
  const btn = document.getElementById('btnRun');

  // 品牌下拉：点开 / 收起
  const trigger = document.getElementById('brandTrigger');
  const menu = document.getElementById('brandMenu');
  const box = document.getElementById('brandBox');
  trigger.addEventListener('click', (e) => {
    e.stopPropagation();
    renderBrandOptions();
    menu.hidden = !menu.hidden;
  });
  document.getElementById('brandClear').addEventListener('click', () => {
    clearBrands();
  });
  document.getElementById('brandConfirm').addEventListener('click', () => {
    updateBrandTrigger();
    menu.hidden = true;
  });
  // 点击页面其它地方时收起品牌下拉
  document.addEventListener('click', () => { if (menu && !menu.hidden) menu.hidden = true; });
  box.addEventListener('click', (e) => e.stopPropagation());
  // 切换品类时同步品牌列表
  document.getElementById('category').addEventListener('change', () => {
    clearBrands();
    renderBrandOptions();
  });
  renderBrandOptions();

  form.addEventListener('submit', async (e) => {
    e.preventDefault();
    const category = document.getElementById('category').value.trim();
    const usage = document.getElementById('usage').value.trim();
    const budget = buildBudgetText();
    if (!budget) return;

    const brands = getSelectedBrands();
    const notes = document.getElementById('notes').value.trim();

    if (!category || !usage) {
      showToast('请选择品类和用途', 'error');
      return;
    }

    btn.disabled = true;
    btn.textContent = 'AI 生成中…';
    try {
      const data = await api('/api/advisor', {
        method: 'POST',
        body: { budget, category, usage, brands, notes },
      });
      renderRecommendations(data.result);
      await loadAdvisorRecords();
    } catch (err) {
      showToast(err.message, 'error');
    } finally {
      btn.disabled = false;
      btn.textContent = '生成推荐';
    }
  });

  document.getElementById('btnCopyAdv').addEventListener('click', () => {
    const result = document.getElementById('advItems').dataset.fullText || '';
    copyText(result);
  });

  const clearBtn = document.getElementById('btnClearAdvRecords');
  if (clearBtn) {
    clearBtn.addEventListener('click', async () => {
      if (!confirm('确定要清空全部选购记录吗？')) return;
      try {
        await api('/api/advisor/records/clear', { method: 'DELETE' });
        await loadAdvisorRecords();
        showToast('已清空全部选购记录');
      } catch (e) { showToast(e.message, 'error'); }
    });
  }
}

async function loadAdvisorRecords() {
  const box = document.getElementById('advRecords');
  try {
    const data = await api('/api/advisor/records');
    if (!data.records || data.records.length === 0) {
      box.innerHTML = '<div class="empty">暂无选购记录，提交一次查询后自动保存在这里。</div>';
      return;
    }
    box.innerHTML = '';
    data.records.forEach(r => {
      let req = {};
      try { req = JSON.parse(r.request); } catch (e) {}
      const brands = req.brands && req.brands.length ? req.brands.join(' / ') : '不限';
      const div = document.createElement('div');
      div.className = 'record-item';
      const desc = document.createElement('div');
      desc.innerHTML = `<div>${esc(req.category || '')}｜品牌：${esc(brands)}｜${esc(req.budget || '')}｜${esc(req.usage || '')}</div><div class="rmeta">${esc(r.created_at)}</div>`;
      const actions = document.createElement('div');
      actions.style.display = 'flex'; actions.style.gap = '6px';
      const view = document.createElement('button');
      view.className = 'btn btn-ghost btn-sm';
      view.textContent = '查看';
      view.addEventListener('click', () => viewAdvisorRecord(JSON.parse(r.result || '{}')));
      const del = document.createElement('button');
      del.className = 'btn btn-danger btn-sm';
      del.textContent = '删除';
      del.addEventListener('click', async () => {
        await api(`/api/advisor/records/${r.id}`, { method: 'DELETE' });
        loadAdvisorRecords();
      });
      actions.append(view, del);
      div.append(desc, actions);
      box.appendChild(div);
    });
  } catch (e) { box.innerHTML = '<div class="empty">读取记录失败</div>'; }
}

function viewAdvisorRecord(result) {
  renderRecommendations(result);
  document.getElementById('advResult').scrollIntoView({ behavior: 'smooth' });
}

function renderRecommendations(result) {
  const box = document.getElementById('advResult');
  box.hidden = false;
  document.getElementById('advTitle').textContent = result.title || '推荐结果';

  // 预算不足 / 平替说明
  const noticeEl = document.getElementById('advNotice');
  if (result.notice && String(result.notice).trim()) {
    noticeEl.textContent = String(result.notice);
    noticeEl.hidden = false;
  } else {
    noticeEl.textContent = '';
    noticeEl.hidden = true;
  }

  const wrap = document.getElementById('advItems');
  wrap.innerHTML = '';

  const recs = result.recommendations || [];
  if (!recs.length) {
    wrap.innerHTML = '<div class="empty">当前预算内暂无合适商品，请查看上方提示或调整预算。</div>';
  }
  recs.forEach(item => {
    const div = document.createElement('div');
    div.className = 'rec-item';
    div.innerHTML = `
      <div class="row">
        <span class="rec-name">${esc(item.name || '未命名')}</span>
        <span class="tag">${esc(item.price || '价格待核实')}</span>
      </div>
      <p><b>核心亮点：</b>${esc(item.core_highlights || '')}</p>
      <p><b>缺点：</b>${esc(item.disadvantages || '【暂无准确数据，仅供参考】')}</p>
      <p><b>适合人群：</b>${esc(item.target_users || '')}</p>
    `;
    wrap.appendChild(div);
  });

  document.getElementById('advSummary').textContent = result.summary || '';

  const lines = [result.title || ''];
  if (result.notice) lines.push('提示：' + result.notice);
  recs.forEach((it, i) => {
    lines.push(`${i + 1}. ${it.name}（${it.price}）`);
    lines.push(`   - 核心亮点：${it.core_highlights}`);
    lines.push(`   - 缺点：${it.disadvantages}`);
    lines.push(`   - 适合人群：${it.target_users}`);
  });
  lines.push('总结：' + (result.summary || ''));
  wrap.dataset.fullText = lines.join('\n');
}

document.addEventListener('DOMContentLoaded', () => {
  renderAdvisor();
  loadAdvisorRecords();
});
