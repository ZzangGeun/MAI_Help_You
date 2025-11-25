/**
 * Authentication Module
 * 로그인, 회원가입, 로그아웃 관련 기능
 */

import { showNotification, showLoading, hideLoading } from './ui.js';
import { saveToStorage, loadFromStorage } from './ui.js';
import { hideLoginPopup, showLoginPopup, hideSignupPopup, hideAccountPopup } from './popup.js';

/**
 * Login/Logout functionality
 */
export function performLogin() {
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

export async function performLogout() {
    showLoading('로그아웃 중...');
    
    try {
        // 실제 Django API 호출
        const response = await fetch('/accounts/api/logout/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            }
        });
        
        const data = await response.json();
        
        // 성공 여부와 관계없이 로컬 스토리지 클리어
        localStorage.removeItem('loginState');
        
        // Update UI
        updateLoginUI(null);
        hideLoading();
        
        if (response.ok && data.status === 'success') {
            showNotification(data.message || '로그아웃되었습니다.', 'info');
        } else {
            showNotification('로그아웃되었습니다.', 'info');
        }
        
        // 계정 팝업이 열려있으면 닫기
        hideAccountPopup();
        
    } catch (error) {
        console.error('Logout error:', error);
        // 오류가 발생해도 로컬 로그아웃 처리
        localStorage.removeItem('loginState');
        updateLoginUI(null);
        hideLoading();
        showNotification('로그아웃되었습니다.', 'info');
    }
}

export function updateLoginUI(loginData) {
    // Navigation elements
    const navLoginSection = document.getElementById('navLoginSection');
    const navUserProfile = document.getElementById('navUserProfile');
    const navLoggedInUser = document.getElementById('navLoggedInUser');
    
    // Chat page specific elements
    const chatHistoryContainer = document.getElementById('chatHistoryContainer');
    const equipmentWindow = document.getElementById('equipmentWindow');
    const equipmentCharacterName = document.getElementById('equipmentCharacterName');
    
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

        // Show equipment window on home page
        if (equipmentWindow) {
            equipmentWindow.classList.remove('hidden');
            if (equipmentCharacterName) {
                equipmentCharacterName.textContent = loginData.username;
            }
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

        // Hide equipment window
        if (equipmentWindow) {
            equipmentWindow.classList.add('hidden');
        }
    }
}

export function initializeLoginState() {
    const loginData = loadFromStorage('loginState');
    updateLoginUI(loginData);
}

/**
 * Perform signup
 */
export async function performSignup() {
    const userIdInput = document.getElementById('signupUserIdInput');
    const passwordInput = document.getElementById('signupPasswordInput');
    const confirmInput = document.getElementById('signupPasswordConfirmInput');
    const mapleNicknameInput = document.getElementById('signupMapleNicknameInput');
    const apiKeyInput = document.getElementById('signupNexonApiKeyInput');
    
    const user_id = userIdInput ? userIdInput.value.trim() : '';
    const password = passwordInput ? passwordInput.value.trim() : '';
    const confirm_password = confirmInput ? confirmInput.value.trim() : '';
    const maple_nickname = mapleNicknameInput ? mapleNicknameInput.value.trim() : '';
    const nexon_api_key = apiKeyInput ? apiKeyInput.value.trim() : '';
    
    // 유효성 검사
    if (!user_id || !password || !confirm_password || !maple_nickname) {
        showNotification('필수 항목을 모두 입력해주세요.', 'warning');
        return;
    }
    
    if (!/^[a-zA-Z0-9_]{4,20}$/.test(user_id)) {
        showNotification('아이디는 4~20자의 영문자, 숫자, 밑줄(_)만 사용할 수 있습니다.', 'warning');
        return;
    }
    
    if (password.length < 8) {
        showNotification('비밀번호는 최소 8자 이상이어야 합니다.', 'warning');
        return;
    }
    
    if (password !== confirm_password) {
        showNotification('비밀번호가 일치하지 않습니다.', 'warning');
        return;
    }
    
    if (maple_nickname.length > 12) {
        showNotification('메이플 닉네임은 최대 12자까지 입력 가능합니다.', 'warning');
        return;
    }
    
    showLoading('회원가입 처리 중...');
    
    try {
        // 실제 Django API 호출
        const response = await fetch('/accounts/api/signup/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                user_id: user_id,
                password: password,
                confirm_password: confirm_password,
                maple_nickname: maple_nickname,
                nexon_api_key: nexon_api_key
            })
        });
        
        const data = await response.json();
        
        if (response.ok && data.status === 'success') {
            // 회원가입 성공
            hideSignupPopup();
            hideLoading();
            showNotification(data.message || '회원가입이 완료되었습니다. 로그인해주세요.', 'success');
            
            // 로그인 팝업 열기
            setTimeout(() => {
                showLoginPopup();
                // 가입한 아이디를 로그인 폼에 자동 입력
                const loginUsernameInput = document.getElementById('popupUsernameInput');
                if (loginUsernameInput) {
                    loginUsernameInput.value = user_id;
                    const loginPasswordInput = document.getElementById('popupPasswordInput');
                    if (loginPasswordInput) loginPasswordInput.focus();
                }
            }, 500);
        } else {
            // 회원가입 실패
            hideLoading();
            showNotification(data.error || '회원가입에 실패했습니다.', 'error');
        }
    } catch (error) {
        console.error('Signup error:', error);
        hideLoading();
        showNotification('네트워크 오류가 발생했습니다.', 'error');
    }
}

/**
 * Popup login functionality
 */
export async function performPopupLogin() {
    const usernameInput = document.getElementById('popupUsernameInput');
    const passwordInput = document.getElementById('popupPasswordInput');
    
    const user_id = usernameInput ? usernameInput.value.trim() : '';
    const password = passwordInput ? passwordInput.value.trim() : '';
    
    if (!user_id || !password) {
        showNotification('아이디와 비밀번호를 모두 입력해주세요.', 'warning');
        return;
    }
    
    showLoading('로그인 중...');
    
    try {
        // 실제 Django API 호출
        const response = await fetch('/accounts/api/login/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                user_id: user_id,
                password: password
            })
        });
        
        const data = await response.json();
        
        if (response.ok && data.status === 'success') {
            // 로그인 성공
            const loginData = {
                isLoggedIn: true,
                username: data.user.user_id,
                email: data.user.email,
                maple_nickname: data.user.maple_nickname,
                loginTime: new Date().toISOString()
            };
            saveToStorage('loginState', loginData);
            
            // Update UI and hide popup
            updateLoginUI(loginData);
            hideLoginPopup();
            hideLoading();
            showNotification(data.message || `${user_id}님, 환영합니다!`, 'success');
        } else {
            // 로그인 실패
            hideLoading();
            showNotification(data.error || '로그인에 실패했습니다.', 'error');
        }
    } catch (error) {
        console.error('Login error:', error);
        hideLoading();
        showNotification('네트워크 오류가 발생했습니다.', 'error');
    }
}
