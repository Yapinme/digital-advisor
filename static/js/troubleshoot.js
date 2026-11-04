/**
 * troubleshoot.js —— 模块3：故障 AI 问诊助手（对话式）
 * 前端维护会话历史，每次把完整消息发给后端，后端只返回“下一步”指导意见。
 */
const chat = {
  messages: [],   // [{role:'user'|'assistant', content}]
};

function renderChat() {
  const box = document.getElementById('chatBox');
  box.innerHTML = '';
  if (chat.messages.length === 0) {
    const welcome = document.createElement('div');
    welcome.className = 'bubble bot-bubble';
    welcome.textContent = '你好，我是数码故障问诊助手。请描述你遇到的设备故障，或点击下方常见问题快速提问：';
    box.appendChild(welcome);

    const QUICK_FAULTS = ['手机充不进电', '笔记本连不上 Wi-Fi', '显示已保存但一直要密码', '键盘按键失灵'];
    const chips = document.createElement('div');
    chips.className = 'quick-chips';
    QUICK_FAULTS.forEach(fault => {
      const chip = document.createElement('button');
      chip.type = 'button';
      chip.className = 'chip';
      chip.textContent = fault;
      chip.addEventListener('click', () => sendMessage(fault));
      chips.appendChild(chip);
    });
    box.appendChild(chips);
    return;
  }
  chat.messages.forEach(m => {
    const div = document.createElement('div');
    div.className = 'bubble ' + (m.role === 'user' ? 'user-bubble' : 'bot-bubble');
    div.textContent = m.content;
    box.appendChild(div);
  });
  box.scrollTop = box.scrollHeight;
}

function addCopyBubble(text) {
  const box = document.getElementById('chatBox');
  const row = document.createElement('div');
  row.style.cssText = 'text-align:right;margin-top:-4px';
  row.appendChild(copyButton(text, '复制该回答'));
  box.appendChild(row);
  box.scrollTop = box.scrollHeight;
}

async function sendMessage(faultText) {
  const input = document.getElementById('chatInput');
  const text = faultText != null ? faultText.trim() : input.value.trim();
  if (!text) { showToast('请先描述你的故障情况', 'error'); return; }

  chat.messages.push({ role: 'user', content: text });
  if (faultText == null) input.value = '';
  renderChat();

  const btn = document.getElementById('btnSend');
  btn.disabled = true;
  btn.textContent = '思考中…';
  try {
    const data = await api('/api/troubleshoot', { method: 'POST', body: { messages: chat.messages } });
    const reply = (data.reply || '').replace(/\*\*/g, '');
    chat.messages.push({ role: 'assistant', content: reply });
    renderChat();
    addCopyBubble(reply);
  } catch (e) {
    showToast(e.message, 'error');
  } finally {
    btn.disabled = false;
    btn.textContent = '发送';
  }
}

function initChat() {
  document.getElementById('btnSend').addEventListener('click', sendMessage);
  document.getElementById('chatInput').addEventListener('keydown', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  });
  document.getElementById('btnNewChat').addEventListener('click', () => {
    chat.messages = [];
    renderChat();
    showToast('已开启新对话');
  });
  renderChat();
}

document.addEventListener('DOMContentLoaded', initChat);
