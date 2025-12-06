import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import Layout from '../components/common/Layout';
import * as homeApi from '../api/home';
import NoticeRoller from '../components/home/NoticeRoller';
import '../styles/home.css';
import '../styles/character.css';

const HomePage = () => {
  const navigate = useNavigate();
  const [searchText, setSearchText] = useState('');
  const [homeData, setHomeData] = useState({
    notices: { updates: [], events: [], cashshop: [] },
    ranking: []
  });
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await homeApi.getHomeData();
        setHomeData(response.data);
      } catch (error) {
        console.error("Failed to fetch home data:", error);
      } finally {
        setIsLoading(false);
      }
    };
    fetchData();
  }, []);

  const handleSearch = (e) => {
    e.preventDefault();
    if (searchText.trim()) {
      navigate('/chat', { state: { initialMessage: searchText } });
    }
  };

  const handleExampleClick = (text) => {
    navigate('/chat', { state: { initialMessage: text } });
  };

  return (
    <Layout>
      <div className="main-container">
        {/* Left Sidebar */}
        <aside className="sidebar-left">
            {/* Character Info Display */}
            <div className="character-info-display" id="characterInfoDisplay">
                <div className="character-info-header">
                    <div className="character-profile-avatar">🧙‍♂️</div>
                    <div className="character-profile-info">
                        <div className="character-profile-name" id="displayCharacterName">검색 결과</div>
                        <div className="character-profile-server" id="displayServerName">-</div>
                    </div>
                </div>
                
                <div className="character-detailed-stats">
                    <div className="detail-stat-row">
                        <span className="detail-stat-label">레벨</span>
                        <span className="detail-stat-value" id="displayCharacterLevel">-</span>
                    </div>
                    <div className="detail-stat-row">
                        <span className="detail-stat-label">직업</span>
                        <span className="detail-stat-value" id="displayCharacterJob">-</span>
                    </div>
                    <div className="detail-stat-row">
                        <span className="detail-stat-label">인기도</span>
                        <span className="detail-stat-value" id="displayCharacterFame">-</span>
                    </div>
                    <div className="detail-stat-row">
                        <span className="detail-stat-label">전투력</span>
                        <span className="detail-stat-value" id="displayCharacterPower">-</span>
                    </div>
                    <div className="detail-stat-row">
                        <span className="detail-stat-label">유니온</span>
                        <span className="detail-stat-value" id="displayUnionLevel">-</span>
                    </div>
                </div>
            </div>

            {/* Character Search Card */}
            <div className="character-search-card">
                    <div className="search-input-group">
                        <input type="text" className="character-search-input" id="characterSearchInput" placeholder="캐릭터 닉네임 입력" />
                        <button className="character-search-btn">
                            <span>검색</span>
                        </button>
                    </div>
                    
                    <div className="search-recent" id="recentSearches">
                        <div className="search-recent-title">최근 검색</div>
                        <div className="search-recent-list" id="recentSearchList">
                        </div>
                    </div>
            </div>
        </aside>

        {/* Main Content */}
        <main className="main-content">
            <h1 className="main-title">메이플 스토리</h1>
            <h2 className="main-subtitle">정보탐색 CHAT BOT</h2>
            <p className="main-description">
                메이플스토리의 모든 정보를 AI와 함께 탐색하세요.<br />
                스킬, 아이템, 사냥터, 보스 공략까지 궁금한 모든 것을 물어보세요!
            </p>
            
            {/* Main Search Box */}
            <div className="main-search-container">
                <form className="main-search-box" onSubmit={handleSearch}>
                    <input 
                        type="text" 
                        className="main-search-input" 
                        id="mainSearchInput" 
                        placeholder="메이플스토리에 관해 무엇이든 물어보세요..." 
                        value={searchText}
                        onChange={(e) => setSearchText(e.target.value)}
                    />
                    <button className="main-search-btn" type="submit">
                        <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor">
                            <path d="M2.01 21L23 12 2.01 3 2 10l15 2-15 2z"/>
                        </svg>
                    </button>
                </form>
            </div>
            
            {/* Search Hint Section */}
            <div className="search-hint">
                <div className="search-hint-title">💡 위 검색창에서 바로 질문해보세요!</div>
                <div className="search-hint-text">질문하면 ChatBot 페이지로 이동하면서 자동으로 질문이 전송됩니다</div>
                <div className="search-examples">
                    {['메르세데스 스킬 알려줘', '180렙 사냥터 추천', '뇌전 드랍 장소', '보스 공략법'].map(text => (
                        <span key={text} className="search-example" onClick={() => handleExampleClick(text)}>{text}</span>
                    ))}
                </div>
            </div>
        </main>

        {/* Right Sidebar */}
        <aside className="sidebar-right">
            <div className="sidebar-ad-long" style={{ minHeight: '500px', height: '100%', background: 'linear-gradient(180deg, #6a11cb 0%, #2575fc 100%)' }}>
              <div className="ad-header">SPONSORED</div>
              <div className="ad-content" style={{ flexDirection: 'column', justifyContent: 'center', height: '100%' }}>
                <div className="ad-image" style={{ fontSize: '80px', marginBottom: '20px' }}>🚀</div>
                <div className="ad-text" style={{ textAlign: 'center' }}>
                  <div className="ad-title" style={{ fontSize: '24px', marginBottom: '10px' }}>메이플스토리 M</div>
                  <div className="ad-description" style={{ fontSize: '16px', opacity: 0.9 }}>
                    언제 어디서나 즐기는<br/>메이플스토리!
                  </div>
                </div>
              </div>
              <div className="ad-button">설치하기 →</div>
            </div>
        </aside>
      </div>

      {/* Modern 4-Grid Bottom Section */}
      <div className="bottom-section">
        {/* Update Notice Card */}
        <div className="section-card">
            <div className="section-header update-header" style={{display:'flex', justifyContent:'space-between'}}>
                업데이트
                <div className="nav-arrows">
                    <button className="nav-arrow">◀</button>
                    <button className="nav-arrow">▶</button>
                </div>
            </div>
            <div className="section-content">
                <div className="notice-scroll-container" id="updateNoticeContainer">
                    <NoticeRoller notices={homeData.notices.updates} />
                </div>
            </div>
        </div>

        {/* Event Notice Card */}
        <div className="section-card">
            <div className="section-header event-header" style={{display:'flex', justifyContent:'space-between'}}>
                이벤트
                <div className="nav-arrows">
                    <button className="nav-arrow">◀</button>
                    <button className="nav-arrow">▶</button>
                </div>
            </div>
            <div className="section-content">
                <div className="notice-scroll-container" id="eventNoticeContainer">
                    {/* 이벤트는 롤링 대신 단순 표시 (기존 로직 확인 필요하나 일단 롤링으로 통일하거나 단일 표시) */}
                    {homeData.notices.events.length > 0 ? (
                        <div className="event-display">
                            <div className="event-icon">🎮</div>
                            <div className="event-title-modern">{homeData.notices.events[0].title}</div>
                            <div className="event-date-modern">{homeData.notices.events[0].date_event_start} ~ {homeData.notices.events[0].date_event_end}</div>
                        </div>
                    ) : (
                        <div>이벤트 없음</div>
                    )}
                </div>
            </div>
        </div>

        {/* CashShop Notice Card */}
        <div className="section-card">
            <div className="section-header cash-header" style={{display:'flex', justifyContent:'space-between'}}>
                캐쉬샵
                <div className="nav-arrows">
                    <button className="nav-arrow">◀</button>
                    <button className="nav-arrow">▶</button>
                </div>
            </div>
            <div className="section-content">
                <div className="notice-scroll-container" id="cashshopNoticeContainer">
                     {homeData.notices.cashshop.length > 0 ? (
                        <div className="cash-display">
                            <div className="cash-banner-image">🎭</div>
                            <div className="cash-banner-title">{homeData.notices.cashshop[0].title}</div>
                            <div className="cash-banner-subtitle">판매 종료: {homeData.notices.cashshop[0].date_sale_end || '상시'}</div>
                        </div>
                     ) : (
                        <div>캐시샵 정보 없음</div>
                     )}
                </div>
            </div>
        </div>

        {/* Combined Ranking Card */}
        <div className="section-card">
            <div className="section-header" style={{display:'flex', justifyContent:'space-between'}}>
                종합랭킹
                <div className="nav-arrows">
                    <button className="nav-arrow">◀</button>
                    <button className="nav-arrow">▶</button>
                </div>
            </div>
            <div className="section-content">
                <div className="ranking-scroll-container" id="rankingContainer">
                    {homeData.ranking.map((rank, idx) => (
                        <div className="ranking-item-modern" key={idx}>
                            <div className={`ranking-badge top-${rank.ranking}`}>{rank.ranking}</div>
                            <div className="ranking-player-info">
                                <span className="ranking-name">{rank.character_name}</span>
                                <span className="ranking-details">Lv.{rank.character_level}</span>
                            </div>
                        </div>
                    ))}
                </div>
            </div>
        </div>
      </div>
    </Layout>
  );
};

export default HomePage;
