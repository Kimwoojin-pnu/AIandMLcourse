"""theory_widget.py — 이론 설명 탭"""
from PySide6.QtWidgets import QWidget, QVBoxLayout, QTextBrowser

_HTML = """
<html><head><style>
body { font-family: 'Malgun Gothic', sans-serif; margin: 20px; background: white; color: #2c3e50; line-height: 1.7; }
h1 { color: #2980b9; font-size: 22px; border-bottom: 2px solid #2980b9; padding-bottom: 8px; }
h2 { color: #2c3e50; font-size: 16px; margin-top: 24px; }
.formula-box {
    background: #f8f9fa; border-left: 4px solid #2980b9;
    padding: 12px 16px; margin: 10px 0; border-radius: 4px;
    font-family: monospace; font-size: 14px;
}
.note { background: #eaf4fb; border-left: 4px solid #3498db; padding: 10px 14px; margin: 8px 0; border-radius: 4px; }
.ok   { background: #eafaf1; border-left: 4px solid #2ecc71; padding: 10px 14px; margin: 8px 0; border-radius: 4px; }
table { border-collapse: collapse; width: 100%; margin: 12px 0; }
th    { background: #2980b9; color: white; padding: 8px 12px; }
td    { border: 1px solid #dee2e6; padding: 8px 12px; }
tr:nth-child(even) { background: #f8f9fa; }
</style></head><body>

<h1>➡️ 순전파 (Forward Propagation)</h1>

<div class="note">
<b>순전파란?</b><br>
입력 데이터가 네트워크를 통해 <b>입력층 → 은닉층 → 출력층</b> 방향으로 흐르며 최종 예측값을 계산하는 과정입니다.
역전파(Backpropagation)와 달리 <b>단방향</b>으로만 진행됩니다.
</div>

<h2>1. 2-3-1 네트워크 구조</h2>
<table>
<tr><th>층</th><th>뉴런 수</th><th>활성화 함수</th><th>역할</th></tr>
<tr><td>입력층</td><td>2</td><td>없음</td><td>x₁, x₂ 입력 수신</td></tr>
<tr><td>은닉층</td><td>3</td><td>ReLU</td><td>비선형 변환</td></tr>
<tr><td>출력층</td><td>1</td><td>Sigmoid</td><td>0~1 확률 출력</td></tr>
</table>

<h2>2. Layer 1 계산 (입력→은닉)</h2>
<div class="formula-box">
z₁ = X @ W₁ + b₁<br>
&nbsp;&nbsp;&nbsp;X: 입력 벡터 (2,)<br>
&nbsp;&nbsp;&nbsp;W₁: 가중치 행렬 (2×3) — 각 원소: 연결 가중치<br>
&nbsp;&nbsp;&nbsp;b₁: 편향 벡터 (3,)<br>
&nbsp;&nbsp;&nbsp;z₁: 선형 결합 결과 (3,) — "활성화 전 값"<br>
<br>
a₁ = ReLU(z₁) = max(0, z₁)  (원소별 적용)<br>
&nbsp;&nbsp;&nbsp;a₁: 은닉층 활성화 (3,) — "활성화 후 값"
</div>

<h2>3. Layer 2 계산 (은닉→출력)</h2>
<div class="formula-box">
z₂ = a₁ @ W₂ + b₂<br>
&nbsp;&nbsp;&nbsp;W₂: 가중치 행렬 (3×1)<br>
&nbsp;&nbsp;&nbsp;z₂: 스칼라 — 출력 뉴런의 선형 결합<br>
<br>
a₂ = Sigmoid(z₂) = 1 / (1 + e<sup>-z₂</sup>)<br>
&nbsp;&nbsp;&nbsp;a₂: 최종 출력 (0~1 확률)
</div>

<h2>4. 가중치 행렬 이해</h2>
<div class="formula-box">
W₁[i, j] = 입력 뉴런 i → 은닉 뉴런 j 의 연결 강도<br>
<br>
예: W₁ = [[0.3, -0.2, 0.8],    ← x₁에서 각 은닉 뉴런으로
           [-0.5, 0.7, 0.1]]   ← x₂에서 각 은닉 뉴런으로
</div>

<h2>5. 핵심 직관</h2>
<ul>
<li><b>행렬 곱셈</b> = 모든 연결의 가중합을 한 번에 계산</li>
<li><b>편향 b</b> = 뉴런의 기준선 (활성화 임계값 조정)</li>
<li><b>ReLU</b> = 음수 신호 차단 → 희소 표현 생성</li>
<li><b>Sigmoid</b> = 임의의 실수 → (0,1) 확률로 압축</li>
</ul>

<div class="ok">
➡️ <b>순전파 탐색</b> 탭에서 x₁·x₂ 슬라이더를 조작하며 각 뉴런의 활성화를 실시간으로 관찰하세요!<br>
➡️ <b>행렬 시각화</b> 탭에서 W₁·W₂ 가중치 행렬의 히트맵을 확인하세요!
</div>

</body></html>
"""


class TheoryWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        browser = QTextBrowser()
        browser.setHtml(_HTML)
        layout.addWidget(browser)
