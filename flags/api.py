from fastapi import FastAPI
from pydantic import BaseModel
from flags.engine import FeatureFlagEngine

app = FastAPI(title="Feature Flag Engine", version="0.1.0")
engine = FeatureFlagEngine()

class EvalReq(BaseModel):
    flag: str
    user_id: str

@app.post("/api/v1/evaluate")
def eval_flag(req: EvalReq):
    is_active = engine.evaluate(req.flag, req.user_id)
    return {"flag": req.flag, "user_id": req.user_id, "enabled": is_active}
