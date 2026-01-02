/* Chat widget */

    function toggleChat() {
      const bubbleEl = document.querySelector(".chat-bubble");
      const chatWindowEl = document.getElementById("chatWindow");

      bubbleEl.classList.toggle("active");
      chatWindowEl.classList.toggle("active");

      if (chatWindowEl.classList.contains("active")) {
        document.getElementById("chatInput").focus();
      }
    }

    function setContext(symbol) {
      chatContext = symbol;
      document.getElementById("contextStock").textContent = symbol;
      document.getElementById("contextBadge").classList.add("show");
    }

    function clearContext() {
      chatContext = null;
      document.getElementById("contextBadge").classList.remove("show");
    }

    function addChatMessage(content, isUser = false) {
      const messagesContainer = document.getElementById("chatMessages");

      const messageDiv = document.createElement("div");
      messageDiv.className = `chat-message ${isUser ? "user-message" : "ai-message"}`;

      messageDiv.innerHTML = `
        <div class="message-avatar">${isUser ? `<i data-lucide="user"></i>` : `<i data-lucide="bot"></i>`}</div>
        <div class="message-content"></div>
      `;
      messageDiv.querySelector(".message-content").textContent = content;

      // Insert before typing indicator
      const typing = document.getElementById("typingIndicator");
      messagesContainer.insertBefore(messageDiv, typing);

      messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }

    function showTypingIndicator() {
      document.getElementById("typingIndicator").classList.add("show");
      const messagesContainer = document.getElementById("chatMessages");
      messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }

    function hideTypingIndicator() {
      document.getElementById("typingIndicator").classList.remove("show");
    }

    async function sendMessage() {
      const input = document.getElementById("chatInput");
      const message = input.value.trim();

      if (!message) return;

      addChatMessage(message, true);
      input.value = "";
      showTypingIndicator();

      try {
        const response = await fetch(`${API}/chat`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ message, context: chatContext }),
        });

        const data = await response.json();
        hideTypingIndicator();

        if (data.success) addChatMessage(data.response || "");
        else addChatMessage("Sorry, I'm having trouble right now. Could you try again?");
      } catch (error) {
        hideTypingIndicator();
        addChatMessage("Oops! I couldn't connect. Make sure your server is running.");
      }
    }

