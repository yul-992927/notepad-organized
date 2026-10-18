# 허가된 본인 소유/실습 대상에서만 스캔하세요. 전체 TCP 포트 스캔은 서비스에 부담을 줄 수 있습니다.
# 사용·변형에 따른 책임은 행위자에게 있습니다. 자세한 내용: ../../docs/LEGAL_AND_SAFETY.md

#!/bin/bash

if [ $# -ne 1 ]; then
  echo "사용법: $0 <대상_IP>"
  exit 1
fi

TARGET=$1
OUTPUT="scan_${TARGET}_$(date +%Y%m%d_%H%M%S).txt"

echo "[*] 대상 IP: $TARGET"
echo "[*] 스캔 시작: $(date)"
echo ""

# 1. Nmap 서비스 버전 스캔
echo "[*] Nmap - 서비스 및 버전 스캔 중..."
nmap -sV --version-intensity 5 -p- $TARGET -oN $OUTPUT

echo ""
echo "[*] 스캔 완료. 결과가 파일에 저장되었습니다: $OUTPUT"

# 2. 주요 포트 및 서비스 정보 추출 (간단 grep)
echo ""
echo "[*] 열린 포트 및 서비스 요약:"
grep -E "^[0-9]+/tcp" $OUTPUT | awk '{print $1, $3, $4}'

echo ""
echo "[*] 다음 단계:"
echo " - 스캔 결과 파일을 참고해 서비스 버전 확인"
echo " - https://www.cvedetails.com/ 나 https://nvd.nist.gov/ 에서 CVE 검색"
echo " - 또는 Vulners, Nessus, OpenVAS 등의 자동화 도구 활용 권장"
