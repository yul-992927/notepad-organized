from __future__ import annotations

from main import NetworkAutomationApp


class GuidedSelectionConsole:
    """Selects one router and one technology, then runs its full profile."""

    def __init__(self, app: NetworkAutomationApp | None = None):
        self.app = app or NetworkAutomationApp()

    def run(self) -> None:
        devices = sorted(
            (name for name in self.app.inventory.devices() if name.startswith("R")),
            key=lambda name: int(name[1:]),
        )
        print("\n=== 장비·기술 선택 자동화 ===")
        for index, name in enumerate(devices, start=1):
            print(f"[{index}] {name}")
        device_choice = self._select_index("라우터 선택: ", len(devices))
        device_name = devices[device_choice]

        options = self.app.list_device_technologies(device_name)
        if not options:
            print(f"{device_name}에 등록된 기술 프로필이 없습니다.")
            return
        for index, option in enumerate(options, start=1):
            status = "실행 가능" if option.status == "ready" else "미확정"
            print(f"[{index}] {option.label} ({status})")
            if option.missing:
                print("    필요값: " + ", ".join(option.missing))
        technology_choice = self._select_index("기술 선택: ", len(options))
        selected = options[technology_choice]

        if selected.status != "ready":
            print("GNS3 상세값 확정 후 프로필을 완성해야 실행할 수 있습니다.")
            return

        mode = input("[1] Dry Run  [2] 실제 적용: ").strip()
        dry_run = mode != "2"
        self.app.run_device_technology(
            device_name,
            selected.key,
            dry_run=dry_run,
            require_confirmation=True,
        )

    def _select_index(self, prompt: str, count: int) -> int:
        value = input(prompt).strip()
        if not value.isdigit() or not 1 <= int(value) <= count:
            raise ValueError("메뉴 범위를 벗어난 선택입니다.")
        return int(value) - 1


if __name__ == "__main__":
    GuidedSelectionConsole().run()
