import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import '../../styles/common.css';

const Navigation = () => {
  const { user, isLoggedIn, logout, openLoginModal } = useAuth();
  const location = useLocation();

  const isActive = (path) => location.pathname === path ? 'active' : '';

  return (
    <nav className="navigation">
      <div className="nav-content">
        <div className="nav-left">
          <Link to="/" className={`nav-item ${isActive('/')}`}>홈</Link>
          <Link to="/chat" className={`nav-item ${isActive('/chat')}`}>CHAT BOT</Link>
          <Link to="/character" className={`nav-item ${isActive('/character')}`}>캐릭터 검색</Link>
          <a href="#cube" className="nav-item">큐브</a>
          <a href="#starforce" className="nav-item">스타포스</a>
        </div>
        
        <div className="nav-right">
          <button className="theme-toggle-btn" id="themeToggleBtn">🌙</button>
          
          {!isLoggedIn ? (
            <div className="nav-login-section">
              <button className="nav-login-btn" onClick={openLoginModal}>로그인</button>
            </div>
          ) : (
            <div className="nav-user-profile">
              <span className="nav-user-name">{user?.nickname || user?.username || '사용자'}</span>
              <button className="nav-profile-btn" onClick={() => alert('프로필 기능 준비 중')}>프로필</button>
              <button className="nav-logout-btn" onClick={logout}>로그아웃</button>
            </div>
          )}
        </div>
      </div>
    </nav>
  );
};

export default Navigation;