'''
# STEP 1: Install required libraries
!pip install yfinance tensorflow scikit-learn

# STEP 2: Import necessary packages
import yfinance as yf
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.preprocessing import MinMaxScaler
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, LSTM, Dropout
import joblib

# STEP 3: Download stock data
stock_symbol = 'MSFT'
data = yf.download(stock_symbol, start='2022-01-01', end='2023-12-31')
data = data[['Close']]

# Check if data is empty
if data.empty:
    raise ValueError("No data was downloaded. Try a different stock symbol or wait a few minutes.")

# STEP 4: Scale data
scaler = MinMaxScaler()
scaled_data = scaler.fit_transform(data)

# Save the scaler
joblib.dump(scaler, 'scaler.pkl')

# STEP 5: Create training data
X_train = []
y_train = []
sequence_length = 60

for i in range(sequence_length, len(scaled_data)):
    X_train.append(scaled_data[i-sequence_length:i, 0])
    y_train.append(scaled_data[i, 0])

X_train, y_train = np.array(X_train), np.array(y_train)
X_train = np.reshape(X_train, (X_train.shape[0], X_train.shape[1], 1))

# STEP 6: Build LSTM model
model = Sequential()
model.add(LSTM(units=50, return_sequences=True, input_shape=(X_train.shape[1], 1)))
model.add(Dropout(0.2))
model.add(LSTM(units=50, return_sequences=False))
model.add(Dropout(0.2))
model.add(Dense(units=1))

model.compile(optimizer='adam', loss='mean_squared_error')
model.fit(X_train, y_train, epochs=25, batch_size=32)

# STEP 7: Save model
model.save('stock_lstm_model.h5')

# STEP 8: Download files
from google.colab import files
files.download('stock_lstm_model.h5')
files.download('scaler.pkl')
'''