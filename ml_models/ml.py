'''
# STEP 1: Install libraries
!pip install yfinance tensorflow scikit-learn ta joblib

# STEP 2: Imports
import yfinance as yf
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.preprocessing import MinMaxScaler
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, GRU, Dense, Dropout
from tensorflow.keras.callbacks import EarlyStopping
from ta.momentum import RSIIndicator
from ta.trend import MACD, EMAIndicator
import joblib

# STEP 3: Download historical stock data (5 years)
stock_symbol = "MSFT"
data = yf.download(stock_symbol, start="2018-01-01", end="2024-01-01")

# STEP 4: Ensure Close column is 1D
close_prices = data["Close"]
if isinstance(close_prices, pd.DataFrame) or len(close_prices.shape) > 1:
    close_prices = close_prices.squeeze()  # convert to 1D Series

# STEP 5: Create Technical Indicators
data["RSI"] = RSIIndicator(close_prices).rsi()
macd = MACD(close_prices)
data["MACD"] = macd.macd()
data["Signal"] = macd.macd_signal()
data["EMA_20"] = EMAIndicator(close_prices, window=20).ema_indicator()
data["EMA_50"] = EMAIndicator(close_prices, window=50).ema_indicator()

# Keep only needed columns
data = data[["Close", "RSI", "MACD", "Signal", "EMA_20", "EMA_50"]]

# Fill missing values
data = data.fillna(method="bfill").fillna(method="ffill")

# STEP 6: Scale all features
scaler = MinMaxScaler()
scaled_data = scaler.fit_transform(data)
joblib.dump(scaler, "scaler.pkl")

# STEP 7: Create sequences
sequence_length = 60
X, y = [], []

for i in range(sequence_length, len(scaled_data)):
    X.append(scaled_data[i-sequence_length:i])
    y.append(scaled_data[i, 0])  # predicting Close price only

X, y = np.array(X), np.array(y)

# STEP 8: Train-test split
split = int(0.8 * len(X))
X_train, X_test = X[:split], X[split:]
y_train, y_test = y[:split], y[split:]

# STEP 9: Build Hybrid LSTM + GRU Model
model = Sequential()
model.add(LSTM(64, return_sequences=True, input_shape=(X.shape[1], X.shape[2])))
model.add(Dropout(0.2))
model.add(GRU(64, return_sequences=False))
model.add(Dropout(0.2))
model.add(Dense(32, activation='relu'))
model.add(Dense(1))
model.compile(optimizer="adam", loss="mse")

# STEP 10: Early Stopping
early_stop = EarlyStopping(monitor='loss', patience=5, restore_best_weights=True)

# Train the model
model.fit(
    X_train, y_train,
    epochs=50,
    batch_size=32,
    callbacks=[early_stop]
)

# STEP 11: Save model
model.save("stock_lstm_gru_model.h5")

# STEP 12: Evaluate accuracy
y_pred = model.predict(X_test)

# Invert scaling
y_test_org = scaler.inverse_transform(
    np.concatenate((y_test.reshape(-1,1), np.zeros((len(y_test), 5))), axis=1)
)[:,0]

y_pred_org = scaler.inverse_transform(
    np.concatenate((y_pred, np.zeros((len(y_pred), 5))), axis=1)
)[:,0]

# RMSE
rmse = np.sqrt(np.mean((y_test_org - y_pred_org)**2))

# MAPE
mape = np.mean(np.abs((y_test_org - y_pred_org) / y_test_org)) * 100

# Approximate accuracy
accuracy = 100 - mape

print("RMSE:", rmse)
print("MAPE (%):", mape)
print(f"Approximate Accuracy: {accuracy:.2f}%")

# STEP 13: Plot
plt.figure(figsize=(12,6))
plt.plot(y_test_org, label="Actual Price")
plt.plot(y_pred_org, label="Predicted Price")
plt.title(f"{stock_symbol} Stock Price Prediction\nApprox. Accuracy: {accuracy:.2f}%")
plt.xlabel("Time")
plt.ylabel("Price ($)")
plt.legend()
plt.show()

# STEP 14: Download model and scaler (for Colab)
from google.colab import files
files.download("stock_lstm_gru_model.h5")
files.download("scaler.pkl")
'''