from __future__ import annotations

import json
import os
from datetime import datetime
from pathlib import Path

from connections.router_connection import DeviceCredentials, RouterConnection
from inventory_loader import InventoryRepository


class CredentialProvider:
    """Reads device credentials from environment variables."""

    def from_environment(self) -> DeviceCredentials:
        username = os.getenv("NETWORK_USERNAME", "")
        password = os.getenv("NETWORK_PASSWORD", "")
        secret = os.getenv("NETWORK_SECRET", "")
        if not username or not password:
            raise RuntimeError("NETWORK_USERNAME과 NETWORK_PASSWORD 환경변수가 필요합니다.")
        return DeviceCredentials(username=username, password=password, secret=secret)


class ExecutionLogger:
    """Stores one JSON audit record for each execution."""

    def __init__(self, log_dir: Path):
        self.log_dir = log_dir

    def save(
        self,
        targets: list[str],
        commands: list[str],
        dry_run: bool,
        results: dict[str, dict],
        operation: str = "auto",
    ) -> Path:
        self.log_dir.mkdir(exist_ok=True)
        now = datetime.now()
        path = self.log_dir / f"run-{now.strftime('%Y%m%d-%H%M%S-%f')}.json"
        payload = {
            "timestamp": now.isoformat(timespec="seconds"),
            "targets": targets,
            "commands": commands,
            "dry_run": dry_run,
            "operation": operation,
            "results": results,
        }
        path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        return path


class DeviceExecutionService:
    """Executes one command set across selected devices."""

    def __init__(
        self,
        inventory: InventoryRepository,
        logger: ExecutionLogger,
        credential_provider: CredentialProvider,
    ):
        self.inventory = inventory
        self.logger = logger
        self.credential_provider = credential_provider

    def execute(
        self,
        targets: list[str],
        commands: list[str],
        *,
        dry_run: bool = True,
        operation: str = "auto",
    ) -> dict[str, dict]:
        if operation not in {"auto", "config", "exec", "show"}:
            raise ValueError(f"지원하지 않는 실행 모드입니다: {operation}")
        results: dict[str, dict] = {}
        credentials = None if dry_run else self.credential_provider.from_environment()

        for name in targets:
            try:
                device = self.inventory.device(name)
                if not device.get("management_ip"):
                    raise ValueError("management_ip 미설정")
                if dry_run:
                    results[name] = {
                        "ok": True,
                        "dry_run": True,
                        "operation": operation,
                        "commands": commands,
                    }
                    continue

                with RouterConnection(device, credentials) as router:
                    effective_operation = operation
                    if operation == "auto":
                        effective_operation = (
                            "show" if all(command.lower().startswith("show ") for command in commands) else "config"
                        )
                    if effective_operation == "show":
                        output = {command: router.show(command) for command in commands}
                    elif effective_operation == "exec":
                        output = {command: router.execute_command(command) for command in commands}
                    else:
                        output = router.configure(commands)
                results[name] = {"ok": True, "output": output}
            except Exception as exc:
                results[name] = {"ok": False, "error": str(exc)}

        self.logger.save(targets, commands, dry_run, results, operation)
        return results
