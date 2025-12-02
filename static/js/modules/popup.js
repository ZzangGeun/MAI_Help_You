/**
 * Popup Management Module
 * 모든 팝업 show/hide 기능 관리
 */

import { showNotification } from './ui.js';
import { loadFromStorage } from './ui.js';
import { performPopupLogin, performSignup, performLogout, updateLoginUI } from './auth.js';
import { searchAndDisplayCharacter } from './character.js';

/**
 * Show signup popup
 */
export function showSignupPopup() {
    const overlay = document.getElementById('signupPopupOverlay');
    
    if (overlay) {
        overlay.classList.remove('hidden');
        overlay.style.display = 'flex';
        document.body.style.overflow = 'hidden';
        
        // Focus on user ID input
        setTimeout(() => {
            const userIdInput = document.getElementById('signupUserIdInput');
            if (userIdInput) userIdInput.focus();
        }, 100);
    }
}

/**
 * Hide signup popup
 */
export function hideSignupPopup() {
    const overlay = document.getElementById('signupPopupOverlay');
    if (overlay) {
        overlay.classList.add('hidden');
        overlay.style.display = 'none';
        document.body.style.overflow = 'auto';
        
        // Clear form inputs
        const userIdInput = document.getElementById('signupUserIdInput');
        const passwordInput = document.getElementById('signupPasswordInput');
        const confirmInput = document.getElementById('signupPasswordConfirmInput');
        const mapleNicknameInput = document.getElementById('signupMapleNicknameInput');
        const apiKeyInput = document.getElementById('signupNexonApiKeyInput');
        
        if (userIdInput) userIdInput.value = '';
        if (passwordInput) passwordInput.value = '';
        if (confirmInput) confirmInput.value = '';
        if (mapleNicknameInput) mapleNicknameInput.value = '';
        if (apiKeyInput) apiKeyInput.value = '';
    }
}

/**
 * Show login popup
 */
export function showLoginPopup() {
    console.log('showLoginPopup called');
    const overlay = document.getElementById('loginPopupOverlay');
    console.log('overlay element:', overlay);
    
    if (overlay) {
        console.log('Removing hidden class');
        overlay.classList.remove('hidden');
        overlay.style.display = 'flex';
        document.body.style.overflow = 'hidden';
        
        // Focus on username input
        setTimeout(() => {
            const usernameInput = document.getElementById('popupUsernameInput');
            if (usernameInput) usernameInput.focus();
        }, 100);
    } else {
        console.log('Login popup overlay not found!');
        const allElements = document.querySelectorAll('[id*="loginPopup"]');
        console.log('Found elements:', allElements);
    }
}

/**
 * Hide login popup
 */
export function hideLoginPopup() {
    const overlay = document.getElementById('loginPopupOverlay');
    if (overlay) {
        overlay.classList.add('hidden');
        overlay.style.display = 'none';
        document.body.style.overflow = 'auto';
        
        // Clear form inputs
        const usernameInput = document.getElementById('popupUsernameInput');
        const passwordInput = document.getElementById('popupPasswordInput');
        if (usernameInput) usernameInput.value = '';
        if (passwordInput) passwordInput.value = '';
    }
}

/**
 * Show account profile popup
 */
export function showAccountPopup() {
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
export function hideAccountPopup() {
    const overlay = document.getElementById('accountPopupOverlay');
    if (overlay) {
        overlay.classList.add('hidden');
        document.body.style.overflow = 'auto';
    }
}

/**
 * Show profile popup
 */
export function showProfilePopup() {
    const loginData = loadFromStorage('loginState');
    if (!loginData || !loginData.isLoggedIn) {
        showNotification('로그인이 필요합니다.', 'warning');
        return;
    }
    
    const overlay = document.getElementById('profilePopupOverlay');
    const nameElement = document.getElementById('profilePopupName');
    const loginTimeElement = document.getElementById('profileLoginTime');
    
    if (overlay) {
        // Update profile info
        if (nameElement) nameElement.textContent = loginData.username;
        if (loginTimeElement) {
            const loginTime = new Date(loginData.loginTime);
            const timeDiff = new Date() - loginTime;
            const minutes = Math.floor(timeDiff / (1000 * 60));
            if (minutes < 1) {
                loginTimeElement.textContent = '방금 전';
            } else if (minutes < 60) {
                loginTimeElement.textContent = `${minutes}분 전`;
            } else {
                const hours = Math.floor(minutes / 60);
                loginTimeElement.textContent = `${hours}시간 전`;
            }
        }
        
        overlay.classList.remove('hidden');
        document.body.style.overflow = 'hidden';
    }
}

/**
 * Hide profile popup
 */
export function hideProfilePopup() {
    const overlay = document.getElementById('profilePopupOverlay');
    if (overlay) {
        overlay.classList.add('hidden');
        document.body.style.overflow = 'auto';
    }
}

/**
 * Initialize popup event listeners
 */
export function initializePopupListeners() {
    // Open popups
    document.querySelector('.nav-login-btn')?.addEventListener('click', () => {
        showLoginPopup();
    });
    document.querySelector('.nav-profile-btn')?.addEventListener('click', () => {
        showAccountPopup();
    });
    document.querySelector('.nav-logout-btn')?.addEventListener('click', () => {
        performLogout();
    });

    // Close popups with close buttons
    document.querySelector('.login-popup-close')?.addEventListener('click', hideLoginPopup);
    document.querySelector('.signup-popup-close')?.addEventListener('click', hideSignupPopup);
    document.querySelector('.account-popup-close')?.addEventListener('click', hideAccountPopup);
    document.querySelector('.profile-popup-close')?.addEventListener('click', hideProfilePopup);

    // Popup actions
    document.querySelector('.login-popup-btn')?.addEventListener('click', performPopupLogin);
    document.querySelector('.signup-popup-btn')?.addEventListener('click', performSignup);
    
    // 회원가입 팝업에서 로그인 팝업으로 이동
    document.querySelector('.signup-to-login-link')?.addEventListener('click', function(e) {
        e.preventDefault();
        hideSignupPopup();
        showLoginPopup();
    });
    
    // Enter key support for login popup
    const popupUsernameInput = document.getElementById('popupUsernameInput');
    const popupPasswordInput = document.getElementById('popupPasswordInput');
    
    if (popupUsernameInput) {
        popupUsernameInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                e.preventDefault();
                if (popupPasswordInput) {
                    popupPasswordInput.focus();
                }
            }
        });
    }
    
    if (popupPasswordInput) {
        popupPasswordInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                e.preventDefault();
                performPopupLogin();
            }
        });
    }
    
    // 로그인 팝업에서 회원가입 링크 클릭 시 회원가입 팝업으로 이동
    document.getElementById('toSignupLink')?.addEventListener('click', function(e) {
        e.preventDefault();
        console.log('회원가입 링크 클릭됨');
        hideLoginPopup();
        showSignupPopup();
    });
    
    // 비밀번호 찾기 링크
    document.getElementById('forgotPasswordLink')?.addEventListener('click', function(e) {
        e.preventDefault();
        showNotification('비밀번호 찾기 기능은 준비 중입니다.', 'info');
    });
    
    // Account popup buttons
    document.querySelector('#myInfoBtn')?.addEventListener('click', () => {
        const loginData = loadFromStorage('loginState');
        if (loginData && loginData.isLoggedIn) {
            hideAccountPopup();
            searchAndDisplayCharacter(loginData.username);
            showNotification(`${loginData.username}님의 캐릭터 정보를 표시합니다.`, 'info');
        }
    });
    document.querySelector('#accountLogoutBtn')?.addEventListener('click', performLogout);
    document.querySelector('.profile-popup-actions .profile-action-btn')?.addEventListener('click', performLogout);

    // ESC key to close all popups
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape') {
            hideLoginPopup();
            hideSignupPopup();
            hideAccountPopup();
            hideProfilePopup();
        }
    });

    // Click outside to close popups
    document.addEventListener('click', function(e) {
        const loginPopupOverlay = document.getElementById('loginPopupOverlay');
        if (loginPopupOverlay && !loginPopupOverlay.classList.contains('hidden')) {
            const loginModal = document.getElementById('loginPopupModal');
            if (loginModal && !loginModal.contains(e.target) && !e.target.closest('.nav-login-btn')) {
                hideLoginPopup();
            }
        }
        
        const signupPopupOverlay = document.getElementById('signupPopupOverlay');
        if (signupPopupOverlay && !signupPopupOverlay.classList.contains('hidden')) {
            const signupModal = document.getElementById('signupPopupModal');
            if (signupModal && !signupModal.contains(e.target)) {
                hideSignupPopup();
            }
        }

        const accountPopupOverlay = document.getElementById('accountPopupOverlay');
        if (accountPopupOverlay && !accountPopupOverlay.classList.contains('hidden')) {
            const accountModal = document.getElementById('accountPopupModal');
            if (accountModal && !accountModal.contains(e.target) && !e.target.closest('.nav-profile-btn')) {
                hideAccountPopup();
            }
        }

        const profilePopupOverlay = document.getElementById('profilePopupOverlay');
        if (profilePopupOverlay && !profilePopupOverlay.classList.contains('hidden')) {
            const profileModal = document.getElementById('profilePopupModal');
            if (profileModal && !profileModal.contains(e.target) && !e.target.closest('.nav-profile-btn')) {
                hideProfilePopup();
            }
        }
    });
}
