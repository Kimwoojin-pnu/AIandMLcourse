"""
03. 헬륨 원자 — Hartree-Fock SCF (Self-Consistent Field)

SCF 알고리즘:
  1. 초기 파동함수: 변분법 최적 Z_eff로 시작 (수렴 안정화)
  2. Hartree 포텐셜 V_H(r) = (1/r)∫₀^r u²dr' + ∫_r^∞ u²/r' dr' 수치 계산
  3. 유효 포텐셜: V_eff(r) = -Z/r + V_H(r)
  4. 1전자 슈뢰딩거 방정식 행렬 대각화 → ε, u_new
  5. 선형 혼합으로 수렴 안정화 (mixing=0.4)
  6. 총 에너지: E_total = 2ε - J  (J = ∫ u² V_H dr)

격자 설계: r = [dr, 2dr, ..., r_max]  (경계 조건 r=0에 정확히 위치)
기대 결과: E_HF ≈ -2.862 Hartree
"""

import sys
import os
import numpy as np
import matplotlib.pyplot as plt
from scipy.linalg import eigh

sys.stdout.reconfigure(encoding='utf-8')
plt.rcParams['font.family'] = 'Malgun Gothic'
plt.rcParams['axes.unicode_minus'] = False

output_dir = 'outputs'
os.makedirs(output_dir, exist_ok=True)

Z     = 2        # 헬륨 핵전하
E_exp = -2.9037  # 실험값 (Hartree)

print("=" * 60)
print("헬륨 원자: Hartree-Fock SCF")
print("=" * 60)

# ─────────────────────────────────────────────────────────
# 방사형 격자: r[0] = dr  (경계 조건 u(r=0)=0 정확히 구현)
# r = linspace(0.001, r_max)를 쓰면 V=-Z/r이 특이점 근처에서
# 수치 불안정 발생 → r[0]=dr 로 설정해야 함
# ─────────────────────────────────────────────────────────
N     = 500
r_max = 15.0
dr    = r_max / N       # = 0.03
r     = np.linspace(dr, r_max, N)   # r[0]=dr, 경계는 r=0

print(f"\n격자 설정: N={N}, r_max={r_max}, dr={dr:.4f}")
print(f"  r[0] = {r[0]:.4f}  (V[0] = {-Z/r[0]:.2f} Ha)")
print(f"  1/dr² = {1/dr**2:.2f}  → H[0,0] = {1/dr**2 - Z/r[0]:.2f}  (양수 ✓)")

# ─────────────────────────────────────────────────────────
# 유틸리티 함수
# ─────────────────────────────────────────────────────────
def hydrogen_like_u(r, Z_eff):
    """수소꼴 1s 방사형 함수 u(r)=r·R(r), ∫u²dr=1"""
    u = 2.0 * Z_eff**1.5 * r * np.exp(-Z_eff * r)
    return u / np.sqrt(np.trapz(u**2, r))

def compute_hartree_potential(r, u):
    """
    V_H(r1) = (1/r1) ∫₀^r1 u²dr' + ∫_{r1}^∞ u²/r' dr'
    O(N) 벡터화 구현
    """
    dR         = r[1] - r[0]
    u_sq       = u**2
    # 내부 적분
    V_inner    = np.cumsum(u_sq) * dR / r
    # 외부 적분
    u_sq_over_r = u_sq / r
    total_outer = np.sum(u_sq_over_r) * dR
    V_outer     = total_outer - np.cumsum(u_sq_over_r) * dR + u_sq_over_r * dR
    return V_inner + V_outer

def build_hamiltonian(r, V_eff):
    """유한 차분 해밀토니안: -1/2 d²/dr² + V_eff"""
    dR       = r[1] - r[0]
    diag     = np.full(len(r), 1.0 / dR**2) + V_eff
    off_diag = np.full(len(r) - 1, -0.5 / dR**2)
    return np.diag(diag) + np.diag(off_diag, 1) + np.diag(off_diag, -1)

# ─────────────────────────────────────────────────────────
# 격자 검증: 수소꼴 원자 (V=-2/r, Hartree 포텐셜 없음) ε=-2 확인
# ─────────────────────────────────────────────────────────
V_ext = -Z / r
H_test = build_hamiltonian(r, V_ext)
test_vals, _ = eigh(H_test, subset_by_index=[0, 0])
print(f"\n격자 검증: V=-Z/r만 사용시 ε = {test_vals[0]:.6f} Ha")
print(f"  (이론값 = {-Z**2/2:.6f} Ha, 오차 = {abs(test_vals[0]+Z**2/2):.6f})")

# ─────────────────────────────────────────────────────────
# SCF 반복
# ─────────────────────────────────────────────────────────
Z_eff_init = Z - 5.0 / 16.0    # = 1.6875 (변분법 최적값)
u          = hydrogen_like_u(r, Z_eff_init)
u_init     = u.copy()

max_iter = 100
tol      = 1e-8
mixing   = 0.4

energy_history  = []
epsilon_history = []
epsilon_old     = 0.0
converged       = False

print(f"\n--- SCF 반복 (mixing={mixing}) ---")
print(f"{'반복':>4}  {'ε (Ha)':>12}  {'E_total (Ha)':>14}  {'|Δε|':>12}")
print("-" * 50)

for it in range(max_iter):
    V_H   = compute_hartree_potential(r, u)
    V_eff = V_ext + V_H
    H     = build_hamiltonian(r, V_eff)

    vals, vecs = eigh(H, subset_by_index=[0, 0])
    eps    = vals[0]
    u_new  = vecs[:, 0]

    # 위상 고정 (양의 방향 강제)
    if u_new[N // 4] < 0:
        u_new = -u_new

    # 정규화
    u_new = u_new / np.sqrt(np.trapz(u_new**2, r))

    # J 적분 (현재 u로 계산)
    J     = np.trapz(u**2 * V_H, r)
    E     = 2.0 * eps - J

    energy_history.append(E)
    epsilon_history.append(eps)

    delta = abs(eps - epsilon_old)
    if it % 5 == 0 or delta < tol * 100:
        print(f"{it+1:>4}  {eps:>12.6f}  {E:>14.6f}  {delta:>12.2e}")

    if delta < tol and it > 2:
        print(f"\n  수렴 완료! (반복 {it+1}회, |Δε| = {delta:.2e})")
        converged = True
        break

    epsilon_old = eps

    # 선형 혼합
    u = mixing * u_new + (1.0 - mixing) * u
    u = u / np.sqrt(np.trapz(u**2, r))
else:
    print(f"\n  경고: 최대 반복 {max_iter}회 도달!")

# ─────────────────────────────────────────────────────────
# 최종 에너지 (수렴 파동함수로 재계산)
# ─────────────────────────────────────────────────────────
V_H_final   = compute_hartree_potential(r, u)
H_final     = build_hamiltonian(r, V_ext + V_H_final)
vals_f, _   = eigh(H_final, subset_by_index=[0, 0])
eps_f       = vals_f[0]
J_final     = np.trapz(u**2 * V_H_final, r)
E_hf        = 2.0 * eps_f - J_final
norm_final  = np.trapz(u**2, r)
Z_eff_hf    = np.sqrt(-2.0 * eps_f)

print(f"\n--- 최종 결과 ---")
print(f"  오비탈 에너지 ε:       {eps_f:.6f} Hartree")
print(f"  Coulomb 적분 J:       {J_final:.6f} Hartree")
print(f"  HF 총 에너지 E=2ε-J:  {E_hf:.6f} Hartree")
print(f"  실험값:               {E_exp:.6f} Hartree")
print(f"  오차:                 {abs(E_hf - E_exp)/abs(E_exp)*100:.2f}%")
print(f"  파동함수 정규화:       ∫u²dr = {norm_final:.6f}")
print(f"  유효 핵전하 Z_eff ≈   {Z_eff_hf:.4f}  (= sqrt(-2ε))")

# ─────────────────────────────────────────────────────────
# 그래프 1: SCF 수렴 곡선
# ─────────────────────────────────────────────────────────
fig, axes = plt.subplots(1, 2, figsize=(14, 6))
iters = np.arange(1, len(energy_history) + 1)

ax1 = axes[0]
ax1.plot(iters, energy_history, 'b-o', markersize=4, linewidth=2,
         label='HF 총 에너지 E=2ε-J')
ax1.axhline(E_hf,  color='r',  linestyle='--', linewidth=2,
            label=f'수렴값 = {E_hf:.4f} Ha')
ax1.axhline(E_exp, color='g',  linestyle=':',  linewidth=2,
            label=f'실험값 = {E_exp:.4f} Ha')
ax1.set_xlabel('SCF 반복 횟수', fontsize=13)
ax1.set_ylabel('에너지 (Hartree)', fontsize=13)
ax1.set_title('SCF 에너지 수렴 곡선', fontsize=13, fontweight='bold')
ax1.legend(fontsize=10)
ax1.grid(True, alpha=0.3)

ax2 = axes[1]
ax2.plot(iters, epsilon_history, 'r-s', markersize=4, linewidth=2,
         label='오비탈 에너지 ε')
ax2.axhline(eps_f, color='darkred', linestyle='--', linewidth=2,
            label=f'수렴값 ε = {eps_f:.4f} Ha')
ax2.set_xlabel('SCF 반복 횟수', fontsize=13)
ax2.set_ylabel('오비탈 에너지 (Hartree)', fontsize=13)
ax2.set_title('오비탈 에너지 ε 수렴', fontsize=13, fontweight='bold')
ax2.legend(fontsize=10)
ax2.grid(True, alpha=0.3)

plt.suptitle(f'Hartree-Fock SCF 수렴 (E_HF = {E_hf:.4f} Ha)', fontsize=14, fontweight='bold')
plt.tight_layout()
path = f'{output_dir}/03_scf_convergence.png'
plt.savefig(path, dpi=150, bbox_inches='tight')
print(f"\n저장: {path}")
plt.close()

# ─────────────────────────────────────────────────────────
# 그래프 2: 포텐셜 비교
# ─────────────────────────────────────────────────────────
r_plot = r[r <= 6]
idx = len(r_plot)

fig, ax = plt.subplots(figsize=(10, 7))
ax.plot(r_plot, V_ext[:idx],          'k-',  linewidth=2.5, label='외부 포텐셜 V_ext = -Z/r')
ax.plot(r_plot, V_H_final[:idx],      'r-',  linewidth=2.5, label='Hartree 포텐셜 V_H(r)')
ax.plot(r_plot, (V_ext+V_H_final)[:idx], 'b--', linewidth=2.5, label='유효 포텐셜 V_eff')
ax.axhline(eps_f, color='purple', linestyle=':', linewidth=2,
           label=f'오비탈 에너지 ε = {eps_f:.4f} Ha')
ax.fill_between(r_plot, V_ext[:idx], (V_ext+V_H_final)[:idx],
                alpha=0.15, color='red', label='Hartree 보정 (+)')
ax.set_xlabel('r (Bohr)', fontsize=13)
ax.set_ylabel('포텐셜 / 에너지 (Hartree)', fontsize=13)
ax.set_title('Hartree-Fock: 포텐셜 분석', fontsize=14, fontweight='bold')
ax.legend(fontsize=10, loc='lower right')
ax.set_ylim(-5, 1)
ax.set_xlim(0, 6)
ax.grid(True, alpha=0.3)
plt.tight_layout()
path = f'{output_dir}/03_hartree_potential.png'
plt.savefig(path, dpi=150, bbox_inches='tight')
print(f"저장: {path}")
plt.close()

# ─────────────────────────────────────────────────────────
# 그래프 3: SCF 전/후 파동함수 비교
# ─────────────────────────────────────────────────────────
u_z2  = hydrogen_like_u(r, 2.0)
u_var = hydrogen_like_u(r, Z_eff_init)

fig, axes = plt.subplots(1, 2, figsize=(14, 6))

ax1 = axes[0]
ax1.plot(r, u_z2,   'g--', linewidth=2,   label=f'초기 추측 (Z=2)')
ax1.plot(r, u_var,  'b--', linewidth=2,   label=f'변분법 (Z_eff={Z_eff_init:.4f})')
ax1.plot(r, u,      'r-',  linewidth=2.5, label=f'HF 수렴 결과')
ax1.axhline(0, color='k', linewidth=0.8, alpha=0.5)
ax1.set_xlabel('r (Bohr)', fontsize=13)
ax1.set_ylabel('u(r)', fontsize=13)
ax1.set_title('파동함수 비교: SCF 수렴 전후', fontsize=13, fontweight='bold')
ax1.legend(fontsize=10)
ax1.set_xlim(0, 6)
ax1.grid(True, alpha=0.3)

ax2 = axes[1]
ax2.plot(r, u_z2**2,  'g--', linewidth=2,   label='초기 추측 (Z=2)')
ax2.plot(r, u_var**2, 'b--', linewidth=2,   label='변분법')
ax2.plot(r, u**2,     'r-',  linewidth=2.5, label='HF 수렴 결과')
ax2.set_xlabel('r (Bohr)', fontsize=13)
ax2.set_ylabel('u²(r)  (방사형 확률밀도)', fontsize=13)
ax2.set_title('방사형 확률밀도 비교', fontsize=13, fontweight='bold')
ax2.legend(fontsize=10)
ax2.set_xlim(0, 6)
ax2.grid(True, alpha=0.3)

plt.suptitle(f'Hartree-Fock SCF 파동함수 (E = {E_hf:.4f} Ha)', fontsize=14, fontweight='bold')
plt.tight_layout()
path = f'{output_dir}/03_scf_wavefunction.png'
plt.savefig(path, dpi=150, bbox_inches='tight')
print(f"저장: {path}")
plt.close()

print("\n" + "=" * 60)
print("Hartree-Fock SCF 완료")
print("=" * 60)
print(f"  E_HF = {E_hf:.6f} Hartree")
