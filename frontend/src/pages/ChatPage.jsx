import React, { useState, useEffect, useRef } from 'react';
import { useAuth } from '../context/AuthContext';
import { useNavigate, useLocation } from 'react-router-dom';
import Layout from '../components/common/Layout';
import * as chatApi from '../api/chat';
import '../styles/chat.css';

const ChatPage = () => {
  const { user, logout, isLoggedIn } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  
  const [sessions, setSessions] = useState([]);
  const [currentSessionId, setCurrentSessionId] = useState(null);
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isInitializing, setIsInitializing] = useState(true);
  
  const messagesEndRef = useRef(null);

  // 홈에서 전달된 초기 메시지 처리
  useEffect(() => {
    if (location.state?.initialMessage) {
      setInput(location.state.initialMessage);
      // 상태 초기화 후 자동 전송은 세션 생성 로직과 맞물려야 하므로 일단 입력창에만 채움
      // 또는 자동 전송 로직 추가 가능
    }
  }, [location.state]);

  // 1. 로그인 체크
  useEffect(() => {
    if (!isLoggedIn) {
      navigate('/login');
    }
  }, [isLoggedIn, navigate]);

  // 2. 초기 세션 로드 및 생성
  useEffect(() => {
    if (!isLoggedIn) return;

    const initializeChat = async () => {
      try {
        const response = await chatApi.getSessions();
        const sessionList = response.data;
        setSessions(sessionList);

        if (sessionList.length > 0) {
          selectSession(sessionList[0].id);
        } else {
          handleNewChat();
        }
      } catch (error) {
        console.error("Failed to load sessions:", error);
      } finally {
        setIsInitializing(false);
      }
    };

    initializeChat();
  }, [isLoggedIn]);

  // 3. 스크롤 자동 이동
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  // 세션 선택 함수
  const selectSession = async (sessionId) => {
    setCurrentSessionId(sessionId);
    setIsLoading(true);
    try {
      const response = await chatApi.getMessages(sessionId);
      const formattedMessages = response.data.map(msg => ({
        role: msg.is_user ? 'user' : 'assistant',
        content: msg.content
      }));
      setMessages(formattedMessages);
    } catch (error) {
      console.error("Failed to load messages:", error);
    } finally {
      setIsLoading(false);
    }
  };

  // 새 채팅 시작 함수
  const handleNewChat = async () => {
    try {
      const response = await chatApi.createSession();
      const newSession = response.data;
      setSessions(prev => [newSession, ...prev]);
      setCurrentSessionId(newSession.id);
      setMessages([]);
    } catch (error) {
      console.error("Failed to create session:", error);
    }
  };

  // 메시지 전송 함수
  const handleSend = async (e) => {
    e.preventDefault();
    if (!input.trim() || isLoading || !currentSessionId) return;

    const userMessage = { role: 'user', content: input };
    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setIsLoading(true);

    try {
      const response = await chatApi.sendMessage(currentSessionId, input);
      const aiMessage = { 
        role: 'assistant', 
        content: response.data.ai_message.content 
      };
      setMessages(prev => [...prev, aiMessage]);
    } catch (error) {
      console.error("Send error:", error);
      setMessages(prev => [...prev, { 
        role: 'assistant', 
        content: "오류가 발생했습니다. 잠시 후 다시 시도해주세요." 
      }]);
    } finally {
      setIsLoading(false);
    }
  };

  // --- Left Sidebar (Chat Specific) ---
  const leftSidebar = (
    <>
      {/* User Profile */}
      <div className="user-profile-container">
        <div className="profile-section">
          <div className="profile-avatar">👤</div>
          <div className="profile-info">
            <div className="profile-name-section">
              <div className="profile-name">{user?.maple_nickname || user?.username || 'User'}</div>
              <div className="profile-server">
                <span className="server-icon"></span>LUNA
              </div>
            </div>
            <div className="divider"></div>
            <div className="profile-stats">
              <div className="stat-row">
                <span className="stat-label">Lv.</span>
                <span className="stat-value">285</span>
              </div>
              <div className="stat-row">
                <span className="stat-label">직업</span>
                <span className="stat-value">아델</span>
              </div>
              <div className="stat-row">
                <span className="stat-label">길드</span>
                <span className="stat-value">MAI</span>
              </div>
            </div>
          </div>
          <div className="detail-link" onClick={() => alert('상세 정보 기능 구현 예정')}>상세</div>
        </div>
        
        <div className="profile-actions">
          <button className="logout-btn" onClick={logout}>로그아웃</button>
        </div>
      </div>

      {/* Chat History */}
      <div className="chat-history-container">
        <div className="chat-history-header">
          채팅 기록
        </div>
        <div className="chat-history-content">
            <button className="btn btn-outline" style={{width: '100%', marginBottom: '10px'}} onClick={handleNewChat}>+ 새 채팅</button>
          
          {sessions.map(session => (
            <div 
              key={session.id} 
              className="history-item" 
              onClick={() => selectSession(session.id)}
              style={{cursor: 'pointer', opacity: session.id === currentSessionId ? 1 : 0.7}}
            >
              <div className="history-date">
                  {new Date(session.created_at).toLocaleDateString()} 
                  {session.id === currentSessionId && ' (현재)'}
              </div>
              <div className="history-text">
                {session.last_message ? session.last_message.substring(0, 20) + '...' : `채팅 #${session.id}`}
              </div>
            </div>
          ))}
        </div>
      </div>
    </>
  );

  // --- Right Sidebar (Ad) ---
  const rightSidebar = (
    <div className="sidebar-ad-long">
      <div className="ad-header">ADVERTISEMENT</div>
        <div className="ad-content">
            <div className="ad-text">
                <div className="ad-title">메이플스토리</div>
                <div className="ad-subtitle">지금 시작하세요!</div>
            </div>
        </div>
    </div>
  );

  return (
    <Layout 
      leftSidebar={leftSidebar} 
      rightSidebar={rightSidebar} 
      layoutClass="chatbot-layout"
    >
      <div className="chat-header">
        <div className="chat-title">MAI HELP YOU</div>
        <div className="chat-subtitle">메이플스토리 AI 챗봇</div>
      </div>

      <div className="chat-messages" id="chatMessages">
        {messages.length === 0 && !isLoading && (
          <div className="welcome-message">
            <div className="welcome-icon">🧚‍♀️</div>
            <div className="welcome-text">안녕하세요! 무엇을 도와드릴까요?</div>
            <div className="welcome-subtext">메이플스토리에 대해 궁금한 점을 물어보세요.</div>
          </div>
        )}

        {messages.map((msg, idx) => (
          <div key={idx} className={`message ${msg.role === 'user' ? 'user' : 'bot'}`}>
            <div className="message-avatar">
              {msg.role === 'user' ? '👤' : '🧚‍♀️'}
            </div>
            <div className="message-content">
              {msg.content}
            </div>
          </div>
        ))}

        {isLoading && (
          <div className="message bot">
            <div className="message-avatar">🧚‍♀️</div>
            <div className="message-content">
              <div className="typing-dots">
                  <div className="typing-dot"></div>
                  <div className="typing-dot"></div>
                  <div className="typing-dot"></div>
              </div>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      <div className="chat-input-container">
        <form className="chat-input-wrapper" onSubmit={handleSend}>
            <textarea 
              className="chat-input-main"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="메시지를 입력하세요..."
              onKeyDown={(e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                  e.preventDefault();
                  handleSend(e);
                }
              }}
            />
          <button 
              type="submit" 
              className="chat-send-main" 
              disabled={isLoading || !currentSessionId}
          >
            ➤
          </button>
        </form>
      </div>
    </Layout>
  );
};

export default ChatPage;
