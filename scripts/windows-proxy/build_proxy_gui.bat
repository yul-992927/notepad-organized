:: proxy_gui.py를 PyInstaller로 패키징하는 보조 스크립트입니다.
@echo off
echo [1/3] PyInstaller 설치 중...
pip install pyinstaller

echo [2/3] 실행 파일(.exe) 생성 중...
:: --noconsole 옵션을 넣으면 실행 시 검은 창이 뜨지 않습니다.
:: --onefile 옵션은 모든 파일을 하나의 .exe로 묶어줍니다.
:: 본인의 파이썬 파일명으로 수정하세요 (예: my_proxy.py)
pyinstaller --noconsole --onefile --name "프록시매니저" proxy_gui.py

echo [3/3] 빌드 완료!
echo 'dist' 폴더 안에 '프록시매니저.exe' 파일이 생성되었습니다.
pause