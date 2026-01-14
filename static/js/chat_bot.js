document.addEventListener("DOMContentLoaded", () => {
    let isFirstOpen = true;
    const chatContainer = document.getElementById("chat-widget-container");
    const chatWindow = document.getElementById("chat-window");
    const chatIcon = document.getElementById("chat-icon-btn");
    const closeBtn = document.querySelector(".btn-close-x");
    if (!chatContainer || !chatWindow || !chatIcon) return;
    chatContainer.addEventListener("mouseenter", () => openChat());
    chatIcon.addEventListener("click", () => openChat());
    if (closeBtn) {
        closeBtn.addEventListener("click", (e) => {
            e.stopPropagation();
            closeChat();
        });
    }

    function openChat() {
        if (chatWindow.classList.contains("active")) return;
        chatWindow.classList.add("active");
        chatIcon.classList.add("active-hidden");
        if (isFirstOpen) {
            isFirstOpen = false;
            const typingId = "dynamic-typing-indicator";
            appendMsg(
                `Typing...<span class="typing-dots" style="margin-left: 4px;"><span></span><span></span><span></span></span>`,
                "bot-message",
                typingId
            );
            setTimeout(() => {
                const typingElem = document.getElementById(typingId);
                if (typingElem) typingElem.remove();

                appendMsg(
                    "<b>Hello! I'm Krishna's Virtual AI Assistant.</b><br>Ask Me about his <b>Projects</b>, <b>Skills</b>, <b>Blog-Posts</b>, <b>Certifications</b> or <b>Contact Info</b>!",
                    "bot-message"
                );
            }, 1500);
        }
    }

    function closeChat() {
        chatWindow.classList.remove("active");
        chatIcon.classList.remove("active-hidden");
    }
    window.closeChatManual = function(e) {
        if (e) e.stopPropagation();
        closeChat();
    };
});

function updateBotUI(status) {
    const input = document.getElementById("user-input");
    const dot = document.getElementById("status-dot");
    const label = document.getElementById("status-label");
    const sendBtn = document.querySelector(".chat-input-area button");
    if (!input || !dot || !label) return;
    if (status === "online") {
        input.disabled = false;
        input.placeholder = "Ask Me about Krishna...";
        input.style.opacity = "1";
        label.innerText = "Online";
        label.className = "text-success";
        dot.style.color = "#2ecc71";
        if (sendBtn) sendBtn.disabled = false;
    } else if (status === "database_mode") {
        input.disabled = false;
        input.placeholder = "Terminal Mode: Asking Database...";
        input.style.opacity = "1";
        label.innerText = "Data-Base Mode";
        label.className = "text-warning";
        dot.style.color = "#f39c12";
        if (sendBtn) sendBtn.disabled = false;
    } else {
        input.disabled = true;
        input.placeholder = "⚠️ System Offline. Try Again Later.";
        input.style.opacity = "0.6";
        label.innerText = "Offline";
        label.className = "text-danger";
        dot.style.color = "#ff4d4d";
        if (sendBtn) sendBtn.disabled = true;
    }
}
async function sendMessage() {
    const input = document.getElementById("user-input");
    if (!input) return;
    const text = input.value.trim();
    if (!text) return;
    appendMsg(text, "user-message");
    input.value = "";
    const tid = "typing-" + Date.now();
    appendMsg(
        `Typing...<span class="typing-dots" style="margin-left: 4px;"><span></span><span></span><span></span></span>`,
        "bot-message",
        tid
    );
    try {
        const res = await fetch("/get_response", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ message: text }),
        });
        if (!res.ok) throw new Error("Offline");
        const data = await res.json();
        const typingElem = document.getElementById(tid);
        if (typingElem) typingElem.remove();
        appendMsg(data.response, "bot-message");
        updateBotUI(data.status || "online");
    } catch (e) {
        const typingElem = document.getElementById(tid);
        if (typingElem) typingElem.remove();
        appendMsg("⚠️ System Offline.", "bot-message");
        updateBotUI("offline");
    }
}

function appendMsg(text, className, id = null) {
    const body = document.getElementById("chat-body");
    if (!body) return;
    const div = document.createElement("div");
    div.className = className;
    if (id) div.id = id;
    div.innerHTML = text;
    body.appendChild(div);
    body.scrollTop = body.scrollHeight;
}

function handleEnter(e) {
    if (e.key === "Enter") sendMessage();
}