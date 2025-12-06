import client from './client';

export const createSession = () => 
  client.post('/chat/api/sessions/');

export const getSessions = () => 
  client.get('/chat/api/sessions/');

export const getSessionDetail = (sessionId) => 
  client.get(`/chat/api/sessions/${sessionId}/`);

export const getMessages = (sessionId) => 
  client.get(`/chat/api/sessions/${sessionId}/messages/`);

export const sendMessage = (sessionId, content) => 
  client.post(`/chat/api/sessions/${sessionId}/messages/`, { content });
