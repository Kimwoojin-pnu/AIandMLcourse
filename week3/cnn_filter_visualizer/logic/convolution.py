def compute_one(pixels, kernel, row, col, mode):
    """
    N×N 픽셀 배열에서 (row, col) 위치의 합성곱 연산 수행.

    Args:
        pixels : N×N int list-of-list
        kernel : 3×3 int list-of-list
        row, col : 출력 Feature Map 위치 (0 ~ N-3)
        mode : 'clamp' or 'abs'

    Returns:
        dict {
            patch      : [9] int list  (입력 패치, 행 우선)
            kflat      : [9] int list  (커널 플랫)
            products   : [9] int list  (원소별 곱)
            raw_sum    : int
            output_val : int (0~255)
        }
    """
    patch    = [pixels[row + kr][col + kc] for kr in range(3) for kc in range(3)]
    kflat    = [kernel[kr][kc]             for kr in range(3) for kc in range(3)]
    products = [p * k for p, k in zip(patch, kflat)]
    raw_sum  = sum(products)

    if mode == "abs":
        output_val = min(255, abs(raw_sum))
    else:
        output_val = max(0, min(255, raw_sum))

    return {
        "patch":      patch,
        "kflat":      kflat,
        "products":   products,
        "raw_sum":    raw_sum,
        "output_val": output_val,
    }


def compute_all(pixels, kernel, mode):
    """(N-2)×(N-2) Feature Map 전체 계산 후 반환."""
    n     = len(pixels)
    out_n = n - 2
    return [
        [compute_one(pixels, kernel, r, c, mode)["output_val"]
         for c in range(out_n)]
        for r in range(out_n)
    ]
