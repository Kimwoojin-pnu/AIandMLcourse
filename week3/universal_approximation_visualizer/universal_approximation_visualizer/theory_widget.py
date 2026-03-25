"""theory_widget.py"""
from PySide6.QtWidgets import QWidget, QVBoxLayout, QTextBrowser

_HTML = """<html><head><style>
body{font-family:'Malgun Gothic',sans-serif;margin:20px;background:white;color:#2c3e50;line-height:1.7}
h1{color:#2980b9;font-size:22px;border-bottom:2px solid #2980b9;padding-bottom:8px}
h2{color:#2c3e50;font-size:16px;margin-top:24px}
.fb{background:#f8f9fa;border-left:4px solid #2980b9;padding:12px 16px;margin:10px 0;border-radius:4px;font-family:monospace;font-size:13px}
.note{background:#eaf4fb;border-left:4px solid #3498db;padding:10px 14px;margin:8px 0;border-radius:4px}
.ok{background:#eafaf1;border-left:4px solid #2ecc71;padding:10px 14px;margin:8px 0;border-radius:4px}
.warn{background:#fef9e7;border-left:4px solid #f39c12;padding:10px 14px;margin:8px 0;border-radius:4px}
table{border-collapse:collapse;width:100%;margin:12px 0}
th{background:#2980b9;color:white;padding:8px 12px}
td{border:1px solid #dee2e6;padding:8px 12px}
</style></head><body>
<h1>🌊 범용 근사 정리 (Universal Approximation Theorem)</h1>

<div class="note"><b>핵심 주장 (Cybenko, 1989)</b><br>
하나의 은닉층을 가진 신경망은 <b>충분한 수의 뉴런</b>이 있다면,<br>
어떤 연속 함수도 <b>임의의 정확도</b>로 근사할 수 있다.
</div>

<h2>1. 공식 표현</h2>
<div class="fb">
f: [0,1]ⁿ → ℝ 이 연속 함수일 때,<br>
∀ε > 0, ∃N, W, b 다음을 만족:<br><br>
&nbsp;&nbsp;|f(x) − Σᵢ wᵢ · σ(vᵢᵀx + bᵢ)| &lt; ε,  ∀x ∈ [0,1]ⁿ<br><br>
여기서 σ는 비선형 활성화 함수 (Sigmoid, Tanh, ReLU 등)
</div>

<h2>2. 직관적 이해</h2>
<ul>
<li>각 은닉 뉴런 = <b>하나의 "bump" (구형 함수)</b> 를 만들 수 있음</li>
<li>충분히 많은 bump들을 합치면 → 임의의 형태를 만들 수 있음</li>
<li>마치 푸리에 급수처럼 — 기저 함수를 더해 복잡한 함수 표현</li>
</ul>

<h2>3. 뉴런 수와 근사 품질</h2>
<table>
<tr><th>뉴런 수</th><th>근사 품질</th><th>파라미터 수</th></tr>
<tr><td>3개</td><td>거친 근사 (대략적 형태)</td><td>~10개</td></tr>
<tr><td>10개</td><td>중간 근사 (형태 잡힘)</td><td>~31개</td></tr>
<tr><td>50개</td><td>정밀 근사 (거의 완벽)</td><td>~151개</td></tr>
</table>

<h2>4. 이론의 한계</h2>
<div class="warn">
<b>존재성 정리일 뿐:</b> "충분히 많은 뉴런이 있으면 근사 가능하다"고만 말함.<br>
정확히 몇 개의 뉴런이 필요한지, 어떻게 학습하는지는 보장하지 않습니다.
</div>

<h2>5. 깊이 vs 폭 (Depth vs Width)</h2>
<ul>
<li><b>이론:</b> 하나의 넓은 은닉층으로 충분</li>
<li><b>실제:</b> 깊은 네트워크(여러 층)가 더 효율적 — 파라미터 수 대비 표현력 ↑</li>
<li>깊은 네트워크는 계층적 특징(hierarchical features)을 학습</li>
</ul>

<div class="ok">
➡️ <b>함수 근사</b> 탭: 뉴런 수 조절하며 근사 품질 실시간 확인<br>
➡️ <b>뉴런 수 비교</b> 탭: 3/10/50개 뉴런을 나란히 비교
</div>
</body></html>"""


class TheoryWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        b = QTextBrowser()
        b.setHtml(_HTML)
        layout.addWidget(b)
