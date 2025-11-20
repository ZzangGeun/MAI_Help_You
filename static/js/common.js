/**
 * Maple Story ChatBot - Common JavaScript
 * 공통 JavaScript 기능들
 */

// Global configuration
const CONFIG = {
    ANIMATION_DURATION: 300,
    DEBOUNCE_DELAY: 500,
    API_BASE_URL: '/api', // 추후 API 연동시 사용
};

/**
 * Navigation related functions
 */
function setActiveNavItem(pageName) {
    document.querySelectorAll('.nav-item').forEach(item => {
        item.classList.remove('active');
        if (item.textContent.trim() === pageName) {
            item.classList.add('active');
        }
    });
}

/**
 * Search functionality
 */
function initializeSearch() {
    const searchInput = document.querySelector('.search-input');
    const searchBtn = document.querySelector('.search-btn');
    
    if (!searchInput || !searchBtn) return;

    let searchTimeout;

    // Debounced search
    searchInput.addEventListener('input', function(e) {
        clearTimeout(searchTimeout);
        searchTimeout = setTimeout(() => {
            performSearch(e.target.value);
        }, CONFIG.DEBOUNCE_DELAY);
    });

    // Search on button click
    searchBtn.addEventListener('click', function() {
        performSearch(searchInput.value);
    });

    // Search on Enter key
    searchInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            performSearch(e.target.value);
        }
    });
}

function performSearch(query) {
    if (!query.trim()) return;
    
    // Check if we're on the home page
    const isHomePage = window.location.pathname === '/' || 
                       window.location.pathname === '' ||
                       document.title.includes('MAI -');
    
    if (isHomePage) {
        // Redirect to chat page with query
        redirectToChatWithQuery(query);
    } else {
        // If already on chat page, just fill the input
        const chatInput = document.getElementById('mainChatInput');
        if (chatInput && window.ChatPage) {
            window.ChatPage.fillInput(query);
            showNotification(`"${query}"를 채팅창에 입력했습니다.`, 'success');
        } else {
            redirectToChatWithQuery(query);
        }
    }
}

function redirectToChatWithQuery(query) {
    // Save query to sessionStorage for the chat page to pick up
    sessionStorage.setItem('pendingChatQuery', query);
    
    // Show loading
    showLoading('ChatBot 페이지로 이동중...');
    
    // Redirect after a short delay for better UX
    setTimeout(() => {
        window.location.href = 'chatbot_page.html';
    }, 500);
}

/**
 * Notification system
 */
function showNotification(message, type = 'info', duration = 3000) {
    // Remove existing notifications
    const existing = document.querySelector('.notification');
    if (existing) {
        existing.remove();
    }

    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.textContent = message;
    
    // Styles
    Object.assign(notification.style, {
        position: 'fixed',
        top: '20px',
        right: '20px',
        padding: '12px 20px',
        borderRadius: '8px',
        color: 'white',
        fontFamily: 'Pretendard, sans-serif',
        fontSize: '14px',
        fontWeight: '500',
        zIndex: '10000',
        boxShadow: '0 4px 15px rgba(0,0,0,0.2)',
        transition: 'all 0.3s ease',
        transform: 'translateX(100%)',
        opacity: '0'
    });

    // Type-specific colors
    const colors = {
        info: '#3498db',
        success: '#2ecc71',
        warning: '#f39c12',
        error: '#e74c3c'
    };
    notification.style.background = colors[type] || colors.info;

    document.body.appendChild(notification);

    // Animate in
    setTimeout(() => {
        notification.style.transform = 'translateX(0)';
        notification.style.opacity = '1';
    }, 10);

    // Animate out
    setTimeout(() => {
        notification.style.transform = 'translateX(100%)';
        notification.style.opacity = '0';
        setTimeout(() => {
            if (notification.parentNode) {
                notification.remove();
            }
        }, 300);
    }, duration);
}

/**
 * Smooth scrolling utility
 */
function smoothScrollTo(element, offset = 0) {
    if (typeof element === 'string') {
        element = document.querySelector(element);
    }
    
    if (!element) return;

    const elementPosition = element.offsetTop - offset;
    const startPosition = window.pageYOffset;
    const distance = elementPosition - startPosition;
    const duration = 800;
    let start = null;

    function animation(currentTime) {
        if (start === null) start = currentTime;
        const timeElapsed = currentTime - start;
        const run = ease(timeElapsed, startPosition, distance, duration);
        window.scrollTo(0, run);
        if (timeElapsed < duration) requestAnimationFrame(animation);
    }

    function ease(t, b, c, d) {
        t /= d / 2;
        if (t < 1) return c / 2 * t * t + b;
        t--;
        return -c / 2 * (t * (t - 2) - 1) + b;
    }

    requestAnimationFrame(animation);
}

/**
 * Theme utilities
 */
function toggleTheme() {
    const body = document.body;
    const isDark = body.classList.contains('dark-theme');
    
    if (isDark) {
        body.classList.remove('dark-theme');
        localStorage.setItem('theme', 'light');
    } else {
        body.classList.add('dark-theme');
        localStorage.setItem('theme', 'dark');
    }
}

function initializeTheme() {
    const savedTheme = localStorage.getItem('theme');
    if (savedTheme === 'dark') {
        document.body.classList.add('dark-theme');
    }
}

/**
 * Loading utilities
 */
function showLoading(message = '로딩중...') {
    const existing = document.querySelector('.loading-overlay');
    if (existing) return;

    const overlay = document.createElement('div');
    overlay.className = 'loading-overlay';
    overlay.innerHTML = `
        <div class="loading-content">
            <div class="loading-spinner"></div>
            <div class="loading-text">${message}</div>
        </div>
    `;

    // Styles
    Object.assign(overlay.style, {
        position: 'fixed',
        top: '0',
        left: '0',
        width: '100%',
        height: '100%',
        background: 'rgba(0,0,0,0.5)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        zIndex: '10001',
        backdropFilter: 'blur(4px)'
    });

    const content = overlay.querySelector('.loading-content');
    Object.assign(content.style, {
        background: 'white',
        padding: '30px',
        borderRadius: '15px',
        textAlign: 'center',
        boxShadow: '0 10px 30px rgba(0,0,0,0.3)'
    });

    const spinner = overlay.querySelector('.loading-spinner');
    Object.assign(spinner.style, {
        width: '40px',
        height: '40px',
        border: '4px solid #f3f3f3',
        borderTop: '4px solid #e89611',
        borderRadius: '50%',
        margin: '0 auto 15px',
        animation: 'spin 1s linear infinite'
    });

    const text = overlay.querySelector('.loading-text');
    Object.assign(text.style, {
        fontFamily: 'Pretendard, sans-serif',
        fontSize: '16px',
        color: '#333'
    });

    // Add spinner animation
    const style = document.createElement('style');
    style.textContent = `
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
    `;
    document.head.appendChild(style);

    document.body.appendChild(overlay);
}

function hideLoading() {
    const overlay = document.querySelector('.loading-overlay');
    if (overlay) {
        overlay.style.opacity = '0';
        setTimeout(() => {
            if (overlay.parentNode) {
                overlay.remove();
            }
        }, 300);
    }
}

/**
 * Responsive utilities
 */
function isMobile() {
    return window.innerWidth <= 768;
}

function isTablet() {
    return window.innerWidth > 768 && window.innerWidth <= 1024;
}

function isDesktop() {
    return window.innerWidth > 1024;
}

/**
 * Local Storage utilities
 */
function saveToStorage(key, value) {
    try {
        localStorage.setItem(key, JSON.stringify(value));
        return true;
    } catch (e) {
        console.error('Failed to save to localStorage:', e);
        return false;
    }
}

function loadFromStorage(key, defaultValue = null) {
    try {
        const item = localStorage.getItem(key);
        return item ? JSON.parse(item) : defaultValue;
    } catch (e) {
        console.error('Failed to load from localStorage:', e);
        return defaultValue;
    }
}

/**
 * Login/Logout functionality
 */
function performLogin() {
    const username = document.getElementById('usernameInput').value.trim();
    const password = document.getElementById('passwordInput').value.trim();
    
    if (!username || !password) {
        showNotification('아이디와 비밀번호를 입력해주세요.', 'warning');
        return;
    }
    
    // Simple login simulation - in real app, this would be an API call
    if (username.length >= 2) {
        showLoading('로그인 중...');
        
        setTimeout(() => {
            // Save login state
            const loginData = {
                isLoggedIn: true,
                username: username,
                loginTime: new Date().toISOString()
            };
            saveToStorage('loginState', loginData);
            
            // Update UI
            updateLoginUI(loginData);
            hideLoading();
            showNotification(`${username}님, 환영합니다!`, 'success');
        }, 1000);
    } else {
        showNotification('올바른 아이디를 입력해주세요.', 'error');
    }
}

function performLogout() {
    showLoading('로그아웃 중...');
    
    setTimeout(() => {
        // Clear login state
        localStorage.removeItem('loginState');
        
        // Update UI
        updateLoginUI(null);
        hideLoading();
        showNotification('로그아웃되었습니다.', 'info');
    }, 500);
}

function updateLoginUI(loginData) {
    // Navigation elements
    const navLoginSection = document.getElementById('navLoginSection');
    const navUserProfile = document.getElementById('navUserProfile');
    const navLoggedInUser = document.getElementById('navLoggedInUser');
    
    // Chat page specific elements
    const chatHistoryContainer = document.getElementById('chatHistoryContainer');
    
    if (loginData && loginData.isLoggedIn) {
        // User is logged in
        if (navLoginSection) navLoginSection.classList.add('hidden');
        
        // Show navigation user profile
        if (navUserProfile) {
            navUserProfile.classList.remove('hidden');
            if (navLoggedInUser) navLoggedInUser.textContent = loginData.username;
        }
        
        // Show chat history on chat page
        if (chatHistoryContainer) {
            chatHistoryContainer.classList.remove('hidden');
        }
        
    } else {
        // User is not logged in
        if (navLoginSection) navLoginSection.classList.remove('hidden');
        
        // Hide navigation user profile
        if (navUserProfile) navUserProfile.classList.add('hidden');
        
        // Hide chat history
        if (chatHistoryContainer) {
            chatHistoryContainer.classList.add('hidden');
        }
    }
}


function initializeLoginState() {
    const loginData = loadFromStorage('loginState');
    updateLoginUI(loginData);
}

/**
 * Show login popup
 */
function showLoginPopup() {
    console.log('showLoginPopup called'); // Debug log
    const overlay = document.getElementById('loginPopupOverlay');
    console.log('overlay element:', overlay); // Debug log
    
    if (overlay) {
        console.log('Removing hidden class'); // Debug log
        overlay.classList.remove('hidden');
        overlay.style.display = 'flex'; // Force display
        document.body.style.overflow = 'hidden';
        
        // Focus on username input
        setTimeout(() => {
            const usernameInput = document.getElementById('popupUsernameInput');
            if (usernameInput) usernameInput.focus();
        }, 100);
    } else {
        console.log('Login popup overlay not found!'); // Debug log
        // Try to find all elements with loginPopup in their ID
        const allElements = document.querySelectorAll('[id*="loginPopup"]');
        console.log('Found elements:', allElements);
    }
}

/**
 * Hide login popup
 */
function hideLoginPopup() {
    const overlay = document.getElementById('loginPopupOverlay');
    if (overlay) {
        overlay.classList.add('hidden');
        overlay.style.display = 'none'; // Force hide
        document.body.style.overflow = 'auto';
        
        // Clear form inputs
        const usernameInput = document.getElementById('popupUsernameInput');
        const passwordInput = document.getElementById('popupPasswordInput');
        if (usernameInput) usernameInput.value = '';
        if (passwordInput) passwordInput.value = '';
    }
}

/**
 * Popup login functionality
 */
function performPopupLogin() {
    const usernameInput = document.getElementById('popupUsernameInput');
    const passwordInput = document.getElementById('popupPasswordInput');
    
    const username = usernameInput ? usernameInput.value.trim() : '';
    const password = passwordInput ? passwordInput.value.trim() : '';
    
    if (!username || !password) {
        showNotification('아이디와 비밀번호를 모두 입력해주세요.', 'warning');
        return;
    }
    
    showLoading('로그인 중...');
    
    // Simulate login API call
    setTimeout(() => {
        if (username.length >= 3) {
            const loginData = {
                isLoggedIn: true,
                username: username,
                loginTime: new Date().toISOString()
            };
            saveToStorage('loginState', loginData);
            
            // Update UI and hide popup
            updateLoginUI(loginData);
            hideLoginPopup();
            hideLoading();
            showNotification(`${username}님, 환영합니다!`, 'success');
        } else {
            hideLoading();
            showNotification('올바른 아이디를 입력해주세요.', 'error');
        }
    }, 1000);
}

/**
 * Show account profile popup
 */
function showAccountPopup() {
    const loginData = loadFromStorage('loginState');
    if (!loginData || !loginData.isLoggedIn) {
        showNotification('로그인이 필요합니다.', 'warning');
        return;
    }
    
    const overlay = document.getElementById('accountPopupOverlay');
    const nameElement = document.getElementById('accountName');
    const lastLoginElement = document.getElementById('accountLastLogin');
    
    if (overlay) {
        // Update account info
        if (nameElement) nameElement.textContent = loginData.username;
        if (lastLoginElement) {
            const loginTime = new Date(loginData.loginTime);
            const timeDiff = new Date() - loginTime;
            const minutes = Math.floor(timeDiff / (1000 * 60));
            if (minutes < 1) {
                lastLoginElement.textContent = '방금 전';
            } else if (minutes < 60) {
                lastLoginElement.textContent = `${minutes}분 전`;
            } else {
                const hours = Math.floor(minutes / 60);
                lastLoginElement.textContent = `${hours}시간 전`;
            }
        }
        
        overlay.classList.remove('hidden');
        document.body.style.overflow = 'hidden';
    }
}

/**
 * Hide account profile popup
 */
function hideAccountPopup() {
    const overlay = document.getElementById('accountPopupOverlay');
    if (overlay) {
        overlay.classList.add('hidden');
        document.body.style.overflow = 'auto';
    }
}

// Keyboard event listeners for popups
document.addEventListener('keydown', function(e) {
    // ESC key to hide popups
    if (e.key === 'Escape') {
        hideLoginPopup();
        hideAccountPopup();
    }
    
    // Enter key in login popup to submit
    const loginOverlay = document.getElementById('loginPopupOverlay');
    if (loginOverlay && !loginOverlay.classList.contains('hidden') && e.key === 'Enter') {
        performPopupLogin();
    }
});

// Click outside to close popups
document.addEventListener('click', function(e) {
    // Login popup
    const loginOverlay = document.getElementById('loginPopupOverlay');
    const loginModal = document.getElementById('loginPopupModal');
    if (loginOverlay && !loginOverlay.classList.contains('hidden') && 
        !loginModal.contains(e.target)) {
        hideLoginPopup();
    }
    
    // Account popup
    const accountOverlay = document.getElementById('accountPopupOverlay');
    const accountModal = document.getElementById('accountPopupModal');
    if (accountOverlay && !accountOverlay.classList.contains('hidden') && 
        !accountModal.contains(e.target)) {
        hideAccountPopup();
    }
});

/**
 * Character search functionality
 */
function searchCharacter(characterName) {
    const searchInput = document.getElementById('characterSearchInput');
    
    // Use provided name or get from input
    const name = characterName || (searchInput ? searchInput.value.trim() : '');
    
    if (!name) {
        showNotification('캐릭터 닉네임을 입력해주세요.', 'warning');
        return;
    }
    
    // Disable search button
    const searchBtn = document.querySelector('.character-search-btn');
    if (searchBtn) {
        searchBtn.disabled = true;
        searchBtn.innerHTML = '<span>검색중...</span>';
    }
    
    showLoading(`${name} 캐릭터 검색 중...`);
    
    // Simulate API call
    setTimeout(() => {
        // Add to recent searches
        addToRecentSearches(name);
        
        // Enable search button
        if (searchBtn) {
            searchBtn.disabled = false;
            searchBtn.innerHTML = '<span>검색</span>';
        }
        
        hideLoading();
        showNotification(`${name} 캐릭터 정보를 찾았습니다!`, 'success');
        
        // Clear input
        if (searchInput && !characterName) {
            searchInput.value = '';
        }
    }, 1500);
}

/**
 * Search and display character info in right sidebar
 */
function searchAndDisplayCharacter(characterName) {
    const searchInput = document.getElementById('characterSearchInput');
    
    // Use provided name or get from input
    const name = characterName || (searchInput ? searchInput.value.trim() : '');
    
    if (!name) {
        showNotification('캐릭터 닉네임을 입력해주세요.', 'warning');
        return;
    }
    
    // Disable search button
    const searchBtn = document.querySelector('.character-search-btn');
    if (searchBtn) {
        searchBtn.disabled = true;
        searchBtn.innerHTML = '<span>검색중...</span>';
    }
    
    showLoading(`${name} 캐릭터 검색 중...`);
    
    // Simulate API call
    setTimeout(() => {
        // Add to recent searches
        addToRecentSearches(name);
        
        // Generate mock character data
        const mockCharacterData = generateMockCharacterData(name);
        
        // Display character info
        displayCharacterInfo(mockCharacterData);
        
        // Enable search button
        if (searchBtn) {
            searchBtn.disabled = false;
            searchBtn.innerHTML = '<span>검색</span>';
        }
        
        hideLoading();
        showNotification(`${name} 캐릭터 정보를 찾았습니다!`, 'success');
        
        // Clear input
        if (searchInput && !characterName) {
            searchInput.value = '';
        }
    }, 1500);
}

/**
 * Search character from recent searches (fills input and searches)
 */
function searchFromRecent(characterName) {
    const searchInput = document.getElementById('characterSearchInput');
    
    // Fill the search input with the character name
    if (searchInput) {
        searchInput.value = characterName;
        
        // Add visual focus effect
        searchInput.focus();
        setTimeout(() => {
            searchInput.blur();
        }, 200);
    }
    
    // Execute the search
    searchAndDisplayCharacter(characterName);
}

/**
 * Generate mock character data
 */
function generateMockCharacterData(name) {
    const servers = ['루나', '스카니아', '베라', '크로아', '유니온', '엘리시움'];
    const jobs = ['키네시스', '아델', '카인', '라라', '제로', '메르세데스', '팬텀', '루미너스', '미하일'];
    
    return {
        name: name,
        server: servers[Math.floor(Math.random() * servers.length)],
        level: Math.floor(Math.random() * 50) + 250, // 250-299
        job: jobs[Math.floor(Math.random() * jobs.length)],
        fame: Math.floor(Math.random() * 50000) + 10000, // 10k-60k
        power: Math.floor(Math.random() * 30) + 15, // 15억-45억
        unionLevel: Math.floor(Math.random() * 3000) + 6000 // 6k-9k
    };
}

/**
 * Display character info in the right sidebar
 */
function displayCharacterInfo(data) {
    const infoDisplay = document.getElementById('characterInfoDisplay');
    if (!infoDisplay) return;
    
    // Update character info
    const nameElement = document.getElementById('displayCharacterName');
    const serverElement = document.getElementById('displayServerName');
    const levelElement = document.getElementById('displayCharacterLevel');
    const jobElement = document.getElementById('displayCharacterJob');
    const fameElement = document.getElementById('displayCharacterFame');
    const powerElement = document.getElementById('displayCharacterPower');
    const unionElement = document.getElementById('displayUnionLevel');
    
    if (nameElement) nameElement.textContent = data.name;
    if (serverElement) serverElement.textContent = data.server;
    if (levelElement) levelElement.textContent = data.level;
    if (jobElement) jobElement.textContent = data.job;
    if (fameElement) fameElement.textContent = data.fame.toLocaleString();
    if (powerElement) powerElement.textContent = `${data.power}억`;
    if (unionElement) unionElement.textContent = data.unionLevel.toLocaleString();
    
    // Show the character info display
    infoDisplay.classList.remove('hidden');
}

function addToRecentSearches(characterName) {
    let recentSearches = loadFromStorage('recentCharacterSearches', []);
    
    // Remove if already exists
    recentSearches = recentSearches.filter(name => name !== characterName);
    
    // Add to beginning
    recentSearches.unshift(characterName);
    
    // Keep only last 5 searches
    recentSearches = recentSearches.slice(0, 5);
    
    // Save to storage
    saveToStorage('recentCharacterSearches', recentSearches);
    
    // Update UI
    updateRecentSearchesUI();
}

function updateRecentSearchesUI() {
    const recentList = document.getElementById('recentSearchList');
    if (!recentList) return;
    
    const recentSearches = loadFromStorage('recentCharacterSearches', []);
    
    recentList.innerHTML = '';
    recentSearches.forEach(name => {
        const item = document.createElement('span');
        item.className = 'search-recent-item';
        item.textContent = name;
        item.onclick = () => searchCharacter(name);
        recentList.appendChild(item);
    });
}

/**
 * Initialize common functionality
 */
function initializeCommon() {
    initializeSearch();
    initializeTheme();
    initializeLoginState();
    updateRecentSearchesUI();
    
    // Add click handlers for common elements
    document.addEventListener('click', function(e) {
        // Handle smooth scroll links
        if (e.target.matches('a[href^="#"]')) {
            e.preventDefault();
            const target = document.querySelector(e.target.getAttribute('href'));
            if (target) {
                smoothScrollTo(target, 100);
            }
        }
    });

    // Handle responsive menu toggle (for mobile)
    const navToggle = document.querySelector('.nav-toggle');
    const navContent = document.querySelector('.nav-content');
    
    if (navToggle && navContent) {
        navToggle.addEventListener('click', function() {
            navContent.classList.toggle('nav-open');
        });
    }

    // Close mobile menu when clicking outside
    document.addEventListener('click', function(e) {
        if (!e.target.closest('.navigation') && navContent) {
            navContent.classList.remove('nav-open');
        }
    });
}

/**
 * Page transition effects
 */
function fadeIn(element, duration = 500) {
    element.style.opacity = '0';
    element.style.transition = `opacity ${duration}ms ease`;
    
    setTimeout(() => {
        element.style.opacity = '1';
    }, 10);
}

function fadeOut(element, duration = 500) {
    element.style.transition = `opacity ${duration}ms ease`;
    element.style.opacity = '0';
    
    return new Promise(resolve => {
        setTimeout(resolve, duration);
    });
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', initializeCommon);

// Export functions for use in other scripts
window.MapleStoryChatBot = {
    setActiveNavItem,
    showNotification,
    smoothScrollTo,
    toggleTheme,
    showLoading,
    hideLoading,
    isMobile,
    isTablet,
    isDesktop,
    saveToStorage,
    loadFromStorage,
    fadeIn,
    fadeOut,
    performSearch,
    redirectToChatWithQuery,
    performLogin,
    performLogout,
    searchCharacter,
    updateLoginUI,
    initializeLoginState
};

// Make functions globally available
window.performLogin = performLogin;
window.performLogout = performLogout;
window.searchCharacter = searchCharacter;
window.searchAndDisplayCharacter = searchAndDisplayCharacter;

/**
 * Main search functionality for home page
 */
function performMainSearch() {
    const mainSearchInput = document.getElementById('mainSearchInput');
    if (!mainSearchInput) return;
    
    const query = mainSearchInput.value.trim();
    if (!query) {
        showNotification('질문을 입력해주세요.', 'warning');
        return;
    }
    
    // Clear input
    mainSearchInput.value = '';
    
    // Redirect to chat with query
    redirectToChatWithQuery(query);
}

// Add Enter key support for main search
document.addEventListener('DOMContentLoaded', function() {
    const mainSearchInput = document.getElementById('mainSearchInput');
    if (mainSearchInput) {
        mainSearchInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                performMainSearch();
            }
        });
    }
});

window.performMainSearch = performMainSearch;

/**
 * Carousel functionality for events and cash items
 */
const carouselData = {
    events: [
        { icon: '🎮', title: '윈터 스페셜 이벤트', description: '12월 한정 특별 이벤트가 진행중입니다', date: '📅 2024.12.01 ~ 2024.12.31' },
        { icon: '🎁', title: '연말 선물 이벤트', description: '매일 접속하고 특별한 선물을 받아보세요', date: '📅 2024.12.15 ~ 2025.01.15' },
        { icon: '⭐', title: '신년 행운 이벤트', description: '새해를 맞이하여 행운의 보상이 기다립니다', date: '📅 2025.01.01 ~ 2025.01.31' }
    ],
    cashItems: [
        { image: '🎭', title: '신년 한정 코스튬', subtitle: '50% 할인 진행중', price: '2,400 캐시' },
        { image: '💼', title: '프리미엄 패키지', subtitle: '특별 혜택 포함', price: '4,800 캐시' },
        { image: '✨', title: '이펙트 아이템', subtitle: 'NEW 출시', price: '1,200 캐시' }
    ]
};

let carouselIndex = { event: 0, cash: 0 };

function changeCarousel(type, direction) {
    const items = carouselData[type + 's'];
    const display = document.getElementById(type + 'Display');
    if (!display || !items) return;
    
    carouselIndex[type] += direction;
    if (carouselIndex[type] < 0) carouselIndex[type] = items.length - 1;
    if (carouselIndex[type] >= items.length) carouselIndex[type] = 0;
    
    // Add transition effect
    display.style.transition = 'opacity 0.3s ease';
    display.style.opacity = '0';
    
    setTimeout(() => {
        const item = items[carouselIndex[type]];
        if (type === 'event') {
            display.innerHTML = `
                <div class="event-icon">${item.icon}</div>
                <div class="event-title-modern">${item.title}</div>
                <div class="event-description">${item.description}</div>
                <div class="event-date-modern">${item.date}</div>
            `;
        } else {
            display.innerHTML = `
                <div class="cash-banner-image">${item.image}</div>
                <div class="cash-banner-title">${item.title}</div>
                <div class="cash-banner-subtitle">${item.subtitle}</div>
                <div class="cash-banner-price">${item.price}</div>
            `;
        }
        display.style.opacity = '1';
    }, 150);
}

function changeEvent(direction) { changeCarousel('event', direction); }
function changeCashItem(direction) { changeCarousel('cash', direction); }

// Auto-rotate carousels
setInterval(() => {
    if (document.getElementById('eventDisplay')) {
        changeEvent(1);
    }
}, 5000);

setInterval(() => {
    if (document.getElementById('cashDisplay')) {
        changeCashItem(1);
    }
}, 6000);


// Make functions globally available
window.changeEvent = changeEvent;
window.changeCashItem = changeCashItem;