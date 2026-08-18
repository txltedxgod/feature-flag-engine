import hashlib
from typing import Dict, Any

class FeatureFlagEngine:
    def __init__(self):
        self.flags = {
            "new_checkout_flow": {"enabled": True, "rollout_pct": 50},
            "dark_mode_v2": {"enabled": True, "rollout_pct": 100},
            "beta_ai_features": {"enabled": False, "rollout_pct": 0}
        }

    def evaluate(self, flag_key: str, user_id: str) -> bool:
        flag = self.flags.get(flag_key)
        if not flag or not flag["enabled"]:
            return False
        pct = flag.get("rollout_pct", 100)
        if pct >= 100:
            return True
        hash_val = int(hashlib.md5(f"{flag_key}_{user_id}".encode()).hexdigest()[:6], 16) % 100
        return hash_val < pct
