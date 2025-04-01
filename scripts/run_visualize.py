# scripts/run_visualize.py

import sys
import os
from datetime import date, timedelta
import argparse

# Add src directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.config import DEFAULT_SMA_WINDOW
from src.database import fetch_ohlcv_data
from src.indicators import calculate_sma
from src.plotting import plot_ohlc_with_indicator, print_summary

# --- Argument Parser ---
parser = argparse.ArgumentParser(description="Visualize market data with indicators.")
parser.add_argument("ticker", type=str, help="Ticker symbol to visualize (e.g., AAPL, SPY).")
parser.add_argument("-d", "--days", type=int, default=180, help="Number of past days data to fetch and plot (default: 180).")
parser.add_argument("-w", "--window", type=int, default=DEFAULT_SMA_WINDOW, help=f"SMA window size (default: {DEFAULT_SMA_WINDOW}).")
parser.add_argument("-s", "--start", type=str, default=None, help="Start date (YYYY-MM-DD). Overrides --days if provided.")
parser.add_argument("-e", "--end", type=str, default=None, help="End date (YYYY-MM-DD). Defaults to today.")

args = parser.parse_args()

# --- Configuration from Args ---
TICKER_TO_PLOT = args.ticker.upper()
SMA_WINDOW = args.window

if args.start:
    START_DATE = args.start
    END_DATE = args.end if args.end else date.today().strftime('%Y-%m-%d')
else:
    END_DATE = args.end if args.end else date.today()
    START_DATE = pd.to_datetime(END_DATE) - timedelta(days=args.days)
    END_DATE = pd.to_datetime(END_DATE).strftime('%Y-%m-%d') # Ensure string format
    START_DATE = START_DATE.strftime('%Y-%m-%d') # Ensure string format


# --- Main Script ---
if __name__ == "__main__":
    print(f"--- Visualizing Data for {TICKER_TO_PLOT} ---")
    print(f"Date Range: {START_DATE} to {END_DATE}")

    # 1. Fetch Data from Database
    df = fetch_ohlcv_data(ticker=TICKER_TO_PLOT, start_date=START_DATE, end_date=END_DATE)

    if df.empty:
        print(f"No data found for {TICKER_TO_PLOT} in the database for the specified period.")
        sys.exit(1)

    # Ensure index is DatetimeIndex for mplfinance
    df.index = pd.to_datetime(df.index)

    # 2. Calculate Indicator(s)
    indicator_name = f"SMA_{SMA_WINDOW}"
    df[indicator_name] = calculate_sma(df['close'], window=SMA_WINDOW)

    # 3. Generate Plot
    plot_ohlc_with_indicator(
        df,
        ticker=TICKER_TO_PLOT,
        indicator_name=indicator_name,
        indicator_series=df[indicator_name],
        filename_suffix=f"{START_DATE}_to_{END_DATE}" # Add date range to filename
    )

    # 4. Print Summary
    print_summary(df, ticker=TICKER_TO_PLOT, indicator_name=indicator_name, indicator_series=df[indicator_name])

    print("\n--- Visualization Complete ---")