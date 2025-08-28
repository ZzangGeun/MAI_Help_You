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
function getAIResponse(userMessage) {
    const message = userMessage.toLowerCase();
    
    // Enhanced keyword responses
    if (message.includes('메르세데스')) {
        return "🏹 **메르세데스 정보**\n\n메르세데스는 궁수 계열 직업으로, 높은 기동성과 아름다운 스킬 이펙트가 특징입니다!\n\n**4차 스킬:**\n• 이슈타르의 링 - 주력 공격 스킬\n• 스피릿 인퓨전 - 데미지 증가\n• 고급 퀴버 - 화살 자동 충전\n• 레전드리 스피어 - 강력한 관통 공격\n\n**특징:**\n• 화려한 스킬 연계\n• 높은 기동성\n• 아름다운 이펙트\n\n궁수 직업 중에서도 가장 우아한 직업이에요! ✨";
    }
    
    if (message.includes('사냥터')) {
        return "🗺️ **180레벨 신궁 추천 사냥터**\n\n**아케인리버 지역:**\n• 츄츄 아일랜드 - 코코넛 해변 ⭐⭐⭐⭐⭐\n• 츄츄 아일랜드 - 슬라임 언덕 ⭐⭐⭐⭐\n• 꿈의 도시 레헬른 - 꿈의 숲 ⭐⭐⭐⭐\n\n**기타 추천 지역:**\n• 라헬 - 사막 지역 ⭐⭐⭐\n• 루디브리엄 - 시계탑 상층부 ⭐⭐⭐\n\n**💡 팁:**\n경험치 효율과 메소 수급을 고려했을 때 츄츄 아일랜드를 강력 추천드려요! 아케인 심볼도 함께 얻을 수 있어서 일석이조랍니다! 🎯";
    }
    
    if (message.includes('뇌전')) {
        return "⚡ **뇌전 드랍 정보**\n\n뇌전은 고급 장비로, 다음 보스들에게서 드랍됩니다:\n\n**주요 드랍 보스:**\n• 자쿠무 (노말/카오스) - 높은 확률 ⭐⭐⭐⭐⭐\n• 혼테일 (노말/카오스) - 중간 확률 ⭐⭐⭐⭐\n• 피아누스 - 중간 확률 ⭐⭐⭐\n• 블러디 퀸 - 낮은 확률 ⭐⭐\n\n**드랍률 정보:**\n• 자쿠무에서 가장 높은 확률\n• 카오스 버전에서 더 높은 드랍률\n• 일일 보스 처치 시 누적 확률 증가\n\n**💡 꿀팁:**\n매일 자쿠무를 처치하면서 운을 시험해보세요! 보통 1-2주 내에는 얻을 수 있어요! 🎲";
    }
    
    if (message.includes('보스')) {
        return "👹 **레벨대별 추천 보스 가이드**\n\n**초보자 (120-150레벨):**\n• 자쿠무 (노말) - 경험치 ⭐⭐⭐\n• 혼테일 (노말) - 경험치 ⭐⭐⭐⭐\n• 매그너스 (이지) - 장비 ⭐⭐⭐\n\n**중급자 (150-200레벨):**\n• 피아누스 - 장비/메소 ⭐⭐⭐⭐\n• 반반 - 경험치 ⭐⭐⭐⭐\n• 카오스 자쿠무 - 장비 ⭐⭐⭐⭐\n\n**고급자 (200레벨 이상):**\n• 카오스 혼테일 - 고급 장비 ⭐⭐⭐⭐⭐\n• 하드 매그너스 - 최고급 장비 ⭐⭐⭐⭐⭐\n• 시그너스 - 스킬북/장비 ⭐⭐⭐⭐\n\n**⚠️ 주의사항:**\n본인의 레벨과 장비 수준에 맞는 보스를 선택하세요! 무리하면 오히려 효율이 떨어져요! 💪";
    }
    
    if (message.includes('치장') || message.includes('핑크')) {
        return "💗 **핑크색 치장 아이템 컬렉션**\n\n**헤어 스타일:**\n• 핑크 트윈테일 - 귀여운 매력 ✨\n• 러블리 핑크 헤어 - 달콤한 느낌 🍭\n• 분홍 포니테일 - 상큼한 스타일 🌸\n\n**얼굴 장식:**\n• 핑크 하트 안경 - 사랑스러운 포인트 💕\n• 러블리 블러셔 - 볼터치 효과 😊\n• 분홍 리본 - 깜찍한 액세서리 🎀\n\n**전신 의상:**\n• 핑크 원피스 세트 - 우아한 드레스 👗\n• 러블리 핑크 교복 - 학생 스타일 📚\n• 분홍 파티 드레스 - 화려한 파티룩 🎉\n\n**💡 구매 팁:**\n캐시샵에서 세트로 구매하면 더 저렴해요! 이벤트 기간을 노려보세요! ✨";
    }
    
    if (message.includes('파편')) {
        return "💥 **뒤엉킨 파편 원킬 공격력 가이드**\n\n**메르세데스 기준:**\n\n**필요 스탯:**\n• 최소 공격력: 약 50만\n• 권장 공격력: 70만 이상\n• 크리티컬 확률: 80% 이상\n• 크리티컬 데미지: 200% 이상\n\n**추천 스킬:**\n• 이슈타르의 링 (풀차지)\n• 스피릿 인퓨전 + 고급 퀴버\n• 레인보우 아치 연계\n\n**장비 세팅:**\n• 무기: 17성 이상 활\n• 방어구: 15성 이상 세트\n• 장신구: 고급 펜던트/반지\n\n**💡 실전 팁:**\n버프 스킬을 모두 사용한 후 이슈타르의 링 풀차지로 공격하면 높은 확률로 원킬 가능해요! 🎯";
    }
    
    if (message.includes('스킬')) {
        return "🎯 **스킬 관련 정보**\n\n어떤 직업의 스킬이 궁금하신가요?\n\n**인기 직업들:**\n• 메르세데스 - 궁수 계열\n• 듀얼블레이드 - 도적 계열  \n• 아란 - 전사 계열\n• 에반 - 마법사 계열\n• 제로 - 특수 계열\n\n구체적인 직업명을 말씀해주시면 더 자세한 스킬 정보를 알려드릴게요! ✨";
    }
    
    if (message.includes('안녕') || message.includes('하이') || message.includes('hello')) {
        return "안녕하세요! 👋 메이플스토리 정령이에요!\n\n저는 메이플스토리의 모든 정보를 알고 있답니다!\n\n**제가 도움드릴 수 있는 것들:**\n• 스킬 정보 및 가이드 🎯\n• 사냥터 추천 🗺️\n• 보스 공략법 ⚔️\n• 장비 정보 🛡️\n• 아이템 드랍 정보 💎\n\n궁금한 것이 있으시면 언제든 물어보세요! 😊";
    }
    
    // Default response
    return "안녕하세요! 🧚‍♀️ 메이플스토리 정령이에요!\n\n죄송하지만 해당 내용에 대한 정보를 찾지 못했어요. 😅\n\n**이런 것들을 물어보세요:**\n• \"메르세데스 스킬 알려줘\"\n• \"180렙 사냥터 추천해줘\"\n• \"뇌전 어디서 나와?\"\n• \"보스 추천해줘\"\n• \"핑크 치장 아이템 보여줘\"\n\n더 구체적으로 질문해주시면 정확한 답변을 드릴 수 있어요! ✨";
}

/**
 * Simulate AI response
 */
function simulateResponse(userMessage) {
    if (isTyping) return;
    
    isTyping = true;
    showTypingIndicator();
    
    const responseDelay = 1000 + Math.random() * 2000; // 1-3 seconds
    
    setTimeout(() => {
        hideTypingIndicator();
        
        const response = getAIResponse(userMessage);
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
function sendMainMessage() {
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
    simulateResponse(message);
    
    // Re-enable send button after response
    setTimeout(() => {
        if (sendButton) {
            sendButton.disabled = false;
        }
    }, 3000);
}

/**
 * Handle input events
 */
function handleInput(event) {
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
        sendMainMessage();
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
function handlePendingQuery() {
    const pendingQuery = sessionStorage.getItem('pendingChatQuery');
    if (pendingQuery) {
        // Clear the stored query
        sessionStorage.removeItem('pendingChatQuery');
        
        // Show notification
        window.MapleStoryChatBot.showNotification(`"${pendingQuery}"에 대해 질문드릴게요!`, 'info', 2000);
        
        // Fill input and focus
        setTimeout(() => {
            const input = document.getElementById('mainChatInput');
            if (input) {
                fillInput(pendingQuery);
                
                // Auto-send after a short delay for better UX
                setTimeout(() => {
                    sendMainMessage();
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

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', initializeChatPage);

// Export functions for global use
window.ChatPage = {
    sendMainMessage,
    fillInput,
    scrollToChat,
    clearChatHistory,
    addMessage,
    simulateResponse
};