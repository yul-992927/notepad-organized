:: 현재 사용자(HKCU)의 프록시 설정을 변경합니다. 적용 대상 계정을 먼저 확인하세요.
 @echo off
:: 관리자 권한 확인
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo 관리자 권한으로 다시 실행합니다...
    powershell -Command "Start-Process '%~f0' -Verb RunAs"
    exit /b
)

:menu
cls
echo ===============================
echo      시스템 프록시 관리자
echo ===============================
echo 1. 프록시 켜기 (ON)
echo 2. 프록시 끄기 (OFF)
echo 3. 종료
echo ===============================
set /p choice="번호를 선택하세요: "

if "%choice%"=="1" goto set_on
if "%choice%"=="2" goto set_off
if "%choice%"=="3" exit

:set_on
set /p ip="IP 주소를 입력하세요 (예: 127.0.0.1): "
set /p port="포트 번호를 입력하세요 (예: 8080): "
reg add "HKCU\Software\Microsoft\Windows\CurrentVersion\Internet Settings" /v ProxyServer /t REG_SZ /d "%ip%:%port%" /f
reg add "HKCU\Software\Microsoft\Windows\CurrentVersion\Internet Settings" /v ProxyEnable /t REG_DWORD /d 1 /f
echo 프록시가 설정되었습니다.
pause
goto menu

:set_off
reg add "HKCU\Software\Microsoft\Windows\CurrentVersion\Internet Settings" /v ProxyEnable /t REG_DWORD /d 0 /f
echo 프록시가 해제되었습니다.
pause
goto menu