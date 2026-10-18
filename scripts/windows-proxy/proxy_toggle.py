"""Windows 현재 사용자 프록시 설정을 켜거나 끄는 콘솔 예제.

레지스트리를 변경하므로 실행 전 현재 설정을 확인하세요.
"""
import winreg
import ctypes
import sys

# 레지스트리 경로
REG_PATH = r"Software\Microsoft\Windows\CurrentVersion\Internet Settings"

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def set_proxy(enable, ip="127.0.0.1", port="8080"):
    """
    enable: True(켜기), False(끄기)
    """
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, REG_PATH, 0, winreg.KEY_WRITE) as key:
            if enable:
                winreg.SetValueEx(key, "ProxyServer", 0, winreg.REG_SZ, f"{ip}:{port}")
                winreg.SetValueEx(key, "ProxyEnable", 0, winreg.REG_DWORD, 1)
                print(f"프록시 설정 완료: {ip}:{port}")
            else:
                winreg.SetValueEx(key, "ProxyEnable", 0, winreg.REG_DWORD, 0)
                print("프록시 설정 해제 완료")

        # 시스템에 변경 사항 알림
        INTERNET_OPTION_REFRESH = 37
        INTERNET_OPTION_SETTINGS_CHANGED = 39
        internet_set_option = ctypes.windll.wininet.InternetSetOptionW
        internet_set_option(0, INTERNET_OPTION_REFRESH, 0, 0)
        internet_set_option(0, INTERNET_OPTION_SETTINGS_CHANGED, 0, 0)
        
    except Exception as e:
        print(f"오류 발생: {e}")

if __name__ == "__main__":
    if not is_admin():
        print("관리자 권한으로 실행 중입니다...")
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
        sys.exit()

    # 사용 예시
    # 프록시를 켜려면 True, 끄려면 False를 전달하세요.
    # set_proxy(True, "127.0.0.1", "8080")
    set_proxy(False)