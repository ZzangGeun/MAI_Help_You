/**
 * Maple Story ChatBot - Chat Page JavaScript
 * 채팅 페이지 전용 기능들
 */

// Chat state management
let chatHistory = [];
let isTyping = false;

/**
 * Auto-resize textarea
 */
function autoResize() {
    const textarea = document.getElementById('mainChatInput');
    if (textarea) {
        textarea.style.height = 'auto';
        textarea.style.height = Math.min(textarea.scrollHeight, 100) + 'px';
    }
}

/**
 * Fill input with suggestion
 */
function fillInput(text) {
    const input = document.getElementById('mainChatInput');
    if (input) {
        input.value = text;
        input.focus();
        autoResize();
        
        // Enable send button
        const sendButton = document.getElementById('sendButton');
        if (sendButton) {
            sendButton.disabled = false;
        }
    }
}

/**
 * Add message to chat
 */
function addMessage(message, isUser = false) {
    const chatMessages = document.getElementById('chatMessages');
    const welcomeMessage = document.getElementById('welcomeMessage');
    
    if (!chatMessages) return;
    
    // Hide welcome message on first chat
    if (welcomeMessage && chatHistory.length === 0) {
        welcomeMessage.style.display = 'none';
    }
    
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${isUser ? 'user' : 'bot'}`;
    
    const avatar = document.createElement('div');
    avatar.className = 'message-avatar';
    avatar.textContent = isUser ? '👤' : '🧚‍♀️';
    
    const content = document.createElement('div');
    content.className = 'message-content';
    content.textContent = message;
    
    messageDiv.appendChild(avatar);
    messageDiv.appendChild(content);
    
    chatMessages.appendChild(messageDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
    
    // Animate message appearance
    window.MapleStoryChatBot.fadeIn(messageDiv, 300);
}

/**
 * Show typing indicator
 */
function showTypingIndicator() {
    const typingIndicator = document.getElementById('typingIndicator');
    const chatMessages = document.getElementById('chatMessages');
    
    if (typingIndicator && chatMessages) {
        typingIndicator.style.display = 'flex';
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }
}

/**
 * Hide typing indicator
 */
function hideTypingIndicator() {
    const typingIndicator = document.getElementById('typingIndicator');
    if (typingIndicator) {
        typingIndicator.style.display = 'none';
    }
}

/**
 * Get AI response based on user message
 */
async function getAIResponse(userMessage) {
    try {
        const response = await fetch(`${CONFIG.API_BASE_URL}/chatbot/ask/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ message: userMessage })
        });
        const data = await response.json();
        if (data.success) {
            return data.response;
        } else {
            return "죄송하지만, AI 응답을 가져오는 데 실패했습니다. 다시 시도해주세요. 😥";
        }
    } catch (error) {
        console.error('Error fetching AI response:', error);
        return "네트워크 오류로 AI 응답을 가져올 수 없습니다. 인터넷 연결을 확인해주세요. 🌐";
    }
}

/**
 * Simulate AI response
 */
async function simulateResponse(userMessage) {
    if (isTyping) return;
    
    isTyping = true;
    showTypingIndicator();
    
    const responseDelay = 1000 + Math.random() * 2000; // 1-3 seconds
    
    setTimeout(async () => {
        hideTypingIndicator();
        
        const response = await getAIResponse(userMessage);
        addMessage(response, false);
        
        // Save to chat history only if logged in
        const loginData = window.MapleStoryChatBot.loadFromStorage('loginState');
        if (loginData && loginData.isLoggedIn) {
            chatHistory.push(
                { type: 'user', message: userMessage, timestamp: new Date() },
                { type: 'bot', message: response, timestamp: new Date() }
            );
            
            // Save to localStorage
            window.MapleStoryChatBot.saveToStorage('chatHistory', chatHistory);
            
            // Update sidebar history display
            updateChatHistoryDisplay();
            
            // Show notification for first message
            if (chatHistory.length === 2) {
                window.MapleStoryChatBot.showNotification('채팅이 시작되었습니다! 🎉', 'success');
            }
        } else {
            // Show login reminder for non-logged-in users
            if (!isTyping && chatHistory.length === 0) {
                setTimeout(() => {
                    window.MapleStoryChatBot.showNotification('로그인하시면 채팅 기록이 저장됩니다.', 'info', 4000);
                }, 2000);
            }
        }
        
        isTyping = false;
    }, responseDelay);
}

/**
 * Send message
 */
async function sendMainMessage() {
    const input = document.getElementById('mainChatInput');
    const message = input.value.trim();
    const sendButton = document.getElementById('sendButton');
    
    if (!message || isTyping) return;
    
    // Add user message
    addMessage(message, true);
    
    // Clear input
    input.value = '';
    autoResize();
    
    // Disable send button temporarily
    if (sendButton) {
        sendButton.disabled = true;
    }
    
    // Simulate AI response
    await simulateResponse(message);
    
    // Re-enable send button after response
    if (sendButton) {
        sendButton.disabled = false;
    }
}

/**
 * Handle input events
 */
async function handleInput(event) {
    const input = event.target;
    const sendButton = document.getElementById('sendButton');
    
    // Auto resize
    autoResize();
    
    // Enable/disable send button
    if (sendButton) {
        sendButton.disabled = input.value.trim() === '' || isTyping;
    }
    
    // Handle Enter key
    if (event.key === 'Enter' && !event.shiftKey) {
        event.preventDefault();
        await sendMainMessage();
    }
}

/**
 * Scroll to chat area
 */
function scrollToChat() {
    const chatMain = document.querySelector('.chat-main');
    if (chatMain) {
        window.MapleStoryChatBot.smoothScrollTo(chatMain, 100);
    }
}

/**
 * Load previous chat history (only if logged in)
 */
function loadChatHistory() {
    // Check if user is logged in
    const loginData = window.MapleStoryChatBot.loadFromStorage('loginState');
    if (!loginData || !loginData.isLoggedIn) {
        chatHistory = [];
        return;
    }
    
    const savedHistory = window.MapleStoryChatBot.loadFromStorage('chatHistory', []);
    if (savedHistory.length > 0) {
        chatHistory = savedHistory;
        
        // Show last few messages
        const recentMessages = chatHistory.slice(-6); // Last 6 messages
        
        if (recentMessages.length > 0) {
            const welcomeMessage = document.getElementById('welcomeMessage');
            if (welcomeMessage) {
                welcomeMessage.style.display = 'none';
            }
            
            recentMessages.forEach(msg => {
                addMessage(msg.message, msg.type === 'user');
            });
        }
        
        // Update chat history display in sidebar
        updateChatHistoryDisplay();
    }
}

/**
 * Update chat history display in sidebar
 */
function updateChatHistoryDisplay() {
    const chatHistoryContent = document.getElementById('chatHistoryContent');
    if (!chatHistoryContent || chatHistory.length === 0) return;
    
    // Get recent conversations (last 6 exchanges)
    const recentHistory = chatHistory.slice(-6);
    const conversations = [];
    
    for (let i = 0; i < recentHistory.length; i += 2) {
        if (recentHistory[i] && recentHistory[i].type === 'user') {
            const userMessage = recentHistory[i];
            const botMessage = recentHistory[i + 1];
            
            const timeAgo = getTimeAgo(new Date(userMessage.timestamp));
            conversations.push({
                date: timeAgo,
                text: userMessage.message.length > 50 ? 
                      userMessage.message.substring(0, 47) + '...' : 
                      userMessage.message
            });
        }
    }
    
    // Update HTML
    chatHistoryContent.innerHTML = '';
    conversations.reverse().forEach((conv, index) => {
        const historyItem = document.createElement('div');
        historyItem.className = 'history-item';
        historyItem.innerHTML = `
            <div class="history-date">${conv.date}</div>
            <div class="history-text">${conv.text}</div>
        `;
        chatHistoryContent.appendChild(historyItem);
    });
}

/**
 * Get time ago string
 */
function getTimeAgo(date) {
    const now = new Date();
    const diffTime = Math.abs(now - date);
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
    
    if (diffDays === 1) return '최근';
    if (diffDays < 7) return `${diffDays}일전`;
    if (diffDays < 30) return `${Math.floor(diffDays / 7)}주전`;
    return `${Math.floor(diffDays / 30)}개월전`;
}

/**
 * Clear chat history
 */
function clearChatHistory() {
    if (confirm('채팅 기록을 모두 삭제하시겠습니까?')) {
        chatHistory = [];
        window.MapleStoryChatBot.saveToStorage('chatHistory', []);
        
        const chatMessages = document.getElementById('chatMessages');
        const welcomeMessage = document.getElementById('welcomeMessage');
        
        if (chatMessages) {
            // Remove all messages except welcome and typing indicator
            const messages = chatMessages.querySelectorAll('.message:not(#typingIndicator)');
            messages.forEach(msg => msg.remove());
        }
        
        if (welcomeMessage) {
            welcomeMessage.style.display = 'flex';
        }
        
        // Clear history display
        updateChatHistoryDisplay();
        
        window.MapleStoryChatBot.showNotification('채팅 기록이 삭제되었습니다.', 'info');
    }
}

/**
 * Handle pending search query from home page
 */
async function handlePendingQuery() {
    const pendingQuery = sessionStorage.getItem('pendingChatQuery');
    if (pendingQuery) {
        // Clear the stored query
        sessionStorage.removeItem('pendingChatQuery');
        
        // Show notification
        window.MapleStoryChatBot.showNotification(`"${pendingQuery}"에 대해 질문드릴게요!`, 'info', 2000);
        
        // Fill input and focus
        setTimeout(async () => {
            const input = document.getElementById('mainChatInput');
            if (input) {
                fillInput(pendingQuery);
                
                // Auto-send after a short delay for better UX
                setTimeout(async () => {
                    await sendMainMessage();
                }, 1000);
            }
        }, 500);
    }
}

/**
 * Initialize chat page
 */
function initializeChatPage() {
    // Set active navigation
    window.MapleStoryChatBot.setActiveNavItem('CHAT BOT');
    
    // Setup input handlers
    const mainInput = document.getElementById('mainChatInput');
    const sendButton = document.getElementById('sendButton');
    
    if (mainInput) {
        mainInput.addEventListener('input', handleInput);
        mainInput.addEventListener('keydown', handleInput);
        
        // Initial state
        if (sendButton) {
            sendButton.disabled = true;
        }
    }

    // Suggestion button clicks
    document.querySelectorAll('.suggestion-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            this.style.transform = 'scale(0.95)';
            setTimeout(() => {
                this.style.transform = 'scale(1)';
            }, 150);
        });
    });
    
    // Load previous chat history
    loadChatHistory();
    
    // Handle pending query from home page search
    handlePendingQuery();
    
    // Add context menu for clearing history
    document.querySelector('.nav-profile-btn')?.addEventListener('click', () => {
        window.MapleStoryChatBot.showProfilePopup();
    });
    const chatMessages = document.getElementById('chatMessages');
    if (chatMessages) {
        chatMessages.addEventListener('contextmenu', function(e) {
            e.preventDefault();
            if (chatHistory.length > 0) {
                clearChatHistory();
            }
        });
    }
}
