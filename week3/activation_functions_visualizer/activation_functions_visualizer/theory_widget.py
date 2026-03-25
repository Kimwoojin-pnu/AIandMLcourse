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
.note   { background: #eaf4fb; border-left: 4px solid #3498db; padding: 10px 14px; margin: 8px 0; border-radius: 4px; }
.warn   { background: #fef9e7; border-left: 4px solid #f39c12; padding: 10px 14px; margin: 8px 0; border-radius: 4px; }
.ok     { background: #eafaf1; border-left: 4px solid #2ecc71; padding: 10px 14px; margin: 8px 0; border-radius: 4px; }
table   { border-collapse: collapse; width: 100%; margin: 12px 0; }
th      { background: #2980b9; color: white; padding: 8px 12px; }
td      { border: 1px solid #dee2e6; padding: 8px 12px; }
tr:nth-child(even) { background: #f8f9fa; }
</style></head><body>

<h1>🧠 활성화 함수 (Activation Functions)</h1>

<div class="note">
<b>왜 활성화 함수가 필요한가?</b><br>
활성화 함수가 없으면 여러 층을 쌓아도 <b>하나의 선형 변환</b>과 동일합니다.
비선형 활성화 함수를 통해 신경망은 복잡한 패턴을 학습할 수 있습니다.
</div>

<h2>1. Sigmoid σ(x)</h2>
<div class="formula-box">
σ(x) = 1 / (1 + e<sup>-x</sup>)&nbsp;&nbsp;&nbsp;&nbsp;범위: (0, 1)<br>
σ'(x) = σ(x) · (1 − σ(x))&nbsp;&nbsp;&nbsp;&nbsp;최댓값: 0.25 (x=0에서)
</div>
<ul>
<li>✅ 확률 해석 가능 (이진 분류 출력층)</li>
<li>✅ 부드러운 미분 가능 곡선</li>
<li>❌ <b>Vanishing Gradient</b> — |x| 클 때 기울기 ≈ 0 → 역전파 신호 소멸</li>
<li>❌ 출력이 0 중심이 아님 → 경사 갱신 비효율</li>
</ul>

<h2>2. Tanh tanh(x)</h2>
<div class="formula-box">
tanh(x) = (e<sup>x</sup> − e<sup>-x</sup>) / (e<sup>x</sup> + e<sup>-x</sup>)&nbsp;&nbsp;&nbsp;&nbsp;범위: (-1, 1)<br>
tanh'(x) = 1 − tanh²(x)&nbsp;&nbsp;&nbsp;&nbsp;최댓값: 1.0 (x=0에서)
</div>
<ul>
<li>✅ <b>0 중심</b> — Sigmoid보다 경사 갱신 효율 좋음</li>
<li>✅ 기울기가 Sigmoid보다 큼</li>
<li>❌ Vanishing Gradient 여전히 존재 (±∞에서 포화)</li>
</ul>

<h2>3. ReLU f(x) = max(0, x)</h2>
<div class="formula-box">
f(x) = max(0, x)&nbsp;&nbsp;&nbsp;&nbsp;범위: [0, ∞)<br>
f'(x) = 1 if x > 0, else 0
</div>
<ul>
<li>✅ 계산 매우 빠름</li>
<li>✅ x > 0 구간에서 Vanishing Gradient 없음</li>
<li>✅ 희소 활성화 (Sparsity) — 일부 뉴런만 활성화</li>
<li>❌ <b>Dying ReLU</b> — 학습 중 x ≤ 0 고착 시 뉴런 영구 비활성</li>
</ul>

<h2>4. Leaky ReLU f(x)</h2>
<div class="formula-box">
f(x) = x if x > 0, else α·x&nbsp;&nbsp;&nbsp;&nbsp;(α = 0.01 기본값)<br>
f'(x) = 1 if x > 0, else α
</div>
<ul>
<li>✅ Dying ReLU 문제 해결 (x ≤ 0에서 약한 경사 유지)</li>
<li>⚠️ α 값 선택 필요 (하이퍼파라미터)</li>
</ul>

<h2>5. 비교 요약</h2>
<table>
<tr><th>함수</th><th>범위</th><th>장점</th><th>단점</th><th>주 용도</th></tr>
<tr><td>Sigmoid</td><td>(0,1)</td><td>확률 해석</td><td>Vanishing Gradient</td><td>이진 분류 출력층</td></tr>
<tr><td>Tanh</td><td>(-1,1)</td><td>0 중심</td><td>Vanishing Gradient</td><td>은닉층 (RNN 등)</td></tr>
<tr><td>ReLU</td><td>[0,∞)</td><td>빠름, 희소성</td><td>Dying ReLU</td><td>은닉층 표준</td></tr>
<tr><td>Leaky ReLU</td><td>(-∞,∞)</td><td>Dying ReLU 해결</td><td>α 선택 필요</td><td>ReLU 대안</td></tr>
</table>

<div class="ok">
<b>💡 권장 사용법</b><br>
- <b>은닉층:</b> ReLU (또는 Leaky ReLU)<br>
- <b>이진 분류 출력층:</b> Sigmoid<br>
- <b>다중 분류 출력층:</b> Softmax<br>
- <b>회귀 출력층:</b> 활성화 함수 없음 (선형)
</div>

<div class="note">
➡️ <b>함수 탐색</b> 탭에서 x값을 조작하며 각 함수의 출력과 기울기를 실시간으로 확인해보세요!<br>
➡️ <b>비교</b> 탭에서 여러 함수를 동시에 비교해보세요!
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
        browser.setOpenExternalLinks(True)
        layout.addWidget(browser)
