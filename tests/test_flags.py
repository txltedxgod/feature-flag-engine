import pytest
from fastapi.testclient import TestClient

from flags.api import app
from flags.engine import FeatureFlagEngine

client = TestClient(app)


def test_flag_rollout() -> None:
    f = FeatureFlagEngine()
    assert f.evaluate("dark_mode_v2", "user-100") is True
    assert f.evaluate("beta_ai_features", "user-100") is False
    assert f.evaluate("missing_flag", "user-100") is False


def test_flag_deterministic_percentage_and_validation() -> None:
    f = FeatureFlagEngine()
    results = [f.evaluate("new_checkout_flow", f"u_{i}") for i in range(200)]
    assert any(results) and not all(results)
    assert f.evaluate("new_checkout_flow", "user_42") == f.evaluate(
        "new_checkout_flow", "user_42"
    )

    f.set_flag("zero_pct", enabled=True, rollout_pct=0)
    assert f.evaluate("zero_pct", "anyone") is False

    with pytest.raises(ValueError, match="rollout_pct"):
        f.set_flag("bad_pct", enabled=True, rollout_pct=101)
    with pytest.raises(ValueError, match="empty"):
        f.set_flag("  ", enabled=True, rollout_pct=50)


def test_flag_api_endpoints() -> None:
    assert client.get("/health").json() == {"status": "ok"}
    assert "dark_mode_v2" in client.get("/api/v1/flags").json()

    upd = client.put(
        "/api/v1/flags/canary_search",
        json={"enabled": True, "rollout_pct": 100},
    )
    assert upd.status_code == 200
    assert upd.json()["enabled"] is True

    ev = client.post(
        "/api/v1/evaluate",
        json={"flag": "canary_search", "user_id": "u-99"},
    )
    assert ev.status_code == 200
    assert ev.json()["enabled"] is True

    bad = client.put(
        "/api/v1/flags/invalid_pct",
        json={"enabled": True, "rollout_pct": 150},
    )
    assert bad.status_code == 422
