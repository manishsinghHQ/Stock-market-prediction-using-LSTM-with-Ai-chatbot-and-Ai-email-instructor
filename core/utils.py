import os
from django.conf import settings
from joblib import load as joblib_load

MODEL = None
SCALER = None

def model_paths():
    base = os.path.join(settings.BASE_DIR, "core", "ml_models")
    return {
        "model": os.path.join(base, "stock_lstm_model.h5"),
        "scaler": os.path.join(base, "scaler.pkl")
    }

def load_model_and_scaler():
    global MODEL, SCALER
    paths = model_paths()
    if MODEL is None:
        try:
            import tensorflow as tf
            MODEL = tf.keras.models.load_model(paths["model"])
        except Exception:
            MODEL = None
    if SCALER is None:
        try:
            if os.path.exists(paths["scaler"]):
                SCALER = joblib_load(paths["scaler"])
        except Exception:
            SCALER = None
    return MODEL, SCALER
