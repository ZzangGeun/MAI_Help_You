import client from './client';

export const getHomeData = () => 
  client.get('/api/home/data/');
