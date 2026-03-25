"""
theory_widget.py
이론 설명 탭 — 퍼셉트론 개념을 HTML로 구조화하여 표시
"""
from PySide6.QtWidgets import QWidget, QVBoxLayout, QTextBrowser
from PySide6.QtCore import Qt

# ─────────────────────────────────────────────────────────────────
# HTML 콘텐츠
# ─────────────────────────────────────────────────────────────────
_THEORY_HTML = """
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
  body {
    font-family: 'Malgun Gothic', 'Apple SD Gothic Neo', 'NanumGothic', sans-serif;
    font-size: 14px;
    color: #2c3e50;
    margin: 24px 32px;
    line-height: 1.7;
  }
  h1 {
    color: #1a6fa3;
    font-size: 22px;
    border-bottom: 3px solid #2980b9;
    padding-bottom: 8px;
    margin-bottom: 16px;
  }
  h2 {
    color: #1e8449;
    font-size: 16px;
    margin-top: 28px;
    margin-bottom: 8px;
    padding-left: 10px;
    border-left: 4px solid #27ae60;
  }
  h3 {
    color: #7d3c98;
    font-size: 14px;
    margin-top: 16px;
  }
  .formula-box {
    background: #f0f4f8;
    border-left: 5px solid #2980b9;
    border-radius: 4px;
    padding: 14px 18px;
    margin: 12px 0;
    font-family: 'Courier New', monospace;
    font-size: 14px;
    color: #1a2634;
    line-height: 1.9;
  }
  .note {
    background: #fef9e7;
    border: 1px solid #f9ca24;
    border-radius: 6px;
    padding: 12px 16px;
    margin: 12px 0;
  }
  .warning {
    background: #fdecea;
    border: 1px solid #e74c3c;
    border-radius: 6px;
    padding: 12px 16px;
    margin: 12px 0;
  }
  .success {
    background: #eafaf1;
    border: 1px solid #27ae60;
    border-radius: 6px;
    padding: 12px 16px;
    margin: 12px 0;
  }
  table {
    border-collapse: collapse;
    margin: 12px 0;
    min-width: 320px;
  }
  th {
    background: #2980b9;
    color: white;
    padding: 8px 18px;
    text-align: center;
    font-size: 13px;
  }
  td {
    border: 1px solid #dee2e6;
    padding: 7px 18px;
    text-align: center;
    font-size: 13px;
  }
  tr:nth-child(even) { background: #f8f9fa; }
  .badge {
    display: inline-block;
    background: #2980b9;
    color: white;
    border-radius: 50%;
    width: 24px; height: 24px;
    text-align: center;
    line-height: 24px;
    font-weight: bold;
    font-size: 12px;
    margin-right: 8px;
  }
  .badge-green { background: #27ae60; }
  .step-row { margin: 10px 0; }
  code {
    background: #f1f2f6;
    border-radius: 3px;
    padding: 1px 5px;
    font-family: 'Courier New', monospace;
    color: #c0392b;
    font-size: 13px;
  }
  .neuron-diagram {
    background: #f8f9fa;
    border: 1px solid #dee2e6;
    border-radius: 8px;
    padding: 16px;
    margin: 12px 0;
    text-align: center;
    font-size: 15px;
    letter-spacing: 2px;
  }
</style>
</head>
<body>

<h1>🧠 퍼셉트론(Perceptron) 완전 이해</h1>

<p>
퍼셉트론은 <strong>1957년 Frank Rosenblatt</strong>이 제안한 
인공 신경망의 가장 기본 단위입니다.  
생물학적 뉴런의 동작을 수학적으로 모델링한 것으로,
현대 딥러닝의 출발점입니다.
</p>

<!-- ──────────────────────────────── -->
<h2>1. 생물학적 뉴런 → 퍼셉트론</h2>

<div class="neuron-diagram">
  입력 신호들 → [수상돌기] → [세포체: 가중합] → [축삭: 활성화] → 출력
  <br>
  x₁, x₂ ──→ [× w₁, × w₂] ──→ [Σ + b] ──→ [step(·)] ──→ y
</div>

<p>
생물 뉴런처럼, 퍼셉트론도 여러 입력에 <strong>중요도(가중치)</strong>를 곱하고,
전부 합산한 뒤 임계값을 넘으면 <strong>"발화(1)"</strong>, 아니면 <strong>"침묵(0)"</strong>을 출력합니다.
</p>

<!-- ──────────────────────────────── -->
<h2>2. 수학적 모델</h2>

<div class="formula-box">
<b>순입력(Net Input):</b><br>
  z = w₁·x₁ + w₂·x₂ + b<br>
<br>
<b>출력(Output):</b><br>
  y = step(z)<br>
<br>
변수 설명:<br>
  x₁, x₂  = 입력값 (Input)<br>
  w₁, w₂  = 가중치 (Weight) — 각 입력의 중요도<br>
  b        = 편향   (Bias)   — 임계값 조정<br>
  step()   = 계단 함수 (Activation Function)
</div>

<!-- ──────────────────────────────── -->
<h2>3. 활성화 함수 — 계단 함수 (Step Function)</h2>

<div class="formula-box">
        ⎧ 1   if  z ≥ 0
step(z) = ⎨
        ⎩ 0   if  z &lt; 0
</div>

<div class="note">
💡 <b>편향(b)의 역할:</b><br>
편향은 계단 함수의 <em>기준점</em>을 이동시킵니다.<br>
b &gt; 0 → 더 쉽게 발화 (임계값이 낮아짐)<br>
b &lt; 0 → 더 어렵게 발화 (임계값이 높아짐)
</div>

<!-- ──────────────────────────────── -->
<h2>4. 학습 알고리즘 (Perceptron Learning Rule)</h2>

<div class="formula-box">
<b>Step 1:</b>  예측값 계산  →  ŷ = step(w·x + b)<br>
<b>Step 2:</b>  오차 계산     →  e = y_true - ŷ<br>
<b>Step 3:</b>  가중치 갱신   →  w ← w + η·e·x<br>
<b>Step 4:</b>  편향 갱신     →  b ← b + η·e<br>
<br>
η (eta) = 학습률 (Learning Rate, 0 &lt; η ≤ 1)
</div>

<p>오차 <code>e</code>가 0이면 가중치가 변하지 않고, ±1이면 <em>오류 방향으로 보정</em>됩니다.</p>

<div class="note">
💡 <b>학습률(η) 선택 가이드:</b><br>
• η = 0.01~0.1  → 안정적, 느린 수렴<br>
• η = 0.5~1.0   → 빠른 수렴, 진동 위험<br>
실습에서 직접 비교해 보세요! (시뮬레이션 탭)
</div>

<!-- ──────────────────────────────── -->
<h2>5. 논리 게이트 진리표</h2>

<table>
<tr><th>x₁</th><th>x₂</th><th>AND</th><th>OR</th><th>XOR</th></tr>
<tr><td>0</td><td>0</td><td>0</td><td>0</td><td>0</td></tr>
<tr><td>0</td><td>1</td><td>0</td><td>1</td><td>1</td></tr>
<tr><td>1</td><td>0</td><td>0</td><td>1</td><td>1</td></tr>
<tr><td>1</td><td>1</td><td>1</td><td>1</td><td>0</td></tr>
</table>

<!-- ──────────────────────────────── -->
<h2>6. 결정 경계 (Decision Boundary)</h2>

<p>퍼셉트론의 결정 경계는 <strong>직선</strong>입니다:</p>

<div class="formula-box">
z = 0  →  w₁·x₁ + w₂·x₂ + b = 0<br>
<br>
x₂ = -(w₁/w₂)·x₁ - (b/w₂)      (w₂ ≠ 0 인 경우)
</div>

<div class="success">
✅ <b>AND 게이트</b> — 선형 분리 가능:<br>
&emsp;(1,1) 하나만 1 → 직선 하나로 분리 가능
</div>

<div class="success">
✅ <b>OR 게이트</b> — 선형 분리 가능:<br>
&emsp;(0,0) 하나만 0 → 직선 하나로 분리 가능
</div>

<div class="warning">
⚠️ <b>XOR 게이트</b> — 선형 분리 <em>불가능</em>:<br>
&emsp;(0,0)→0, (0,1)→1, (1,0)→1, (1,1)→0<br>
&emsp;어떤 직선을 그어도 0과 1을 완전히 분리할 수 없습니다!<br>
&emsp;해결하려면 <b>다층 퍼셉트론(MLP)</b>이 필요합니다.
</div>

<!-- ──────────────────────────────── -->
<h2>7. 수렴 정리 (Convergence Theorem)</h2>

<div class="success">
📐 <b>퍼셉트론 수렴 정리:</b><br>
선형 분리 가능한 데이터에 대해, 퍼셉트론 학습 알고리즘은
<em>유한한 스텝 안에 반드시 수렴</em>합니다 (Rosenblatt, 1962).
</div>

<!-- ──────────────────────────────── -->
<h2>8. 학습 과정 요약</h2>

<div class="step-row">
  <span class="badge">1</span>
  <b>초기화:</b> 가중치 w, 편향 b 를 작은 랜덤값으로 초기화
</div>
<div class="step-row">
  <span class="badge">2</span>
  <b>순전파:</b> 각 학습 샘플에 대해 ŷ = step(w·x + b) 계산
</div>
<div class="step-row">
  <span class="badge">3</span>
  <b>오차 계산:</b> e = y_true - ŷ
</div>
<div class="step-row">
  <span class="badge">4</span>
  <b>가중치 갱신:</b> e ≠ 0 이면 w, b 업데이트
</div>
<div class="step-row">
  <span class="badge">5</span>
  <b>반복:</b> 모든 샘플에 대해 오차가 0이 될 때까지 2~4 반복
</div>

<br>
<div class="note">
🔬 <b>직접 확인해보기:</b><br>
• <b>시뮬레이션 탭</b>에서 AND/OR/XOR 게이트를 학습시키고
  결정 경계가 어떻게 변하는지 확인해 보세요.<br>
• <b>직접 조작 탭</b>에서 가중치와 편향을 직접 바꾸면서
  결정 경계가 어떻게 이동하는지 느껴보세요.
</div>

<br><br>
</body>
</html>
"""


class TheoryWidget(QWidget):
    """이론 설명 탭 위젯"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        browser = QTextBrowser()
        browser.setHtml(_THEORY_HTML)
        browser.setOpenExternalLinks(True)
        browser.setStyleSheet("""
            QTextBrowser {
                border: none;
                background: white;
            }
            QScrollBar:vertical {
                width: 8px;
                background: #f4f6f8;
            }
            QScrollBar::handle:vertical {
                background: #bdc3c7;
                border-radius: 4px;
            }
        """)
        layout.addWidget(browser)
