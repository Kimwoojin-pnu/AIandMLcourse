"""
04. 헬륨 원자 — 종합 비교 및 시각화

세 가지 근사법 결과를 실험값 -2.904 Hartree와 비교:

  방법               에너지(Ha)  오차
  독립 전자 근사     -4.000     ~38%  (전자 반발 완전 무시)
  변분법             -2.848     ~2%   (유효 핵전하 최적화)
  Hartree-Fock SCF   ~-2.862   ~1%   (평균장 자기일관장)
  실험값             -2.904     기준
"""

import sys
import os
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
from scipy.optimize import minimize_scalar
from scipy.linalg import eigh

sys.stdout.reconfigure(encoding='utf-8')
plt.rcParams['font.family'] = 'Malgun Gothic'
plt.rcParams['axes.unicode_minus'] = False

output_dir = 'outputs'
os.makedirs(output_dir, exist_ok=True)

Z     = 2
E_exp = -2.9037   # 실험값 (정확한 비상대론적 값)

print("=" * 65)
print("헬륨 원자: 종합 비교 (독립 전자 / 변분법 / HF SCF)")
print("=" * 65)

# ═══════════════════════════════════════════════════════════
# 공통 방사형 격자
# ═══════════════════════════════════════════════════════════
N     = 1000
r_max = 20.0
r     = np.linspace(0.001, r_max, N)
dr    = r[1] - r[0]

def normalize_u(u, r):
    return u / np.sqrt(np.trapz(u**2, r))

def hydrogen_like_u(r, Z_eff):
    u = 2.0 * Z_eff**1.5 * r * np.exp(-Z_eff * r)
    return normalize_u(u, r)

# ═══════════════════════════════════════════════════════════
# 방법 1: 독립 전자 근사
# ═══════════════════════════════════════════════════════════
E_indep    = -float(Z**2)    # = -4.000 Ha
E_repul    = 5.0 * Z / 8.0   # <1/r12> = 1.250 Ha (1차 섭동)
E_perturb  = E_indep + E_repul  # = -2.750 Ha
u_indep    = hydrogen_like_u(r, Z)
J_indep    = 5.0 * Z / 8.0   # 해석적 값

print(f"\n[방법 1] 독립 전자 근사")
print(f"  에너지: {E_indep:.4f} Ha  |  오차: {abs(E_indep-E_exp)/abs(E_exp)*100:.1f}%")
print(f"  (1차 섭동 후: {E_perturb:.4f} Ha)")

# ═══════════════════════════════════════════════════════════
# 방법 2: 변분법
# ═══════════════════════════════════════════════════════════
def variational_energy(Z_eff, Z=2):
    return Z_eff**2 - 2 * Z * Z_eff + 5 * Z_eff / 8

res       = minimize_scalar(variational_energy, bounds=(0.1, 3.5),
                             method='bounded', args=(Z,))
Z_eff_opt = res.x
E_var     = res.fun
u_var     = hydrogen_like_u(r, Z_eff_opt)
J_var     = 5.0 * Z_eff_opt / 8.0

print(f"\n[방법 2] 변분법")
print(f"  최적 Z_eff: {Z_eff_opt:.6f}  (해석: {Z-5/16:.6f})")
print(f"  에너지: {E_var:.4f} Ha  |  오차: {abs(E_var-E_exp)/abs(E_exp)*100:.2f}%")

# ═══════════════════════════════════════════════════════════
# 방법 3: Hartree-Fock SCF
# ═══════════════════════════════════════════════════════════
print(f"\n[방법 3] Hartree-Fock SCF 계산 중...")

def build_hamiltonian(r, V_eff):
    dR       = r[1] - r[0]
    N        = len(r)
    diag     = 1.0 / dR**2 + V_eff
    off_diag = np.full(N - 1, -0.5 / dR**2)
    return np.diag(diag) + np.diag(off_diag, 1) + np.diag(off_diag, -1)

def compute_hartree_potential(r, u):
    dR           = r[1] - r[0]
    u_sq         = u**2
    inner        = np.cumsum(u_sq) * dR
    V_inner      = inner / r
    u_sq_over_r  = u_sq / r
    total_outer  = np.sum(u_sq_over_r) * dR
    V_outer      = total_outer - np.cumsum(u_sq_over_r) * dR + u_sq_over_r * dR
    return V_inner + V_outer

# SCF 반복 (N=600 격자 사용)
N_scf   = 600
r_scf   = np.linspace(0.001, r_max, N_scf)
dr_scf  = r_scf[1] - r_scf[0]
V_ext   = -Z / r_scf

u_scf   = hydrogen_like_u(r_scf, Z_eff_opt)
max_iter = 100
tol      = 1e-8
mixing   = 0.4
eps_old  = 0.0
e_hist   = []

for it in range(max_iter):
    V_H   = compute_hartree_potential(r_scf, u_scf)
    V_eff = V_ext + V_H
    H     = build_hamiltonian(r_scf, V_eff)
    vals, vecs = eigh(H, subset_by_index=[0, 0])
    eps    = vals[0]
    u_new  = vecs[:, 0]
    if u_new[N_scf // 4] < 0:
        u_new = -u_new
    u_new  = normalize_u(u_new, r_scf)
    J_now  = np.trapz(u_scf**2 * V_H, r_scf)
    e_hist.append(2 * eps - J_now)
    if abs(eps - eps_old) < tol and it > 2:
        break
    eps_old = eps
    u_scf   = mixing * u_new + (1 - mixing) * u_scf
    u_scf   = normalize_u(u_scf, r_scf)

# 최종 에너지
V_H_f  = compute_hartree_potential(r_scf, u_scf)
H_f    = build_hamiltonian(r_scf, V_ext + V_H_f)
eps_f, _ = eigh(H_f, subset_by_index=[0, 0])
eps_f  = eps_f[0]
J_hf   = np.trapz(u_scf**2 * V_H_f, r_scf)
E_hf   = 2 * eps_f - J_hf

# HF 파동함수를 N=1000 격자에 보간
from scipy.interpolate import interp1d
interp_u = interp1d(r_scf, u_scf, kind='cubic', fill_value='extrapolate')
u_hf     = normalize_u(np.maximum(interp_u(r), 0), r)

Z_eff_hf = np.sqrt(-2 * eps_f)   # 유효 핵전하 추정

print(f"  오비탈 에너지 ε = {eps_f:.6f} Ha")
print(f"  Coulomb 적분 J  = {J_hf:.6f} Ha")
print(f"  HF 에너지: {E_hf:.4f} Ha  |  오차: {abs(E_hf-E_exp)/abs(E_exp)*100:.2f}%")

# ═══════════════════════════════════════════════════════════
# 에너지 오차 요약 테이블
# ═══════════════════════════════════════════════════════════
print("\n" + "=" * 65)
print("최종 비교 (기준: 실험값 -2.904 Hartree)")
print("=" * 65)
methods_info = [
    ("독립 전자 근사", E_indep, 2.0,    J_indep),
    ("변분법",        E_var,   Z_eff_opt, J_var),
    ("Hartree-Fock", E_hf,   Z_eff_hf,  J_hf),
    ("실험값",        E_exp,   None,     None),
]
print(f"{'방법':<18} {'에너지(Ha)':>12} {'오차(%)':>9} {'Z_eff':>8} {'J(Ha)':>8}")
print("-" * 60)
for name, E, Zeff, J in methods_info:
    err = abs(E - E_exp) / abs(E_exp) * 100
    zstr = f"{Zeff:.4f}" if Zeff else "  —  "
    jstr = f"{J:.4f}"   if J else "  —  "
    print(f"{name:<18} {E:>12.4f} {err:>9.2f} {zstr:>8} {jstr:>8}")

# ═══════════════════════════════════════════════════════════
# 그래프 ①: 에너지 비교 막대그래프
# ═══════════════════════════════════════════════════════════
method_names = ['독립 전자\n근사', '변분법', 'Hartree-\nFock', '실험값\n(기준)']
energies_all = [E_indep, E_var, E_hf, E_exp]
colors_all   = ['#E74C3C', '#F39C12', '#3498DB', '#2ECC71']

fig, ax = plt.subplots(figsize=(11, 7))
bars = ax.bar(method_names, energies_all, color=colors_all, width=0.55,
              edgecolor='black', linewidth=1.5, alpha=0.9)

for bar, E in zip(bars, energies_all):
    err = abs(E - E_exp) / abs(E_exp) * 100
    ax.text(bar.get_x() + bar.get_width()/2, E - 0.10,
            f'{E:.3f} Ha\n({err:.1f}% 오차)', ha='center', va='top',
            fontsize=11, fontweight='bold', color='white')

ax.axhline(E_exp, color='#1A5276', linestyle='--', linewidth=2.5,
           label=f'실험값 = {E_exp:.4f} Ha (기준)')
ax.set_ylabel('총 에너지 (Hartree)', fontsize=13)
ax.set_title('헬륨 원자 기저 상태 에너지 비교\n(기준: 실험값 -2.904 Ha)',
             fontsize=14, fontweight='bold')
ax.legend(fontsize=12)
ax.set_ylim(min(energies_all) - 0.5, 0.5)
ax.grid(True, axis='y', alpha=0.3)
ax.tick_params(axis='x', labelsize=12)

plt.tight_layout()
path = f'{output_dir}/04_energy_comparison.png'
plt.savefig(path, dpi=150, bbox_inches='tight')
print(f"\n저장: {path}")
plt.close()

# ═══════════════════════════════════════════════════════════
# 그래프 ②: 방사형 파동함수 비교
# ═══════════════════════════════════════════════════════════
fig, ax = plt.subplots(figsize=(10, 7))
ax.plot(r, u_indep, 'r-',  linewidth=2.5, label=f'독립 전자 (Z=2)')
ax.plot(r, u_var,   'b--', linewidth=2.5, label=f'변분법 (Z_eff={Z_eff_opt:.4f})')
ax.plot(r, u_hf,    'g:',  linewidth=3.0, label=f'Hartree-Fock (Z_eff≈{Z_eff_hf:.4f})')
ax.axhline(0, color='k', linewidth=0.8, alpha=0.5)
ax.set_xlabel('r (Bohr)', fontsize=13)
ax.set_ylabel('u(r)', fontsize=13)
ax.set_title('방사형 파동함수 u(r) 비교: 세 가지 근사법', fontsize=14, fontweight='bold')
ax.legend(fontsize=12)
ax.set_xlim(0, 6)
ax.grid(True, alpha=0.3)
plt.tight_layout()
path = f'{output_dir}/04_radial_comparison.png'
plt.savefig(path, dpi=150, bbox_inches='tight')
print(f"저장: {path}")
plt.close()

# ═══════════════════════════════════════════════════════════
# 그래프 ③: 방사형 확률밀도 비교
# ═══════════════════════════════════════════════════════════
fig, ax = plt.subplots(figsize=(10, 7))
ax.plot(r, u_indep**2, 'r-',  linewidth=2.5, label=f'독립 전자 (Z=2)')
ax.plot(r, u_var**2,   'b--', linewidth=2.5, label=f'변분법 (Z_eff={Z_eff_opt:.4f})')
ax.plot(r, u_hf**2,    'g:',  linewidth=3.0, label=f'Hartree-Fock')

# 최대 확률 반경 표시
for u_, lab, col in [(u_indep,'독립','r'), (u_var,'변분','b'), (u_hf,'HF','g')]:
    r_peak = r[np.argmax(u_**2)]
    ax.axvline(r_peak, color=col, linestyle=':', linewidth=1.2, alpha=0.6)

ax.set_xlabel('r (Bohr)', fontsize=13)
ax.set_ylabel('방사형 확률밀도 u²(r)', fontsize=13)
ax.set_title('방사형 확률밀도 비교: 세 가지 근사법', fontsize=14, fontweight='bold')
ax.legend(fontsize=12)
ax.set_xlim(0, 6)
ax.grid(True, alpha=0.3)
plt.tight_layout()
path = f'{output_dir}/04_probability_comparison.png'
plt.savefig(path, dpi=150, bbox_inches='tight')
print(f"저장: {path}")
plt.close()

# ═══════════════════════════════════════════════════════════
# 그래프 ④: 전자-전자 반발 포텐셜 기댓값 비교
# ═══════════════════════════════════════════════════════════
fig, ax = plt.subplots(figsize=(10, 7))

method_names4 = ['독립 전자\n근사', '변분법', 'Hartree-Fock']
J_values      = [J_indep, J_var, J_hf]
colors4       = ['#E74C3C', '#F39C12', '#3498DB']

bars = ax.bar(method_names4, J_values, color=colors4, width=0.4,
              edgecolor='black', linewidth=1.5, alpha=0.9)
for bar, J in zip(bars, J_values):
    ax.text(bar.get_x() + bar.get_width()/2, J + 0.01,
            f'{J:.4f} Ha', ha='center', va='bottom',
            fontsize=13, fontweight='bold')

ax.set_ylabel('<1/r₁₂>  전자-전자 반발 기댓값 (Hartree)', fontsize=12)
ax.set_title('전자-전자 반발 에너지 <1/r₁₂> 비교', fontsize=14, fontweight='bold')
ax.grid(True, axis='y', alpha=0.3)
ax.set_ylim(0, max(J_values) + 0.15)
ax.tick_params(axis='x', labelsize=12)

plt.tight_layout()
path = f'{output_dir}/04_repulsion_comparison.png'
plt.savefig(path, dpi=150, bbox_inches='tight')
print(f"저장: {path}")
plt.close()

# ═══════════════════════════════════════════════════════════
# 그래프 ⑤: 차폐 효과 요약 (Z → Z_eff)
# ═══════════════════════════════════════════════════════════
fig, axes = plt.subplots(1, 2, figsize=(14, 6))

ax1 = axes[0]
method_labels = ['독립 전자 근사', '변분법', 'Hartree-Fock']
Z_eff_vals    = [2.0, Z_eff_opt, Z_eff_hf]
sigma_vals    = [Z - ze for ze in Z_eff_vals]
colors5       = ['#E74C3C', '#F39C12', '#3498DB']

x_pos = np.arange(len(method_labels))
bars1 = ax1.bar(x_pos - 0.2, [Z]*3, 0.35, color='#AED6F1',
                edgecolor='k', linewidth=1.2, label='실제 Z = 2', alpha=0.8)
bars2 = ax1.bar(x_pos + 0.2, Z_eff_vals, 0.35, color=colors5,
                edgecolor='k', linewidth=1.2, label='유효 Z_eff', alpha=0.9)

for bar, ze in zip(bars2, Z_eff_vals):
    ax1.text(bar.get_x() + bar.get_width()/2, ze + 0.03,
             f'{ze:.4f}', ha='center', va='bottom', fontsize=11, fontweight='bold')

ax1.set_xticks(x_pos)
ax1.set_xticklabels(method_labels, fontsize=11)
ax1.set_ylabel('핵전하', fontsize=13)
ax1.set_title('Z vs Z_eff: 전자 차폐 효과', fontsize=13, fontweight='bold')
ax1.legend(fontsize=11)
ax1.set_ylim(0, 2.5)
ax1.grid(True, axis='y', alpha=0.3)

ax2 = axes[1]
ax2.barh(method_labels[::-1], sigma_vals[::-1], color=colors5[::-1],
         edgecolor='k', linewidth=1.2, alpha=0.9)
for i, (s, ze) in enumerate(zip(sigma_vals[::-1], Z_eff_vals[::-1])):
    ax2.text(s + 0.005, i, f'σ={s:.4f}  (Z_eff={ze:.4f})',
             va='center', fontsize=11, fontweight='bold')

ax2.set_xlabel('차폐 상수 σ = Z - Z_eff', fontsize=13)
ax2.set_title('각 방법의 차폐 상수 σ', fontsize=13, fontweight='bold')
ax2.set_xlim(0, max(sigma_vals) + 0.2)
ax2.grid(True, axis='x', alpha=0.3)

plt.suptitle('헬륨 전자-전자 차폐 효과 요약', fontsize=14, fontweight='bold')
plt.tight_layout()
path = f'{output_dir}/04_screening_summary.png'
plt.savefig(path, dpi=150, bbox_inches='tight')
print(f"저장: {path}")
plt.close()

# ═══════════════════════════════════════════════════════════
# 최종 요약 출력
# ═══════════════════════════════════════════════════════════
print("\n" + "=" * 65)
print("최종 오차 비교 — 실험값 -2.904 Hartree 대비")
print("=" * 65)
results = [
    ("독립 전자 근사", E_indep),
    ("변분법",        E_var),
    ("Hartree-Fock",  E_hf),
]
for name, E in results:
    abs_err = abs(E - E_exp)
    rel_err = abs_err / abs(E_exp) * 100
    print(f"  {name:<18}: {E:>8.4f} Ha  |  절대오차 {abs_err:.4f} Ha  |  상대오차 {rel_err:.2f}%")
print(f"  {'실험값 (기준)':<18}: {E_exp:>8.4f} Ha")
print("\n  정확도 순서: HF > 변분법 > 독립 전자 근사")
print("=" * 65)
