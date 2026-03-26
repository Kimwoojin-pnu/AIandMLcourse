IMG_N = 128  # 입력 이미지 해상도 (N×N)


def load_image_as_grid(filepath):
    """
    이미지 파일을 그레이스케일 IMG_N×IMG_N 정수 배열로 변환.

    Args:
        filepath : str  (PNG / JPG / JPEG / BMP)

    Returns:
        list[list[int]]  IMG_N×IMG_N, 값 범위 0~255

    Raises:
        ImportError  Pillow 미설치 시
        OSError      파일 읽기 실패 시
    """
    try:
        from PIL import Image
    except ImportError:
        raise ImportError(
            "Pillow가 설치되지 않았습니다.\n"
            "터미널에서 다음 명령을 실행하세요: pip install pillow"
        )

    img = Image.open(filepath).convert("L")
    img = img.resize((IMG_N, IMG_N), Image.LANCZOS)
    return [[img.getpixel((c, r)) for c in range(IMG_N)] for r in range(IMG_N)]


# 기본 픽셀: 좌절반=200(밝음), 우절반=30(어둠) 수직 경계 패턴
# Sobel X 필터로 중앙 경계선을 명확하게 확인할 수 있음
DEFAULT_PIXELS = [
    [200 if c < IMG_N // 2 else 30 for c in range(IMG_N)]
    for _ in range(IMG_N)
]
