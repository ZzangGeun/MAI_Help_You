/**
 * Maple Story ChatBot - Common JavaScript (Refactored)
 * 핵심 공통 기능 및 모듈 초기화
 */

// Import modules
import { 
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
    initializeTheme
} from './modules/ui.js';

import { 
    performLogin, 
    performLogout, 
    updateLoginUI, 
    initializeLoginState 
} from './modules/auth.js';

import { 
    showLoginPopup,
    showSignupPopup,
    showAccountPopup,
    showProfilePopup,
    hideProfilePopup,
    initializePopupListeners
} from './modules/popup.js';

import { 
    searchCharacter, 
    searchAndDisplayCharacter, 
    searchFromRecent,
    updateRecentSearchesUI
} from './modules/character.js';

import { 
    changeEvent, 
    changeCashItem,
    initializeCarousel
} from './modules/carousel.js';

// Global configuration
const CONFIG = {
    ANIMATION_DURATION: 300,
    DEBOUNCE_DELAY: 500,
    API_BASE_URL: '/api',
};

/**
 * Navigation related functions
 */
export function setActiveNavItem(pageName) {
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
        window.location.href = '/chatbot/';
    }, 500);
}

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

/**
 * Initialize common functionality
 */
function initializeCommon() {
    initializeSearch();
    initializeTheme();
    initializeLoginState();
    updateRecentSearchesUI();
    initializePopupListeners();
    initializeCarousel();
    
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
    
    // Theme toggle
    document.getElementById('themeToggleBtn')?.addEventListener('click', toggleTheme);
    
    // Add Enter key support for main search
    const mainSearchInput = document.getElementById('mainSearchInput');
    if (mainSearchInput) {
        mainSearchInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                performMainSearch();
            }
        });
    }
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', initializeCommon);

// Export functions for use in other scripts and global access
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
    initializeLoginState,
    showProfilePopup,
    hideProfilePopup,
    showLoginPopup,
    showSignupPopup,
    showAccountPopup
};

// Make commonly used functions globally available
window.performLogin = performLogin;
window.performLogout = performLogout;
window.searchCharacter = searchCharacter;
window.searchAndDisplayCharacter = searchAndDisplayCharacter;
window.searchFromRecent = searchFromRecent;
window.performMainSearch = performMainSearch;
window.changeEvent = changeEvent;
window.changeCashItem = changeCashItem;
window.initializeCarousel = initializeCarousel;
