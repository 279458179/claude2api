import json
import os
from pathlib import Path
from typing import Any, Dict, List, Optional

DEFAULT_CONFIG = {
    "accounts": [],
    "proxy": {
        "enabled": False,
        "http": "",
        "https": ""
    },
    "server": {
        "host": "0.0.0.0",
        "port": 8000
    }
}


class Config:
    def __init__(self):
        # Support Docker environment with configurable path
        config_dir = os.environ.get("CONFIG_DIR", Path(__file__).parent.parent)
        self._config_path: Path = Path(config_dir) / "config.json"
        self._config: Dict[str, Any] = {}
        self._accounts: List[Dict[str, Any]] = []

    @property
    def accounts(self) -> List[Dict[str, Any]]:
        return self._accounts

    @accounts.setter
    def accounts(self, value: List[Dict[str, Any]]):
        self._accounts = value
        self._config["accounts"] = value

    @property
    def proxy(self) -> Dict[str, Any]:
        return self._config.get("proxy", {})

    @property
    def server(self) -> Dict[str, Any]:
        return self._config.get("server", {})

    def load(self) -> None:
        """Load configuration from file"""
        if self._config_path.exists():
            with open(self._config_path, "r", encoding="utf-8") as f:
                self._config = json.load(f)
        else:
            self._config = DEFAULT_CONFIG.copy()
            self._save_config()

        self._accounts = self._config.get("accounts", [])

    def save(self) -> None:
        """Save configuration to file"""
        self._config["accounts"] = self._accounts
        self._save_config()

    def _save_config(self) -> None:
        with open(self._config_path, "w", encoding="utf-8") as f:
            json.dump(self._config, f, indent=2, ensure_ascii=False)

    def get_active_accounts(self) -> List[Dict[str, Any]]:
        """Get all active accounts"""
        return [acc for acc in self._accounts if acc.get("active", True)]

    def get_account_by_id(self, account_id: str) -> Optional[Dict[str, Any]]:
        """Get account by ID"""
        for acc in self._accounts:
            if acc.get("account_id") == account_id:
                return acc
        return None


config = Config()