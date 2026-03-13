import torch
import torch.nn as nn
import numpy as np

# ────────────────────────────────────────────
# 슬라이드의 코드: Dense Layer를 직접 구현
# ────────────────────────────────────────────
class MyDenseLayer(nn.Module):
    def __init__(self, input_dim, output_dim):
        super(MyDenseLayer, self).__init__()

        # 가중치(W)와 편향(b)을 랜덤으로 초기화
        # requires_grad=True → 나중에 역전파(Backpropagation)로 학습 가능하게 설정
        self.W = nn.Parameter(torch.randn(input_dim, output_dim, requires_grad=True))
        self.b = nn.Parameter(torch.randn(1, output_dim, requires_grad=True))

    def forward(self, inputs):
        # 순전파(Forward Propagation): ŷ = g(XW + b)
        z = torch.matmul(inputs, self.W) + self.b   # 선형 변환
        output = torch.sigmoid(z)                    # 비선형 활성화 함수 적용
        return output


# ────────────────────────────────────────────
# 직접 실행해보기
# ────────────────────────────────────────────
if __name__ == "__main__":
    # 입력 데이터: 3개의 샘플, 각 샘플은 특징(feature) 4개
    # 예: 학생 3명, 각자 [강의출석수, 과제점수, 중간고사, 기말고사] 4가지 정보
    X = torch.tensor([
        [4.0, 5.0, 70.0, 80.0],
        [1.0, 2.0, 40.0, 50.0],
        [7.0, 9.0, 90.0, 95.0],
    ])

    print("=" * 50)
    print("[ 입력 데이터 (Input) ]")
    print(f"  shape: {X.shape}  → {X.shape[0]}개 샘플, {X.shape[1]}개 feature")
    print(X)

    # Dense Layer 생성: 입력 4개 → 출력 2개 (예: 수업통과 확률, 장학금 확률)
    layer = MyDenseLayer(input_dim=4, output_dim=2)

    print("\n[ 학습 전 초기 가중치 W ]")
    print(layer.W.data)
    print("[ 편향 b ]")
    print(layer.b.data)

    # 순전파 실행
    output = layer(X)

    print("\n[ 출력 결과 (Output) - Sigmoid 통과 후 0~1 사이 확률값 ]")
    print(f"  shape: {output.shape}  → {output.shape[0]}개 샘플, {output.shape[1]}개 출력")
    print(output.detach())

    print("\n[ 해석 ]")
    for i, row in enumerate(output.detach()):
        print(f"  학생 {i+1}: 출력1={row[0]:.4f}, 출력2={row[1]:.4f}")

    # ────────────────────────────────────────
    # PyTorch 내장 Linear와 비교 (결과는 다르지만 구조는 동일)
    # ────────────────────────────────────────
    print("\n" + "=" * 50)
    print("[ 비교: PyTorch 내장 nn.Linear 사용 (내부 구조 동일) ]")
    builtin_layer = nn.Linear(in_features=4, out_features=2)
    builtin_output = torch.sigmoid(builtin_layer(X))
    print(builtin_output.detach())
    print("→ 가중치 초기값이 달라서 숫자는 다르지만, 구조는 완전히 같습니다!")
