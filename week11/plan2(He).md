# 헬륨 원자(He) 양자역학 시뮬레이션 — 구현 Plan

## 개요

헬륨 원자는 전자가 2개인 **가장 간단한 다체(many-body) 양자 시스템**이다.
전자-전자 반발 항 때문에 수소 원자와 달리 정확한 해석해가 존재하지 않아,
수치 근사 기법이 반드시 필요하다.

| 항목 | 내용 |
|------|------|
| 총 파일 수 | 4개 |
| 주요 라이브러리 | `numpy`, `scipy`, `matplotlib` |
| 출력 디렉토리 | `helium/outputs/` |
| 실행 방법 | `python <파일명>` 또는 `uv run python <파일명>` |

---

## 핵심 물리 배경

### 헬륨 원자 해밀토니안

```
Ĥ = -ℏ²/2m ∇₁² - ℏ²/2m ∇₂²   ← 전자 1, 2의 운동에너지
    - Ze²/r₁ - Ze²/r₂           ← 핵-전자 인력 (Z=2)
    + e²/r₁₂                    ← 전자-전자 반발 (이것 때문에 정확해 없음!)
```

**전자-전자 반발항** `e²/r₁₂`이 없으면 수소꼴 원자 2개로 분리되어 풀 수 있지만,
이 항 때문에 근사 기법이 필요하다.

### 주요 근사 기법 비교

| 기법 | 아이디어 | 정확도 | 구현 난이도 |
|------|----------|--------|------------|
| 독립 전자 근사 | 전자-전자 반발 무시 | 낮음 | ★☆☆ |
| 변분법 | 시도 파동함수 최적화 | 중간 | ★★☆ |
| Hartree-Fock | 평균장으로 반발 처리 | 높음 | ★★★ |

---

## 파일별 구현 계획

### 01 `01independent_electron.py` — 독립 전자 근사

**목표:** 전자-전자 반발을 무시하고 수소꼴 원자 2개로 취급하여 기저 상태 계산.

#### 물리 모델

```
V(r) = -Ze²/r  (Z=2, e=1 자연 단위)
ψ(r₁, r₂) = ψ₁s(r₁) · ψ₁s(r₂)
```

#### 핵심 함수

```python
def hydrogen_like_wavefunction(r, Z=2, n=1):
    """수소꼴 1s 파동함수: ψ(r) = (Z/a₀)^(3/2) * exp(-Zr/a₀) / √π"""
    a0 = 1.0  # 보어 반지름 (자연 단위)
    return (Z / a0)**1.5 * np.exp(-Z * r / a0) / np.sqrt(np.pi)

def energy_independent(Z=2):
    """독립 전자 근사 에너지: E = -Z²(1/1² + 1/2²) Ry"""
    return -Z**2 * (1 + 1)  # 두 전자 모두 1s
```

#### 출력 그래프

- `outputs/01_independent_radial.png` — 1s 방사형 파동함수 + 확률밀도
- `outputs/01_energy_comparison.png` — 근사값 vs 실험값 비교 막대그래프

---

### 02 `02variational.py` — 변분법 (Variational Method)

**목표:** 변분 원리를 이용해 유효 핵전하 `Z_eff`를 최적화하여 에너지를 최소화.

#### 물리 모델

시도 파동함수(trial wavefunction):
```
ψ_trial(r₁, r₂) = (Z_eff³/π) · exp(-Z_eff(r₁ + r₂))
```

기댓값 에너지:
```
E(Z_eff) = Z_eff² - 2Z·Z_eff + 5Z_eff/8
```

`dE/dZ_eff = 0` → 최적 `Z_eff = Z - 5/16 = 2 - 5/16 ≈ 1.6875`

#### 핵심 함수

```python
def variational_energy(Z_eff, Z=2):
    """변분 에너지 공식 (원자 단위)"""
    return Z_eff**2 - 2 * Z * Z_eff + 5 * Z_eff / 8

def optimize_Z_eff(Z=2):
    """scipy.optimize.minimize_scalar 로 Z_eff 최적화"""
    from scipy.optimize import minimize_scalar
    result = minimize_scalar(variational_energy, bounds=(0.1, 3.0),
                             method='bounded', args=(Z,))
    return result.x, result.fun
```

#### 출력 그래프

- `outputs/02_energy_vs_Zeff.png` — E(Z_eff) 곡선 + 최솟값 표시
- `outputs/02_trial_wavefunction.png` — 최적 Z_eff의 시도 파동함수
- `outputs/02_screening.png` — 차폐 효과 시각화 (Z vs Z_eff)

---

### 03 `03hartree_fock.py` — Hartree-Fock 자기 일관장 (SCF)

**목표:** Self-Consistent Field(SCF) 반복으로 전자-전자 반발을 평균장으로 처리.

#### SCF 알고리즘

```
1. 초기 파동함수 추정: ψ⁰(r) = 수소꼴 1s
2. 반복 (수렴까지):
   a. 현재 ψ로 Hartree 포텐셜 계산:
      V_H(r₁) = ∫ |ψ(r₂)|² / r₁₂ dr₂
   b. 유효 포텐셜: V_eff(r) = -Z/r + V_H(r)
   c. 1전자 슈뢰딩거 방정식 풀기: [-∇²/2 + V_eff]ψ_new = ε·ψ_new
   d. 수렴 확인: |E_new - E_old| < 1e-6
3. 총 에너지 계산: E_total = 2ε - E_H  (이중 계산 보정)
```

#### 핵심 함수

```python
def compute_hartree_potential(r, psi, dr):
    """방사형 격자에서 Hartree 포텐셜 수치 적분"""
    ...

def scf_iteration(r, V_ext, psi_init, max_iter=100, tol=1e-6):
    """SCF 반복 루프 → 수렴된 (psi, energy, n_iter) 반환"""
    ...
```

#### 출력 그래프

- `outputs/03_scf_convergence.png` — 반복 횟수 vs 에너지 수렴 곡선
- `outputs/03_hartree_potential.png` — 외부 포텐셜 + Hartree 포텐셜 + 유효 포텐셜
- `outputs/03_scf_wavefunction.png` — SCF 수렴 전/후 파동함수 비교

---

### 04 `04comparison.py` — 종합 비교 및 시각화

**목표:** 세 가지 근사의 결과를 실험값과 비교하고, 각 방법의 물리적 의미를 시각화.

#### 에너지 비교표 (원자 단위, Hartree)

| 방법 | 에너지 (Hartree) | 오차 |
|------|-----------------|------|
| 독립 전자 근사 | -4.000 | ~8% |
| 변분법 | -2.848 | ~2% |
| Hartree-Fock | -2.862 | ~1% |
| 실험값 | -2.904 | 기준 |

#### 구현할 시각화 5종

| 번호 | 내용 |
|------|------|
| ① | 방법별 에너지 비교 막대그래프 (실험값 기준선 포함) |
| ② | 방법별 방사형 파동함수 중첩 비교 |
| ③ | 방법별 방사형 확률밀도 `r²\|ψ\|²` 비교 |
| ④ | 전자-전자 반발 포텐셜 `1/r₁₂` 기댓값 비교 |
| ⑤ | 차폐 효과 요약: Z=2 → Z_eff 시각화 |

---

## 구현 순서 (권장)

```
1단계  공통 유틸 준비
       방사형 격자 생성, 파동함수 정규화, 수치 적분 함수

2단계  01 독립 전자 근사
       가장 단순 → 기준값으로 활용

3단계  02 변분법
       해석적 풀이 + scipy 최적화 → 빠르게 구현 가능

4단계  03 Hartree-Fock SCF
       가장 복잡한 핵심 파트 → 수렴 안정성 주의

5단계  04 종합 비교
       앞 세 파일 결과를 import해서 통합 시각화
```

---

## 공통 유틸 설계

```python
# utils.py (또는 각 파일 상단에 포함)

import numpy as np

# 자연 단위계 (원자 단위)
hbar = 1.0
m_e  = 1.0
e    = 1.0
a0   = 1.0   # 보어 반지름

def make_radial_grid(r_max=20.0, N=1000):
    """로그 스케일 방사형 격자 (r=0 근처 정밀도 향상)"""
    return np.linspace(0.001, r_max, N)

def normalize_radial(psi, r, dr):
    """방사형 파동함수 정규화: ∫|ψ|²r²dr = 1"""
    norm = np.sqrt(np.trapz(np.abs(psi)**2 * r**2, r))
    return psi / norm

def expectation_value(psi, operator_values, r):
    """기댓값 계산: <O> = ∫ ψ* O ψ r²dr"""
    return np.trapz(np.abs(psi)**2 * operator_values * r**2, r)
```

---

## 검증 체크리스트

### 물리 정확도

- [ ] 독립 전자 근사 에너지 = -4.000 Hartree 재현
- [ ] 변분법 최적 Z_eff ≈ 1.6875 재현
- [ ] 변분법 에너지 ≈ -2.848 Hartree 재현
- [ ] SCF 수렴 (에너지 변화 < 1e-6)
- [ ] 모든 파동함수 정규화 확인: `∫|ψ|²r²dr ≈ 1.000`
- [ ] 실험값(-2.904 Hartree)과 오차율 확인

### 코드 품질

- [ ] 각 파일 단독 실행 가능
- [ ] `outputs/` 폴더 자동 생성
- [ ] 한국어 폰트 설정 (Malgun Gothic)
- [ ] 그래프마다 물리량 단위 명시 (Hartree, Bohr 등)
- [ ] SCF 루프에 최대 반복 횟수 제한 및 경고 출력

---

## 예상 소요 시간

| 파일 | 예상 시간 |
|------|-----------|
| `01independent_electron.py` | 1시간 |
| `02variational.py` | 1시간 |
| `03hartree_fock.py` | 2시간 |
| `04comparison.py` | 1시간 |
| 디버깅 & 정리 | 0.5시간 |
| **합계** | **약 5.5시간** |

---

## 참고 자료

- Griffiths, *Introduction to Quantum Mechanics*, Chapter 5 (identical particles)
- Griffiths, *Introduction to Quantum Mechanics*, Chapter 7 (variational principle)
- Szabo & Ostlund, *Modern Quantum Chemistry*, Chapter 3 (Hartree-Fock)

---

*Helium Atom Quantum Simulation Plan*
*라이브러리: Python 3.x + NumPy + SciPy + Matplotlib*