import os, json, pickle, requests
import numpy as np
import pandas as pd
import yfinance as yf
from keras.models import load_model
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponseBadRequest
from django.conf import settings
from .models import ChatMessage
from dashboard.models import WatchlistItem
import joblib
from core.ai_local import local_ai_reply
# ==========================
# Load ML Model + Scaler
# ==========================
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL_PATH = os.path.join(BASE_DIR,  "ml_models", "stock_lstm_model.h5")
SCALER_PATH = os.path.join(BASE_DIR,  "ml_models", "scaler.pkl")

try:
    lstm_model = load_model(MODEL_PATH)
    print("✅ LSTM model loaded successfully.")
except Exception as e:
    lstm_model = None
    print("❌ Failed to load LSTM model:", e)

try:
    with open(SCALER_PATH, "rb") as f:
        scaler = joblib.load(f)
    print("✅ Scaler loaded successfully.")
except Exception as e:
    scaler = None
    print("❌ Failed to load scaler:", e)


# ==========================
# API Endpoints
# ==========================
@login_required
def stock_history(request, ticker):
    """Fetch historical stock data"""
    ticker = ticker.upper()[:16]
    period = request.GET.get("period", "6mo")
    interval = request.GET.get("interval", "1d")
    try:
        df = yf.download(tickers=ticker, period=period, interval=interval, progress=False, timeout=60)
        if df.empty:
            return JsonResponse({"error": f"No data for {ticker}"}, status=404)

        df = df.reset_index()
        data = {
            "dates": df["Date"].astype(str).squeeze().tolist(),
            "close": df["Close"].astype(float).squeeze().tolist(),
            "open": df["Open"].astype(float).squeeze().tolist(),
            "high": df["High"].astype(float).squeeze().tolist(),
            "low": df["Low"].astype(float).squeeze().tolist(),
            "volume": df["Volume"].fillna(0).astype(int).squeeze().tolist(),
        }
        return JsonResponse(data)
    except Exception as e:
        import traceback
        print("❌ stock_history error:", e)
        traceback.print_exc()
        return JsonResponse({"error": str(e)}, status=500)


@login_required
def predict_price(request, ticker):
    """Predict next-day price using LSTM model + return historical data + accuracy"""
    ticker = ticker.upper()[:16]
    try:
        df = yf.download(tickers=ticker, period="6mo", interval="1d", progress=False)
        if df.empty:
            return JsonResponse({"error": "No data"}, status=404)

        # Use Close prices for prediction
        data = df["Close"].values.reshape(-1, 1)

        if not scaler:
            return JsonResponse({"error": "Scaler not available"}, status=500)

        scaled_data = scaler.transform(data)
        lookback = 60
        if len(scaled_data) < lookback:
            return JsonResponse({"error": "Not enough data"}, status=400)

        # Prepare sequences for evaluation (optional, using last 20% for test)
        split = int(0.8 * len(scaled_data))
        X_eval, y_eval = [], []
        for i in range(lookback, len(scaled_data)):
            X_eval.append(scaled_data[i-lookback:i])
            y_eval.append(scaled_data[i, 0])
        X_eval, y_eval = np.array(X_eval), np.array(y_eval)

        # Predict all for evaluation
        if lstm_model:
            y_pred_scaled = lstm_model.predict(X_eval)
            y_pred_org = scaler.inverse_transform(
                np.concatenate((y_pred_scaled, np.zeros((len(y_pred_scaled), data.shape[1]-1))), axis=1)
            )[:,0]

            y_test_org = scaler.inverse_transform(
                np.concatenate((y_eval.reshape(-1,1), np.zeros((len(y_eval), data.shape[1]-1))), axis=1)
            )[:,0]

            # Accuracy metrics
            rmse = float(np.sqrt(np.mean((y_test_org - y_pred_org)**2)))
            mape = float(np.mean(np.abs((y_test_org - y_pred_org)/y_test_org)) * 100)
            accuracy = 100 - mape

            # Predict next-day price
            last_sequence = scaled_data[-lookback:]
            X_test = np.array([last_sequence]).reshape(1, lookback, data.shape[1])
            prediction_scaled = lstm_model.predict(X_test)
            prediction = scaler.inverse_transform(
                np.concatenate((prediction_scaled, np.zeros((1, data.shape[1]-1))), axis=1)
            )[0][0]
        else:
            # Fallback: last close price
            prediction = float(data[-1])
            rmse = mape = 0.0
            accuracy = 0.0

        # Prepare historical data safely
        df = df.reset_index()
        history = {
            "dates": df["Date"].astype(str).values.tolist(),
            "close": df["Close"].astype(float).values.tolist(),
            "open": df["Open"].astype(float).values.tolist(),
            "high": df["High"].astype(float).values.tolist(),
            "low": df["Low"].astype(float).values.tolist(),
            "volume": df["Volume"].fillna(0).astype(int).values.tolist(),


            
        }

        return JsonResponse({
            "ticker": ticker,
            "prediction": round(float(prediction), 2),
            "rmse": round(rmse, 2),
            "mape": round(mape, 2),
            "accuracy": round(accuracy, 2),
            "history": history
        })

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


@login_required
@require_http_methods(["POST"])
def chatbot(request):
    """Chatbot powered by local Hugging Face model (offline mode)."""
    try:
        body = json.loads(request.body.decode("utf-8"))
        user_msg = body.get("message", "").strip()
        if not user_msg:
            return HttpResponseBadRequest("Empty message")
    except Exception:
        return HttpResponseBadRequest("Invalid JSON")

    # Save user message
    ChatMessage.objects.create(user=request.user, role="user", content=user_msg)

    # Get local AI reply
    assistant_reply = local_ai_reply(user_msg)

    # Save assistant message
    ChatMessage.objects.create(user=request.user, role="assistant", content=assistant_reply)

    return JsonResponse({"reply": assistant_reply})


@login_required
@require_http_methods(["GET", "POST", "DELETE"])
def watchlist(request):
    """Manage user watchlist (GET = list, POST = add, DELETE = remove)"""

    if request.method == "GET":
        items = list(WatchlistItem.objects.filter(user=request.user).values("ticker", "added_at"))
        return JsonResponse({"watchlist": items})

    elif request.method == "POST":
        try:
            body = json.loads(request.body.decode("utf-8"))
            ticker = body.get("ticker", "").upper().strip()
            if not ticker:
                return HttpResponseBadRequest("Ticker required")

            # Avoid duplicates
            item, created = WatchlistItem.objects.get_or_create(user=request.user, ticker=ticker)
            if created:
                return JsonResponse({"message": f"{ticker} added to watchlist"})
            else:
                return JsonResponse({"message": f"{ticker} already in watchlist"})
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)

    elif request.method == "DELETE":
        try:
            body = json.loads(request.body.decode("utf-8"))
            ticker = body.get("ticker", "").upper().strip()
            deleted, _ = WatchlistItem.objects.filter(user=request.user, ticker=ticker).delete()
            if deleted:
                return JsonResponse({"message": f"{ticker} removed from watchlist"})
            else:
                return JsonResponse({"message": f"{ticker} not found in watchlist"})
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)

    return HttpResponseBadRequest("Unsupported method")
