from __future__ import annotations

import ipaddress
import re
from dataclasses import dataclass


@dataclass(frozen=True)
class EigrpRequest:
    action: str
    as_number: int
    network: str | None = None
    wildcard: str | None = None
    interface: str | None = None


class EigrpFeature:
    """Validates EIGRP input and generates Cisco IOS commands."""

    MENU = {
        "1": ("EIGRP 프로세스 생성", "create"),
        "2": ("Network 대역 추가", "network"),
        "3": ("Passive Interface 설정", "passive_interface"),
        "4": ("현재 EIGRP 상태 조회", "show"),
    }
    INTERFACE_PATTERN = re.compile(r"^[A-Za-z][A-Za-z0-9./_-]*$")

    def validate(self, request: EigrpRequest) -> None:
        if not 1 <= request.as_number <= 65535:
            raise ValueError("EIGRP AS 번호는 1~65535 범위여야 합니다.")
        if request.action == "network":
            if not request.network or not request.wildcard:
                raise ValueError("Network와 Wildcard Mask가 필요합니다.")
            ipaddress.IPv4Address(request.network)
            ipaddress.IPv4Address(request.wildcard)
        elif request.action == "passive_interface":
            if not request.interface or not self.INTERFACE_PATTERN.fullmatch(request.interface):
                raise ValueError("올바른 인터페이스 이름이 필요합니다.")
        elif request.action not in {"create", "show"}:
            raise ValueError(f"지원하지 않는 EIGRP 작업입니다: {request.action}")

    def generate_commands(self, request: EigrpRequest) -> list[str]:
        self.validate(request)
        if request.action == "show":
            return [
                "show ip eigrp neighbors",
                "show ip route eigrp",
                f"show running-config | section router eigrp {request.as_number}",
            ]

        commands = [f"router eigrp {request.as_number}"]
        if request.action == "network":
            commands.append(f"network {request.network} {request.wildcard}")
        elif request.action == "passive_interface":
            commands.append(f"passive-interface {request.interface}")
        return commands

