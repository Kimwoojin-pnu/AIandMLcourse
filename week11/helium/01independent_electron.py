"""
01. 헬륨 원자 — 독립 전자 근사 (Independent Electron Approximation)

전자-전자 반발을 완전히 무시하고 두 전자를 독립된 수소꼴 원자로 취급.
기저 상태 에너지: E = -Z² = -4.000 Hartree

1차 섭동 보정: E = -4.000 + 5Z/8 = -2.750 Hartree
"""

import sys
import os
import numpy as np
import matplotlib.pyplot as plt

sys.stdout.reconfigure(encoding='utf-8')
plt.rcParams['font.family'] = 'Malgun Gothic'
plt.rcParams['axes.unicode_minus'] = False

output_dir = 'outputs'
os.makedirs(output_dir, exist_ok=True)

# 자연 단위계 (원자 단위, Hartree)
hbar = 1.0
m_e  = 1.0
a0   = 1.0
Z    = 2      # 헬륨 핵전하

print("=" * 60)
print("헬륨 원자: 독립 전자 근사")
print("=" * 60)

# ─────────────────────────────────────────────────────────
# 방사형 격자
# ─────────────────────────────────────────────────────────
N     = 1000
r_max = 20.0
r     = np.linspace(0.001, r_max, N)
dr    = r[1] - r[0]

# ─────────────────────────────────────────────────────────
# 수소꼴 1s 방사형 함수 u(r) = r·R(r)
#   ∫₀^∞ u² dr = 1 (정규화)
# ─────────────────────────────────────────────────────────
def hydrogen_like_u(r, Z_eff):
    u = 2.0 * Z_eff**1.5 * r * np.exp(-Z_eff * r)
    norm = np.sqrt(np.trapz(u**2, r))
    return u / norm

u_indep = hydrogen_like_u(r, Z)

# 정규화 검증
norm_check = np.trapz(u_indep**2, r)
print(f"\n파동함수 정규화 확인: ∫u²dr = {norm_check:.6f}  (목표: 1.000)")

# ─────────────────────────────────────────────────────────
# 에너지 계산
# ─────────────────────────────────────────────────────────
# 독립 전자 근사: E = 2 * (-Z²/2) = -Z²
E_indep = -Z**2  # = -4.000 Hartree

# 1차 섭동 보정: <1/r12> = 5Z/8
E_repulsion = 5.0 * Z / 8.0   # = 1.250 Hartree
E_perturbed = E_indep + E_repulsion  # = -2.750 Hartree

# 실험값
E_exp = -2.9037  # Hartree (정확한 비상대론적 값)

err_indep    = abs(E_indep - E_exp) / abs(E_exp) * 100
err_perturb  = abs(E_perturbed - E_exp) / abs(E_exp) * 100

print(f"\n--- 에너지 결과 (단위: Hartree) ---")
print(f"  독립 전자 근사 (반발 무시):  E = {E_indep:.4f}  (오차 {err_indep:.1f}%)")
print(f"  1차 섭동 보정 후:           E = {E_perturbed:.4f}  (오차 {err_perturb:.1f}%)")
print(f"  실험값 (기준):              E = {E_exp:.4f}")
print(f"\n  반발 에너지 <1/r12>: {E_repulsion:.4f} Hartree")

# 기댓값들
E_kinetic_one = Z**2 / 2.0           # 전자 1개 운동에너지
E_nuclear_one = -Z**2                 # 전자 1개 핵-전자 인력
print(f"\n  전자 1개 운동에너지 <T>:  {E_kinetic_one:.4f}")
print(f"  전자 1개 핵-전자 인력 <Vne>: {E_nuclear_one:.4f}")

# ─────────────────────────────────────────────────────────
# 그래프 1: 방사형 파동함수 + 확률밀도
# ─────────────────────────────────────────────────────────
fig, axes = plt.subplots(1, 2, figsize=(14, 6))

# 왼쪽: 파동함수 u(r)와 확률밀도
ax1 = axes[0]
ax1.plot(r, u_indep, 'b-', linewidth=2.5, label='u(r) = r·R₁ₛ(r)')
ax1.plot(r, u_indep**2, 'r--', linewidth=2.5, label='|u(r)|²  (확률밀도)')
ax1.axhline(0, color='k', linewidth=0.8, alpha=0.5)
ax1.set_xlabel('r (Bohr)', fontsize=13)
ax1.set_ylabel('파동함수 / 확률밀도', fontsize=13)
ax1.set_title('1s 방사형 파동함수  (Z=2)', fontsize=14, fontweight='bold')
ax1.legend(fontsize=11)
ax1.set_xlim(0, 5)
ax1.grid(True, alpha=0.3)

# 오른쪽: 방사형 확률밀도 r²|ψ|² ∝ u²
ax2 = axes[1]
prob_radial = u_indep**2   # ∫u²dr = 1과 동치
ax2.plot(r, prob_radial, 'g-', linewidth=2.5, label='방사형 확률밀도 u²(r)')
r_peak = r[np.argmax(prob_radial)]
ax2.axvline(r_peak, color='r', linestyle='--', linewidth=1.5,
            label=f'최대 확률 반경 = {r_peak:.3f} Bohr')
ax2.fill_between(r, prob_radial, alpha=0.2, color='g')
ax2.set_xlabel('r (Bohr)', fontsize=13)
ax2.set_ylabel('확률밀도 u²(r)', fontsize=13)
ax2.set_title('방사형 확률밀도  (Z=2)', fontsize=14, fontweight='bold')
ax2.legend(fontsize=11)
ax2.set_xlim(0, 5)
ax2.grid(True, alpha=0.3)

plt.suptitle('헬륨 원자 독립 전자 근사: 1s 오비탈 (Z=2)', fontsize=15, fontweight='bold')
plt.tight_layout()
path = f'{output_dir}/01_independent_radial.png'
plt.savefig(path, dpi=150, bbox_inches='tight')
print(f"\n저장: {path}")
plt.close()

# ─────────────────────────────────────────────────────────
# 그래프 2: 에너지 비교 막대그래프
# ─────────────────────────────────────────────────────────
fig, ax = plt.subplots(figsize=(10, 7))

methods  = ['독립 전자 근사\n(반발 무시)', '1차 섭동\n보정', '실험값\n(기준)']
energies = [E_indep, E_perturbed, E_exp]
colors   = ['#E74C3C', '#F39C12', '#2ECC71']
errors   = [err_indep, err_perturb, 0.0]

bars = ax.bar(methods, energies, color=colors, width=0.5,
              edgecolor='black', linewidth=1.5, alpha=0.85)

for bar, E, err in zip(bars, energies, errors):
    y_label = E - 0.12
    ax.text(bar.get_x() + bar.get_width()/2, y_label,
            f'{E:.3f} Ha\n(오차 {err:.1f}%)', ha='center', va='top',
            fontsize=12, fontweight='bold', color='white')

ax.axhline(E_exp, color='#2ECC71', linestyle='--', linewidth=2.5,
           alpha=0.8, label=f'실험값 = {E_exp:.4f} Ha')
ax.set_ylabel('에너지 (Hartree)', fontsize=13)
ax.set_title('헬륨 원자 에너지: 독립 전자 근사 vs 실험값', fontsize=14, fontweight='bold')
ax.legend(fontsize=12, loc='upper right')
ax.set_ylim(min(energies) - 0.5, 0.5)
ax.grid(True, axis='y', alpha=0.3)
ax.tick_params(axis='x', labelsize=12)

plt.tight_layout()
path = f'{output_dir}/01_energy_comparison.png'
plt.savefig(path, dpi=150, bbox_inches='tight')
print(f"저장: {path}")
plt.close()

print("\n" + "=" * 60)
print("독립 전자 근사 완료")
print("=" * 60)
