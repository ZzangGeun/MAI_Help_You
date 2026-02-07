import client from './client';

export const login = (username, password) => 
  client.post('/accounts/api/login/', { username, password });

export const logout = () => 
  client.post('/accounts/api/logout/');

export const signup = (userData) => 
  client.post('/accounts/api/signup/', userData);

export const getUserInfo = () => 
  client.get('/accounts/api/user/');
