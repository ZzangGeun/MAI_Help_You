/**
 * Carousel Module
 * 홈페이지 이벤트 및 캐시 아이템 캐러셀 기능
 */

/**
 * Carousel data (백엔드에서 전달받거나 기본값 사용)
 */
const defaultCarouselData = {
    events: [
        { icon: '🎮', title: '윈터 스페셜 이벤트', description: '12월 한정 특별 이벤트가 진행중입니다', date: '📅 2024.12.01 ~ 2024.12.31' },
        { icon: '🎁', title: '연말 선물 이벤트', description: '매일 접속하고 특별한 선물을 받아보세요', date: '📅 2024.12.15 ~ 2025.01.15' },
        { icon: '⭐', title: '신년 행운 이벤트', description: '새해를 맞이하여 행운의 보상이 기다립니다', date: '📅 2025.01.01 ~ 2025.01.31' }
    ],
    cashItems: [
        { image: '🎭', title: '신년 한정 코스튬', subtitle: '50% 할인 진행중' },
        { image: '💼', title: '프리미엄 패키지', subtitle: '특별 혜택 포함' },
        { image: '✨', title: '이펙트 아이템', subtitle: 'NEW 출시' }
    ]
};

// 백엔드 데이터가 있으면 사용, 없으면 기본값 사용
const carouselData = window.carouselBackendData || defaultCarouselData;

// 디버깅: 데이터 확인
console.log('Carousel Data:', carouselData);
console.log('Events:', carouselData.events);
console.log('Cash Items:', carouselData.cashItems);

let carouselIndex = { event: 0, cash: 0 };

/**
 * Change carousel item
 */
function changeCarousel(type, direction) {
    // 'event' -> events, 'cash' -> cashItems (특이한 네이밍: cashItems)
    const items = (type === 'cash') ? carouselData.cashItems : carouselData.events;
    const display = document.getElementById((type === 'cash') ? 'cashDisplay' : 'eventDisplay');
    if (!display || !items || items.length === 0) return;
    
    carouselIndex[type] += direction;
    if (carouselIndex[type] < 0) carouselIndex[type] = items.length - 1;
    if (carouselIndex[type] >= items.length) carouselIndex[type] = 0;
    
    // Add transition effect
    display.style.transition = 'opacity 0.3s ease';
    display.style.opacity = '0';
    
    setTimeout(() => {
        const item = items[carouselIndex[type]];
        if (type === 'event') {
            // 이벤트 데이터 렌더링 (백엔드 형식 지원)
            const eventHtml = item.url 
                ? `<a href="${item.url}" target="_blank" style="text-decoration: none; color: inherit;">
                    <div class="event-icon">${item.icon || '⭐'}</div>
                    <div class="event-title-modern">${item.title}</div>
                    <div class="event-description">${item.description}</div>
                    <div class="event-date-modern">${item.date || ''}</div>
                   </a>`
                : `<div class="event-icon">${item.icon || '⭐'}</div>
                   <div class="event-title-modern">${item.title}</div>
                   <div class="event-description">${item.description}</div>
                   <div class="event-date-modern">${item.date || ''}</div>`;
            display.innerHTML = eventHtml;
        } else {
            // 캐시샵 데이터 렌더링 (백엔드 형식 지원)
            const cashHtml = item.url
                ? `<a href="${item.url}" target="_blank" style="text-decoration: none; color: inherit;">
                    <div class="cash-banner-image">${item.image || '💰'}</div>
                    <div class="cash-banner-title">${item.title}</div>
                    <div class="cash-banner-subtitle">${item.subtitle}</div>
                   </a>`
                : `<div class="cash-banner-image">${item.image || '💰'}</div>
                   <div class="cash-banner-title">${item.title}</div>
                   <div class="cash-banner-subtitle">${item.subtitle}</div>`;
            display.innerHTML = cashHtml;
        }
        display.style.opacity = '1';
    }, 150);
}

/**
 * Change event carousel
 */
export function changeEvent(direction) { 
    changeCarousel('event', direction); 
}

/**
 * Change cash item carousel
 */
export function changeCashItem(direction) { 
    changeCarousel('cash', direction); 
}

/**
 * Initialize carousel auto-rotation
 */
export function initializeCarousel() {
    // 초기 데이터 표시
    if (document.getElementById('eventDisplay')) {
        changeCarousel('event', 0);
    }
    if (document.getElementById('cashDisplay')) {
        changeCarousel('cash', 0);
    }

    // Auto-rotate event carousel
    setInterval(() => {
        if (document.getElementById('eventDisplay')) {
            changeEvent(1);
        }
    }, 5000);

    // Auto-rotate cash item carousel
    setInterval(() => {
        if (document.getElementById('cashDisplay')) {
            changeCashItem(1);
        }
    }, 6000);
}
