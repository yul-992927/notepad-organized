from __future__ import annotations

import json
from pathlib import Path

from features.custom_command import CustomCommandFeature, ManualCommandRequest
from features.eigrp import EigrpFeature, EigrpRequest
from features.guided_command import GuidedCommandFeature, GuidedCommandRequest, TechnologyOption
from inventory_loader import InventoryRepository
from profile_repository import TechnologyProfileRepository
from services import CredentialProvider, DeviceExecutionService, ExecutionLogger


class NetworkAutomationApp:
    """Application facade used by both CLI and Jupyter Notebook."""

    def __init__(self, project_root: Path | None = None):
        self.project_root = project_root or Path(__file__).resolve().parent
        self.inventory = InventoryRepository(self.project_root / "inventory")
        self.profiles = TechnologyProfileRepository(
            self.project_root / "inventory" / "technology_profiles.yaml"
        )
        self.eigrp = EigrpFeature()
        self.custom_commands = CustomCommandFeature()
        self.guided_commands = GuidedCommandFeature(self.profiles)
        self.executor = DeviceExecutionService(
            inventory=self.inventory,
            logger=ExecutionLogger(self.project_root / "logs"),
            credential_provider=CredentialProvider(),
        )

    def preview(self, targets: list[str], commands: list[str]) -> str:
        lines = ["적용 대상: " + ", ".join(targets), "생성 명령:"]
        lines.extend(f"  {command}" for command in commands)
        return "\n".join(lines)

    def build_eigrp_commands(self, action: str, as_number: int, **kwargs) -> list[str]:
        request = EigrpRequest(action=action, as_number=as_number, **kwargs)
        return self.eigrp.generate_commands(request)

    def list_device_technologies(self, device_name: str) -> list[TechnologyOption]:
        self.inventory.device(device_name)
        return self.guided_commands.available_technologies(device_name)

    def run_device_technology(
        self,
        device_name: str,
        technology_key: str,
        *,
        dry_run: bool = True,
        require_confirmation: bool = True,
    ) -> dict[str, dict]:
        self.inventory.device(device_name)
        batch = self.guided_commands.generate(
            GuidedCommandRequest(device_name=device_name, technology_key=technology_key)
        )
        commands = list(batch.commands)
        print(f"선택 기술: {batch.label}")
        print(self.preview([device_name], commands))
        if not dry_run and require_confirmation:
            answer = input("실제로 적용하려면 APPLY를 입력하세요: ").strip()
            if answer != "APPLY":
                print("실행을 취소했습니다.")
                return {}
        return self.executor.execute(
            [device_name], commands, dry_run=dry_run, operation=batch.operation
        )

    def run_eigrp_group(
        self,
        group_name: str,
        action: str,
        as_number: int,
        *,
        dry_run: bool = True,
        require_confirmation: bool = True,
        **kwargs,
    ) -> dict[str, dict]:
        targets = self.inventory.devices_for_group(group_name)
        commands = self.build_eigrp_commands(action, as_number, **kwargs)
        print(self.preview(targets, commands))

        if not dry_run and require_confirmation:
            answer = input("실제로 적용하려면 APPLY를 입력하세요: ").strip()
            if answer != "APPLY":
                print("실행을 취소했습니다.")
                return {}
        return self.executor.execute(targets, commands, dry_run=dry_run, operation="auto")

    def run_manual_group(
        self,
        group_name: str,
        command_text: str,
        *,
        operation: str = "config",
        dry_run: bool = True,
        require_confirmation: bool = True,
    ) -> dict[str, dict]:
        targets = self.inventory.devices_for_group(group_name)
        return self.run_manual_devices(
            targets,
            command_text,
            operation=operation,
            dry_run=dry_run,
            require_confirmation=require_confirmation,
        )

    def run_manual_devices(
        self,
        targets: list[str],
        command_text: str,
        *,
        operation: str = "config",
        dry_run: bool = True,
        require_confirmation: bool = True,
    ) -> dict[str, dict]:
        request = ManualCommandRequest(command_text=command_text, operation=operation)
        commands = self.custom_commands.generate_commands(request)
        for target in targets:
            self.inventory.device(target)

        print(self.preview(targets, commands))
        print(f"실행 모드: {operation}")
        if not dry_run and require_confirmation:
            answer = input("수동 명령을 실제 적용하려면 APPLY를 입력하세요: ").strip()
            if answer != "APPLY":
                print("실행을 취소했습니다.")
                return {}
        return self.executor.execute(
            targets,
            commands,
            dry_run=dry_run,
            operation=operation,
        )

    def run_demo(self) -> dict[str, dict]:
        result = self.run_eigrp_group(
            "eigrp_100",
            action="network",
            as_number=100,
            network="198.18.0.0",
            wildcard="0.0.127.255",
            dry_run=True,
        )
        print("\n기본 실행은 Dry Run입니다.")
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return result


if __name__ == "__main__":
    NetworkAutomationApp().run_demo()
