# StockAI Starter (Django + Plotly + DeepSeek Chatbot)

A minimal, working starter for a stock market prediction web app with:

- Django backend (auth + persistent sessions with "Remember me").
- Watchlist, saved preferences, and chat history.
- Plotly interactive graphs (client-side).
- Simple ML placeholder and a slot for an LSTM model.
- DeepSeek chatbot endpoint stub (replace API key and endpoint).

## Quick Start

```bash
# 1) Create & activate venv (Windows PowerShell example)
python -m venv venv
venv\Scripts\activate

# 2) Install dependencies
pip install -r requirements.txt

# 3) Create .env from example and set keys
copy .env.example .env
# Edit .env to add SECRET_KEY and DEEPSEEK_API_KEY

# 4) Run migrations & create superuser
python manage.py migrate
python manage.py createsuperuser

# 5) Start the dev server
python manage.py runserver
```

Open http://127.0.0.1:8000/

## Features

- Login with "Remember me" checkbox (long-lived session until explicit logout).
- Dashboard with:
  - Ticker search
  - Watchlist (add/remove tickers)
  - Interactive Plotly chart for selected ticker
  - Simple price prediction endpoint (placeholder)
- Chatbot panel using DeepSeek API via `/api/chatbot/`

## Notes

- By default uses SQLite. For MySQL, set `DATABASE_URL` in `.env`.
- yfinance fetches data from the internet; ensure you have connectivity.
- This is a **starter**. Extend models, ML, and UI as needed.
