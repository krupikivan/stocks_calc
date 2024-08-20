import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# Define the date range
today = datetime.now()
eight_weeks_ago = today - timedelta(weeks=8)
four_weeks_ago = today - timedelta(weeks=4)


# Fetch the S&P 500 symbols dynamically
def fetch_sp500_symbols():
    table = pd.read_html("https://en.wikipedia.org/wiki/List_of_S%26P_500_companies")
    return table[0]["Symbol"].tolist()


def get_stock_data(stock_symbol, start_date, end_date):
    # Fetch historical data
    data = yf.download(stock_symbol, start=start_date, end=end_date)
    return data


def identify_daily_pumps(stock_data, min_pump=0.05):
    # Calculate daily percentage change
    stock_data["Pct_Change"] = stock_data["Close"].pct_change()
    # Identify daily pumps
    pumps = stock_data[stock_data["Pct_Change"] >= min_pump]
    return pumps


# Get S&P 500 symbols
stock_symbols = fetch_sp500_symbols()

# Create a dataframe to store the results
pumps_df = pd.DataFrame(
    columns=["Stock", "Pump_Date", "Pump_Pct", "Price_Before_Pump", "Current_Price"]
)

# Calculate daily pumps for each stock
for symbol in stock_symbols:
    try:
        data = get_stock_data(symbol, eight_weeks_ago, today)
        pumps = identify_daily_pumps(data.loc[four_weeks_ago:eight_weeks_ago])
        for index, pump in pumps.iterrows():
            price_before_pump = data.loc[:index].iloc[-2]["Close"]
            current_price = data.iloc[-1]["Close"]
            if np.isclose(current_price, price_before_pump):
                pumps_df = pumps_df.append(
                    {
                        "Stock": symbol,
                        "Pump_Date": index,
                        "Pump_Pct": pump["Pct_Change"],
                        "Price_Before_Pump": price_before_pump,
                        "Current_Price": current_price,
                    },
                    ignore_index=True,
                )
    except Exception as e:
        print(f"Error processing {symbol}: {e}")

# Sort by pump percentage in descending order and get top 20
top_20_pumps = pumps_df.sort_values(by="Pump_Pct", ascending=False).head(20)

print(top_20_pumps)

# Save to CSV file
top_20_pumps.to_csv("top_20_daily_pumps.csv", index=False)
