from app import app
from predictor import router as prediction_router
from scaler import router as scale_router
app.include_router(prediction_router)
app.include_router(scale_router)
