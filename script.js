// static/script.js
document.addEventListener("DOMContentLoaded", () => {
    // Configuration elements
    const apiKeyInput = document.getElementById("api-key");
    const urlInput = document.getElementById("website-url");
    const maxPagesInput = document.getElementById("max-pages");
    const scrapeButton = document.getElementById("scrape-button");
    const scrapeStatus = document.getElementById("scrape-status");

    // Chat elements
    const chatHistory = document.getElementById("chat-history");
    const chatInput = document.getElementById("chat-input");
    const sendButton = document.getElementById("send-button");

    // --- Scrape Button Logic ---
    scrapeButton.addEventListener("click", async () => {
        const apiKey = apiKeyInput.value.trim();
        const url = urlInput.value.trim();
        const maxPages = maxPagesInput.value;

        if (!apiKey || !url) {
            showStatus("API Key and Website URL are required.", "error");
            return;
        }

        // Show loading status
        showStatus("Scraping website... This may take a moment.", "loading");
        scrapeButton.disabled = true;

        try {
            const response = await fetch("/scrape", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({
                    api_key: apiKey,
                    url: url,
                    max_pages: maxPages,
                }),
            });

            const data = await response.json();

            if (!response.ok) {
                showStatus(data.error || "An unknown error occurred.", "error");
            } else {
                showStatus(`✅ Scraped ${data.pages_scraped} pages successfully!`, "success");
                // Enable chat
                chatInput.disabled = false;
                sendButton.disabled = false;
                addMessageToChat("assistant", "Website content is loaded. You can now ask questions!");
            }
        } catch (error) {
            showStatus(`An error occurred: ${error.message}`, "error");
        } finally {
            scrapeButton.disabled = false;
        }
    });

    // --- Chat Logic ---
    sendButton.addEventListener("click", handleSendMessage);
    chatInput.addEventListener("keydown", (e) => {
        if (e.key === "Enter" && !e.shiftKey) {
            e.preventDefault();
            handleSendMessage();
        }
    });

    async function handleSendMessage() {
        const query = chatInput.value.trim();
        if (!query) return;

        // Add user message to chat
        addMessageToChat("user", query);
        chatInput.value = "";
        
        // Add loading message for assistant
        const loadingMessageId = "loading-" + Date.now();
        addMessageToChat("assistant", "...", loadingMessageId);
        
        try {
            const response = await fetch("/chat", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({ query: query }),
            });

            const data = await response.json();
            
            if (!response.ok) {
                updateMessage(loadingMessageId, data.error || "Error getting response.");
            } else {
                // Update loading message with actual response
                updateMessage(loadingMessageId, data.response, data.sources);
            }

        } catch (error) {
             updateMessage(loadingMessageId, `An error occurred: ${error.message}`);
        }
    }

    // --- Helper Functions ---

    function showStatus(message, type) {
        scrapeStatus.textContent = message;
        scrapeStatus.className = `status-message ${type}`;
    }

    function addMessageToChat(role, text, id = null) {
        const messageDiv = document.createElement("div");
        messageDiv.className = `message ${role}`;
        if (id) {
            messageDiv.id = id;
        }
        
        const p = document.createElement("p");
        p.textContent = text;
        messageDiv.appendChild(p);
        
        chatHistory.appendChild(messageDiv);
        scrollToBottom();
    }

    function updateMessage(id, newText, sources = null) {
        const messageDiv = document.getElementById(id);
        if (!messageDiv) return;

        const p = messageDiv.querySelector("p");
        p.textContent = newText; // Using textContent to avoid XSS

        if (sources && sources.length > 0) {
            const sourcesDiv = document.createElement("div");
            sourcesDiv.className = "sources";
            sourcesDiv.innerHTML = "<h4>📚 Sources</h4>";

            const details = document.createElement("details");
            const summary = document.createElement("summary");
            summary.textContent = `View ${sources.length} relevant source(s)`;
            details.appendChild(summary);

            sources.forEach((source, index) => {
                const sourceItem = document.createElement("div");
                sourceItem.innerHTML = `
                    <strong>${index + 1}. ${source.title}</strong><br>
                    <small>Relevance: ${source.score.toFixed(2)} | <a href="${source.url}" target="_blank">Link</a></small>
                    <code>${source.content}</code>
                `;
                details.appendChild(sourceItem);
            });

            sourcesDiv.appendChild(details);
            messageDiv.appendChild(sourcesDiv);
        }
        
        scrollToBottom();
    }

    function scrollToBottom() {
        chatHistory.scrollTop = chatHistory.scrollHeight;
    }
});