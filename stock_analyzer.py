import yfinance as yf
import pandas as pd
import numpy as np

# Define your investments (symbols, purchased amount, buy price, sell price)
investments_dict = {
    "HOOD": {"amount": 57, "buy": 8.82, "sell": 12.01},
    "AI": {"amount": 16, "buy": 30.37, "sell": 0},
    "HSY": {"amount": 2, "buy": 185.66, "sell": 199},
    "BABA": {"amount": 7, "buy": 74.46, "sell": 77.23},
    "BQ": {"amount": 1680, "buy": 0.3418, "sell": 0},
    "RPHM": {"amount": 340, "buy": 1.47, "sell": 0},
    "ASYS": {"amount": 52, "buy": 4.21, "sell": 5.12},
    "BLUE": {"amount": 150, "buy": 1.36, "sell": 0},
    "ALVR": {"amount": 125, "buy": 0.8, "sell": 0},
    "BHAT": {"amount": 102, "buy": 0.9893, "sell": 1.02},
    "TSLA": {"amount": 6, "buy": 194, "sell": 0},
    "ALTM": {"amount": 107, "buy": 4.69, "sell": 0},
    "LAAC": {"amount": 119, "buy": 4.22, "sell": 5.22},
    "NCL": {"amount": 658, "buy": 0.76, "sell": 0},
    "ORGN": {"amount": 1930, "buy": 0.52, "sell": 0},
    "LIFW": {"amount": 1278, "buy": 0.7825, "sell": 0},
    "MOBX": {"amount": 250, "buy": 1.98, "sell": 2.16},
    "AMLX": {"amount": 152, "buy": 3.29, "sell": 0},
    "DMTK": {"amount": 1472, "buy": 0.679, "sell": 0},
    "WIMI": {"amount": 600, "buy": 0.9101, "sell": 0},
    "GMM": {"amount": 600, "buy": 0.905, "sell": 0},
    "INTJ": {"amount": 250, "buy": 2, "sell": 0},
}

investments_dict = dict(
    sorted(investments_dict.items(), key=lambda item: item[1]["sell"] == 0)
)


# Convert the dictionary to a DataFrame
investments = pd.DataFrame.from_dict(investments_dict, orient="index")
pd.set_option("display.float_format", "{:.3f}".format)
investments.reset_index(inplace=True)
investments.rename(columns={"index": "symbol"}, inplace=True)


# Function to fetch current quotes using yfinance
def fetch_current_quotes(symbols):
    try:
        data = yf.download(symbols, period="1d")["Adj Close"]
        return data.iloc[-1]
    except Exception as e:
        return None

    # quotes = {}
    # for symbol in symbols:
    #     ticker = yf.Ticker(symbol)
    #     quote = ticker.history(period="1d")["Close"].iloc[
    #         0
    #     ]  # Get the most recent closing price
    #     quotes[symbol] = quote
    # return quotes


# Fetch current quotes for the interested symbols
symbols = investments["symbol"].tolist()
current_quotes = fetch_current_quotes(symbols)

# Calculate current value and add columns
investments["current"] = investments["symbol"].map(current_quotes)

# Calculate gain/loss in USD considering current quotes
investments["profit"] = investments.apply(
    lambda row: (
        row["amount"] * (row["current"] - row["buy"])
        if row["sell"] == 0
        else row["amount"] * (row["sell"] - row["buy"])
    ),
    axis=1,
)

# Calculate 'TAX' column for positive gains
investments["TAX"] = investments["profit"].apply(lambda x: x * 0.24 if x > 0 else 0)

# Corrected calculation for dividends
# Dividends are considered here as a concept and not based on actual dividend payments from the stocks
investments["dividends"] = investments.apply(
    lambda row: ((row["profit"] - row["TAX"]) / 2 if row["profit"] > 0 else 0),
    axis=1,
)

# Calculate '%' column
investments["%"] = (
    investments["profit"] / (investments["amount"] * investments["buy"])
) * 100

# Sum specific columns for the total row
totals = investments[["amount", "profit", "TAX", "dividends", "%"]].sum()
totals_row = pd.DataFrame(
    {
        "symbol": ["Total"],
        "amount": [totals["amount"]],
        "buy": [None],  # Not aggregating this column as it doesn't make sense to sum
        "sell": [None],  # Same as buy
        "current": [
            None
        ],  # Not aggregating, could calculate weighted average if meaningful
        "profit": [totals["profit"]],
        "TAX": [totals["TAX"]],
        "dividends": [totals["dividends"]],
        "%": [
            totals["%"]
        ],  # Calculating total performance might not be meaningful as is
    }
)

# Append the totals row to the DataFrame
investments_with_total = pd.concat([investments, totals_row], ignore_index=True)

transition_index = investments_with_total[
    investments_with_total["sell"] == 0
].index.min()

separator_row = pd.DataFrame(
    {
        "symbol": "---",
        "amount": "---",
        "buy": "---",
        "sell": "---",
        "current": "---",
        "profit": "---",
        "TAX": "---",
        "dividends": "---",
        "%": "---",
    },
    index=[transition_index - 0.5],
)

investments_with_separator = (
    pd.concat([investments_with_total, separator_row])
    .sort_index()
    .reset_index(drop=True)
)


# Display the DataFrame with the separator
print(
    investments_with_separator[
        [
            "symbol",
            "amount",
            "buy",
            "sell",
            "current",
            "profit",
            "TAX",
            "dividends",
            "%",
        ]
    ]
)

print(
    "\n Total Investment: $",
    sum(investments["amount"] * investments["buy"])
    - sum(investments["amount"] * investments["sell"]),
)


# Export the table to a CSV file
# investments.to_csv("investment_summary.csv", index=False)
