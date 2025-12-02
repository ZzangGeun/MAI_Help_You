/**
 * Character Search Module
 * 캐릭터 검색 및 정보 표시 기능
 */

import { showNotification, showLoading, hideLoading } from './ui.js';
import { saveToStorage, loadFromStorage } from './ui.js';

// Global configuration for API
const CONFIG = {
    API_BASE_URL: '/api'
};

/**
 * Character search functionality
 */
export async function searchCharacter(characterName) {
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
    
    const characterData = await fetchCharacterData(name);
    
    // Add to recent searches only if data is successfully fetched
    if (characterData) {
        addToRecentSearches(name);
        showNotification(`${name} 캐릭터 정보를 찾았습니다!`, 'success');
    } else {
        showNotification(`${name} 캐릭터 정보를 찾을 수 없습니다.`, 'error');
    }
    
    // Enable search button
    if (searchBtn) {
        searchBtn.disabled = false;
        searchBtn.innerHTML = '<span>검색</span>';
    }
    
    hideLoading();
    
    // Clear input
    if (searchInput && !characterName) {
        searchInput.value = '';
    }
}

/**
 * Search and display character info in right sidebar
 */
export async function searchAndDisplayCharacter(characterName) {
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
    
    const characterData = await fetchCharacterData(name);
    
    // Add to recent searches only if data is successfully fetched
    if (characterData) {
        addToRecentSearches(name);
        displayCharacterInfo(characterData);
        showNotification(`${name} 캐릭터 정보를 찾았습니다!`, 'success');
    } else {
        showNotification(`${name} 캐릭터 정보를 찾을 수 없습니다.`, 'error');
    }
    
    // Enable search button
    if (searchBtn) {
        searchBtn.disabled = false;
        searchBtn.innerHTML = '<span>검색</span>';
    }
    
    hideLoading();
    
    // Clear input
    if (searchInput && !characterName) {
        searchInput.value = '';
    }
}

/**
 * Search character from recent searches (fills input and searches)
 */
export function searchFromRecent(characterName) {
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
 * Fetch character data from API
 */
async function fetchCharacterData(name) {
    try {
        const response = await fetch(`${CONFIG.API_BASE_URL}/character_info/search/?character_name=${encodeURIComponent(name)}`);
        const data = await response.json();
        if (data.success) {
            return data.data;
        } else {
            showNotification(`캐릭터 정보를 가져오는 데 실패했습니다: ${data.message || '알 수 없는 오류'}`, 'error');
            return null;
        }
    } catch (error) {
        console.error('Error fetching character data:', error);
        showNotification('네트워크 오류로 캐릭터 정보를 가져올 수 없습니다.', 'error');
        return null;
    }
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
    
    if (nameElement) nameElement.textContent = data.character_name;
    if (serverElement) serverElement.textContent = data.world_name;
    if (levelElement) levelElement.textContent = data.character_level;
    if (jobElement) jobElement.textContent = data.character_class;
    if (fameElement) fameElement.textContent = data.character_popularity.toLocaleString();
    if (powerElement) powerElement.textContent = data.combat_power.toLocaleString();
    if (unionElement) unionElement.textContent = data.union_level.toLocaleString();
    
    // Show the character info display
    infoDisplay.classList.remove('hidden');
}

/**
 * Add to recent searches
 */
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

/**
 * Update recent searches UI
 */
export function updateRecentSearchesUI() {
    const recentList = document.getElementById('recentSearchList');
    if (!recentList) return;
    
    const recentSearches = loadFromStorage('recentCharacterSearches', []);
    
    recentList.innerHTML = '';
    recentSearches.forEach(name => {
        const item = document.createElement('span');
        item.className = 'search-recent-item';
        item.textContent = name;
        item.onclick = () => searchFromRecent(name);
        recentList.appendChild(item);
    });
}
