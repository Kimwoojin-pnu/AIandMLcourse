import torch
import torch.nn as nn

torch.manual_seed(42)

# ────────────────────────────────────────────
# 데이터 준비 (정규화 포함)
# ────────────────────────────────────────────
# 입력: 학생 6명 [출석, 과제, 중간, 기말]
X_raw = torch.tensor([
    [4.0, 5.0, 70.0, 80.0],
    [1.0, 2.0, 40.0, 50.0],
    [7.0, 9.0, 90.0, 95.0],
    [3.0, 4.0, 60.0, 65.0],
    [6.0, 8.0, 85.0, 88.0],
    [2.0, 3.0, 55.0, 58.0],
])

# 정답(label): 수업 통과 여부 (1=통과, 0=탈락)
y = torch.tensor([[1.], [0.], [1.], [0.], [1.], [0.]])

# Z-score 정규화
X = (X_raw - X_raw.mean(dim=0)) / X_raw.std(dim=0)

# ────────────────────────────────────────────
# 모델 정의
# ────────────────────────────────────────────
model = nn.Sequential(
    nn.Linear(4, 4),   # 입력층 → 은닉층
    nn.ReLU(),
    nn.Linear(4, 1),   # 은닉층 → 출력층
    nn.Sigmoid()
)

# ────────────────────────────────────────────
# 손실함수 & 옵티마이저
# ────────────────────────────────────────────
loss_fn   = nn.BCELoss()           # Binary Cross Entropy
optimizer = torch.optim.SGD(model.parameters(), lr=0.1)

# ────────────────────────────────────────────
# 학습 루프
# ────────────────────────────────────────────
print("=" * 50)
print("[ 학습 시작 ]")
print(f"{'Epoch':>6} | {'Loss':>10} | {'정확도':>6}")
print("-" * 30)

for epoch in range(1, 201):
    # 1. 순전파
    y_pred = model(X)

    # 2. 손실 계산
    loss = loss_fn(y_pred, y)

    # 3. 역전파
    optimizer.zero_grad()
    loss.backward()

    # 4. 가중치 업데이트
    optimizer.step()

    # 20 epoch마다 출력
    if epoch % 20 == 0:
        correct = ((y_pred > 0.5) == y).float().mean()
        print(f"{epoch:>6} | {loss.item():>10.4f} | {correct.item()*100:>5.1f}%")

# ────────────────────────────────────────────
# 최종 결과
# ────────────────────────────────────────────
print("\n" + "=" * 50)
print("[ 학습 완료 후 예측 결과 ]")
with torch.no_grad():
    final_pred = model(X)

print(f"\n{'학생':>4} | {'예측 확률':>8} | {'예측':>4} | {'정답':>4} | {'맞춤?':>5}")
print("-" * 38)
for i in range(len(X)):
    prob   = final_pred[i].item()
    pred   = 1 if prob > 0.5 else 0
    label  = int(y[i].item())
    check  = "O" if pred == label else "X"
    print(f"  {i+1}번  | {prob:>8.4f} | {pred:>4} | {label:>4} | {check:>5}")
