let isFirstOpen = true;

function setBotOnline() {
  const input = document.getElementById('user-input');
  const statusDot = document.getElementById('status-dot');
  const statusLabel = id = "status-label";
  const sendBtn = document.querySelector('.chat-input-area button');

  if (input) {
    input.placeholder = "Ask me anything...";
    input.disabled = false;
  }
  if (sendBtn) sendBtn.disabled = false;

  if (statusDot) statusDot.style.color = "#2ecc71";
  if (document.getElementById('status-label')) {
    document.getElementById('status-label').innerHTML = "Online";
    document.getElementById('status-label').className = "text-success";
  }
}

function setBotOffline() {
  const input = document.getElementById('user-input');
  const statusDot = document.getElementById('status-dot');
  const sendBtn = document.querySelector('.chat-input-area button');

  if (input) {
    input.placeholder = "currently sleeping";
    input.disabled = true;
  }
  if (sendBtn) sendBtn.disabled = true;

  if (statusDot) statusDot.style.color = "#ff4d4d";
  if (document.getElementById('status-label')) {
    document.getElementById('status-label').innerHTML = "Offline";
    document.getElementById('status-label').className = "text-danger";
  }
}

function toggleChat() {
  const chatWindow = document.getElementById('chat-window');
  const chatIcon = document.querySelector('.chat-icon-btn');
  if (!chatWindow || !chatIcon) return;

  if (chatWindow.classList.contains('active')) {
    chatWindow.classList.remove('active');
    setTimeout(() => {
      chatWindow.style.display = 'none';
      chatIcon.classList.remove('hidden');
    }, 400);
  } else {
    chatIcon.classList.add('hidden');
    chatWindow.style.display = 'flex';
    setTimeout(() => { chatWindow.classList.add('active'); }, 50);
    if (isFirstOpen) {
      handleInitialGreeting();
      isFirstOpen = false;
    }
  }
}

function handleInitialGreeting() {
  const typing = document.getElementById('typing-indicator');
  const greeting = document.getElementById('greeting-message');
  if (typing && greeting) {
    typing.style.display = 'flex';
    greeting.style.display = 'none';
    setTimeout(() => {
      typing.style.display = 'none';
      greeting.style.display = 'block';
    }, 2000);
  }
}

async function sendMessage() {
  const input = document.getElementById('user-input');
  const text = input.value.trim();
  if (!text) return;

  appendMsg(text, 'user-message');
  input.value = '';

  const tid = 't-' + Date.now();
  appendMsg(`<div class="typing-wrapper">Typing <div class="typing-dots"><span></span><span></span><span></span></div></div>`, 'bot-message', tid);

  try {
    const res = await fetch('/get_response', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message: text })
    });

    if (!res.ok) throw new Error('Offline');

    const data = await res.json();
    document.getElementById(tid).remove();
    appendMsg(data.response, 'bot-message');
    setBotOnline();
  } catch (e) {
    if (document.getElementById(tid)) document.getElementById(tid).remove();

    appendMsg("currently sleeping", 'bot-message');
    setBotOffline();
  }
}

function appendMsg(text, cls, id = null) {
  const body = document.getElementById('chat-body');
  const div = document.createElement('div');
  div.className = cls;
  if (id) div.id = id;
  div.innerHTML = text;
  body.appendChild(div);
  body.scrollTop = body.scrollHeight;
}

function handleEnter(e) { if (e.key === 'Enter') sendMessage(); }