"""Windows 사용자 프록시 설정을 관리하는 Tkinter GUI.

레지스트리를 변경하므로 실행 전 현재 설정과 적용 계정을 확인하세요.
"""

import tkinter as tk
from tkinter import messagebox, ttk
import winreg
import ctypes
import sys
import webbrowser

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

class ProxyManagerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("프록시 설정 매니저")
        self.root.geometry("350x300")
        self.root.resizable(False, False)

        # Registry Path
        self.reg_path = r"Software\Microsoft\Windows\CurrentVersion\Internet Settings"

        # Main Frame
        main_frame = ttk.Frame(root, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Title
        ttk.Label(main_frame, text="시스템 프록시 설정", font=("Malgun Gothic", 12, "bold")).pack(pady=(0, 15))

        # IP Input
        ip_frame = ttk.Frame(main_frame)
        ip_frame.pack(fill=tk.X, pady=5)
        ttk.Label(ip_frame, text="프록시 IP:", width=10).pack(side=tk.LEFT)
        self.ip_entry = ttk.Entry(ip_frame)
        self.ip_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)

        # Port Input
        port_frame = ttk.Frame(main_frame)
        port_frame.pack(fill=tk.X, pady=5)
        ttk.Label(port_frame, text="포트:", width=10).pack(side=tk.LEFT)
        self.port_entry = ttk.Entry(port_frame)
        self.port_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)

        # Load Current Settings
        current_ip, current_port, current_state = self.get_current_proxy_settings()
        self.ip_entry.insert(0, current_ip if current_ip else "127.0.0.1")
        self.port_entry.insert(0, current_port if current_port else "8080")

        # Status Label
        self.status_var = tk.StringVar(value=f"현재 상태: {'ON' if current_state else 'OFF'}")
        self.status_label = ttk.Label(main_frame, textvariable=self.status_var, font=("Malgun Gothic", 10))
        self.status_label.pack(pady=10)

        # Buttons
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(pady=10)
        
        self.on_btn = ttk.Button(btn_frame, text="프록시 ON", command=lambda: self.set_proxy(True))
        self.on_btn.pack(side=tk.LEFT, padx=5)
        
        self.off_btn = ttk.Button(btn_frame, text="프록시 OFF", command=lambda: self.set_proxy(False))
        self.off_btn.pack(side=tk.LEFT, padx=5)

        # Footer
        footer = tk.Label(main_frame, text="천재공샘", fg="blue", cursor="hand2", font=("Malgun Gothic", 10, "underline"))
        footer.pack(side="bottom", pady=10)
        footer.bind("<Button-1>", lambda e: webbrowser.open("https://www.ubiedu.co.kr"))

    def get_current_proxy_settings(self):
        try:
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, self.reg_path, 0, winreg.KEY_READ) as key:
                try:
                    proxy_server, _ = winreg.QueryValueEx(key, "ProxyServer")
                    ip, port = proxy_server.split(":")
                except:
                    ip, port = "", ""
                
                try:
                    proxy_enable, _ = winreg.QueryValueEx(key, "ProxyEnable")
                except:
                    proxy_enable = 0
                
                return ip, port, bool(proxy_enable)
        except Exception:
            return "", "", False

    def set_proxy(self, enable):
        ip = self.ip_entry.get().strip()
        port = self.port_entry.get().strip()

        if enable and (not ip or not port):
            messagebox.showwarning("경고", "IP와 포트를 입력해 주세요.")
            return

        try:
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, self.reg_path, 0, winreg.KEY_WRITE) as key:
                if enable:
                    winreg.SetValueEx(key, "ProxyServer", 0, winreg.REG_SZ, f"{ip}:{port}")
                    winreg.SetValueEx(key, "ProxyEnable", 0, winreg.REG_DWORD, 1)
                else:
                    winreg.SetValueEx(key, "ProxyEnable", 0, winreg.REG_DWORD, 0)

            # Notify system of settings change
            INTERNET_OPTION_REFRESH = 37
            INTERNET_OPTION_SETTINGS_CHANGED = 39
            internet_set_option = ctypes.windll.wininet.InternetSetOptionW
            internet_set_option(0, INTERNET_OPTION_REFRESH, 0, 0)
            internet_set_option(0, INTERNET_OPTION_SETTINGS_CHANGED, 0, 0)

            state_text = "ON" if enable else "OFF"
            self.status_var.set(f"현재 상태: {state_text}")
            messagebox.showinfo("성공", f"프록시가 {state_text} 되었습니다.")
        except Exception as e:
            messagebox.showerror("오류", f"설정 변경 중 오류가 발생했습니다: {e}")

def main():
    if not is_admin():
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
        sys.exit()

    root = tk.Tk()
    app = ProxyManagerGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()