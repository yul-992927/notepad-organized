from __future__ import annotations

from dataclasses import dataclass

from profile_repository import TechnologyProfileRepository


@dataclass(frozen=True)
class GuidedCommandRequest:
    device_name: str
    technology_key: str


@dataclass(frozen=True)
class TechnologyOption:
    key: str
    label: str
    status: str
    missing: tuple[str, ...] = ()


@dataclass(frozen=True)
class GuidedCommandBatch:
    device_name: str
    technology_key: str
    label: str
    operation: str
    commands: tuple[str, ...]


class GuidedCommandFeature:
    """Turns a device/technology selection into a complete command batch."""

    def __init__(self, profiles: TechnologyProfileRepository):
        self.profiles = profiles

    def available_technologies(self, device_name: str) -> list[TechnologyOption]:
        options: list[TechnologyOption] = []
        for key, profile in self.profiles.device_profiles(device_name).items():
            options.append(
                TechnologyOption(
                    key=key,
                    label=profile.get("label", key),
                    status=profile.get("status", "pending"),
                    missing=tuple(profile.get("missing", [])),
                )
            )
        return options

    def generate(self, request: GuidedCommandRequest) -> GuidedCommandBatch:
        profile = self.profiles.technology_profile(request.device_name, request.technology_key)
        status = profile.get("status", "pending")
        if status != "ready":
            missing = ", ".join(profile.get("missing", [])) or "GNS3 상세값"
            raise ValueError(
                f"아직 자동 실행할 수 없는 기술입니다. 먼저 확정할 값: {missing}"
            )
        commands = tuple(profile.get("commands", []))
        if not commands:
            raise ValueError("프로필에 실행 명령이 없습니다.")
        return GuidedCommandBatch(
            device_name=request.device_name,
            technology_key=request.technology_key,
            label=profile.get("label", request.technology_key),
            operation=profile.get("operation", "config"),
            commands=commands,
        )
