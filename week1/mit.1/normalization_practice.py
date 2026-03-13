import torch
import torch.nn as nn

# ────────────────────────────────────────────
# 정규화(Normalization) 전후 비교
# ────────────────────────────────────────────

# 동일한 가중치로 비교하기 위해 seed 고정
torch.manual_seed(42)

# 입력 데이터 (정규화 전)
X_raw = torch.tensor([
    [4.0, 5.0, 70.0, 80.0],
    [1.0, 2.0, 40.0, 50.0],
    [7.0, 9.0, 90.0, 95.0],
])

# ────────────────────────────────────────────
# Min-Max 정규화: 0~1 사이로 스케일 조정
# ────────────────────────────────────────────
X_min = X_raw.min(dim=0).values
X_max = X_raw.max(dim=0).values
X_minmax = (X_raw - X_min) / (X_max - X_min)

# ────────────────────────────────────────────
# Z-score 정규화: 평균 0, 표준편차 1로 조정
# ────────────────────────────────────────────
X_mean = X_raw.mean(dim=0)
X_std  = X_raw.std(dim=0)
X_zscore = (X_raw - X_mean) / X_std

# ────────────────────────────────────────────
# 동일한 Dense Layer로 3가지 입력 비교
# ────────────────────────────────────────────
class MyDenseLayer(nn.Module):
    def __init__(self, input_dim, output_dim):
        super().__init__()
        self.W = nn.Parameter(torch.randn(input_dim, output_dim))
        self.b = nn.Parameter(torch.randn(1, output_dim))

    def forward(self, x):
        return torch.sigmoid(torch.matmul(x, self.W) + self.b)

# seed 고정 후 레이어 생성 (세 번 모두 같은 가중치 사용)
def make_layer():
    torch.manual_seed(42)
    return MyDenseLayer(4, 2)

layer_raw    = make_layer()
layer_minmax = make_layer()
layer_zscore = make_layer()

out_raw    = layer_raw(X_raw)
out_minmax = layer_minmax(X_minmax)
out_zscore = layer_zscore(X_zscore)

print("=" * 55)
print("[ 입력값 비교 ]")
print(f"\n정규화 전 (Raw):\n{X_raw}")
print(f"\nMin-Max 정규화 (0~1):\n{X_minmax.round(decimals=4)}")
print(f"\nZ-score 정규화 (평균0, 표준편차1):\n{X_zscore.round(decimals=4)}")

print("\n" + "=" * 55)
print("[ 출력값 비교 (같은 가중치, 다른 입력) ]")
print(f"\n정규화 전:\n{out_raw.detach()}")
print(f"\nMin-Max 정규화:\n{out_minmax.detach()}")
print(f"\nZ-score 정규화:\n{out_zscore.detach()}")

print("\n" + "=" * 55)
print("[ 분석 ]")
print(f"정규화 전    - 출력 범위: {out_raw.detach().min():.4f} ~ {out_raw.detach().max():.4f}")
print(f"Min-Max 후   - 출력 범위: {out_minmax.detach().min():.4f} ~ {out_minmax.detach().max():.4f}")
print(f"Z-score 후   - 출력 범위: {out_zscore.detach().min():.4f} ~ {out_zscore.detach().max():.4f}")
print()
print("→ 정규화 전: 출력이 0 또는 1에 극단적으로 몰림 (Sigmoid 포화)")
print("→ 정규화 후: 출력이 0~1 사이 다양한 값 → 학습에 유리!")
