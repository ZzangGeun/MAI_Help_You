import client from './client';

export const getHomeData = () => 
  client.get('/api/home/data/');

export const searchCharacter = (name) =>
  client.get('/character/api/search/', { params: { character_name: name } });
