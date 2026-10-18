from __future__ import annotations

import json
from pathlib import Path


class InventoryRepository:
    """Loads devices and logical groups from the project inventory."""

    def __init__(self, inventory_dir: Path | None = None):
        root = Path(__file__).resolve().parent
        self.inventory_dir = inventory_dir or root / "inventory"
        self._devices: dict[str, dict] | None = None
        self._groups: dict[str, dict] | None = None

    def _load_document(self, path: Path) -> dict:
        try:
            import yaml
        except ImportError:
            # JSON is valid YAML. The bundled inventory therefore works before
            # optional dependencies are installed.
            return json.loads(path.read_text(encoding="utf-8"))
        with path.open("r", encoding="utf-8") as handle:
            return yaml.safe_load(handle) or {}

    def devices(self) -> dict[str, dict]:
        if self._devices is None:
            document = self._load_document(self.inventory_dir / "devices.yaml")
            self._devices = document.get("devices", {})
        return self._devices

    def groups(self) -> dict[str, dict]:
        if self._groups is None:
            document = self._load_document(self.inventory_dir / "groups.yaml")
            self._groups = document.get("groups", {})
        return self._groups

    def device(self, name: str) -> dict:
        try:
            return self.devices()[name]
        except KeyError as exc:
            raise KeyError(f"인벤토리에 없는 장비입니다: {name}") from exc

    def devices_for_group(self, group_name: str) -> list[str]:
        try:
            group = self.groups()[group_name]
        except KeyError as exc:
            raise KeyError(f"알 수 없는 장비 그룹입니다: {group_name}") from exc
        return list(group.get("devices", []))

