import client from './client';

// 세션 생성
export const createSession = () => 
  client.post('/mai_chat/api/chat/sessions/create/');

// 세션 목록 조회
export const getSessions = () => 
  client.get('/mai_chat/api/chat/sessions/');

// 세션 상세 조회 (레거시)
export const getSessionDetail = (sessionId) => 
  client.get(`/mai_chat/api/chat/sessions/${sessionId}/`);

// 세션의 메시지 목록 조회
export const getMessages = (sessionId) => 
  client.get(`/mai_chat/api/chat/sessions/${sessionId}/messages/`);

// 메시지 전송
export const sendMessage = (sessionId, content) => 
  client.post(`/mai_chat/api/chat/sessions/${sessionId}/send/`, { content });

// 세션 삭제
export const deleteSession = (sessionId) =>
  client.delete(`/mai_chat/api/chat/sessions/${sessionId}/delete/`);

