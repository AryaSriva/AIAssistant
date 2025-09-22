let isLoading = false;

// Load conversation history when page loads
window.addEventListener("load", loadHistory);

async function loadHistory() {
  try {
    const response = await fetch("/api/history");
    const data = await response.json();

    if (data.success) {
      const container = document.getElementById("messagesContainer");
      container.innerHTML =
        '<div class="typing-indicator" id="typingIndicator"><div class="typing-dots"><div class="typing-dot"></div><div class="typing-dot"></div><div class="typing-dot"></div></div><span style="margin-left: 10px; color: #666;">Assistant is typing...</span></div>';

      data.messages.forEach((message) => {
        addMessage(message.content, message.role);
      });
    }
  } catch (error) {
    console.error("Error loading history:", error);
  }
}

async function sendMessage() {
  const input = document.getElementById("messageInput");
  const message = input.value.trim();

  if (!message || isLoading) return;

  // Add user message to chat
  addMessage(message, "user");
  input.value = "";

  // Show loading state
  setLoading(true);

  try {
    const response = await fetch("/api/chat", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ message: message }),
    });

    const data = await response.json();

    if (data.success) {
      addMessage(data.response, "assistant");
    } else {
      showError(data.error || "An error occurred");
    }
  } catch (error) {
    showError("Network error. Please try again.");
    console.error("Error:", error);
  } finally {
    setLoading(false);
  }
}

function addMessage(content, role) {
  const container = document.getElementById("messagesContainer");
  const messageDiv = document.createElement("div");
  messageDiv.className = `message ${role}`;

  const contentDiv = document.createElement("div");
  contentDiv.className = "message-content";
  contentDiv.textContent = content;

  messageDiv.appendChild(contentDiv);

  // Insert before typing indicator
  const typingIndicator = document.getElementById("typingIndicator");
  container.insertBefore(messageDiv, typingIndicator);

  // Scroll to bottom
  container.scrollTop = container.scrollHeight;
}

function setLoading(loading) {
  isLoading = loading;
  const sendBtn = document.getElementById("sendBtn");
  const typingIndicator = document.getElementById("typingIndicator");
  const input = document.getElementById("messageInput");

  if (loading) {
    sendBtn.disabled = true;
    sendBtn.textContent = "Sending...";
    typingIndicator.style.display = "flex";
    input.disabled = true;
  } else {
    sendBtn.disabled = false;
    sendBtn.textContent = "Send";
    typingIndicator.style.display = "none";
    input.disabled = false;
    input.focus();
  }

  // Scroll to bottom
  const container = document.getElementById("messagesContainer");
  container.scrollTop = container.scrollHeight;
}

function showError(message) {
  const container = document.getElementById("messagesContainer");
  const errorDiv = document.createElement("div");
  errorDiv.className = "error-message";
  errorDiv.textContent = `Error: ${message}`;

  const typingIndicator = document.getElementById("typingIndicator");
  container.insertBefore(errorDiv, typingIndicator);

  // Remove error after 5 seconds
  setTimeout(() => {
    errorDiv.remove();
  }, 5000);
}

async function clearConversation() {
  if (!confirm("Are you sure you want to clear the conversation?")) return;

  try {
    const response = await fetch("/api/clear", {
      method: "POST",
    });

    const data = await response.json();

    if (data.success) {
      const container = document.getElementById("messagesContainer");
      container.innerHTML =
        '<div class="typing-indicator" id="typingIndicator"><div class="typing-dots"><div class="typing-dot"></div><div class="typing-dot"></div><div class="typing-dot"></div></div><span style="margin-left: 10px; color: #666;">Assistant is typing...</span></div>';
    } else {
      showError(data.error || "Failed to clear conversation");
    }
  } catch (error) {
    showError("Network error. Please try again.");
    console.error("Error:", error);
  }
}

function handleKeyPress(event) {
  if (event.key === "Enter" && !event.shiftKey) {
    event.preventDefault();
    sendMessage();
  }
}

// Focus input on page load
window.addEventListener("load", () => {
  document.getElementById("messageInput").focus();
});
