from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable


class ConnectionDependencyError(RuntimeError):
    pass


@dataclass(frozen=True)
class DeviceCredentials:
    username: str
    password: str
    secret: str = ""


class RouterConnection:
    """Direct SSH connection to a routed management IP.

    R12 acts as the routed gateway in this design. It is not treated as an
    application-level SSH proxy.
    """

    def __init__(self, device: dict, credentials: DeviceCredentials, timeout: int = 15):
        self.device = device
        self.credentials = credentials
        self.timeout = timeout
        self._session = None

    def __enter__(self) -> "RouterConnection":
        try:
            from netmiko import ConnectHandler
        except ImportError as exc:
            raise ConnectionDependencyError(
                "Netmiko가 설치되지 않았습니다. requirements.txt를 설치하세요."
            ) from exc

        host = self.device.get("management_ip")
        if not host:
            raise ValueError("장비의 management_ip가 설정되지 않았습니다.")

        self._session = ConnectHandler(
            device_type=self.device.get("platform", "cisco_ios"),
            host=host,
            username=self.credentials.username,
            password=self.credentials.password,
            secret=self.credentials.secret,
            timeout=self.timeout,
        )
        if self.credentials.secret:
            self._session.enable()
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        if self._session is not None:
            self._session.disconnect()
            self._session = None

    def show(self, command: str) -> str:
        if self._session is None:
            raise RuntimeError("SSH 세션이 열려 있지 않습니다.")
        return self._session.send_command(command)

    def execute_command(self, command: str) -> str:
        """Runs a privileged EXEC command outside configuration mode."""
        if self._session is None:
            raise RuntimeError("SSH 세션이 열려 있지 않습니다.")
        return self._session.send_command(command)

    def configure(self, commands: Iterable[str]) -> str:
        if self._session is None:
            raise RuntimeError("SSH 세션이 열려 있지 않습니다.")
        return self._session.send_config_set(list(commands))
