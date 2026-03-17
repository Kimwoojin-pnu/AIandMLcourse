"""
Week 2 실험: 하이퍼파라미터와 데이터 변화 비교
- learning_rate 비교: 0.01, 0.1, 1.0
- epochs 비교: 100, 1000, 5000
- 노이즈 크기 비교: scale=0.5, 2.0, 5.0
- 다른 데이터: 집 가격 예측 (방 개수 → 가격)
"""

import tensorflow as tf
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
import os

matplotlib.rcParams['axes.unicode_minus'] = False

output_dir = 'outputs'
os.makedirs(output_dir, exist_ok=True)

# 공통 데이터 (훅의 법칙)
np.random.seed(42)
weights = np.array([0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10], dtype=float)
true_lengths = 2 * weights + 10

def make_data(scale):
    noise = np.random.normal(0, scale, len(weights))
    return true_lengths + noise

def train_model(x, y, learning_rate, epochs):
    model = tf.keras.Sequential([
        tf.keras.layers.Input(shape=[1]),
        tf.keras.layers.Dense(units=1)
    ])
    model.compile(
        optimizer=tf.keras.optimizers.SGD(learning_rate=learning_rate),
        loss='mean_squared_error'
    )
    history = model.fit(x, y, epochs=epochs, verbose=0)
    w = float(model.layers[0].get_weights()[0].flatten()[0])
    b = float(model.layers[0].get_weights()[1].flatten()[0])
    return w, b, history.history['loss']

# ─────────────────────────────────────────────
# 실험 1: Learning Rate 비교
# ─────────────────────────────────────────────
print("=" * 50)
print("실험 1: Learning Rate 비교 (0.01, 0.1, 1.0)")
print("=" * 50)

np.random.seed(42)
measured = make_data(scale=1.5)
learning_rates = [0.01, 0.1, 1.0]
lr_colors = ['blue', 'green', 'red']

fig, axes = plt.subplots(1, 3, figsize=(18, 5))
fig.suptitle('Experiment 1: Learning Rate Comparison (500 epochs, noise scale=1.5)', fontsize=14)

for i, lr in enumerate(learning_rates):
    np.random.seed(0)
    w, b, loss_hist = train_model(weights, measured, learning_rate=lr, epochs=500)
    ax = axes[i]

    diverged = np.isnan(w) or np.isinf(w)
    x_plot = np.linspace(0, 10, 100)
    ax.scatter(weights, measured, color='gray', label='Data', zorder=3)
    ax.plot(weights, true_lengths, 'g--', label='True (y=2x+10)')

    if diverged:
        ax.text(5, 20, '발산! (NaN)\nLR이 너무 큼', ha='center', va='center',
                fontsize=14, color='red', fontweight='bold',
                bbox=dict(boxstyle='round', facecolor='lightyellow', edgecolor='red'))
        ax.set_title(f'LR={lr}\n*** DIVERGED (LR too large) ***')
        print(f"  LR={lr:4}: 발산! (NaN) - learning rate가 너무 커서 튕겨나감")
    else:
        ax.plot(x_plot, w * x_plot + b, color=lr_colors[i], label=f'AI: y={w:.2f}x+{b:.2f}')
        ax.set_title(f'LR={lr}\nFinal loss: {loss_hist[-1]:.4f}')
        print(f"  LR={lr:4}: y = {w:.3f}x + {b:.3f}  (final loss: {loss_hist[-1]:.4f})")

    ax.set_xlabel('Weight (kg)')
    ax.set_ylabel('Length (cm)')
    ax.legend(fontsize=8)
    ax.grid(True)

plt.tight_layout()
path = os.path.join(output_dir, 'exp1_learning_rate.png')
plt.savefig(path)
print(f"  -> 저장: {path}\n")

# ─────────────────────────────────────────────
# 실험 2: Epochs 비교
# ─────────────────────────────────────────────
print("=" * 50)
print("실험 2: Epochs 비교 (100, 1000, 5000)")
print("=" * 50)

np.random.seed(42)
measured = make_data(scale=1.5)
epoch_list = [100, 1000, 5000]

fig, axes = plt.subplots(2, 3, figsize=(18, 10))
fig.suptitle('Experiment 2: Epochs Comparison (LR=0.01, noise scale=1.5)', fontsize=14)

for i, ep in enumerate(epoch_list):
    np.random.seed(0)
    w, b, loss_hist = train_model(weights, measured, learning_rate=0.01, epochs=ep)

    # 위쪽: 피팅 결과
    ax_top = axes[0][i]
    x_plot = np.linspace(0, 10, 100)
    ax_top.scatter(weights, measured, color='gray', label='Data', zorder=3)
    ax_top.plot(weights, true_lengths, 'g--', label='True (y=2x+10)')
    ax_top.plot(x_plot, w * x_plot + b, 'r-', label=f'AI: y={w:.2f}x+{b:.2f}')
    ax_top.set_title(f'Epochs={ep}\nFinal loss: {loss_hist[-1]:.4f}')
    ax_top.set_xlabel('Weight (kg)')
    ax_top.set_ylabel('Length (cm)')
    ax_top.legend(fontsize=8)
    ax_top.grid(True)

    # 아래쪽: 손실 곡선
    ax_bot = axes[1][i]
    ax_bot.plot(loss_hist, color='red')
    ax_bot.set_title(f'Loss Curve (epochs={ep})')
    ax_bot.set_xlabel('Epoch')
    ax_bot.set_ylabel('MSE Loss')
    ax_bot.grid(True)

    print(f"  Epochs={ep:5}: y = {w:.3f}x + {b:.3f}  (final loss: {loss_hist[-1]:.4f})")

plt.tight_layout()
path = os.path.join(output_dir, 'exp2_epochs.png')
plt.savefig(path)
print(f"  -> 저장: {path}\n")

# ─────────────────────────────────────────────
# 실험 3: 노이즈 크기 비교
# ─────────────────────────────────────────────
print("=" * 50)
print("실험 3: 노이즈 크기 비교 (scale=0.5, 2.0, 5.0)")
print("=" * 50)

noise_scales = [0.5, 2.0, 5.0]
noise_colors = ['purple', 'orange', 'brown']

fig, axes = plt.subplots(1, 3, figsize=(18, 5))
fig.suptitle('Experiment 3: Noise Scale Comparison (LR=0.01, 500 epochs)', fontsize=14)

for i, scale in enumerate(noise_scales):
    np.random.seed(42)
    measured = make_data(scale=scale)
    np.random.seed(0)
    w, b, loss_hist = train_model(weights, measured, learning_rate=0.01, epochs=500)

    ax = axes[i]
    x_plot = np.linspace(0, 10, 100)
    ax.scatter(weights, measured, color='gray', label='Data', zorder=3, alpha=0.7)
    ax.plot(weights, true_lengths, 'g--', label='True (y=2x+10)')
    ax.plot(x_plot, w * x_plot + b, color=noise_colors[i], label=f'AI: y={w:.2f}x+{b:.2f}')
    ax.set_title(f'Noise scale={scale}\nFinal loss: {loss_hist[-1]:.4f}')
    ax.set_xlabel('Weight (kg)')
    ax.set_ylabel('Length (cm)')
    ax.legend(fontsize=8)
    ax.grid(True)

    print(f"  scale={scale}: y = {w:.3f}x + {b:.3f}  (final loss: {loss_hist[-1]:.4f})")

plt.tight_layout()
path = os.path.join(output_dir, 'exp3_noise.png')
plt.savefig(path)
print(f"  -> 저장: {path}\n")

# ─────────────────────────────────────────────
# 실험 4: 다른 데이터 - 집 가격 예측
# ─────────────────────────────────────────────
print("=" * 50)
print("실험 4: 다른 데이터 - 집 가격 예측")
print("  방 개수(rooms) -> 가격(만원)")
print("  실제 공식: 가격 = 3000 * 방수 + 5000")
print("=" * 50)

np.random.seed(42)
rooms = np.array([1, 2, 3, 4, 5, 6, 7, 8], dtype=float)
true_prices = 3000 * rooms + 5000
noise = np.random.normal(0, 800, len(rooms))
measured_prices = true_prices + noise

# 가격 단위가 커서 정규화 후 학습
prices_min, prices_max = measured_prices.min(), measured_prices.max()
prices_norm = (measured_prices - prices_min) / (prices_max - prices_min)
rooms_min, rooms_max = rooms.min(), rooms.max()
rooms_norm = (rooms - rooms_min) / (rooms_max - rooms_min)

np.random.seed(0)
w_norm, b_norm, loss_hist = train_model(rooms_norm, prices_norm, learning_rate=0.1, epochs=1000)

# 원래 단위로 역변환
# price_norm = w_norm * room_norm + b_norm
# price_norm = (price - prices_min) / (prices_max - prices_min)
# room_norm = (room - rooms_min) / (rooms_max - rooms_min)
# -> price = w_norm*(rooms_max-rooms_min)/(prices_max-prices_min) * room + ...
scale_w = (prices_max - prices_min) / (rooms_max - rooms_min)
w_orig = w_norm * scale_w
b_orig = b_norm * (prices_max - prices_min) + prices_min - w_norm * scale_w * rooms_min

print(f"  예측 식: 가격 = {w_orig:.0f} * 방수 + {b_orig:.0f} (만원)")
print(f"  실제 식: 가격 = 3000 * 방수 + 5000 (만원)")
print(f"  final loss (normalized): {loss_hist[-1]:.6f}")

fig, axes = plt.subplots(1, 2, figsize=(14, 5))
fig.suptitle('Experiment 4: House Price Prediction (rooms -> price)', fontsize=14)

# 피팅 결과
ax = axes[0]
x_plot = np.linspace(1, 8, 100)
ax.scatter(rooms, measured_prices, color='steelblue', label='Measured Data', zorder=3, s=80)
ax.plot(rooms, true_prices, 'g--', label='True: 3000x+5000')
ax.plot(x_plot, w_orig * x_plot + b_orig, 'r-',
        label=f'AI: {w_orig:.0f}x+{b_orig:.0f}')
ax.set_title('House Price Prediction')
ax.set_xlabel('Number of Rooms')
ax.set_ylabel('Price (10,000 KRW)')
ax.legend()
ax.grid(True)

# 손실 곡선
ax2 = axes[1]
ax2.plot(loss_hist, color='red')
ax2.set_title('Loss Curve (1000 epochs)')
ax2.set_xlabel('Epoch')
ax2.set_ylabel('MSE Loss (normalized)')
ax2.grid(True)

plt.tight_layout()
path = os.path.join(output_dir, 'exp4_house_price.png')
plt.savefig(path)
print(f"  -> 저장: {path}\n")

# ─────────────────────────────────────────────
# 요약 출력
# ─────────────────────────────────────────────
print("=" * 50)
print("실험 완료! 생성된 파일:")
print("  outputs/exp1_learning_rate.png")
print("  outputs/exp2_epochs.png")
print("  outputs/exp3_noise.png")
print("  outputs/exp4_house_price.png")
print()
print("[핵심 관찰 포인트]")
print("  실험1 - LR=0.01: 안정적으로 수렴  /  LR=0.1 이상: 발산(NaN) - 보폭이 너무 커서 튕겨나감")
print("  실험2 - Epochs 100: 덜 학습됨     / 1000: 충분     / 5000: 과학습 위험")
print("  실험3 - noise 0.5: 깨끗한 데이터  / 2.0: 보통      / 5.0: 노이즈 많아 정확도 낮음")
print("  실험4 - 정규화 후 학습하면 단위가 다른 데이터도 잘 학습됨!")
