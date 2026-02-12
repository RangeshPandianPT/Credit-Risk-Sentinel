from __future__ import annotations

try:
    import bentoml
    import numpy as np
except ImportError as exc:
    raise SystemExit("BentoML is not installed. Run: pip install bentoml") from exc

model_ref = bentoml.xgboost.get("home_credit_risk:latest")
model_runner = model_ref.to_runner()

svc = bentoml.Service("risk_intervention_service", runners=[model_runner])


@svc.api(input=bentoml.io.NumpyNdarray(), output=bentoml.io.NumpyNdarray())
def predict(input_data: np.ndarray) -> np.ndarray:
    return model_runner.predict.run(input_data)
