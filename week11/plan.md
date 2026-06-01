# Week 11: 양자역학 시뮬레이션 — 실습 코드 구현 Plan

## 개요

| 항목 | 내용 |
|------|------|
| 총 파일 수 | 4개 (`01schrodinger.py` ~ `04wells_oscillator.py`) |
| 주요 라이브러리 | `numpy`, `scipy`, `matplotlib` |
| 출력 디렉토리 | `week11/outputs/` |
| 실행 방법 | `uv run python <파일명>` |

---

## 환경 세팅

```bash
# 프로젝트 구조
week11/
├── 01schrodinger.py
├── 02wavefunction.py
├── 03tunneling.py
├── 04wells_oscillator.py
└── outputs/          # 그래프 저장 폴더 (자동 생성)
```

```bash
# 의존성 설치
pip install numpy scipy matplotlib
```

**공통 상수 (모든 파일에서 사용)**

```python
hbar = 1.0          # 자연 단위계 (ℏ = 1)
m    = 1.0          # 전자 질량 = 1
```

---

## 파일별 구현 계획

### 01 `01schrodinger.py` — 슈뢰딩거 방정식 풀기

**목표:** 유한 차분법으로 해밀토니안 행렬을 구성하고, `scipy.linalg.eigh`로 고유값/고유벡터를 계산한다.

#### 핵심 함수

| 함수 | 역할 |
|------|------|
| `create_hamiltonian(x, V)` | 운동에너지(T) + 포텐셜(V) 행렬 합산 |
| `solve_schrodinger(x, V, n_states)` | eigh 호출 → 에너지 E, 파동함수 ψ 반환 |
| `normalize(psi, dx)` | `∫\|ψ\|²dx = 1` 정규화 |

#### 구현할 포텐셜 3종

```
포텐셜 1: 무한 사각 우물
  - V = 0  (0 < x < L)
  - V = 1e6 (경계)
  - 격자: x = linspace(0, L, 1000)

포텐셜 2: 조화 진동자
  - V(x) = 0.5 * k * x²
  - 격자: x = linspace(-6, 6, 1000)

포텐셜 3: 유한 사각 우물
  - V = -V₀  (우물 안)
  - V = 0    (우물 밖)
  - 격자: x = linspace(-10, 10, 1000)
```

#### 출력 그래프

- `outputs/01_infinite_square_well.png` — 에너지 준위 + 파동함수 (상/하 2패널)
- `outputs/01_harmonic_oscillator.png` — 조화 진동자 (고전 전환점 표시)
- `outputs/01_finite_square_well.png` — 유한 우물 (금지 영역 음영)

---

### 02 `02wavefunction.py` — 파동함수 시각화

**목표:** 복소 파동함수의 실수부/허수부/확률밀도/위상을 한 화면에 시각화한다.

#### 구현할 시각화 3종

**① 가우시안 파동 패킷**

```python
# 수식: ψ(x) = exp(-(x-x₀)²/4σ²) * exp(ik₀x)
def gaussian_wave_packet(x, x0=0, sigma=2.0, k0=2.0):
    envelope = np.exp(-(x - x0)**2 / (4 * sigma**2))
    phase    = np.exp(1j * k0 * x)
    return envelope * phase
```

4패널 구성: 실수부 / 허수부 / 확률밀도 |ψ|² / 위상 arg(ψ)

**② 중첩 상태 (Superposition)**

무한 우물의 고유함수를 조합:
- `ψ₁ + ψ₃` (비대칭 간섭)
- `ψ₁ + ψ₅` (복잡한 간섭)
- 균등 중첩 `(ψ₁ + ψ₂ + ψ₃ + ψ₄) / 2`

**③ 수소 원자 오비탈 (2D 단면)**

| 오비탈 | n | l |
|--------|---|---|
| 1s | 1 | 0 |
| 2s | 2 | 0 |
| 2p | 2 | 1 |
| 3s | 3 | 0 |

`scipy.special.sph_harm` + `np.meshgrid` 로 2D 확률밀도 히트맵

#### 출력 그래프

- `outputs/02_gaussian_wave_packet.png`
- `outputs/02_superposition_states.png`
- `outputs/02_hydrogen_orbitals.png`

---

### 03 `03tunneling.py` — 터널링 효과

**목표:** 전달 행렬법(Transfer Matrix Method)으로 투과율 T를 에너지 함수로 계산한다.

#### 핵심 로직

```python
def transmission_coefficient(E, V0, a, hbar=1.0, m=1.0):
    """
    E  : 입자 에너지
    V0 : 장벽 높이
    a  : 장벽 너비
    """
    if E < V0:
        kappa = np.sqrt(2 * m * (V0 - E)) / hbar   # 감쇠 계수
        T = 1 / (1 + (V0**2 * np.sinh(kappa * a)**2)
                     / (4 * E * (V0 - E)))
    else:
        k2 = np.sqrt(2 * m * (E - V0)) / hbar
        k1 = np.sqrt(2 * m * E) / hbar
        T = 1 / (1 + ((k1**2 - k2**2)**2 * np.sin(k2 * a)**2)
                     / (4 * k1**2 * k2**2))
    return T
```

#### 구현할 시뮬레이션 3종

**① 사각 장벽 터널링**
- 에너지 E = 0.5, 1.0, 1.5 세 케이스
- 공간 파동함수 ψ(x) 시각화: 입사파·장벽 내 감쇠·투과파

**② 공명 터널링 (이중 장벽)**
- 장벽 두 개 사이 우물 형성
- T vs E 그래프: 공명 피크 확인

**③ 매개변수 의존성**
- V₀ 변화 (2, 4, 6, 8): T vs E 곡선 4개
- 장벽 너비 a 변화 (1, 2, 3, 4): T vs E 곡선 4개

#### 출력 그래프

- `outputs/03_rectangular_barrier.png`
- `outputs/03_resonant_tunneling.png`
- `outputs/03_parameter_dependence.png`

---

### 04 `04wells_oscillator.py` — 유한 우물 & 조화 진동자 상세 분석

**목표:** 포텐셜 파라미터 변화에 따른 에너지 준위 이동을 비교 분석한다.

#### 구현할 분석 5종

| 번호 | 분석 내용 | 변수 | 고정값 |
|------|-----------|------|--------|
| ① | 유한 우물 깊이 의존성 | V₀ = 5, 10, 20 | L = 10 |
| ② | 유한 우물 너비 의존성 | L = 4, 8, 12 | V₀ = 10 |
| ③ | 조화 진동자 상세 (n=0~5) | — | ω = 1 |
| ④ | 우물 3종 비교 | — | 동일 L, 유사 V |
| ⑤ | 고전 vs 양자 확률 분포 | n = 0, 5, 20 | 조화 진동자 |

**⑤ 고전 확률 밀도 계산**

```python
def classical_probability(x, E, omega=1.0, m=1.0):
    """
    고전 조화 진동자의 위치 확률 밀도
    P_cl(x) = 1 / (π * sqrt(x_tp² - x²))
    x_tp: 전환점 = sqrt(2E / mω²)
    """
    x_tp = np.sqrt(2 * E / (m * omega**2))
    mask = np.abs(x) < x_tp
    P = np.zeros_like(x)
    P[mask] = 1 / (np.pi * np.sqrt(x_tp**2 - x[mask]**2))
    return P
```

#### 출력 그래프

- `outputs/04_finite_well_depth.png`
- `outputs/04_finite_well_width.png`
- `outputs/04_harmonic_oscillator_detail.png`
- `outputs/04_well_comparison.png`
- `outputs/04_classical_vs_quantum.png`

---

## 구현 순서 (권장)

```
1단계  공통 유틸 확보
       create_hamiltonian() / solve_schrodinger() / normalize() 구현 및 테스트

2단계  01schrodinger.py 완성
       세 포텐셜 → eigh 풀이 → 그래프 저장까지 end-to-end 확인

3단계  02wavefunction.py 완성
       가우시안 → 중첩 → 오비탈 순서로 구현

4단계  03tunneling.py 완성
       transmission_coefficient() 먼저 단위 테스트 후 시각화

5단계  04wells_oscillator.py 완성
       ①~⑤ 분석을 루프로 자동화, subplot 레이아웃 정리
```

---

## 검증 체크리스트

### 물리 정확도

- [ ] 무한 우물 에너지 공식 확인: `Eₙ = n²π²ℏ²/(2mL²)` (n=1,2,3,4,5)
- [ ] 조화 진동자 에너지 간격이 균등한지 확인: `ΔE = ℏω`
- [ ] 모든 파동함수의 총 확률 = 1.000 ± 0.001
- [ ] 터널링 투과율 0 ≤ T ≤ 1 범위 확인
- [ ] 유한 우물 파동함수가 금지 영역으로 지수 감쇠하는지 확인

### 코드 품질

- [ ] 각 파일 단독 실행 가능 (`uv run python XX.py`)
- [ ] `outputs/` 폴더 자동 생성 (`os.makedirs` 사용)
- [ ] 한국어 폰트 설정 (`Malgun Gothic` / `AppleGothic`)
- [ ] 마이너스 기호 깨짐 방지 (`axes.unicode_minus = False`)
- [ ] 그래프 저장 후 콘솔에 경로 출력

---

## 예상 소요 시간

| 파일 | 예상 시간 |
|------|-----------|
| `01schrodinger.py` | 1.5시간 |
| `02wavefunction.py` | 1.5시간 |
| `03tunneling.py` | 1시간 |
| `04wells_oscillator.py` | 1.5시간 |
| 디버깅 & 정리 | 0.5시간 |
| **합계** | **약 6시간** |

---

*Computational Physics Course — Week 11*