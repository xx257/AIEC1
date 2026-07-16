// Frontend for the chat skeleton: sends messages to /api/chat and renders both
// sides of the conversation. No framework — plain DOM APIs.

const messagesEl = document.getElementById("messages");
const formEl = document.getElementById("composer");
const inputEl = document.getElementById("input");
const sendEl = document.getElementById("send");

// One conversation id per page load. Sent with every request so the backend
// can associate messages once it grows real memory/history.
const conversationId = crypto.randomUUID();

/** Append a message bubble and scroll to the bottom. Returns the element. */
function addMessage(text, role) {
  const el = document.createElement("div");
  el.className = `message message--${role}`;
  el.textContent = text;
  messagesEl.appendChild(el);
  messagesEl.scrollTop = messagesEl.scrollHeight;
  return el;
}

function setBusy(busy) {
  inputEl.disabled = busy;
  sendEl.disabled = busy;
  if (!busy) inputEl.focus();
}

/** Stream the agent's reply, showing each tool call as it happens. */
function sendMessage(message) {
  addMessage(message, "user");
  const pending = addMessage("Thinking…", "assistant");
  pending.classList.add("message--pending");
  setBusy(true);

  const url =
    "/api/chat/stream?message=" +
    encodeURIComponent(message) +
    "&conversation_id=" +
    encodeURIComponent(conversationId);
  const source = new EventSource(url);

  const finish = (text, className) => {
    source.close();
    pending.className = className;
    pending.textContent = text;
    messagesEl.scrollTop = messagesEl.scrollHeight;
    setBusy(false);
  };

  source.onmessage = (event) => {
    const data = JSON.parse(event.data);
    if (data.type === "tool") {
      // Progress: show what the agent is doing right now, in place.
      pending.textContent = `${data.label}…`;
      pending.classList.add("message--tool");
    } else if (data.type === "done") {
      finish(data.reply, "message message--assistant");
    } else if (data.type === "error") {
      finish(data.reply, "message message--error");
    }
  };

  // Fires on a dropped connection; a clean close after "done" already returned.
  source.onerror = () => {
    if (source.readyState === EventSource.CLOSED) return;
    finish("Error: lost connection to the server.", "message message--error");
  };
}

formEl.addEventListener("submit", (event) => {
  event.preventDefault();
  const message = inputEl.value.trim();
  if (!message) return;
  inputEl.value = "";
  sendMessage(message);
});

inputEl.focus();
