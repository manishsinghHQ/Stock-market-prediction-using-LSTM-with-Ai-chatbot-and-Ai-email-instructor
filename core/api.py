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
    """Predict next-day price using LSTM model + return historical data"""
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

        last_sequence = scaled_data[-lookback:]
        X_test = np.array([last_sequence]).reshape(1, lookback, 1)

        if lstm_model:
            prediction_scaled = lstm_model.predict(X_test)
            prediction = scaler.inverse_transform(prediction_scaled)[0][0]
        else:
            prediction = float(data[-1])

        # Prepare historical data safely
        df = df.reset_index()
        history = {
            "dates": df["Date"].astype(str).squeeze().tolist(),
            "close": df["Close"].astype(float).squeeze().tolist(),
            "open": df["Open"].astype(float).squeeze().tolist(),
            "high": df["High"].astype(float).squeeze().tolist(),
            "low": df["Low"].astype(float).squeeze().tolist(),
            "volume": df["Volume"].fillna(0).astype(int).squeeze().tolist(),
        }

        return JsonResponse({
            "ticker": ticker,
            "prediction": round(float(prediction), 2),
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
