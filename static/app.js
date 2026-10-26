const log = document.getElementById("log");
const form = document.getElementById("composer");
const input = document.getElementById("message");
const send = document.getElementById("send");
const status = document.getElementById("status");
const newChat = document.getElementById("new-chat");

let conversationId = localStorage.getItem("bytebaazConversationId");

function addBubble(role, text) {
  const bubble = document.createElement("div");
  bubble.className = `bubble ${role}`;
  const who = document.createElement("span");
  who.className = "who";
  who.textContent = role === "user" ? "You" : role === "error" ? "Error" : "ByteBaaz";
  bubble.append(who, document.createTextNode(text));
  log.append(bubble);
  log.scrollTop = log.scrollHeight;
}

function setBusy(busy) {
  send.disabled = busy;
  input.disabled = busy;
}

function showStatus(message) {
  if (!message) {
    status.hidden = true;
    status.textContent = "";
    return;
  }
  status.hidden = false;
  status.textContent = message;
}

if (!log.childElementCount) {
  addBubble(
    "bot",
    "Namaste. I am ByteBaaz. Tell me your name, what you are studying, and one thing you want to remember across this chat."
  );
}

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  const message = input.value.trim();
  if (!message) return;

  addBubble("user", message);
  input.value = "";
  setBusy(true);
  showStatus("");

  try {
    const response = await fetch("/api/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message, conversation_id: conversationId }),
    });
    const payload = await response.json().catch(() => ({}));
    if (!response.ok) {
      const detail = payload.detail || "The server could not complete this reply.";
      addBubble("error", detail);
      showStatus(detail);
      return;
    }
    conversationId = payload.conversation_id;
    localStorage.setItem("bytebaazConversationId", conversationId);
    addBubble("bot", payload.reply);
  } catch (error) {
    const detail =
      "Could not reach the chatbot server. Make sure it is running, then try again.";
    addBubble("error", detail);
    showStatus(detail);
  } finally {
    setBusy(false);
    input.focus();
  }
});

newChat.addEventListener("click", () => {
  conversationId = null;
  localStorage.removeItem("bytebaazConversationId");
  log.replaceChildren();
  showStatus("");
  addBubble("bot", "Fresh chat started. What should I remember this time?");
  input.focus();
});

input.addEventListener("keydown", (event) => {
  if (event.key === "Enter" && !event.shiftKey) {
    event.preventDefault();
    form.requestSubmit();
  }
});
