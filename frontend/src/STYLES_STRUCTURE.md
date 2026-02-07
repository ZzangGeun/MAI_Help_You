# 프론트엔드 스타일 구조 개선 가이드

## 📁 새로운 폴더 구조

### styles/
프로젝트의 모든 CSS 파일이 기능별로 정리되어 있습니다.

```
styles/
├── globals/                    # 전역 스타일
│   ├── variables.css           # 색상, 그림자, 테마 변수
│   ├── reset.css               # 초기화 스타일, 유틸리티 클래스
│   └── common.css              # Header, Nav, Layout, Button, Card 스타일
│
├── components/                 # 컴포넌트별 스타일
│   ├── auth.css                # 인증 관련 (Login, Signup popups)
│   └── common.css              # Layout, Sidebar, Profile, Chat History
│
├── pages/                      # 페이지별 스타일
│   ├── home.css                # 홈 페이지 스타일
│   ├── chat.css                # 채팅 페이지 스타일
│   ├── character.css           # 캐릭터 페이지 스타일
│   └── community.css           # 커뮤니티 페이지 스타일
│
# 이전 파일들 (더 이상 사용 안 함)
├── home.css                    # ❌ 삭제됨
├── chat.css                    # ❌ 삭제됨
├── character.css               # ❌ 삭제됨
├── community.css               # ❌ 삭제됨
└── common.css                  # ❌ 삭제됨
```

## 🎨 CSS 파일별 내용

### globals/variables.css
CSS 커스텀 속성으로 테마 색상, 그림자, 테두리 반경 등 정의
```css
:root {
    --primary-color: #ff9800;
    --text-primary: #1a1a1a;
    --shadow-medium: 0 4px 15px rgba(255, 152, 0, 0.1);
    /* ... */
}
```

### globals/reset.css
- 모든 요소 리셋 (margin, padding, box-sizing)
- 기본 타이포그래피
- 유틸리티 클래스 (.flex, .gap-small, .text-center 등)

### globals/common.css
- Header, Navigation 스타일
- Main Container, Sidebar 레이아웃
- 버튼, 카드 기본 스타일
- 반응형 디자인

### components/auth.css
- Login/Signup Popup 스타일
- 인증 관련 모든 모달 및 폼

### components/common.css
- Layout 컴포넌트 관련 스타일
- Sidebar (프로필, 채팅 히스토리)
- Ad 배너 스타일

### pages/home.css
- 홈 페이지 배너, 검색창
- 섹션 카드, 랭킹, 공지사항
- 광고 배너 위치 및 스타일

### pages/chat.css
- 채팅 메인 컨테이너
- 메시지 스타일 (user, bot)
- 입력창, 사고 과정 표시
- Markdown 렌더링 스타일

### pages/character.css
- 캐릭터 정보 컨테이너
- 탭 네비게이션
- 장비 그리드
- 통계 표시

### pages/community.css
- 게시물 리스트
- 카테고리 탭
- 글쓰기 모달
- 검색 및 정렬

## 🔄 Import 경로 변경

### 이전 (변경 전)
```jsx
import '../styles/home.css';
import '../styles/common.css';
import '../styles/chat.css';
```

### 현재 (변경 후)
```jsx
// 글로벌 스타일 (모든 페이지에서 필요)
import '../styles/globals/common.css';

// 페이지별 스타일 (해당 페이지에서만 사용)
import '../styles/pages/home.css';
import '../styles/pages/chat.css';

// 컴포넌트별 스타일 (필요한 컴포넌트에서)
import '../styles/components/auth.css';
import '../styles/components/common.css';
```

## 📝 수정된 파일 목록

### main.jsx
```jsx
import './styles/globals/common.css'
```

### Pages
- HomePage.jsx: `'../styles/pages/home.css'`
- ChatPage.jsx: `'../styles/pages/chat.css'`
- CharacterPage.jsx: `'../styles/pages/character.css'`
- CommunityPage.jsx: `'../styles/pages/community.css'`
- LoginPage.jsx: `'../styles/globals/common.css'`

### Components
- Layout.jsx: `'../../styles/globals/common.css'`
- Header.jsx: `'../../styles/globals/common.css'`
- LoginPopup.jsx: `'../../styles/components/auth.css'`
- SignupPopup.jsx: `'../../styles/components/auth.css'`

## 🚀 사용 팁

### 새 스타일 추가 시
1. **전역 스타일**: `styles/globals/` (colors, reset 등)
2. **컴포넌트 스타일**: `styles/components/` (재사용 가능한 컴포넌트)
3. **페이지 스타일**: `styles/pages/` (특정 페이지만 필요)

### 색상 변경
모든 색상은 `globals/variables.css`에서 관리합니다:
```css
/* 변경 전 */
background: #ff9800;

/* 변경 후 */
background: var(--primary-color);
```

### 새 레이아웃 추가
```jsx
import '../styles/globals/common.css';  // 필수
import '../styles/pages/yourPage.css';  // 페이지별 스타일
```

## 📊 폴더 정리 효과

✅ **장점:**
- 스타일 파일 찾기가 쉬움
- 코드 유지보수 개선
- 페이지 로딩 속도 최적화 (필요한 스타일만 import)
- CSS 변수로 일관된 테마 관리
- 컴포넌트 재사용성 증대

✅ **결과:**
- 프로젝트 구조가 더 명확해짐
- 개발 생산성 향상
- 스타일 충돌 감소
- 향후 확장 용이

## 🔍 이전 파일 제거 예정

다음 파일들은 더 이상 사용되지 않으므로 나중에 삭제 가능:
- `styles/home.css`
- `styles/chat.css`
- `styles/character.css`
- `styles/community.css`
- `styles/common.css`

---

**변경 날짜**: 2026-01-13
**변경자**: Frontend Restructuring Project
