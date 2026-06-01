"""
02. 헬륨 원자 — 변분법 (Variational Method)

시도 파동함수: ψ_trial(r1,r2) = (Z_eff³/π) exp(-Z_eff(r1+r2))
에너지 기댓값: E(Z_eff) = Z_eff² - 2Z·Z_eff + 5Z_eff/8
최적화: dE/dZ_eff = 0  →  Z_eff* = Z - 5/16 = 1.6875
최소 에너지: E_min ≈ -2.848 Hartree
"""

import sys
import os
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import minimize_scalar

sys.stdout.reconfigure(encoding='utf-8')
plt.rcParams['font.family'] = 'Malgun Gothic'
plt.rcParams['axes.unicode_minus'] = False

output_dir = 'outputs'
os.makedirs(output_dir, exist_ok=True)

Z   = 2      # 헬륨 핵전하
a0  = 1.0    # 보어 반지름
E_exp = -2.9037  # 실험값 (Hartree)

print("=" * 60)
print("헬륨 원자: 변분법")
print("=" * 60)

# ─────────────────────────────────────────────────────────
# 변분 에너지 함수
# ─────────────────────────────────────────────────────────
def variational_energy(Z_eff, Z=2):
    """E(Z_eff) = Z_eff² - 2Z·Z_eff + 5Z_eff/8  (원자 단위)"""
    return Z_eff**2 - 2 * Z * Z_eff + 5 * Z_eff / 8

def optimize_Z_eff(Z=2):
    result = minimize_scalar(variational_energy,
                             bounds=(0.1, 3.5),
                             method='bounded',
                             args=(Z,))
    return result.x, result.fun

# 최적 Z_eff 계산
Z_eff_opt, E_min = optimize_Z_eff(Z)
Z_eff_analytical = Z - 5.0 / 16.0   # 해석적 값 = 1.6875

print(f"\n--- 변분법 결과 ---")
print(f"  최적 Z_eff (scipy):   {Z_eff_opt:.6f}")
print(f"  최적 Z_eff (해석적):   {Z_eff_analytical:.6f}  (= Z - 5/16)")
print(f"  최소 에너지:          {E_min:.6f} Hartree")
print(f"  실험값:              {E_exp:.4f} Hartree")
print(f"  오차:                {abs(E_min - E_exp)/abs(E_exp)*100:.2f}%")

# 에너지 구성 분석
T_term  = Z_eff_opt**2                      # 운동에너지 (2전자)
Vne_term = -2 * Z * Z_eff_opt              # 핵-전자 인력 (2전자)
Vee_term = 5 * Z_eff_opt / 8              # 전자-전자 반발
print(f"\n  에너지 구성 (Z_eff = {Z_eff_opt:.4f}):")
print(f"    <T>  (운동에너지):     {T_term:.4f} Ha")
print(f"    <Vne>(핵-전자 인력):  {Vne_term:.4f} Ha")
print(f"    <Vee>(전자-전자 반발): {Vee_term:.4f} Ha")
print(f"    합계:                {T_term + Vne_term + Vee_term:.4f} Ha")

# 차폐 효과
screening = Z - Z_eff_opt
print(f"\n  차폐 상수 σ = Z - Z_eff = {screening:.4f}")
print(f"  각 전자는 핵전하 {Z}에서 {screening:.4f} 만큼 차폐됨")

# ─────────────────────────────────────────────────────────
# 방사형 격자
# ─────────────────────────────────────────────────────────
N = 1000
r = np.linspace(0.001, 20.0, N)
dr = r[1] - r[0]

def hydrogen_like_u(r, Z_eff):
    u = 2.0 * Z_eff**1.5 * r * np.exp(-Z_eff * r)
    norm = np.sqrt(np.trapz(u**2, r))
    return u / norm

# ─────────────────────────────────────────────────────────
# 그래프 1: E(Z_eff) 곡선
# ─────────────────────────────────────────────────────────
Z_eff_range = np.linspace(0.5, 3.0, 500)
E_range = variational_energy(Z_eff_range, Z)

fig, ax = plt.subplots(figsize=(10, 7))
ax.plot(Z_eff_range, E_range, 'b-', linewidth=2.5, label='E(Z_eff)')
ax.scatter([Z_eff_opt], [E_min], color='red', s=200, zorder=5,
           label=f'최솟값: Z_eff*={Z_eff_opt:.4f}, E={E_min:.4f} Ha')
ax.axhline(E_exp, color='g', linestyle='--', linewidth=2,
           label=f'실험값 = {E_exp:.4f} Ha')
ax.axvline(Z_eff_opt, color='r', linestyle=':', linewidth=1.5, alpha=0.7)
ax.axvline(Z, color='gray', linestyle=':', linewidth=1.5, alpha=0.7,
           label=f'Z = {Z} (차폐 없음)')

ax.set_xlabel('유효 핵전하 Z_eff', fontsize=13)
ax.set_ylabel('에너지 (Hartree)', fontsize=13)
ax.set_title('변분 에너지 E(Z_eff) = Z_eff² - 2Z·Z_eff + 5Z_eff/8', fontsize=14, fontweight='bold')
ax.legend(fontsize=11)
ax.set_ylim(-3.5, -1.5)
ax.grid(True, alpha=0.3)

# 최솟값 주석
ax.annotate(f'Z_eff* = {Z_eff_opt:.4f}\nE_min = {E_min:.4f} Ha',
            xy=(Z_eff_opt, E_min), xytext=(Z_eff_opt + 0.4, E_min + 0.3),
            fontsize=11, color='red',
            arrowprops=dict(arrowstyle='->', color='red', lw=1.5))

plt.tight_layout()
path = f'{output_dir}/02_energy_vs_Zeff.png'
plt.savefig(path, dpi=150, bbox_inches='tight')
print(f"\n저장: {path}")
plt.close()

# ─────────────────────────────────────────────────────────
# 그래프 2: 시도 파동함수 비교 (여러 Z_eff)
# ─────────────────────────────────────────────────────────
Z_eff_list = [1.0, Z_eff_opt, Z]
labels = ['Z_eff=1.0 (약한 차폐)', f'Z_eff={Z_eff_opt:.4f} (최적)', f'Z_eff=Z={Z} (차폐 없음)']
colors = ['#3498DB', '#E74C3C', '#2ECC71']

fig, axes = plt.subplots(1, 2, figsize=(14, 6))

ax1 = axes[0]
for z, lab, col in zip(Z_eff_list, labels, colors):
    u = hydrogen_like_u(r, z)
    ax1.plot(r, u, color=col, linewidth=2.5, label=lab)
ax1.axhline(0, color='k', linewidth=0.8, alpha=0.5)
ax1.set_xlabel('r (Bohr)', fontsize=13)
ax1.set_ylabel('u(r)', fontsize=13)
ax1.set_title('시도 파동함수 u(r): Z_eff 비교', fontsize=13, fontweight='bold')
ax1.legend(fontsize=10)
ax1.set_xlim(0, 6)
ax1.grid(True, alpha=0.3)

ax2 = axes[1]
for z, lab, col in zip(Z_eff_list, labels, colors):
    u = hydrogen_like_u(r, z)
    ax2.plot(r, u**2, color=col, linewidth=2.5, label=lab)
    r_peak = r[np.argmax(u**2)]
    ax2.axvline(r_peak, color=col, linestyle=':', linewidth=1.0, alpha=0.6)
ax2.set_xlabel('r (Bohr)', fontsize=13)
ax2.set_ylabel('u²(r)  (방사형 확률밀도)', fontsize=13)
ax2.set_title('방사형 확률밀도: Z_eff 비교', fontsize=13, fontweight='bold')
ax2.legend(fontsize=10)
ax2.set_xlim(0, 6)
ax2.grid(True, alpha=0.3)

plt.suptitle('시도 파동함수 시각화 — 헬륨 변분법', fontsize=14, fontweight='bold')
plt.tight_layout()
path = f'{output_dir}/02_trial_wavefunction.png'
plt.savefig(path, dpi=150, bbox_inches='tight')
print(f"저장: {path}")
plt.close()

# ─────────────────────────────────────────────────────────
# 그래프 3: 차폐 효과 요약
# ─────────────────────────────────────────────────────────
Z_test   = np.arange(1, 6)
Z_eff_vs = Z_test - 5.0 / 16.0
screening_vs = Z_test - Z_eff_vs  # = 5/16 = 0.3125 (상수)
E_var_vs = variational_energy(Z_eff_vs, Z_test)

fig, axes = plt.subplots(1, 2, figsize=(14, 6))

ax1 = axes[0]
ax1.bar(Z_test, Z_test, color='#AED6F1', edgecolor='k', linewidth=1.2,
        width=0.4, label='실제 핵전하 Z', align='edge')
ax1.bar(Z_test - 0.4, Z_eff_vs, color='#1A5276', edgecolor='k', linewidth=1.2,
        width=0.4, label='유효 핵전하 Z_eff = Z - 5/16', align='edge')
ax1.set_xlabel('핵전하 Z', fontsize=13)
ax1.set_ylabel('핵전하', fontsize=13)
ax1.set_title('핵전하 Z vs 유효 핵전하 Z_eff', fontsize=13, fontweight='bold')
ax1.legend(fontsize=11)
ax1.set_xticks(Z_test)
ax1.grid(True, axis='y', alpha=0.3)

# 헬륨(Z=2) 강조
ax1.annotate(f'He: Z_eff={Z_eff_opt:.4f}', xy=(2, Z_eff_opt),
             xytext=(3, Z_eff_opt + 0.3), fontsize=11, color='white',
             arrowprops=dict(arrowstyle='->', color='white'))

ax2 = axes[1]
# 각 Z에서 에너지 비교: 독립 vs 변분
E_indep_vs = -Z_test**2
E_var_vs_plot = variational_energy(Z_eff_vs, Z_test)
ax2.plot(Z_test, E_indep_vs, 'rs--', markersize=8, linewidth=2,
         label='독립 전자 근사 (반발 무시)')
ax2.plot(Z_test, E_var_vs_plot, 'b^-', markersize=8, linewidth=2,
         label='변분법 (최적 Z_eff)')
ax2.set_xlabel('핵전하 Z', fontsize=13)
ax2.set_ylabel('에너지 (Hartree)', fontsize=13)
ax2.set_title('수소꼴 원자 에너지 비교', fontsize=13, fontweight='bold')
ax2.legend(fontsize=11)
ax2.grid(True, alpha=0.3)
ax2.set_xticks(Z_test)

plt.suptitle('전자-전자 차폐 효과 시각화', fontsize=14, fontweight='bold')
plt.tight_layout()
path = f'{output_dir}/02_screening.png'
plt.savefig(path, dpi=150, bbox_inches='tight')
print(f"저장: {path}")
plt.close()

print("\n" + "=" * 60)
print("변분법 완료")
print("=" * 60)
