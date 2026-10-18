"""입력 문자열의 형식을 추정하는 학습용 도구.

해시를 복호화하거나 알고리즘을 확정하지 않습니다. 형식이 비슷한 값은 오탐될 수 있습니다.
"""

import base64
import re


def identify_algorithm(data: str) -> list:
    """입력된 문자열의 특징을 분석하여 사용되었을 추정 알고리즘을 반환합니다."""
    candidates = []
    data = data.strip()
    length = len(data)

    # 1. Base64 인코딩 확인 (패딩 및 문자셋 검증)
    base64_pattern = re.compile(
        r"^(?:[A-Za-z0-9+/]{4})*(?:[A-Za-z0-9+/]{2}==|[A-Za-z0-9+/]{3}=)?$"
    )
    if (
        length % 4 == 0
        and base64_pattern.match(data)
        and not re.fullmatch(r"^[0-9a-fA-F]+$", data)
    ):
        candidates.append("Base64 Encoding")

    # 2. 16진수(Hex) 기반 해시 및 인코딩 확인
    if re.fullmatch(r"^[0-9a-fA-F]+$", data):
        if length == 32:
            candidates.append("MD5 / NTLM Hash")
        elif length == 40:
            candidates.append("SHA-1 / RIPEMD-160")
        elif length == 56:
            candidates.append("SHA-224")
        elif length == 64:
            candidates.append("SHA-256 / SHA3-256")
        elif length == 96:
            candidates.append("SHA-384")
        elif length == 128:
            candidates.append("SHA-512 / SHA3-512")
        elif length % 2 == 0:
            candidates.append("Hex Encoded Data")

    # 3. JWT (JSON Web Token) 구조 확인
    jwt_pattern = re.compile(
        r"^[A-Za-z0-9-_]+\.[A-Za-z0-9-_]+\.[A-Za-z0-9-_]*$"
    )
    if jwt_pattern.match(data):
        candidates.append("JWT (JSON Web Token) - HS256/RS256 등")

    # 4. 기타 패스워드 해시 형식 (Bcrypt, MD5-Crypt 등)
    if data.startswith("$2a$") or data.startswith("$2b$") or data.startswith("$2y$"):
        candidates.append("Bcrypt Password Hash")
    elif data.startswith("$1$"):
        candidates.append("MD5-Crypt (Unix)")
    elif data.startswith("$5$"):
        candidates.append("SHA-256 Crypt (Unix)")
    elif data.startswith("$6$"):
        candidates.append("SHA-512 Crypt (Unix)")

    if not candidates:
        candidates.append(
            "알 수 없거나 일반 텍스트(Plain Text)일 가능성이 높습니다."
        )

    return candidates


if __name__ == "__main__":
    print("=== 알고리즘 판별 도구 ===")
    user_input = input("분석할 입력값을 입력하세요: ")

    results = identify_algorithm(user_input)

    print("\n[분석 결과]")
    for res in results:
        print(f"- {res}")