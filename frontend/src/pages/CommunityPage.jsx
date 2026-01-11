import React, { useState, useEffect } from 'react';
import Layout from '../components/common/Layout';
import { useAuth } from '../context/AuthContext';
import '../styles/community.css';

const CommunityPage = () => {
    const { user, isLoggedIn, openLoginModal } = useAuth();
    const [posts, setPosts] = useState([]);
    const [categories, setCategories] = useState([
        { id: 'all', name: '전체', count: 0 },
        { id: 'free', name: '자유', count: 0 },
        { id: 'question', name: '질문', count: 0 },
        { id: 'guide', name: '공략', count: 0 },
        { id: 'trade', name: '거래', count: 0 },
        { id: 'guild', name: '길드', count: 0 }
    ]);
    const [selectedCategory, setSelectedCategory] = useState('all');
    const [searchText, setSearchText] = useState('');
    const [sortBy, setSortBy] = useState('latest');
    const [isLoading, setIsLoading] = useState(true);
    const [showWriteModal, setShowWriteModal] = useState(false);
    const [writeForm, setWriteForm] = useState({
        title: '',
        content: '',
        category: 'free'
    });

    useEffect(() => {
        fetchPosts();
    }, [selectedCategory, sortBy]);

    const fetchPosts = async () => {
        setIsLoading(true);
        try {
            const mockPosts = [
                {
                    id: 1,
                    title: '메르세데스 5차 스킬 공략 공유합니다',
                    content: '오늘 메르세데스 5차 스킬 퀘스트를 클리어해서 팁 공유드립니다...',
                    category: 'guide',
                    author: '메르공략왕',
                    authorLevel: 250,
                    views: 1250,
                    likes: 45,
                    comments: 23,
                    createdAt: '2024-01-10 15:30',
                    isRecommended: true
                },
                {
                    id: 2,
                    title: '180렙 사냥터 어디가 좋을까요?',
                    content: '현재 180레벨 전사인데 사냥터 추천해주세요...',
                    category: 'question',
                    author: '초보전사',
                    authorLevel: 180,
                    views: 320,
                    likes: 12,
                    comments: 18,
                    createdAt: '2024-01-10 14:15'
                },
                {
                    id: 3,
                    title: '레전드리 장비 팝니다',
                    content: '캐시 아이템으로 레전드리 장비 정리합니다...',
                    category: 'trade',
                    author: '장비장수',
                    authorLevel: 200,
                    views: 890,
                    likes: 8,
                    comments: 15,
                    createdAt: '2024-01-10 13:20'
                },
                {
                    id: 4,
                    title: '우리 길드원 모집합니다!',
                    content: '활동적인 길드에 오실 분을 모집합니다...',
                    category: 'guild',
                    author: '길드마스터',
                    authorLevel: 260,
                    views: 450,
                    likes: 25,
                    comments: 32,
                    createdAt: '2024-01-10 12:00'
                },
                {
                    id: 5,
                    title: '오늘 업데이트 정말 좋네요',
                    content: '이번 업데이트로 인해서 게임이 훨씬 재밌어졌어요...',
                    category: 'free',
                    author: '메이플러버',
                    authorLevel: 195,
                    views: 670,
                    likes: 56,
                    comments: 41,
                    createdAt: '2024-01-10 11:45',
                    isRecommended: true
                }
            ];

            const filteredPosts = selectedCategory === 'all'
                ? mockPosts
                : mockPosts.filter(post => post.category === selectedCategory);

            const sortedPosts = [...filteredPosts].sort((a, b) => {
                if (sortBy === 'latest') {
                    return new Date(b.createdAt) - new Date(a.createdAt);
                } else if (sortBy === 'popular') {
                    return (b.likes + b.comments) - (a.likes + a.comments);
                } else if (sortBy === 'views') {
                    return b.views - a.views;
                }
                return 0;
            });

            setPosts(sortedPosts);

            const categoryCounts = categories.map(cat => ({
                ...cat,
                count: cat.id === 'all' ? mockPosts.length : mockPosts.filter(post => post.category === cat.id).length
            }));
            setCategories(categoryCounts);
        } catch (error) {
            console.error('Failed to fetch posts:', error);
        } finally {
            setIsLoading(false);
        }
    };

    const handleWritePost = () => {
        if (!isLoggedIn) {
            openLoginModal();
            return;
        }
        setShowWriteModal(true);
    };

    const handleSubmitPost = (e) => {
        e.preventDefault();
        const newPost = {
            id: posts.length + 1,
            title: writeForm.title,
            content: writeForm.content,
            category: writeForm.category,
            author: user?.nickname || user?.username || '익명',
            authorLevel: user?.profile?.level || 100,
            views: 0,
            likes: 0,
            comments: 0,
            createdAt: new Date().toLocaleString('ko-KR', {
                year: 'numeric',
                month: '2-digit',
                day: '2-digit',
                hour: '2-digit',
                minute: '2-digit'
            }).replace(/\./g, '-').replace(/:\s*$/, '')
        };

        setPosts([newPost, ...posts]);
        setShowWriteModal(false);
        setWriteForm({ title: '', content: '', category: 'free' });
    };

    const handleSearch = (e) => {
        e.preventDefault();
        console.log('Searching for:', searchText);
    };

    const getCategoryIcon = (categoryId) => {
        const icons = {
            free: '💬',
            question: '❓',
            guide: '📖',
            trade: '💰',
            guild: '🏰'
        };
        return icons[categoryId] || '📄';
    };

    return (
        <Layout layoutClass="narrow-layout">
            <div className="community-container">
                <div className="community-header">
                    <h1>메이플 커뮤니티</h1>
                    <p>메이플 스토리 플레이어들이 소통하는 공간</p>
                </div>

                <div className="community-controls">
                    <div className="category-tabs">
                        {categories.map(category => (
                            <button
                                key={category.id}
                                className={`category-tab ${selectedCategory === category.id ? 'active' : ''}`}
                                onClick={() => setSelectedCategory(category.id)}
                            >
                                <span className="category-icon">
                                    {category.id === 'all' ? '🌟' : getCategoryIcon(category.id)}
                                </span>
                                <span className="category-name">{category.name}</span>
                                <span className="category-count">({category.count})</span>
                            </button>
                        ))}
                    </div>

                    <div className="community-actions">
                        <form className="search-form" onSubmit={handleSearch}>
                            <input
                                type="text"
                                className="search-input"
                                placeholder="제목 or 내용 검색..."
                                value={searchText}
                                onChange={(e) => setSearchText(e.target.value)}
                            />
                            <button type="submit" className="search-btn">검색</button>
                        </form>

                        <div className="sort-dropdown">
                            <select value={sortBy} onChange={(e) => setSortBy(e.target.value)} className="sort-select">
                                <option value="latest">최신순</option>
                                <option value="popular">인기순</option>
                                <option value="views">조회순</option>
                            </select>
                        </div>

                        <button className="write-btn" onClick={handleWritePost}>
                            ✍️ 글쓰기
                        </button>
                    </div>
                </div>

                <div className="posts-container">
                    {isLoading ? (
                        <div className="loading">로딩 중...</div>
                    ) : posts.length === 0 ? (
                        <div className="empty-posts">
                            <div className="empty-icon">📭</div>
                            <p>아직 게시글이 없습니다.</p>
                            <p>첫 번째 게시글을 작성해보세요!</p>
                        </div>
                    ) : (
                        <div className="posts-list">
                            {posts.map(post => (
                                <div key={post.id} className="post-item">
                                    <div className="post-category">
                                        <span className="category-badge" data-category={post.category}>
                                            {getCategoryIcon(post.category)} {categories.find(c => c.id === post.category)?.name}
                                        </span>
                                        {post.isRecommended && <span className="recommended-badge">⭐ 추천</span>}
                                    </div>

                                    <div className="post-content">
                                        <h3 className="post-title">{post.title}</h3>
                                        <p className="post-preview">{post.content}</p>
                                    </div>

                                    <div className="post-meta">
                                        <div className="author-info">
                                            <span className="author-name">{post.author}</span>
                                            <span className="author-level">Lv.{post.authorLevel}</span>
                                        </div>

                                        <div className="post-stats">
                                            <span className="stat">👁️ {post.views.toLocaleString()}</span>
                                            <span className="stat">👍 {post.likes}</span>
                                            <span className="stat">💬 {post.comments}</span>
                                            <span className="post-time">{post.createdAt}</span>
                                        </div>
                                    </div>
                                </div>
                            ))}
                        </div>
                    )}
                </div>

                {showWriteModal && (
                    <div className="modal-overlay" onClick={() => setShowWriteModal(false)}>
                        <div className="write-modal" onClick={(e) => e.stopPropagation()}>
                            <div className="modal-header">
                                <h2>게시글 작성</h2>
                                <button className="close-btn" onClick={() => setShowWriteModal(false)}>×</button>
                            </div>

                            <form className="write-form" onSubmit={handleSubmitPost}>
                                <div className="form-group">
                                    <label>카테고리</label>
                                    <select
                                        value={writeForm.category}
                                        onChange={(e) => setWriteForm({ ...writeForm, category: e.target.value })}
                                        className="category-select"
                                    >
                                        {categories.filter(c => c.id !== 'all').map(category => (
                                            <option key={category.id} value={category.id}>
                                                {getCategoryIcon(category.id)} {category.name}
                                            </option>
                                        ))}
                                    </select>
                                </div>

                                <div className="form-group">
                                    <label>제목</label>
                                    <input
                                        type="text"
                                        value={writeForm.title}
                                        onChange={(e) => setWriteForm({ ...writeForm, title: e.target.value })}
                                        placeholder="제목을 입력하세요"
                                        required
                                        className="title-input"
                                    />
                                </div>

                                <div className="form-group">
                                    <label>내용</label>
                                    <textarea
                                        value={writeForm.content}
                                        onChange={(e) => setWriteForm({ ...writeForm, content: e.target.value })}
                                        placeholder="내용을 입력하세요"
                                        required
                                        className="content-textarea"
                                        rows="10"
                                    />
                                </div>

                                <div className="form-actions">
                                    <button type="button" className="cancel-btn" onClick={() => setShowWriteModal(false)}>
                                        취소
                                    </button>
                                    <button type="submit" className="submit-btn">
                                        작성 완료
                                    </button>
                                </div>
                            </form>
                        </div>
                    </div>
                )}
            </div>
        </Layout>
    );
};

export default CommunityPage;