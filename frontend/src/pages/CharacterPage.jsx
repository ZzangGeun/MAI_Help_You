import React, { useState } from 'react';
import Layout from '../components/common/Layout';
import * as characterApi from '../api/character';
import '../styles/character.css';
import '../styles/common.css';

const CharacterPage = () => {
    const [searchName, setSearchName] = useState('');
    const [characterData, setCharacterData] = useState(null);
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState(null);
    const [activeTab, setActiveTab] = useState('basic');

    const handleSearch = async (e) => {
        e.preventDefault();
        if (!searchName.trim()) return;

        setIsLoading(true);
        setError(null);
        setCharacterData(null);

        try {
            const response = await characterApi.searchCharacter(searchName.trim());
            if (response.data.status === 'success') {
                setCharacterData(response.data.data);
            } else {
                setError(response.data.error || '캐릭터를 찾을 수 없습니다.');
            }
        } catch (err) {
            console.error('Search error:', err);
            if (err.response?.data?.error) {
                setError(err.response.data.error);
            } else {
                setError('캐릭터 검색 중 오류가 발생했습니다.');
            }
        } finally {
            setIsLoading(false);
        }
    };

    // 기본 정보 렌더링
    const renderBasicInfo = () => {
        const basicInfo = characterData?.basic_info;
        if (!basicInfo) return <div className="info-card"><p>기본 정보가 없습니다.</p></div>;

        const fields = [
            { label: '닉네임', value: basicInfo.character_name },
            { label: '레벨', value: basicInfo.character_level },
            { label: '직업', value: basicInfo.character_class },
            { label: '직업 차수', value: basicInfo.character_class_level },
            { label: '월드', value: basicInfo.world_name },
            { label: '성별', value: basicInfo.character_gender },
            { label: '길드', value: basicInfo.character_guild_name || '없음' },
            { label: '인기도', value: basicInfo.character_popularity },
            { label: '경험치 비율', value: `${basicInfo.character_exp_rate}%` },
            { label: '해방 퀘스트', value: basicInfo.liberation_quest_clear === '1' ? '완료' : '미완료' },
            { label: '캐릭터 생성일', value: basicInfo.character_date_create?.split('T')[0] },
        ];

        return (
            <div className="info-card">
                <h3 className="info-card-title">📋 기본 정보</h3>
                <div className="stat-grid">
                    {fields.map(({ label, value }, idx) => (
                        <div key={idx} className="stat-item">
                            <span className="stat-label">{label}</span>
                            <span className="stat-value">{value ?? '-'}</span>
                        </div>
                    ))}
                </div>
            </div>
        );
    };

    // 스탯 정보 렌더링
    const renderStatInfo = () => {
        const statInfo = characterData?.stat_info;
        if (!statInfo) return <div className="info-card"><p>스탯 정보가 없습니다.</p></div>;

        // 주요 스탯 그룹
        const combatStats = [
            { label: '전투력', value: statInfo['전투력'] },
            { label: '최소 스탯공격력', value: statInfo['최소_스탯공격력'] },
            { label: '최대 스탯공격력', value: statInfo['최대_스탯공격력'] },
            { label: '데미지', value: `${statInfo['데미지']}%` },
            { label: '보스 데미지', value: `${statInfo['보스_몬스터_데미지']}%` },
            { label: '최종 데미지', value: `${statInfo['최종_데미지']}%` },
            { label: '방어율 무시', value: `${statInfo['방어율_무시']}%` },
            { label: '크리티컬 확률', value: `${statInfo['크리티컬_확률']}%` },
            { label: '크리티컬 데미지', value: `${statInfo['크리티컬_데미지']}%` },
        ];

        const mainStats = [
            { label: 'STR', value: statInfo['STR'] },
            { label: 'DEX', value: statInfo['DEX'] },
            { label: 'INT', value: statInfo['INT'] },
            { label: 'LUK', value: statInfo['LUK'] },
            { label: 'HP', value: statInfo['HP'] },
            { label: 'MP', value: statInfo['MP'] },
            { label: '공격력', value: statInfo['공격력'] },
            { label: '마력', value: statInfo['마력'] },
        ];

        const forceStats = [
            { label: '스타포스', value: statInfo['스타포스'] },
            { label: '아케인포스', value: statInfo['아케인포스'] },
            { label: '어센틱포스', value: statInfo['어센틱포스'] },
        ];

        const utilityStats = [
            { label: '아이템 드롭률', value: `${statInfo['아이템_드롭률']}%` },
            { label: '메소 획득량', value: `${statInfo['메소_획득량']}%` },
            { label: '버프 지속시간', value: `${statInfo['버프_지속시간']}%` },
            { label: '추가 경험치', value: `${statInfo['추가_경험치_획득']}%` },
        ];

        return (
            <>
                <div className="info-card">
                    <h3 className="info-card-title">⚔️ 전투 스탯</h3>
                    <div className="stat-grid">
                        {combatStats.map(({ label, value }, idx) => (
                            <div key={idx} className="stat-item">
                                <span className="stat-label">{label}</span>
                                <span className="stat-value" style={{ color: 'var(--primary-color)', fontWeight: '700' }}>
                                    {value ?? '-'}
                                </span>
                            </div>
                        ))}
                    </div>
                </div>

                <div className="info-card">
                    <h3 className="info-card-title">📊 기본 스탯</h3>
                    <div className="stat-grid">
                        {mainStats.map(({ label, value }, idx) => (
                            <div key={idx} className="stat-item">
                                <span className="stat-label">{label}</span>
                                <span className="stat-value">{value ?? '-'}</span>
                            </div>
                        ))}
                    </div>
                </div>

                <div className="info-card">
                    <h3 className="info-card-title">✨ 포스 / 유틸</h3>
                    <div className="stat-grid">
                        {[...forceStats, ...utilityStats].map(({ label, value }, idx) => (
                            <div key={idx} className="stat-item">
                                <span className="stat-label">{label}</span>
                                <span className="stat-value">{value ?? '-'}</span>
                            </div>
                        ))}
                    </div>
                </div>
            </>
        );
    };

    // 장비 정보 렌더링
    const renderEquipmentInfo = () => {
        const itemEquipment = characterData?.item_info?.item_equipment;
        if (!itemEquipment) return <div className="info-card"><p>장비 정보가 없습니다.</p></div>;

        const equipmentList = Object.entries(itemEquipment);

        // 잠재 등급 색상
        const getGradeColor = (grade) => {
            if (!grade) return '#999';
            if (grade.includes('레전드리')) return '#00ff00';
            if (grade.includes('유니크')) return '#ffcc00';
            if (grade.includes('에픽')) return '#cc66ff';
            if (grade.includes('레어')) return '#66ccff';
            return '#999';
        };

        return (
            <div className="info-card">
                <h3 className="info-card-title">🎒 장비 정보 ({equipmentList.length}개)</h3>
                <div className="equipment-grid">
                    {equipmentList.map(([slot, item], idx) => (
                        <div key={idx} className="equipment-item">
                            <div className="equipment-icon">
                                {item.icon ? (
                                    <img src={item.icon} alt={item.name} />
                                ) : (
                                    <span style={{ fontSize: '32px' }}>❓</span>
                                )}
                            </div>
                            <div className="equipment-name">{item.name}</div>
                            <div className="equipment-part">{item.part}</div>
                            {item.starforce && item.starforce !== '0' && (
                                <div className="equipment-starforce">⭐ {item.starforce}</div>
                            )}
                            {item.potential_option_grade && (
                                <div
                                    className="equipment-potential"
                                    style={{
                                        background: `${getGradeColor(item.potential_option_grade)}20`,
                                        color: getGradeColor(item.potential_option_grade),
                                        border: `1px solid ${getGradeColor(item.potential_option_grade)}40`
                                    }}
                                >
                                    {item.potential_option_grade}
                                </div>
                            )}
                        </div>
                    ))}
                </div>
            </div>
        );
    };

    // Raw JSON 렌더링
    const renderRawData = () => {
        if (!characterData) return null;

        return (
            <div className="info-card">
                <h3 className="info-card-title">🔧 전체 JSON 데이터</h3>
                <pre className="raw-data-pre">
                    {JSON.stringify(characterData, null, 2)}
                </pre>
            </div>
        );
    };

    // 프로필 정보
    const basicInfo = characterData?.basic_info;

    return (
        <Layout>
            <div className="main-content">
                {/* 검색 헤더 */}
                <div style={{ marginBottom: '24px' }}>
                    <h1 style={{ fontSize: '28px', fontWeight: '700', color: 'var(--text-primary)', marginBottom: '16px' }}>
                        🍁 캐릭터 검색
                    </h1>
                    <form onSubmit={handleSearch} className="search-input-group">
                        <input
                            type="text"
                            className="character-search-input"
                            placeholder="캐릭터 닉네임을 입력하세요"
                            value={searchName}
                            onChange={(e) => setSearchName(e.target.value)}
                        />
                        <button type="submit" className="character-search-btn" disabled={isLoading}>
                            {isLoading ? '검색 중...' : '🔍 검색'}
                        </button>
                    </form>
                </div>

                {/* 에러 메시지 */}
                {error && (
                    <div style={{
                        padding: '16px',
                        background: '#fff5f5',
                        border: '1px solid #ffcdd2',
                        borderRadius: '12px',
                        color: '#c62828',
                        marginBottom: '20px'
                    }}>
                        ⚠️ {error}
                    </div>
                )}

                {/* 로딩 상태 */}
                {isLoading && (
                    <div style={{ textAlign: 'center', padding: '40px', color: 'var(--text-muted)' }}>
                        <div style={{ fontSize: '48px', marginBottom: '16px', animation: 'spin 1s linear infinite' }}>🔄</div>
                        캐릭터 정보를 불러오는 중...
                    </div>
                )}

                {/* 캐릭터 정보 */}
                {characterData && !isLoading && (
                    <>
                        {/* 캐릭터 프로필 카드 */}
                        <div className="character-info-display" style={{ marginBottom: '24px' }}>
                            <div className="character-info-header">
                                <div className="character-profile-avatar" style={{ overflow: 'hidden' }}>
                                    {basicInfo?.character_image ? (
                                        <img
                                            src={basicInfo.character_image}
                                            alt={basicInfo.character_name}
                                            style={{ width: '100%', height: '100%', objectFit: 'contain' }}
                                        />
                                    ) : '🧙'}
                                </div>
                                <div>
                                    <div className="character-profile-name">{basicInfo?.character_name}</div>
                                    <div className="character-profile-server">
                                        {basicInfo?.world_name} | Lv.{basicInfo?.character_level} {basicInfo?.character_class}
                                    </div>
                                    <div style={{ marginTop: '8px', fontSize: '14px', color: 'var(--text-muted)' }}>
                                        ⚔️ 전투력: <strong style={{ color: 'var(--primary-color)' }}>
                                            {Number(characterData?.stat_info?.['전투력']).toLocaleString()}
                                        </strong>
                                    </div>
                                </div>
                            </div>
                        </div>

                        {/* 탭 네비게이션 */}
                        <div className="details-tabs">
                            <button
                                className={`tab-button ${activeTab === 'basic' ? 'active' : ''}`}
                                onClick={() => setActiveTab('basic')}
                            >
                                기본 정보
                            </button>
                            <button
                                className={`tab-button ${activeTab === 'stat' ? 'active' : ''}`}
                                onClick={() => setActiveTab('stat')}
                            >
                                스탯 정보
                            </button>
                            <button
                                className={`tab-button ${activeTab === 'equipment' ? 'active' : ''}`}
                                onClick={() => setActiveTab('equipment')}
                            >
                                장비 정보
                            </button>
                            <button
                                className={`tab-button ${activeTab === 'raw' ? 'active' : ''}`}
                                onClick={() => setActiveTab('raw')}
                            >
                                Raw JSON
                            </button>
                        </div>

                        {/* 탭 컨텐츠 */}
                        <div className={`tab-content ${activeTab === 'basic' ? 'active' : ''}`}>
                            {renderBasicInfo()}
                        </div>
                        <div className={`tab-content ${activeTab === 'stat' ? 'active' : ''}`}>
                            {renderStatInfo()}
                        </div>
                        <div className={`tab-content ${activeTab === 'equipment' ? 'active' : ''}`}>
                            {renderEquipmentInfo()}
                        </div>
                        <div className={`tab-content ${activeTab === 'raw' ? 'active' : ''}`}>
                            {renderRawData()}
                        </div>
                    </>
                )}

                {/* 검색 전 안내 */}
                {!characterData && !isLoading && !error && (
                    <div style={{ textAlign: 'center', padding: '60px 20px', color: 'var(--text-muted)' }}>
                        <div style={{ fontSize: '64px', marginBottom: '20px' }}>🍁</div>
                        <h2 style={{ fontSize: '22px', fontWeight: '600', marginBottom: '12px', color: 'var(--text-secondary)' }}>
                            캐릭터를 검색해보세요
                        </h2>
                        <p>메이플스토리 캐릭터 닉네임을 입력하면 상세 정보를 확인할 수 있습니다.</p>
                    </div>
                )}
            </div>
        </Layout>
    );
};

export default CharacterPage;
