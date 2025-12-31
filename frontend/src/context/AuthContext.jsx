import React, { createContext, useContext, useReducer, useEffect, useCallback } from 'react';
import * as authApi from '../api/auth';

const AuthContext = createContext();

const initialState = {
  isLoggedIn: false,
  user: null,
  isLoading: true,
  error: null,
  isLoginModalOpen: false, // 모달 상태 추가
};

const authReducer = (state, action) => {
  switch (action.type) {
    case 'AUTH_START':
      return { ...state, isLoading: true, error: null };
    case 'LOGIN_SUCCESS':
      return { 
        ...state, 
        isLoggedIn: true, 
        user: action.payload, 
        isLoading: false,
        error: null,
        isLoginModalOpen: false // 로그인 성공 시 모달 닫기
      };
    case 'LOGIN_FAILURE':
      return { 
        ...state, 
        isLoggedIn: false, 
        user: null, 
        isLoading: false,
        error: action.payload 
      };
    case 'LOGOUT':
      return { 
        ...state, 
        isLoggedIn: false, 
        user: null, 
        isLoading: false
      };
    case 'OPEN_LOGIN_MODAL':
      return { ...state, isLoginModalOpen: true, error: null };
    case 'CLOSE_LOGIN_MODAL':
      return { ...state, isLoginModalOpen: false, error: null };
    default:
      return state;
  }
};

export const AuthProvider = ({ children }) => {
  const [state, dispatch] = useReducer(authReducer, initialState);

  useEffect(() => {
    const checkAuth = async () => {
      dispatch({ type: 'AUTH_START' });
      try {
        const response = await authApi.getUserInfo();
        dispatch({ type: 'LOGIN_SUCCESS', payload: response.data });
      } catch (error) {
        dispatch({ type: 'LOGIN_FAILURE', payload: null });
      }
    };
    checkAuth();
  }, []);

  const login = async (username, password) => {
    dispatch({ type: 'AUTH_START' });
    try {
      const response = await authApi.login(username, password);
      dispatch({ type: 'LOGIN_SUCCESS', payload: response.data.user });
      return { success: true };
    } catch (error) {
      const errorMessage = error.response?.data?.error || '로그인 실패';
      dispatch({ type: 'LOGIN_FAILURE', payload: errorMessage });
      return { success: false, error: errorMessage };
    }
  };

  const logout = async () => {
    try {
      await authApi.logout();
    } catch (error) {
      console.error('Logout failed:', error);
    } finally {
      dispatch({ type: 'LOGOUT' });
    }
  };

  const openLoginModal = () => dispatch({ type: 'OPEN_LOGIN_MODAL' });
  const closeLoginModal = () => dispatch({ type: 'CLOSE_LOGIN_MODAL' });

  const value = {
    ...state,
    login,
    logout,
    openLoginModal,
    closeLoginModal
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