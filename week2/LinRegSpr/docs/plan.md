# Plan: Hooke's Law TensorFlow Web App

## Feature
훅의 법칙(Hooke's Law) TensorFlow 학습 및 예측 웹 애플리케이션

## Requirements Checklist

### Tech Stack
- [x] FastAPI backend
- [x] Tailwind CSS frontend
- [x] TensorFlow model

### Core Features
- [x] TensorFlow으로 훅의 법칙 학습 (F = kx, x = mg/k)
- [x] 새로운 질량 입력 시 늘어나는 길이 예측
- [x] 대화형 질량 슬라이더 (실시간 예측)
- [x] 스프링 SVG 애니메이션 (예측값 시각화)

### Visualisation (PNG Output)
- [x] training_data.png — 학습 데이터 시각화
- [x] loss_history.png — epoch별 loss 함수 plot
- [x] predictions.png — 모델 예측 vs 이론값 + 잔차
- [x] spring_physics.png — 다양한 질량별 스프링 시각화
- [x] dashboard.png — 종합 대시보드

### Output Directory
- [x] 모든 PNG를 output/ 디렉토리에 저장

### UI Quality
- [x] 전문가가 감탄할 수준의 디자인
- [x] 다크 테마 (GitHub-style)
- [x] 글래스모피즘 카드
- [x] 파티클 배경 애니메이션
- [x] Chart.js 인터랙티브 차트 (epoch별 loss 실시간 렌더링)
- [x] 반응형 디자인

### API Endpoints
- [x] GET  /               — HTML 페이지
- [x] POST /api/predict    — 질량 → 늘어나는 길이 예측
- [x] GET  /api/model-info — 모델 통계
- [x] GET  /api/history    — 학습 히스토리 JSON
- [x] GET  /api/health     — 헬스체크

### Code Quality
- [x] 타입 힌트
- [x] Pydantic 요청/응답 스키마
- [x] 구조화된 로깅
- [x] 조기 종료 (EarlyStopping) 콜백
- [x] ReduceLROnPlateau 콜백
- [x] 재현성 (seed=42)

## Design Score Target: 98%
