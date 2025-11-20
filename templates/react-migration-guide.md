# React 마이그레이션 가이드

## 🎯 주요 컴포넌트 구현 예시

### 1. App.jsx (메인 앱 컴포넌트)

```jsx
import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { AuthProvider } from './context/AuthContext';
import { ChatProvider } from './context/ChatContext';
import { NotificationProvider } from './context/NotificationContext';
import Header from './components/common/Header';
import Navigation from './components/common/Navigation';
import HomePage from './components/home/HomePage';
import ChatPage from './components/chat/ChatPage';
import FloatingButton from './components/common/FloatingButton';
import './styles/globals.css';

function App() {
  return (
    <AuthProvider>
      <ChatProvider>
        <NotificationProvider>
          <Router>
            <div className="App">
              <Header />
              <Navigation />
              
              <Routes>
                <Route path="/" element={<HomePage />} />
                <Route path="/chat" element={<ChatPage />} />
              </Routes>
              
              <FloatingButton />
            </div>
          </Router>
        </NotificationProvider>
      </ChatProvider>
    </AuthProvider>
  );
}

export default App;
```

### 2. AuthContext.js (인증 상태 관리)

```jsx
import React, { createContext, useContext, useReducer, useEffect } from 'react';
import { useLocalStorage } from '../hooks/useLocalStorage';

const AuthContext = createContext();

const authReducer = (state, action) => {
  switch (action.type) {
    case 'LOGIN':
      return {
        ...state,
        isLoggedIn: true,
        user: action.payload,
        loginTime: new Date().toISOString()
      };
    case 'LOGOUT':
      return {
        ...state,
        isLoggedIn: false,
        user: null,
        loginTime: null
      };
    default:
      return state;
  }
};

export const AuthProvider = ({ children }) => {
  const [savedAuth, setSavedAuth] = useLocalStorage('loginState', null);
  const [authState, dispatch] = useReducer(authReducer, {
    isLoggedIn: savedAuth?.isLoggedIn || false,
    user: savedAuth?.user || null,
    loginTime: savedAuth?.loginTime || null
  });

  useEffect(() => {
    setSavedAuth(authState);
  }, [authState, setSavedAuth]);

  const login = async (username, password) => {
    // 실제 API 호출 대신 시뮬레이션
    if (username.length >= 2) {
      dispatch({
        type: 'LOGIN',
        payload: { username }
      });
      return { success: true };
    }
    return { success: false, error: '올바른 아이디를 입력해주세요.' };
  };

  const logout = () => {
    dispatch({ type: 'LOGOUT' });
  };

  const value = {
    ...authState,
    login,
    logout
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within AuthProvider');
  }
  return context;
};
```

### 3. ChatContext.js (채팅 상태 관리)

```jsx
import React, { createContext, useContext, useReducer, useCallback } from 'react';
import { useAuth } from './AuthContext';
import { useLocalStorage } from '../hooks/useLocalStorage';
import { getAIResponse } from '../services/chatService';

const ChatContext = createContext();

const chatReducer = (state, action) => {
  switch (action.type) {
    case 'SET_TYPING':
      return { ...state, isTyping: action.payload };
    case 'ADD_MESSAGE':
      return {
        ...state,
        messages: [...state.messages, action.payload],
        history: [...state.history, action.payload]
      };
    case 'CLEAR_MESSAGES':
      return { ...state, messages: [] };
    case 'LOAD_HISTORY':
      return { ...state, history: action.payload };
    case 'CLEAR_HISTORY':
      return { ...state, history: [] };
    default:
      return state;
  }
};

export const ChatProvider = ({ children }) => {
  const { isLoggedIn } = useAuth();
  const [savedHistory, setSavedHistory] = useLocalStorage('chatHistory', []);
  
  const [chatState, dispatch] = useReducer(chatReducer, {
    messages: [],
    history: savedHistory,
    isTyping: false
  });

  const addMessage = useCallback((message, isUser = false) => {
    const newMessage = {
      id: Date.now(),
      type: isUser ? 'user' : 'bot',
      message,
      timestamp: new Date()
    };
    
    dispatch({ type: 'ADD_MESSAGE', payload: newMessage });
    
    // 로그인된 사용자만 히스토리 저장
    if (isLoggedIn) {
      setSavedHistory(prev => [...prev, newMessage]);
    }
  }, [isLoggedIn, setSavedHistory]);

  const sendMessage = useCallback(async (userMessage) => {
    if (chatState.isTyping) return;

    // 사용자 메시지 추가
    addMessage(userMessage, true);

    // 타이핑 상태 시작
    dispatch({ type: 'SET_TYPING', payload: true });

    try {
      // AI 응답 시뮬레이션
      setTimeout(() => {
        const response = getAIResponse(userMessage);
        addMessage(response, false);
        dispatch({ type: 'SET_TYPING', payload: false });
      }, 1000 + Math.random() * 2000);
    } catch (error) {
      dispatch({ type: 'SET_TYPING', payload: false });
      addMessage('죄송합니다. 오류가 발생했습니다.', false);
    }
  }, [chatState.isTyping, addMessage]);

  const clearHistory = useCallback(() => {
    dispatch({ type: 'CLEAR_HISTORY' });
    dispatch({ type: 'CLEAR_MESSAGES' });
    setSavedHistory([]);
  }, [setSavedHistory]);

  const value = {
    ...chatState,
    addMessage,
    sendMessage,
    clearHistory
  };

  return (
    <ChatContext.Provider value={value}>
      {children}
    </ChatContext.Provider>
  );
};

export const useChat = () => {
  const context = useContext(ChatContext);
  if (!context) {
    throw new Error('useChat must be used within ChatProvider');
  }
  return context;
};
```

### 4. LoginForm.jsx (로그인 폼 컴포넌트)

```jsx
import React, { useState } from 'react';
import { useAuth } from '../../context/AuthContext';
import { useNotification } from '../../context/NotificationContext';
import Button from '../ui/Button';
import Input from '../ui/Input';

const LoginForm = () => {
  const { login, isLoggedIn, user, logout } = useAuth();
  const { showNotification } = useNotification();
  const [credentials, setCredentials] = useState({
    username: '',
    password: ''
  });
  const [loading, setLoading] = useState(false);

  const handleChange = (e) => {
    setCredentials({
      ...credentials,
      [e.target.name]: e.target.value
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!credentials.username || !credentials.password) {
      showNotification('아이디와 비밀번호를 입력해주세요.', 'warning');
      return;
    }

    setLoading(true);
    
    try {
      const result = await login(credentials.username, credentials.password);
      
      if (result.success) {
        showNotification(`${credentials.username}님, 환영합니다!`, 'success');
        setCredentials({ username: '', password: '' });
      } else {
        showNotification(result.error, 'error');
      }
    } catch (error) {
      showNotification('로그인 중 오류가 발생했습니다.', 'error');
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = () => {
    logout();
    showNotification('로그아웃되었습니다.', 'info');
  };

  if (isLoggedIn) {
    return (
      <div className="user-profile-card">
        <div className="profile-header">
          <div className="profile-avatar-large">👤</div>
          <div className="profile-info-main">
            <div className="profile-name-main">{user?.username}</div>
            <div className="profile-status">온라인</div>
          </div>
        </div>
        
        <div className="profile-stats-simple">
          <div className="stat-item">
            <span className="stat-number">15</span>
            <span className="stat-text">질문</span>
          </div>
          <div className="stat-item">
            <span className="stat-number">42</span>
            <span className="stat-text">답변</span>
          </div>
          <div className="stat-item">
            <span className="stat-number">7일</span>
            <span className="stat-text">활동</span>
          </div>
        </div>
        
        <Button onClick={handleLogout} variant="danger" size="small">
          로그아웃
        </Button>
      </div>
    );
  }

  return (
    <form onSubmit={handleSubmit} className="login-form">
      <div className="login-header">
        <h3>로그인</h3>
        <p>채팅 히스토리와 개인화된 서비스를 이용하려면 로그인하세요.</p>
      </div>
      
      <Input
        type="text"
        name="username"
        placeholder="아이디"
        value={credentials.username}
        onChange={handleChange}
        required
      />
      
      <Input
        type="password"
        name="password"
        placeholder="비밀번호"
        value={credentials.password}
        onChange={handleChange}
        required
      />
      
      <Button 
        type="submit" 
        loading={loading}
        variant="primary"
        fullWidth
      >
        {loading ? '로그인 중...' : '로그인'}
      </Button>
    </form>
  );
};

export default LoginForm;
```

### 5. ChatArea.jsx (채팅 영역 컴포넌트)

```jsx
import React, { useRef, useEffect } from 'react';
import { useChat } from '../../context/ChatContext';
import { useAuth } from '../../context/AuthContext';
import MessageBubble from './MessageBubble';
import TypingIndicator from './TypingIndicator';
import WelcomeMessage from './WelcomeMessage';

const ChatArea = () => {
  const { messages, isTyping } = useChat();
  const { isLoggedIn } = useAuth();
  const messagesEndRef = useRef(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isTyping]);

  return (
    <div className="chat-messages">
      {messages.length === 0 ? (
        <WelcomeMessage />
      ) : (
        messages.map((message) => (
          <MessageBubble 
            key={message.id} 
            message={message} 
          />
        ))
      )}
      
      {isTyping && <TypingIndicator />}
      <div ref={messagesEndRef} />
    </div>
  );
};

export default ChatArea;
```

### 6. useLocalStorage Hook

```jsx
import { useState, useEffect } from 'react';

export const useLocalStorage = (key, initialValue) => {
  const [storedValue, setStoredValue] = useState(() => {
    try {
      const item = window.localStorage.getItem(key);
      return item ? JSON.parse(item) : initialValue;
    } catch (error) {
      console.error(`Error reading localStorage key "${key}":`, error);
      return initialValue;
    }
  });

  const setValue = (value) => {
    try {
      const valueToStore = value instanceof Function ? value(storedValue) : value;
      setStoredValue(valueToStore);
      window.localStorage.setItem(key, JSON.stringify(valueToStore));
    } catch (error) {
      console.error(`Error setting localStorage key "${key}":`, error);
    }
  };

  return [storedValue, setValue];
};
```

## 📦 필수 패키지 목록

```json
{
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "react-router-dom": "^6.8.0",
    "styled-components": "^5.3.9",
    "lucide-react": "^0.263.1",
    "uuid": "^9.0.0"
  },
  "devDependencies": {
    "@types/react": "^18.2.0",
    "@types/react-dom": "^18.2.0",
    "tailwindcss": "^3.3.0"
  }
}
```

## 🚀 마이그레이션 단계별 진행

1. **1단계**: Create React App으로 기본 프로젝트 생성
2. **2단계**: Context API로 전역 상태 관리 설정
3. **3단계**: 공통 컴포넌트 (Header, Navigation) 구현
4. **4단계**: 홈페이지 컴포넌트들 구현
5. **5단계**: 채팅 관련 컴포넌트들 구현
6. **6단계**: 사이드바 컴포넌트들 구현
7. **7단계**: 스타일링 및 반응형 디자인 적용
8. **8단계**: 테스트 및 최적화

이렇게 React로 마이그레이션하면 더 모듈화되고 유지보수가 쉬운 코드 구조를 가질 수 있습니다!