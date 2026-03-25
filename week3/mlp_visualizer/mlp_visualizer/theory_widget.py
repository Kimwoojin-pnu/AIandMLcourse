"""theory_widget.py"""
from PySide6.QtWidgets import QWidget, QVBoxLayout, QTextBrowser

_HTML = """<html><head><style>
body{font-family:'Malgun Gothic',sans-serif;margin:20px;background:white;color:#2c3e50;line-height:1.7}
h1{color:#2980b9;font-size:22px;border-bottom:2px solid #2980b9;padding-bottom:8px}
h2{color:#2c3e50;font-size:16px;margin-top:24px}
.fb{background:#f8f9fa;border-left:4px solid #2980b9;padding:12px 16px;margin:10px 0;border-radius:4px;font-family:monospace;font-size:13px}
.note{background:#eaf4fb;border-left:4px solid #3498db;padding:10px 14px;margin:8px 0;border-radius:4px}
.ok{background:#eafaf1;border-left:4px solid #2ecc71;padding:10px 14px;margin:8px 0;border-radius:4px}
table{border-collapse:collapse;width:100%;margin:12px 0}
th{background:#2980b9;color:white;padding:8px 12px}
td{border:1px solid #dee2e6;padding:8px 12px}
</style></head><body>
<h1>🧠 MLP와 역전파 (Backpropagation)</h1>
<div class="note"><b>왜 MLP가 필요한가?</b><br>
단층 퍼셉트론은 XOR을 학습할 수 없습니다 (선형 분리 불가).
<b>은닉층을 추가한 MLP</b>는 비선형 결정 경계를 학습할 수 있습니다.</div>

<h2>1. XOR 문제</h2>
<table>
<tr><th>x₁</th><th>x₂</th><th>XOR 출력</th><th>선형 분리?</th></tr>
<tr><td>0</td><td>0</td><td>0</td><td rowspan="4" style="text-align:center;color:#e74c3c"><b>불가능 ✗</b></td></tr>
<tr><td>0</td><td>1</td><td>1</td></tr>
<tr><td>1</td><td>0</td><td>1</td></tr>
<tr><td>1</td><td>1</td><td>0</td></tr>
</table>

<h2>2. MLP 구조 (2→hidden→1)</h2>
<div class="fb">
순전파:<br>
  z₁ = X @ W₁ + b₁;  a₁ = σ(z₁)<br>
  z₂ = a₁ @ W₂ + b₂;  a₂ = σ(z₂)<br><br>
Loss = MSE = (1/m) Σ (a₂ - y)²
</div>

<h2>3. 역전파 (Chain Rule)</h2>
<div class="fb">
출력층 경사:<br>
  δ₂ = a₂ - y<br>
  dW₂ = (1/m) a₁ᵀ @ δ₂<br><br>
은닉층 경사:<br>
  da₁ = δ₂ @ W₂ᵀ<br>
  δ₁  = da₁ ⊙ σ'(z₁)   ← 연쇄 법칙<br>
  dW₁ = (1/m) Xᵀ @ δ₁<br><br>
가중치 업데이트:<br>
  W ← W - α · dW
</div>

<h2>4. Xavier 초기화</h2>
<div class="fb">W ~ N(0, √(2/fan_in))  — 기울기 소실/폭발 방지</div>

<div class="ok">➡️ <b>학습 시뮬레이션</b> 탭: XOR 학습 과정을 실시간으로 관찰<br>
➡️ <b>경사 시각화</b> 탭: dW₁·dW₂ 크기 변화 확인</div>
</body></html>"""


class TheoryWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        b = QTextBrowser()
        b.setHtml(_HTML)
        layout.addWidget(b)
