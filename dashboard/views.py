from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import WatchlistItem, Preference

@login_required
def dashboard(request):
    pref, _ = Preference.objects.get_or_create(user=request.user)
    watchlist = WatchlistItem.objects.filter(user=request.user)
    return render(request, "dashboard/dashboard.html", {"pref": pref, "watchlist": watchlist})

@login_required
def add_watchlist(request):
    if request.method == "POST":
        ticker = request.POST.get("ticker", "").upper()[:16]
        if ticker:
            WatchlistItem.objects.get_or_create(user=request.user, ticker=ticker)
    return redirect("dashboard:dashboard")

@login_required
def remove_watchlist(request):
    if request.method == "POST":
        ticker = request.POST.get("ticker", "").upper()[:16]
        if ticker:
            WatchlistItem.objects.filter(user=request.user, ticker=ticker).delete()
    return redirect("dashboard:dashboard")
 
import io
import matplotlib.pyplot as plt
from django.core.mail import EmailMessage
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
import requests
import base64
import json
@csrf_exempt
def send_graph_email(request):
    print("POST data received:", request.body)

    if request.method != 'POST':
        return JsonResponse({"error": "Invalid request"}, status=400)

    try:
        data = json.loads(request.body)
        email = data.get("email")
        ticker = data.get("ticker")
        summary = data.get("summary")
        predicted_data = data.get("predicted_data")

        if not email or not ticker or not predicted_data or len(predicted_data) == 0:
            return JsonResponse({"error": "Missing required data."}, status=400)

        # --- Step 1: Generate Graph ---
        plt.figure(figsize=(6, 4))
        plt.plot(predicted_data, marker='o', label='Predicted Trend')
        plt.title(f'{ticker} Stock Prediction Graph')
        plt.xlabel('Time')
        plt.ylabel('Price')
        plt.legend()
        plt.tight_layout()

        buf = io.BytesIO()
        plt.savefig(buf, format='png')
        buf.seek(0)
        plt.close()

        # ----------------------------
        # STEP 2 — AI EXPLANATION (OpenRouter)
        # ----------------------------
        ai_explanation = f"Predicted trend for {ticker}: {summary}"

        try:
            url = "https://openrouter.ai/api/v1/chat/completions"

            headers = {
                "Authorization": f"Bearer {settings.OPENROUTER_API_KEY}",
                "HTTP-Referer": "http://localhost",
                "X-Title": "StockAI",
                "Content-Type": "application/json",
            }

            payload = {
                "model": "arcee-ai/trinity-large-preview:free",
                "messages": [
                    {"role": "system", "content": "You are a financial analyst who explains trends in simple language."},
                    {"role": "user", "content": f"Explain the predicted stock trend for {ticker}.\nSummary:\n{summary}"},
                ]
            }

            response = requests.post(url, json=payload, headers=headers, timeout=10)

            print("AI API response:", response.text)

            if response.status_code == 200:
                resp = response.json()
                choice = resp.get("choices", [{}])[0]

                # Chat-style response
                msg = choice.get("message", {}).get("content")
                # Text-only response (Nemotron free)
                txt = choice.get("text")

                if msg:
                    ai_explanation = msg
                elif txt:
                    ai_explanation = txt

        except Exception as e:
            print("AI API exception:", e)

        # --- Step 3: Send Email ---
        subject = f"📊 StockAI Prediction Report for {ticker}"
        body = (
            f"Hello,\n\n"
            f"Here is your stock prediction report for {ticker}:\n\n"
            f"{ai_explanation}\n\n"
            f"Best,\nStockAI Team"
        )

        try:
            email_msg = EmailMessage(
                subject,
                body,
                settings.DEFAULT_FROM_EMAIL,
                [email],
            )
            email_msg.attach(f'{ticker}_prediction.png', buf.getvalue(), 'image/png')
            email_msg.send(fail_silently=False)
        except Exception as e:
            print("Email sending error:", e)
            return JsonResponse({"error": f"Failed to send email: {str(e)}"}, status=500)

        return JsonResponse({"success": True, "message": "Email sent successfully!"})

    except Exception as e:
        print("General error:", e)
        return JsonResponse({"error": f"Failed to send email: {str(e)}"}, status=500)
