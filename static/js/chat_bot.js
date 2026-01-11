let isFirstOpen = true;

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
    setTimeout(() => {
      chatWindow.classList.add('active');
    }, 50);

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
    const data = await res.json();
    document.getElementById(tid).remove();
    appendMsg(data.response, 'bot-message');
  } catch (e) {
    if (document.getElementById(tid)) document.getElementById(tid).remove();
    appendMsg("⚠️ Error: Couldn't reach the bot.", 'bot-message');
  }
}

function appendMsg(text, cls, id = null) {
  const body = document.getElementById('chat-body');
  const d = document.createElement('div');
  d.className = cls;
  if (id) d.id = id;
  d.innerHTML = text;
  body.appendChild(d);
  body.scrollTop = body.scrollHeight;
}

function handleEnter(event) {
  if (event.key === 'Enter') sendMessage();
}