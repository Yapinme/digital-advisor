/**
 * compare.js —— 模块2：参数对比
 * 输入两款产品 -> 后端生成固定格式 Markdown 表格 + 总结 -> 前端渲染 + 可保存记录。
 */
let lastCompareResult = null;
let lastCompareReq = null;

async function renderCompare() {
  const form = document.getElementById('compareForm');
  const btn = document.getElementById('btnCompare');
  const saveBtn = document.getElementById('btnSaveCompare');

  form.addEventListener('submit', async (e) => {
    e.preventDefault();
    const a = document.getElementById('compareA').value.trim();
    const b = document.getElementById('compareB').value.trim();
    const notes = document.getElementById('compareNotes').value.trim();

    if (!a || !b) { showToast('请填写两款产品的型号', 'error'); return; }

    btn.disabled = true;
    btn.textContent = '对比中…';
    try {
      const data = await api('/api/compare', { method: 'POST', body: { a, b, notes } });
      lastCompareResult = data.result;
      lastCompareReq = { a, b };
      renderCompareResult(data.result);
      saveBtn.hidden = false;
    } catch (err) {
      showToast(err.message, 'error');
    } finally {
      btn.disabled = false;
      btn.textContent = '开始对比';
    }
  });

  saveBtn.addEventListener('click', async () => {
    if (!lastCompareResult || !lastCompareReq) return;
    try {
      await api('/api/compare/save', {
        method: 'POST',
        body: { a: lastCompareReq.a, b: lastCompareReq.b, result: lastCompareResult },
      });
      showToast('对比记录已保存到 D 盘数据库');
      saveBtn.hidden = true;
      loadCompareRecords();
    } catch (e) { showToast(e.message, 'error'); }
  });

  const clearBtn = document.getElementById('btnClearCompareRecords');
  if (clearBtn) {
    clearBtn.addEventListener('click', async () => {
      if (!confirm('确定要清空全部对比记录吗？')) return;
      try {
        await api('/api/compare/records/clear', { method: 'DELETE' });
        await loadCompareRecords();
        showToast('已清空全部对比记录');
      } catch (e) { showToast(e.message, 'error'); }
    });
  }
}

function renderCompareResult(result) {
  const box = document.getElementById('compareResult');
  box.hidden = false;

  const cols = result.columns || [];
  const rows = result.rows || [];
  const md = result.markdown || '';

  let html = '<div class="result-head"><h2>对比结果</h2>';
  html += '<button class="btn btn-ghost btn-sm" id="btnCopyCompare">一键复制</button></div>';

  if (cols.length) {
    html += '<table><thead><tr>';
    cols.forEach(c => { html += `<th>${esc(c)}</th>`; });
    html += '</tr></thead><tbody>';
    rows.forEach(r => {
      html += '<tr>';
      cols.forEach((_, i) => { html += `<td>${esc(r[i] || '')}</td>`; });
      html += '</tr>';
    });
    html += '</tbody></table>';
  } else {
    html += '<div class="empty">未能解析为统一对比表格，请重试或检查型号写法。</div>';
  }

  html += `<div class="summary">${esc(result.summary || '')}</div>`;
  box.innerHTML = html;

  document.getElementById('btnCopyCompare').addEventListener('click', () => copyText((md || '').replace(/\*\*/g, '') || sqliteFallbackText(result)));
}

function sqliteFallbackText(result) {
  // 备用复制文本：行列拼接
  const cols = result.columns || [];
  const rows = result.rows || [];
  let s = '对比结果\n';
  s += cols.join(' | ') + '\n';
  rows.forEach(r => { s += r.join(' | ') + '\n'; });
  s += '\n总结：' + (result.summary || '');
  return s;
}

async function loadCompareRecords() {
  const box = document.getElementById('compareRecords');
  try {
    const data = await api('/api/compare/records');
    if (!data.records || data.records.length === 0) {
      box.innerHTML = '<div class="empty">暂无保存的对比记录。</div>';
      return;
    }
    box.innerHTML = '';
    data.records.forEach(r => {
      let req = {};
      try { req = JSON.parse(r.request); } catch (e) {}
      const div = document.createElement('div');
      div.className = 'record-item';
      const main = document.createElement('div');
      main.innerHTML = `<div>${esc(req.a || '')}  vs  ${esc(req.b || '')}</div><div class="rmeta">${esc(r.created_at)}</div>`;
      const actions = document.createElement('div');
      actions.style.display = 'flex'; actions.style.gap = '6px';
      const view = document.createElement('button');
      view.className = 'btn btn-ghost btn-sm';
      view.textContent = '查看';
      view.addEventListener('click', () => viewCompareRecord(JSON.parse(r.result || '{}')));
      const del = document.createElement('button');
      del.className = 'btn btn-danger btn-sm';
      del.textContent = '删除';
      del.addEventListener('click', async () => {
        await api(`/api/compare/records/${r.id}`, { method: 'DELETE' });
        loadCompareRecords();
      });
      actions.append(view, del);
      div.append(main, actions);
      box.appendChild(div);
    });
  } catch (e) { box.innerHTML = '<div class="empty">读取记录失败</div>'; }
}

function viewCompareRecord(result) {
  renderCompareResult(result);
  document.getElementById('compareResult').scrollIntoView({ behavior: 'smooth' });
  document.getElementById('btnSaveCompare').hidden = true;
}

document.addEventListener('DOMContentLoaded', () => {
  renderCompare();
  loadCompareRecords();
});
