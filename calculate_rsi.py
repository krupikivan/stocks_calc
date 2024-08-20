import yfinance as yf
import pandas as pd

# Fetch historical data from Yahoo Finance
symbol = "LIFW"  # Example: Apple Inc.
data = yf.download(symbol, start="2023-01-01", end="2024-04-01")


# Assuming 'data' DataFrame has 'Close' prices, calculate RSI
def calculate_rsi(series, period=14):
    delta = series.diff(1)
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()

    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return rsi


# Stochastic RSI calculation
def calculate_stoch_rsi(rsi, period=14):
    min_rsi = rsi.rolling(window=period).min()
    max_rsi = rsi.rolling(window=period).max()

    stoch_rsi = (rsi - min_rsi) / (max_rsi - min_rsi)
    return stoch_rsi


# Calculate RSI and Stoch RSI
data["RSI"] = calculate_rsi(data["Close"])
data["Stoch_RSI"] = calculate_stoch_rsi(data["RSI"])

# Display the last few rows to see the calculation
print(data.tail())
