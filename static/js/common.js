/**
 * common.js —— 全局公共脚本
 * 包含：请求封装、Toast、HTML 转义、一键复制、
 *       登录/注册/游客模式、设置弹窗（仅登录用户）。
 */
let authState = { logged_in: false, mode: 'guest', user: null };

// ---------- 请求封装 ----------
async function api(path, options = {}) {
  const opts = Object.assign({ headers: { 'Content-Type': 'application/json' } }, options);
  if (options.body && typeof options.body !== 'string') {
    opts.body = JSON.stringify(options.body);
  }
  const resp = await fetch(path, opts);
  let data = {};
  try { data = await resp.json(); } catch (e) { data = {}; }
  if (!resp.ok || data.ok === false) {
    throw new Error(data.error || data.message || '请求失败，请重试');
  }
  return data;
}

// ---------- Toast 提示 ----------
function showToast(msg, type = 'info') {
  let el = document.getElementById('toast');
  if (!el) {
    el = document.createElement('div');
    el.id = 'toast';
    document.body.appendChild(el);
  }
  el.textContent = msg;
  el.classList.add('show');
  el.style.background = type === 'error' ? '#b91c1c' : '#111827';
  setTimeout(() => el.classList.remove('show'), 2200);
}

// ---------- HTML 转义 ----------
function esc(str) {
  return String(str == null ? '' : str)
    .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;').replace(/'/g, '&#39;');
}

// ---------- 复制 ----------
async function copyText(text) {
  try {
    await navigator.clipboard.writeText(text);
    showToast('已复制到剪贴板');
  } catch (e) {
    const ta = document.createElement('textarea');
    ta.value = text;
    document.body.appendChild(ta);
    ta.select();
    document.execCommand('copy');
    ta.remove();
    showToast('已复制到剪贴板');
  }
}

function copyButton(text, label = '一键复制') {
  const btn = document.createElement('button');
  btn.className = 'btn btn-ghost btn-sm';
  btn.textContent = label;
  btn.addEventListener('click', () => copyText(text));
  return btn;
}

// ---------- 登录 / 注册 / 游客模式 ----------
function renderUserArea() {
  const area = document.getElementById('userArea');
  if (!area) return;
  area.innerHTML = '';

  // 用户名（或 游客模式）超链接，点击进入个人中心
  const profileLink = document.createElement('a');
  profileLink.className = 'user-link';
  profileLink.href = '/profile';
  profileLink.textContent = authState.logged_in ? (authState.user ? authState.user.username : '已登录') : '游客模式';
  profileLink.title = '进入个人中心';
  area.appendChild(profileLink);

  if (authState.logged_in) {
    const settingsBtn = document.createElement('button');
    settingsBtn.className = 'btn btn-ghost btn-sm';
    settingsBtn.textContent = '⚙ 设置';
    settingsBtn.addEventListener('click', () => {
      document.getElementById('settingsModal').hidden = false;
      loadSettingsIntoForm();
    });

    const logoutBtn = document.createElement('button');
    logoutBtn.className = 'btn btn-ghost btn-sm';
    logoutBtn.textContent = '退出';
    logoutBtn.addEventListener('click', async () => {
      try { await api('/api/auth/logout', { method: 'POST', body: {} }); } catch (e) {}
      authState = { logged_in: false, mode: 'guest' };
      renderUserArea();
      showToast('已退出登录');
    });

    area.append(settingsBtn, logoutBtn);
  } else {
    const loginBtn = document.createElement('button');
    loginBtn.className = 'btn btn-primary btn-sm';
    loginBtn.textContent = '登录';
    loginBtn.addEventListener('click', () => openLoginModal('login'));

    area.append(loginBtn);
  }
}

function openLoginModal(mode) {
  document.getElementById('loginModal').hidden = false;
  setLoginMode(mode);
}

function setLoginMode(mode) {
  const isLogin = mode === 'login';
  document.getElementById('btnLogin').textContent = isLogin ? '登录' : '注册';
  document.getElementById('btnToggleMode').textContent = isLogin ? '注册账号' : '已有账号？去登录';
  document.getElementById('loginTitle').textContent = isLogin ? '账号登录' : '注册账号';
  document.getElementById('confirmRow').hidden = isLogin;
  document.getElementById('loginMsg').textContent = '';
  document.getElementById('loginModal').dataset.mode = mode;
}

function setAuthMsg(text, ok = false) {
  const el = document.getElementById('loginMsg');
  el.textContent = text || '';
  el.className = 'auth-msg' + (ok ? ' ok' : '');
}

async function initAuth() {
  renderUserArea();
  try {
    const data = await api('/api/auth/me');
    authState = { logged_in: data.logged_in, mode: data.mode, user: data.user };
  } catch (e) {
    authState = { logged_in: false, mode: 'guest', user: null };
  }
  renderUserArea();
}

function initAuthEvents() {
  const modal = document.getElementById('loginModal');
  if (!modal) return;

  document.getElementById('btnToggleMode').addEventListener('click', () => {
    const isLogin = modal.dataset.mode !== 'login';
    setLoginMode(isLogin ? 'login' : 'register');
  });

  // 游客模式：不登录直接关闭弹窗，正常使用 AI 助手
  document.getElementById('btnGuest').addEventListener('click', () => {
    modal.hidden = true;
    authState = { logged_in: false, mode: 'guest', user: null };
    renderUserArea();
    showToast('游客模式：可直接使用 AI 助手');
  });

  document.getElementById('btnLogin').addEventListener('click', async () => {
    const mode = modal.dataset.mode || 'login';
    const username = document.getElementById('login_username').value.trim();
    const password = document.getElementById('login_password').value;
    if (!username || !password) { setAuthMsg('请输入账号和密码'); return; }

    if (mode === 'register') {
      const confirm = document.getElementById('login_confirm').value;
      if (password !== confirm) { setAuthMsg('两次输入的密码不一致'); return; }
      try {
        await api('/api/auth/register', { method: 'POST', body: { username, password, confirm } });
        setAuthMsg('注册成功，请直接登录', true);
        setLoginMode('login');
        return;
      } catch (e) { setAuthMsg(e.message); return; }
    }

    try {
      const data = await api('/api/auth/login', { method: 'POST', body: { username, password } });
      authState = { logged_in: true, mode: 'user', user: data.user };
      modal.hidden = true;
      document.getElementById('login_username').value = '';
      document.getElementById('login_password').value = '';
      renderUserArea();
      showToast('登录成功');
    } catch (e) {
      setAuthMsg(e.message);
    }
  });

  // 点击遮罩空白处可关闭登录弹窗
  modal.addEventListener('click', (e) => {
    if (e.target === modal) modal.hidden = true;
  });
}

// ---------- 设置弹窗（仅登录用户可打开，后端也做了登录校验）----------
async function loadSettingsIntoForm() {
  try {
    const data = await api('/api/settings');
    const s = data.settings;
    document.getElementById('cfg_api_key').placeholder = s.has_api_key ? '已配置（留空保持不变）' : 'sk-...';
    document.getElementById('cfg_base_url').value = s.base_url || '';
    document.getElementById('cfg_model').value = s.model || '';
    document.getElementById('cfg_temperature').value = s.temperature || 0.7;
  } catch (e) {
    showToast(e.message, 'error');
    document.getElementById('settingsModal').hidden = true;
  }
}

function initSettings() {
  const mask = document.getElementById('settingsModal');
  const closeBtn = document.getElementById('closeSettings');
  const saveBtn = document.getElementById('saveSettings');
  if (!mask) return;

  closeBtn.addEventListener('click', () => { mask.hidden = true; });

  saveBtn.addEventListener('click', async () => {
    const body = {
      api_key: document.getElementById('cfg_api_key').value.trim(),
      base_url: document.getElementById('cfg_base_url').value.trim(),
      model: document.getElementById('cfg_model').value.trim(),
      temperature: parseFloat(document.getElementById('cfg_temperature').value) || 0.7,
    };
    try {
      await api('/api/settings', { method: 'POST', body });
      showToast('设置已保存到 D 盘');
      document.getElementById('cfg_api_key').value = '';
      mask.hidden = true;
    } catch (e) { showToast(e.message, 'error'); }
  });

  mask.addEventListener('click', (e) => {
    if (e.target === mask) mask.hidden = true;
  });
}

// ---------- 深色模式 ----------
function applyTheme(theme) {
  const dark = theme === 'dark';
  document.documentElement.classList.toggle('dark-theme', dark);
  const btn = document.getElementById('darkModeToggle');
  if (btn) btn.textContent = dark ? '☀️' : '🌙';
}

function initTheme() {
  const saved = localStorage.getItem('digital-advisor-theme');
  applyTheme(saved === 'dark' ? 'dark' : 'light');
  const btn = document.getElementById('darkModeToggle');
  if (btn) {
    btn.addEventListener('click', () => {
      const next = document.documentElement.classList.contains('dark-theme') ? 'light' : 'dark';
      localStorage.setItem('digital-advisor-theme', next);
      applyTheme(next);
      showToast(next === 'dark' ? '已切换到深色模式' : '已切换到浅色模式');
    });
  }
}

document.addEventListener('DOMContentLoaded', () => {
  initTheme();
  initAuthEvents();
  initSettings();
  initAuth();
});
