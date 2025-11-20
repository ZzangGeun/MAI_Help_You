// DOM이 완전히 로드된 후 스크립트 실행
document.addEventListener('DOMContentLoaded', function() {

    // ===================================================================
    // 함수 정의
    // ===================================================================

    /**
     * 랭킹 데이터를 기반으로 랭킹 목록 HTML을 생성하고 삽입합니다。
     * @param {string} containerSelector - 랭킹 목록을 담을 컨테이너의 CSS 선택자
     * @param {Array} rankingData - 랭킹 데이터 배열
     * @param {string} type - 'general' 또는 'power'
     */
    function populateRanking(containerSelector, rankingData, type) {
        const container = document.querySelector(containerSelector);
        if (!container) return;

        container.innerHTML = ''; // 기존 내용 비우기

        rankingData.forEach(item => {
            const rankBadgeClass = item.ranking <= 3 ? `top-${item.ranking}` : 'other';
            const details = type === 'general'
                ? `${item.world_name} · Lv.${item.character_level}`
                : `${item.world_name} · Lv.${item.union_level}`;

            const rankingItemHTML = `
                <div class="ranking-item-modern">
                    <div class="ranking-badge ${rankBadgeClass}">${item.ranking}</div>
                    <div class="ranking-player-info">
                        <div class="ranking-name">${item.character_name}</div>
                        <div class="ranking-details">${details}</div>
                    </div>
                </div>
            `;
            container.insertAdjacentHTML('beforeend', rankingItemHTML);
        });
    }

    /**
     * API를 통해 랭킹 데이터를 비동기적으로 가져와 화면에 표시합니다.
     * @param {string} type - 'general' 또는 'power'
     */
    async function fetchAndPopulateRanking(type) {
        const containerSelector = type === 'general'
            ? '.bottom-section .section-card:nth-child(3) .ranking-scroll-container'
            : '.bottom-section .section-card:nth-child(4) .ranking-scroll-container';
        
        try {
            const response = await fetch(`/api/rankings/?type=${type}`);
            const result = await response.json();
            if (result.success) {
                populateRanking(containerSelector, result.data, type);
            }
        } catch (error) {
            console.error(`${type} 랭킹 데이터를 가져오는 중 오류 발생:`, error);
        }
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
    const eventCard = document.querySelector('.bottom-section .section-card:nth-child(1)');
    eventCard?.querySelector('.nav-arrow:nth-child(1)')?.addEventListener('click', () => {
        // changeEvent 함수는 common.js에 있다고 가정
        if (window.changeEvent) changeEvent(-1);
    });
    eventCard?.querySelector('.nav-arrow:nth-child(2)')?.addEventListener('click', () => {
        if (window.changeEvent) changeEvent(1);
    });

    const cashCard = document.querySelector('.bottom-section .section-card:nth-child(2)');
    cashCard?.querySelector('.nav-arrow:nth-child(1)')?.addEventListener('click', () => {
        // changeCashItem 함수는 common.js에 있다고 가정
        if (window.changeCashItem) changeCashItem(-1);
    });
    cashCard?.querySelector('.nav-arrow:nth-child(2)')?.addEventListener('click', () => {
        if (window.changeCashItem) changeCashItem(1);
    });

    // ===================================================================
    // 초기화 코드
    // ===================================================================

    // setActiveNavItem 함수가 common.js에 있다고 가정
    if(window.setActiveNavItem) setActiveNavItem('홈');

    // 랭킹 목록 동적 생성
    fetchAndPopulateRanking('general');
    fetchAndPopulateRanking('power');

    // 캐러셀 데이터 로드
    fetchCarouselData(); // Fetch carousel data on load

});