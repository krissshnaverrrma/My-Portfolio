const BOT_IMG_PATH = "/static/assets/assistant/assistant.png";
const USER_IMG_PATH = "static/assets/assistant/user.png";
let isProcessing = false;

document.addEventListener("DOMContentLoaded", () => {
    const label = document.getElementById("status-label");
    const botIcon = document.getElementById("bot-status-icon");
    const dot = document.getElementById("status-dot");
    if (label) {
        label.innerText = "Connecting...";
        if (botIcon) botIcon.style.borderColor = "#666";
        if (dot) dot.className = "fas fa-circle";
    }
    setTimeout(() => {
        checkSystemStatus();
    }, 1500);
    const inputField = document.getElementById("user-input");
    if (inputField) {
        inputField.addEventListener("keydown", (e) => {
            if (e.key === "Enter" && !isProcessing) {
                handleSend();
            }
        });
    }
});

function updateBotUI(status) {
    const input = document.getElementById("user-input");
    const label = document.getElementById("status-label");
    const dot = document.getElementById("status-dot");
    const sendBtn = document.getElementById("send-btn");
    const micBtn = document.getElementById("mic-btn");
    const botIcon = document.getElementById("bot-status-icon");
    if (!input || !label) return;
    const baseDotClass = "fas fa-circle ";
    if (status === "cached_mode") {
        input.disabled = false;
        input.placeholder = "Cache Mode: Limited Responses";
        label.innerText = "Cached Mode";
        label.className = "text-info-cache";
        if (dot) dot.className = baseDotClass + "text-info-cache";
        if (botIcon) {
            botIcon.style.borderColor = "#f1c40f";
            botIcon.style.boxShadow = "0 0 20px rgba(241, 196, 15, 0.4)";
        }
        if (sendBtn) sendBtn.disabled = false;
        if (micBtn) micBtn.disabled = false;
    } else if (status && status.includes("online")) {
        input.disabled = false;
        input.placeholder = "Ask Me about Krishna";
        label.innerText = "Online";
        label.className = "text-success";
        if (dot) dot.className = baseDotClass + "text-success";
        if (botIcon) {
            botIcon.style.borderColor = "#2ecc71";
            botIcon.style.boxShadow = "0 0 20px rgba(46, 204, 113, 0.4)";
        }
        if (sendBtn) sendBtn.disabled = false;
        if (micBtn) micBtn.disabled = false;
    } else if (status === "database_mode" || status === "database") {
        input.disabled = false;
        input.placeholder = "Terminal Mode: Database Access";
        label.innerText = "Database Mode";
        label.className = "text-warning";
        if (dot) dot.className = baseDotClass + "text-warning";
        if (botIcon) {
            botIcon.style.borderColor = "#e67e22";
            botIcon.style.boxShadow = "0 0 20px rgba(230, 126, 34, 0.4)";
        }
        if (sendBtn) sendBtn.disabled = false;
        if (micBtn) micBtn.disabled = false;
    } else {
        input.disabled = true;
        input.placeholder = "⚠️ System Offline (Rate Limit/Error)";
        label.innerText = "Offline";
        label.className = "text-danger";
        if (dot) dot.className = baseDotClass + "text-danger";
        if (botIcon) {
            botIcon.style.borderColor = "#ff4d4d";
            botIcon.style.boxShadow = "0 0 20px rgba(255, 77, 77, 0.4)";
        }
        if (sendBtn) sendBtn.disabled = true;
        if (micBtn) micBtn.disabled = true;
    }
}

async function checkSystemStatus() {
    try {
        const res = await fetch("/get_status");
        if (!res.ok) throw new Error(`Status Error: ${res.status}`);
        const data = await res.json();
        updateBotUI(data.status);
        const body = document.getElementById("chat-body");
        if (body && body.children.length === 0) {
            showTyping();
            setTimeout(() => {
                hideTyping();
                addMessage("<b>Hello! I'm Krishna's Virtual AI Assistant.</b><br>Ask Me about his <b>Projects</b>, <b>Skills</b>, <b>Blog-Posts</b>, <b>Certifications</b> or <b>Contact Info</b>!", "bot");
            }, 1000);
        }
    } catch (e) {
        updateBotUI("offline");
        const body = document.getElementById("chat-body");
        if (body && body.children.length === 0) {
            addMessage("System is currently offline. Please reload.", "bot");
        }
    }
}

function addMessage(text, sender, isTypingIndicator = false) {
    const body = document.getElementById("chat-body");
    if (!body) return;
    const container = document.createElement("div");
    container.className = `message-container ${sender}-container`;
    if (isTypingIndicator) container.id = "typing-container";
    const avatar = document.createElement("img");
    avatar.src = sender === "bot" ? BOT_IMG_PATH : USER_IMG_PATH;
    avatar.className = "chat-avatar";
    avatar.alt = sender;
    const bubble = document.createElement("div");
    bubble.className = sender === "bot" ? "bot-message" : "user-message";
    if (isTypingIndicator) {
        bubble.innerHTML = `<span class="typing-text">Typing<span class="typing-dots"><span></span><span></span><span></span></span></span>`;
    } else {
        const safeText = String(text || "");
        let formatted = safeText.replace(/\*\*(.*?)\*\*/g, '<b>$1</b>').replace(/\n/g, '<br>');
        formatted = formatted.replace(
            /(\b(https?|ftp):\/\/[-A-Z0-9+&@#\/%?=~_|!:,.;]*[-A-Z0-9+&@#\/%=~_|])/gim,
            '<a href="$1" target="_blank" class="chat-link">$1</a>'
        );
        formatted = formatted.replace(
            /(^|[^\/])(www\.[-A-Z0-9+&@#\/%?=~_|!:,.;]*[-A-Z0-9+&@#\/%=~_|])/gim,
            '$1<a href="https://$2" target="_blank" class="chat-link">$2</a>'
        );
        bubble.innerHTML = formatted;
    }
    container.appendChild(avatar);
    container.appendChild(bubble);
    body.appendChild(container);
    body.scrollTop = body.scrollHeight;
}

function showTyping() {
    if (!document.getElementById("typing-container")) addMessage("", "bot", true);
}

function hideTyping() {
    const typing = document.getElementById("typing-container");
    if (typing) typing.remove();
}

function calculateTypingDelay(text) {
    const safeText = text || "";
    const base = 1000;
    const perChar = 30;
    const max = 4000;
    return Math.min(Math.max(safeText.length * perChar, base), max);
}

async function handleSend() {
    const input = document.getElementById("user-input");
    const text = input.value.trim();
    if (!text || isProcessing) return;
    addMessage(text, "user");
    input.value = "";
    isProcessing = true;
    showTyping();
    try {
        const response = await fetch("/get_response", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ message: text }),
        });
        if (!response.ok) throw new Error("Offline");
        const data = await response.json();
        const delay = calculateTypingDelay(data.response);
        setTimeout(() => {
            hideTyping();
            addMessage(data.response, "bot");
            updateBotUI(data.status);
            isProcessing = false;
            document.getElementById("user-input").focus();
        }, delay);
    } catch (e) {
        hideTyping();
        addMessage("⚠️ System Offline.", "bot");
        updateBotUI("offline");
        isProcessing = false;
        document.getElementById("user-input").focus();
    }
}

function toggleVoice() {
    const micBtn = document.getElementById("mic-btn");
    const input = document.getElementById("user-input");
    if (!('webkitSpeechRecognition' in window) && !('SpeechRecognition' in window)) {
        alert("Speech recognition not supported in this browser.");
        return;
    }
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    const recognition = new SpeechRecognition();
    recognition.lang = 'en-US';
    recognition.onstart = () => {
        micBtn.classList.add("mic-active");
        input.placeholder = "Listening...";
    };
    recognition.onend = () => {
        micBtn.classList.remove("mic-active");
        input.placeholder = "Processing...";
    };

    recognition.onresult = (e) => {
        input.value = e.results[0][0].transcript;
        handleSend();
    };

    recognition.start();
}