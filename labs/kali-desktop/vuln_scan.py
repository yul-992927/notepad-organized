# 허가된 본인 소유/실습 대상에서만 스캔하세요. 전체 TCP 포트 스캔은 서비스에 부담을 줄 수 있습니다.
# 사용·변형에 따른 책임은 행위자에게 있습니다. 자세한 내용: ../../docs/LEGAL_AND_SAFETY.md

import subprocess
import sys
import re
from datetime import datetime

def run_nmap(target):
    output_file = f"scan_{target}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    print(f"[*] 대상 IP: {target}")
    print(f"[*] 스캔 시작: {datetime.now()}")
    
    # nmap -sV 모든 포트 스캔 및 결과 저장
    cmd = ["nmap", "-sV", "-p-", target, "-oN", output_file]
    subprocess.run(cmd)
    
    print(f"[*] 스캔 완료. 결과 파일: {output_file}")
    
    # 열린 포트 및 서비스 요약 출력
    with open(output_file, "r") as f:
        lines = f.readlines()
        
    print("\n[*] 열린 포트 및 서비스 요약:")
    for line in lines:
        if re.match(r"^\d+/tcp", line):
            parts = line.split()
            port = parts[0]
            state = parts[1]
            service = parts[2]
            version = " ".join(parts[3:]) if len(parts) > 3 else ""
            print(f"{port} - {service} {version}")
    
    print("\n[*] 다음 단계:")
    print(" - CVE 데이터베이스에서 취약점 검색 권장")
    print(" - https://www.cvedetails.com/ 또는 https://nvd.nist.gov/ 활용")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("사용법: python vuln_scan.py <대상_IP>")
        sys.exit(1)
    target_ip = sys.argv[1]
    run_nmap(target_ip)
