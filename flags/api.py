from __future__ import annotations

from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, Field

from flags.engine import FeatureFlagEngine

app = FastAPI(title="Feature Flag Engine", version="0.1.0")
engine = FeatureFlagEngine()


class EvalReq(BaseModel):
    flag: str
    user_id: str


class FlagUpdateReq(BaseModel):
    enabled: bool = True
    rollout_pct: int = Field(default=100, ge=0, le=100)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/api/v1/flags")
def list_flags() -> dict[str, dict[str, bool | int]]:
    return engine.list_flags()


@app.put("/api/v1/flags/{flag_key}")
def upsert_flag(flag_key: str, req: FlagUpdateReq) -> dict[str, object]:
    try:
        cfg = engine.set_flag(flag_key, enabled=req.enabled, rollout_pct=req.rollout_pct)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc
    return {"flag": flag_key, **cfg}


@app.post("/api/v1/evaluate")
def eval_flag(req: EvalReq) -> dict[str, object]:
    is_active = engine.evaluate(req.flag, req.user_id)
    return {"flag": req.flag, "user_id": req.user_id, "enabled": is_active}
