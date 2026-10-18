from __future__ import annotations

from main import NetworkAutomationApp
from guided_console import GuidedSelectionConsole


class ConsoleMenu:
    """Simple lab console exposing guided and manual execution modes."""

    def __init__(self, app: NetworkAutomationApp | None = None):
        self.app = app or NetworkAutomationApp()

    def run(self) -> None:
        print("\n=== Network Automation Lab ===")
        print("[1] 장비·기술 선택 → 전체 명령 자동 입력")
        print("[2] EIGRP 값 직접 입력 → 명령 자동 생성")
        print("[3] Cisco IOS 명령 직접 입력")
        choice = input("실행 모드 선택: ").strip()
        if choice == "1":
            GuidedSelectionConsole(self.app).run()
        elif choice == "2":
            self._run_guided_eigrp()
        elif choice == "3":
            self._run_manual()
        else:
            print("지원하지 않는 메뉴입니다.")

    def _run_guided_eigrp(self) -> None:
        group = input("대상 그룹 (eigrp_100/eigrp_200): ").strip()
        action = input("작업 (create/network/passive_interface/show): ").strip()
        as_number = int(input("EIGRP AS 번호: ").strip())
        values: dict[str, str] = {}
        if action == "network":
            values["network"] = input("Network: ").strip()
            values["wildcard"] = input("Wildcard Mask: ").strip()
        elif action == "passive_interface":
            values["interface"] = input("Interface: ").strip()
        self.app.run_eigrp_group(group, action, as_number, dry_run=True, **values)

    def _run_manual(self) -> None:
        group = input("대상 그룹: ").strip()
        operation = input("실행 모드 (config/exec/show): ").strip().lower()
        print("명령을 여러 줄로 입력하고, 마지막 줄에 END를 입력하세요.")
        lines: list[str] = []
        while True:
            line = input()
            if line.strip() == "END":
                break
            lines.append(line)
        self.app.run_manual_group(
            group,
            "\n".join(lines),
            operation=operation,
            dry_run=True,
        )


if __name__ == "__main__":
    ConsoleMenu().run()
