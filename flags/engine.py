from __future__ import annotations

import hashlib
import threading


class FeatureFlagEngine:
    """Thread-safe feature flag evaluator with deterministic percentage rollouts."""

    def __init__(self) -> None:
        self._lock = threading.RLock()
        self.flags: dict[str, dict[str, bool | int]] = {
            "new_checkout_flow": {"enabled": True, "rollout_pct": 50},
            "dark_mode_v2": {"enabled": True, "rollout_pct": 100},
            "beta_ai_features": {"enabled": False, "rollout_pct": 0},
        }

    def set_flag(
        self, flag_key: str, enabled: bool, rollout_pct: int = 100
    ) -> dict[str, bool | int]:
        cleaned = flag_key.strip()
        if not cleaned:
            raise ValueError("flag_key must not be empty")
        if rollout_pct < 0 or rollout_pct > 100:
            raise ValueError("rollout_pct must be between 0 and 100")
        entry: dict[str, bool | int] = {"enabled": enabled, "rollout_pct": rollout_pct}
        with self._lock:
            self.flags[cleaned] = entry
        return dict(entry)

    def list_flags(self) -> dict[str, dict[str, bool | int]]:
        with self._lock:
            return {k: dict(v) for k, v in self.flags.items()}

    def evaluate(self, flag_key: str, user_id: str) -> bool:
        with self._lock:
            flag = self.flags.get(flag_key)
            if not flag or not flag["enabled"]:
                return False
            pct = int(flag.get("rollout_pct", 100))

        if pct <= 0:
            return False
        if pct >= 100:
            return True

        digest = hashlib.sha256(f"{flag_key}_{user_id}".encode()).hexdigest()
        bucket = int(digest[:8], 16) % 100
        return bucket < pct
