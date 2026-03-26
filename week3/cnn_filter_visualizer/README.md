# CNN 합성곱 필터 시각화

MIT 6.S191 Introduction to Deep Learning — Lecture 3 학습 프로젝트

합성곱(Convolution) 연산이 이미지에 적용되는 전 과정을 단계별로 시각화하는 데스크탑 앱.

---

## 실행 방법

```bash
# 1. 의존성 설치 (최초 1회)
pip install pillow

# 2. 실행
python main.py
```

## 파일 구조

```
cnn_filter_visualizer/
├── main.py                  # 진입점
├── app.py                   # 전체 창 + 상태 관리
├── panels/
│   ├── input_panel.py       # 왼쪽: 8×8 픽셀 그리드 + 파일 업로드
│   ├── control_panel.py     # 중앙: 필터 선택 + 계산식 + 버튼
│   └── output_panel.py      # 오른쪽: Feature Map
├── logic/
│   ├── filters.py           # 필터 커널 상수
│   └── convolution.py       # 합성곱 순수 함수
└── utils/
    └── image_loader.py      # PIL 이미지 → 8×8 배열
```

## 사용 방법

1. 왼쪽 그리드에 픽셀값(0~255) 입력, 또는 **이미지 파일 열기** 버튼으로 업로드
2. 중앙에서 필터 선택 (Sharpen / Edge Detect / Sobel X)
3. **Step →** 버튼: 한 칸씩 이동하며 계산 과정 확인
4. **▶ Auto** 버튼: 자동 재생 (속도 슬라이더로 조절)
5. **↺ Reset** 버튼: 처음부터 다시

## 필터 설명

| 필터 | 효과 |
|------|------|
| Sharpen | 에지 강조, 균일 영역 유지 |
| Edge Detect | 모든 방향 에지 검출 (Laplacian) |
| Sobel X | 수직 에지 강조 (좌우 밝기 변화) |
