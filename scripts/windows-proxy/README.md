# Windows 프록시 설정 예제

Windows 현재 사용자(`HKCU`)의 시스템 프록시 값을 바꾸는 실습 코드입니다.

- `proxy_menu.bat`: 메뉴형 배치 스크립트
- `proxy_toggle.py`: 콘솔형 Python 예제. 기본 실행은 프록시 해제입니다.
- `proxy_gui.py`: Tkinter GUI. 원본에서 `.bat`로 잘못 저장된 Python 코드를 확장자에 맞게 정리했습니다.
- `build_proxy_gui.bat`: `proxy_gui.py`를 PyInstaller로 패키징합니다. 빌드 시 패키지 설치가 발생합니다.

실행 전에 기존 프록시 값을 기록해 두세요. 관리자 권한으로 재실행하는 코드가 포함되어 있어, 현재 로그인 사용자와 관리자 계정이 다르면 적용되는 `HKCU`가 기대와 다를 수 있습니다. 원본 레지스트리 내보내기(`.reg`) 파일은 사용자 환경 정보가 들어갈 수 있어 공개하지 않았습니다.
