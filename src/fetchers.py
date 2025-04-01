# src/fetchers.py

import yfinance as yf
import pandas as pd
import time
from datetime import date, timedelta

def fetch_yfinance_data(ticker, start_date, end_date):
    """
    Fetches daily OHLCV data using yfinance.

    Args:
        ticker (str): Ticker symbol.
        start_date (str or date): Start date.
        end_date (str or date): End date.

    Returns:
        pd.DataFrame: DataFrame with OHLCV data and date index, or empty DataFrame on error.
    """
    print(f"Fetching data for {ticker} from yfinance ({start_date} to {end_date})...")
    try:
        # yfinance expects end_date to be exclusive for daily data, so add 1 day
        end_date_yf = pd.to_datetime(end_date) + timedelta(days=1)
        stock = yf.Ticker(ticker)
        # Use period or start/end. Use auto_adjust=False to get 'Adj Close' separate if needed,
        # but simpler to use auto_adjust=True and rely on yfinance's adjusted OHLC.
        # Setting interval='1d' explicitly.
        hist = stock.history(start=start_date, end=end_date_yf, interval='1d', auto_adjust=True)

        if hist.empty:
            print(f"No data returned from yfinance for {ticker} for the period.")
            return pd.DataFrame()

        # Rename columns to lowercase and match database schema
        hist.rename(columns={
            'Open': 'open',
            'High': 'high',
            'Low': 'low',
            'Close': 'close',
            'Volume': 'volume'
        }, inplace=True)

        # Ensure date is the index and remove timezone if present
        hist.index = pd.to_datetime(hist.index).tz_localize(None).date
        hist.index.name = 'date'

        # Select only the required columns
        required_cols = ['open', 'high', 'low', 'close', 'volume']
        # Ensure only existing columns are selected in case yfinance changes output
        cols_to_select = [col for col in required_cols if col in hist.columns]
        hist = hist[cols_to_select]


        print(f"Successfully fetched {len(hist)} rows for {ticker} from yfinance.")
        # Add a small delay to be polite
        time.sleep(0.5)
        return hist

    except Exception as e:
        print(f"Error fetching yfinance data for {ticker}: {e}")
        # Consider more specific error handling (e.g., network errors, ticker not found)
        return pd.DataFrame()
