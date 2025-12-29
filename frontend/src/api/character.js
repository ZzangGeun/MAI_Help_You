import client from './client';

// 캐릭터 정보 검색
export const searchCharacter = (characterName) =>
    client.get(`/character/api/search/?character_name=${encodeURIComponent(characterName)}`);
