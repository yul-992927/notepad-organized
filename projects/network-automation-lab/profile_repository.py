from __future__ import annotations

import json
from pathlib import Path


class TechnologyProfileRepository:
    """Provides device-specific command profiles for guided selection."""

    def __init__(self, profile_path: Path | None = None):
        root = Path(__file__).resolve().parent
        self.profile_path = profile_path or root / "inventory" / "technology_profiles.yaml"
        self._profiles: dict[str, dict] | None = None

    def _load(self) -> dict[str, dict]:
        if self._profiles is None:
            text = self.profile_path.read_text(encoding="utf-8")
            try:
                import yaml
            except ImportError:
                document = json.loads(text)
            else:
                document = yaml.safe_load(text) or {}
            self._profiles = document.get("profiles", {})
        return self._profiles

    def device_profiles(self, device_name: str) -> dict[str, dict]:
        return dict(self._load().get(device_name, {}))

    def technology_profile(self, device_name: str, technology_key: str) -> dict:
        profiles = self.device_profiles(device_name)
        try:
            return dict(profiles[technology_key])
        except KeyError as exc:
            raise KeyError(f"{device_name}에 등록되지 않은 기술입니다: {technology_key}") from exc

