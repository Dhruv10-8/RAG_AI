const chatBox = document.getElementById('chat-box');
const userInput = document.getElementById('user-input');
const sendBtn = document.getElementById('send-btn');

const API_URL = 'http://127.0.0.1:8000/ask'; // ✅ FastAPI endpoint

function addMessage(text, type) {
  const messageDiv = document.createElement('div');
  messageDiv.className = `message ${type}`;
  messageDiv.innerHTML = type === 'bot' ? marked.parse(text) : text;
  chatBox.appendChild(messageDiv);
  chatBox.scrollTo({ top: chatBox.scrollHeight, behavior: 'smooth' });
}

function addLoadingMessage() {
  const loadingDiv = document.createElement('div');
  loadingDiv.className = 'loading';
  loadingDiv.id = 'loading-message';
  loadingDiv.textContent = '🏏 Fetching IPL data...';
  chatBox.appendChild(loadingDiv);
  chatBox.scrollTo({ top: chatBox.scrollHeight, behavior: 'smooth' });
}

function removeLoadingMessage() {
  const loadingMsg = document.getElementById('loading-message');
  if (loadingMsg) loadingMsg.remove();
}

async function sendMessage() {
  const message = userInput.value.trim();
  if (!message) return;

  addMessage(message, 'user');
  userInput.value = '';
  sendBtn.disabled = true;
  addLoadingMessage();

  try {
    const res = await fetch(API_URL, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ question: message }),
    });

    if (!res.ok) throw new Error('Network response was not ok');

    const data = await res.json();
    removeLoadingMessage();
    addMessage(data.answer || 'Sorry, I could not find that information.', 'bot');
  } catch (err) {
    console.error(err);
    removeLoadingMessage();
    const errorDiv = document.createElement('div');
    errorDiv.className = 'error';
    errorDiv.textContent = '⚠️ Error connecting to server. Please try again.';
    chatBox.appendChild(errorDiv);
    chatBox.scrollTo({ top: chatBox.scrollHeight, behavior: 'smooth' });
  } finally {
    sendBtn.disabled = false;
    userInput.focus();
  }
}

sendBtn.addEventListener('click', sendMessage);
userInput.addEventListener('keypress', (e) => {
  if (e.key === 'Enter') sendMessage();
});

userInput.focus();
