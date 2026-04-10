const messageList = document.getElementById("messageList");
const chatForm = document.getElementById("chatForm");
const messageInput = document.getElementById("messageInput");
const sendButton = document.getElementById("sendButton");
const threadIdInput = document.getElementById("threadIdInput");
const newThreadButton = document.getElementById("newThreadButton");
const statusBadge = document.getElementById("statusBadge");
const messageTemplate = document.getElementById("messageTemplate");

const state = {
  loading: false,
  threadId: loadThreadId(),
};

threadIdInput.value = state.threadId;

renderMessage(
  "assistant",
  "Hello! This basic UI is ready. Send a message and it will call your FastAPI /chat route through the local UI server."
);

chatForm.addEventListener("submit", async (event) => {
  event.preventDefault();

  if (state.loading) {
    return;
  }

  const message = messageInput.value.trim();

  if (!message) {
    return;
  }

  const threadId = threadIdInput.value.trim() || createThreadId();
  updateThreadId(threadId);

  renderMessage("user", message);
  messageInput.value = "";
  autoResizeTextarea();
  setLoading(true, "Thinking");

  try {
    const response = await fetch("/api/chat", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        message,
        threadId,
      }),
    });

    const payload = await response.json();

    if (!response.ok) {
      throw new Error(payload.error || "The backend request failed.");
    }

    renderMessage("assistant", payload.response || "No response received.");
    setLoading(false, "Connected");
  } catch (error) {
    renderMessage(
      "assistant",
      `Request failed: ${error.message}. Make sure FastAPI is running on the backend URL configured in ui/server.py.`
    );
    setLoading(false, "Error");
  }
});

messageInput.addEventListener("input", autoResizeTextarea);
threadIdInput.addEventListener("change", () => {
  const nextThreadId = threadIdInput.value.trim() || createThreadId();
  updateThreadId(nextThreadId);
});

newThreadButton.addEventListener("click", () => {
  const nextThreadId = createThreadId();
  updateThreadId(nextThreadId);
  messageList.innerHTML = "";
  renderMessage(
    "assistant",
    "Started a fresh thread. Your next message will be sent with the new thread ID."
  );
  setLoading(false, "Idle");
});

messageInput.addEventListener("keydown", (event) => {
  if (event.key === "Enter" && !event.shiftKey) {
    event.preventDefault();
    chatForm.requestSubmit();
  }
});

autoResizeTextarea();

function renderMessage(role, content) {
  const fragment = messageTemplate.content.cloneNode(true);
  const article = fragment.querySelector(".message");
  const roleLabel = fragment.querySelector(".message-role");
  const messageContent = fragment.querySelector(".message-content");

  article.classList.add(role);
  roleLabel.textContent = role === "user" ? "You" : "Assistant";
  messageContent.textContent = content;

  messageList.appendChild(fragment);
  messageList.scrollTop = messageList.scrollHeight;
}

function setLoading(isLoading, label) {
  state.loading = isLoading;
  sendButton.disabled = isLoading;
  newThreadButton.disabled = isLoading;
  threadIdInput.disabled = isLoading;
  messageInput.disabled = isLoading;
  statusBadge.textContent = label;

  if (!isLoading) {
    messageInput.focus();
  }
}

function updateThreadId(threadId) {
  state.threadId = threadId;
  threadIdInput.value = threadId;
  localStorage.setItem("personal-ai-thread-id", threadId);
}

function loadThreadId() {
  return localStorage.getItem("personal-ai-thread-id") || createThreadId();
}

function createThreadId() {
  if (window.crypto && typeof window.crypto.randomUUID === "function") {
    return window.crypto.randomUUID();
  }

  return `thread-${Date.now()}`;
}

function autoResizeTextarea() {
  messageInput.style.height = "auto";
  messageInput.style.height = `${Math.min(messageInput.scrollHeight, 220)}px`;
}
