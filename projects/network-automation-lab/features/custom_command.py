from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ManualCommandRequest:
    command_text: str
    operation: str = "config"


class CustomCommandFeature:
    """Validates and prepares operator-supplied Cisco IOS commands."""

    SUPPORTED_OPERATIONS = {"config", "exec", "show"}
    BLOCKED_PREFIXES = (
        "reload",
        "erase startup-config",
        "write erase",
        "format ",
        "delete /force",
    )

    def generate_commands(self, request: ManualCommandRequest) -> list[str]:
        operation = request.operation.strip().lower()
        if operation not in self.SUPPORTED_OPERATIONS:
            raise ValueError("수동 명령 모드는 config, exec, show 중 하나여야 합니다.")

        commands = [line.strip() for line in request.command_text.splitlines() if line.strip()]
        if not commands:
            raise ValueError("실행할 명령어를 한 줄 이상 입력해야 합니다.")

        for command in commands:
            lowered = command.lower()
            if lowered.startswith(self.BLOCKED_PREFIXES):
                raise ValueError(f"초기 버전에서 차단된 명령입니다: {command}")

        if operation == "show" and any(not command.lower().startswith("show ") for command in commands):
            raise ValueError("show 모드에는 show 명령만 입력할 수 있습니다.")
        return commands

