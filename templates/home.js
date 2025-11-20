// DOM이 완전히 로드된 후 스크립트 실행
document.addEventListener('DOMContentLoaded', function() {

    // ===================================================================
    // 데이터 (실제로는 API를 통해 받아올 데이터의 예시)
    // ===================================================================
    const generalRankingData = [
        { rank: 1, name: '오징어괴물', server: '루나', level: 299 },
        { rank: 2, name: '안녕하세요', server: '스카니아', level: 299 },
        { rank: 3, name: '오징어물괴', server: '베라', level: 298 },
        { rank: 4, name: '메이플러버', server: '크로아', level: 298 },
        { rank: 5, name: '최강전사', server: '유니온', level: 297 },
        { rank: 6, name: '파이터킹', server: '엘리시움', level: 297 },
        { rank: 7, name: '던전마스터', server: '아케인', level: 296 },
        { rank: 8, name: '마법사왕', server: '노바', level: 296 },
        { rank: 9, name: '궁수전설', server: '제니스', level: 295 },
        { rank: 10, name: '도적황제', server: '오로라', level: 295 },
    ];

    const powerRankingData = [
        { rank: 1, name: '전설의파워', server: '루나', power: '25억' },
        { rank: 2, name: '최강무자비', server: '스카니아', power: '24억' },
        { rank: 3, name: '파워킹덤', server: '베라', power: '23억' },
        { rank: 4, name: '무적전사', server: '크로아', power: '22억' },
        { rank: 5, name: '데미지킹', server: '유니온', power: '21억' },
        { rank: 6, name: '폭딜마스터', server: '엘리시움', power: '20억' },
        { rank: 7, name: '극딜전문가', server: '아케인', power: '19억' },
        { rank: 8, name: '원펀치맨', server: '노바', power: '18억' },
        { rank: 9, name: '절대강자', server: '제니스', power: '17억' },
        { rank: 10, name: '최종병기', server: '오로라', power: '16억' },
    ];

    // ===================================================================
    // 함수 정의
    // ===================================================================

    /**
     * 랭킹 데이터를 기반으로 랭킹 목록 HTML을 생성하고 삽입합니다.
     * @param {string} containerSelector - 랭킹 목록을 담을 컨테이너의 CSS 선택자
     * @param {Array} rankingData - 랭킹 데이터 배열
     * @param {string} type - 'general' 또는 'power'
     */
    function populateRanking(containerSelector, rankingData, type) {
        const container = document.querySelector(containerSelector);
        if (!container) return;

        container.innerHTML = ''; // 기존 내용 비우기

        rankingData.forEach(item => {
            const rankBadgeClass = item.rank <= 3 ? `top-${item.rank}` : 'other';
            const details = type === 'general'
                ? `${item.server} · Lv.${item.level}`
                : `${item.server} · ${item.power}`;

            const rankingItemHTML = `
                <div class="ranking-item-modern">
                    <div class="ranking-badge ${rankBadgeClass}">${item.rank}</div>
                    <div class="ranking-player-info">
                        <div class="ranking-name">${item.name}</div>
                        <div class="ranking-details">${details}</div>
                    </div>
                </div>
            `;
            container.insertAdjacentHTML('beforeend', rankingItemHTML);
        });
    }

    // 검색 예시 클릭 시 메인 검색창에 텍스트를 설정하고 검색을 실행합니다.
    function searchExample(query) {
        const mainSearchInput = document.getElementById('mainSearchInput');
        if (mainSearchInput) {
            mainSearchInput.value = query;
            // performMainSearch 함수가 전역에 정의되어 있다고 가정
            if (window.performMainSearch) {
                window.performMainSearch();
            } else {
                // Fallback: chatbot 페이지로 쿼리와 함께 이동
                sessionStorage.setItem('pendingChatQuery', query);
                window.location.href = '/chatbot/';
            }
        }
    }

    // ===================================================================
    // 이벤트 리스너 바인딩
    // ===================================================================

    // 네비게이션 바
    document.querySelector('.nav-login-btn')?.addEventListener('click', () => {
        console.log('Login button clicked');
        // showLoginPopup 함수는 common.js에 있다고 가정
        if (window.showLoginPopup) showLoginPopup();
    });
    document.querySelector('.nav-profile-btn')?.addEventListener('click', () => {
        // showAccountPopup 함수는 common.js에 있다고 가정
        if (window.showAccountPopup) showAccountPopup();
    });
    document.querySelector('.nav-logout-btn')?.addEventListener('click', () => {
        // performLogout 함수는 common.js에 있다고 가정
        if (window.performLogout) performLogout();
    });

    // 캐릭터 검색
    document.querySelector('.character-search-btn')?.addEventListener('click', () => {
        // searchAndDisplayCharacter 함수는 common.js에 있다고 가정
        if (window.searchAndDisplayCharacter) searchAndDisplayCharacter();
    });

    // 최근 검색어
    document.querySelectorAll('.search-recent-item').forEach(item => {
        item.addEventListener('click', () => {
            const characterName = item.textContent;
            // searchFromRecent 함수는 common.js에 있다고 가정
            if (window.searchFromRecent) searchFromRecent(characterName);
        });
    });

    // 메인 챗봇 검색
    document.querySelector('.main-search-btn')?.addEventListener('click', () => {
        // performMainSearch 함수는 common.js에 있다고 가정
        if (window.performMainSearch) performMainSearch();
    });

    // 검색 예시
    document.querySelectorAll('.search-example').forEach(item => {
        item.addEventListener('click', () => {
            searchExample(item.textContent);
        });
    });

    // 하단 섹션 카드 네비게이션
    const eventCard = document.querySelector('.section-card:nth-child(1)');
    eventCard?.querySelector('.nav-arrow:nth-child(1)')?.addEventListener('click', () => {
        // changeEvent 함수는 common.js에 있다고 가정
        if (window.changeEvent) changeEvent(-1);
    });
    eventCard?.querySelector('.nav-arrow:nth-child(2)')?.addEventListener('click', () => {
        if (window.changeEvent) changeEvent(1);
    });

    const cashCard = document.querySelector('.section-card:nth-child(2)');
    cashCard?.querySelector('.nav-arrow:nth-child(1)')?.addEventListener('click', () => {
        // changeCashItem 함수는 common.js에 있다고 가정
        if (window.changeCashItem) changeCashItem(-1);
    });
    cashCard?.querySelector('.nav-arrow:nth-child(2)')?.addEventListener('click', () => {
        if (window.changeCashItem) changeCashItem(1);
    });

    // 팝업 닫기/액션 버튼
    document.querySelector('.profile-popup-close')?.addEventListener('click', () => {
        if (window.hideProfilePopup) hideProfilePopup();
    });
    document.querySelector('.profile-popup-actions .profile-action-btn')?.addEventListener('click', () => {
        if (window.performLogout) performLogout();
    });

    document.querySelector('.login-popup-close')?.addEventListener('click', () => {
        if (window.hideLoginPopup) hideLoginPopup();
    });
    document.querySelector('.login-popup-btn')?.addEventListener('click', () => {
        if (window.performPopupLogin) performPopupLogin();
    });

    document.querySelector('.account-popup-close')?.addEventListener('click', () => {
        if (window.hideAccountPopup) hideAccountPopup();
    });
    document.querySelector('.account-actions .secondary')?.addEventListener('click', () => {
        if (window.performLogout) performLogout();
    });

    // ESC 키로 팝업 닫기
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape') {
            if (window.hideProfilePopup) hideProfilePopup();
            if (window.hideLoginPopup) hideLoginPopup();
            if (window.hideAccountPopup) hideAccountPopup();
        }
    });

    // 팝업 외부 클릭 시 닫기
    document.addEventListener('click', function(e) {
        const profilePopupOverlay = document.getElementById('profilePopupOverlay');
        if (profilePopupOverlay && !profilePopupOverlay.classList.contains('hidden')) {
            if (!document.getElementById('profilePopupModal').contains(e.target)) {
                if (window.hideProfilePopup) hideProfilePopup();
            }
        }

        const loginPopupOverlay = document.getElementById('loginPopupOverlay');
        if (loginPopupOverlay && !loginPopupOverlay.classList.contains('hidden')) {
            if (!document.getElementById('loginPopupModal').contains(e.target)) {
                if (window.hideLoginPopup) hideLoginPopup();
            }
        }

        const accountPopupOverlay = document.getElementById('accountPopupOverlay');
        if (accountPopupOverlay && !accountPopupOverlay.classList.contains('hidden')) {
            if (!document.getElementById('accountPopupModal').contains(e.target)) {
                if (window.hideAccountPopup) hideAccountPopup();
            }
        }
    });

    // ===================================================================
    // 초기화 코드
    // ===================================================================

    // setActiveNavItem 함수가 common.js에 있다고 가정
    if(window.setActiveNavItem) setActiveNavItem('홈');

    // 랭킹 목록 동적 생성
    populateRanking('.section-card:nth-child(3) .ranking-scroll-container', generalRankingData, 'general');
    populateRanking('.section-card:nth-child(4) .ranking-scroll-container', powerRankingData, 'power');

});