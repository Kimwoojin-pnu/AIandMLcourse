# Plan: pusan-physics-website

## Executive Summary

| Perspective | Description |
|-------------|-------------|
| **Problem** | 부산대학교 물리학과 공식 웹사이트가 노후화되어 학과의 연구 역량과 학문적 위상을 충분히 표현하지 못함 |
| **Solution** | FastAPI + Tailwind CSS 기반의 현대적이고 전문적인 물리학과 소개 웹사이트를 제작하여 시각적 탁월성과 정보 접근성을 동시에 달성 |
| **Functional UX Effect** | 물리학의 심오함을 담은 다크 우주 테마 + 인터랙티브 파티클 애니메이션으로 방문자가 즉시 감탄하는 몰입형 경험 제공 |
| **Core Value** | 전문가가 보아도 수준 높은 디자인 퀄리티로 학과의 브랜드 가치 상승 및 우수 학생·연구자 유치 |

---

## 1. Background & Objectives

### 1.1 Problem Statement
- 기존 phys.pusan.ac.kr 사이트는 2000년대 스타일의 정적 레이아웃
- 물리학의 역동성과 첨단 연구를 시각적으로 전달하지 못함
- 모바일 반응형 미지원, 접근성 부족
- 국제 연구자 유치를 위한 영문 콘텐츠 및 현대적 UX 부재

### 1.2 Target Users
- 입학 예정 학부생 (18-22세)
- 대학원 진학 희망자
- 국내외 연구 협력 교수/연구자
- 물리학과 현황을 확인하는 일반인 및 언론

### 1.3 Success Metrics
- 디자인 설계치 달성률 ≥ 98%
- 페이지 로드 속도 < 2초
- 모바일 반응형 완전 지원
- 전문가 평가 기준 "감탄" 수준

---

## 2. Scope

### 2.1 In Scope (핵심 기능)
1. **Hero Section** - 인터랙티브 파티클/별자리 배경 + 임팩트 있는 헤드라인
2. **학과소개** - 역사, 비전, 미션, 주요 수상/실적
3. **연구 분야** - 8개 연구그룹 카드 (실험/이론 물리, 나노, 광학 등)
4. **교수진** - 프로필 카드 그리드 (전공, 연구실, 이메일)
5. **교육 프로그램** - 학부/대학원 커리큘럼 탭
6. **뉴스 & 공지** - 최신 학과 소식, 세미나 일정
7. **Contact / Footer** - 위치, 연락처, SNS

### 2.2 Out of Scope
- 실제 DB 연동 (더미 데이터 사용)
- 로그인/회원가입 시스템
- 실시간 공지사항 CMS

---

## 3. Tech Stack

| Layer | Technology | Reason |
|-------|-----------|--------|
| Backend | FastAPI (Python) | 빠른 API 서빙, 정적 파일 제공 |
| Frontend Styling | Tailwind CSS (CDN) | 유틸리티 퍼스트, 빠른 커스텀 디자인 |
| Animation | Three.js / Particles.js | 물리학 테마 인터랙티브 배경 |
| Icons | Heroicons + Phosphor Icons | 현대적 아이콘 |
| Fonts | Inter + Pretendard (Google Fonts) | 한글/영문 최적화 |
| Template | Jinja2 | FastAPI 서버사이드 렌더링 |

---

## 4. Design Direction

### 4.1 Design Theme
- **컨셉**: "우주와 입자" - 물리학의 거시/미시 세계를 시각화
- **컬러 팔레트**:
  - Primary: Deep Space Navy `#0a0e27`
  - Accent: Quantum Blue `#3b82f6`
  - Highlight: Particle Gold `#f59e0b`
  - Text: Stellar White `#f1f5f9`
- **타이포그래피**: 대형 헤드라인 + 정갈한 본문
- **인터랙션**: 스크롤 애니메이션, 호버 효과, 파티클 배경

### 4.2 Layout Structure
```
┌─────────────────────────────────┐
│  Sticky Navigation (투명→불투명) │
├─────────────────────────────────┤
│  Hero: 파티클 배경 + 대형 타이틀  │
├─────────────────────────────────┤
│  Stats Bar (숫자로 보는 학과)    │
├─────────────────────────────────┤
│  학과소개 (글 + 이미지)          │
├─────────────────────────────────┤
│  연구 분야 (카드 그리드)         │
├─────────────────────────────────┤
│  교수진 (프로필 카드)            │
├─────────────────────────────────┤
│  교육 프로그램 (탭 인터페이스)   │
├─────────────────────────────────┤
│  뉴스 & 공지                    │
├─────────────────────────────────┤
│  Contact & Footer               │
└─────────────────────────────────┘
```

---

## 5. Project Structure

```
pnu-physics/
├── main.py                 # FastAPI app entry point
├── requirements.txt
├── static/
│   ├── css/
│   │   └── custom.css      # Tailwind 확장 커스텀 스타일
│   ├── js/
│   │   ├── particles.js    # 파티클 애니메이션
│   │   ├── scroll.js       # 스크롤 애니메이션
│   │   └── main.js         # 메인 JS
│   └── images/
│       └── (더미 이미지들)
├── templates/
│   ├── base.html           # 기본 레이아웃
│   ├── index.html          # 메인 페이지
│   ├── partials/
│   │   ├── nav.html
│   │   ├── hero.html
│   │   ├── about.html
│   │   ├── research.html
│   │   ├── faculty.html
│   │   ├── education.html
│   │   ├── news.html
│   │   └── footer.html
└── data/
    ├── faculty.json        # 교수진 더미 데이터
    ├── research.json       # 연구 분야 데이터
    └── news.json           # 뉴스 더미 데이터
```

---

## 6. Implementation Plan

| Phase | Task | Priority |
|-------|------|----------|
| 1 | FastAPI 프로젝트 셋업 + 정적 파일 서빙 | Critical |
| 2 | base.html + Navigation | Critical |
| 3 | Hero Section (파티클 애니메이션) | Critical |
| 4 | 학과소개 + Stats Bar | High |
| 5 | 연구 분야 섹션 | High |
| 6 | 교수진 섹션 | High |
| 7 | 교육 프로그램 탭 | Medium |
| 8 | 뉴스 & 공지 | Medium |
| 9 | Contact & Footer | Medium |
| 10 | 반응형 디자인 최적화 | High |
| 11 | 스크롤 애니메이션 | High |
| 12 | 최종 QA 및 폴리싱 | Critical |

---

## 7. Quality Standards

- 설계치 달성률 목표: **≥ 98%**
- 전문가 평가 기준: 디자인 완성도, 인터랙션 품질, 코드 품질
- Tailwind 유틸리티 클래스 최대 활용
- CSS 커스텀 최소화 (Tailwind 확장으로 처리)
- 접근성: WCAG 2.1 AA 준수
