from flags.engine import FeatureFlagEngine

def test_flag_rollout():
    f = FeatureFlagEngine()
    assert f.evaluate("dark_mode_v2", "user-100") is True
    assert f.evaluate("beta_ai_features", "user-100") is False
