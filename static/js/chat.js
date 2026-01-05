document.addEventListener('DOMContentLoaded', () => {
    const chatFab = document.getElementById('chat-fab');
    const chatWindow = document.getElementById('chat-window');
    const closeBtn = document.getElementById('chat-close');
    const sendBtn = document.getElementById('chat-send');
    const chatInput = document.getElementById('chat-input');
    const messages = document.getElementById('chat-messages');

    if (!chatFab) return; // Not on a page with chat

    // Toggle Chat Window
    chatFab.addEventListener('click', () => {
        chatWindow.style.display = chatWindow.style.display === 'flex' ? 'none' : 'flex';
        if (chatWindow.style.display === 'flex') {
            chatInput.focus();
            if (messages.children.length === 0) {
                appendMessage("Hi! I'm your Data Analyst AI. accessing your latest dataset. Ask me anything!", 'bot');
            }
        }
    });

    closeBtn.addEventListener('click', () => {
        chatWindow.style.display = 'none';
    });

    // Send Message Logic
    function sendMessage() {
        const text = chatInput.value.trim();
        if (!text) return;

        appendMessage(text, 'user');
        chatInput.value = '';

        // Show loading state
        const loadingId = appendMessage("Thinking...", 'bot', true);

        // API Call with Streaming
        fetch('/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ question: text })
        })
            .then(async res => {
                if (!res.ok) {
                    if (res.status === 401) throw new Error("Your session has expired. Please log in again.");
                    throw new Error("Server error occurred.");
                }

                // Remove "Thinking..." and prepare bot message bubble
                removeMessage(loadingId);
                const botMsgId = 'bot-' + Date.now();
                appendMessage("", 'bot', false, botMsgId);
                const botMsgDiv = document.getElementById(botMsgId);

                const reader = res.body.getReader();
                const decoder = new TextDecoder();

                while (true) {
                    const { done, value } = await reader.read();
                    if (done) break;

                    const chunk = decoder.decode(value, { stream: true });
                    botMsgDiv.textContent += chunk;
                    messages.scrollTop = messages.scrollHeight;
                }
            })
            .catch(err => {
                removeMessage(loadingId);
                appendMessage("Sorry, " + err.message, 'bot');
            });
    }

    sendBtn.addEventListener('click', sendMessage);
    chatInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') sendMessage();
    });

    function appendMessage(text, sender, isLoading = false, id = null) {
        const div = document.createElement('div');
        div.className = `message ${sender}`;
        div.textContent = text;
        if (isLoading) div.id = 'loading-msg';
        if (id) div.id = id;

        messages.appendChild(div);
        const currentId = div.id;
        messages.scrollTop = messages.scrollHeight;
        return currentId;
    }

    function removeMessage(id) {
        const el = document.getElementById(id);
        if (el) el.remove();
    }
});
