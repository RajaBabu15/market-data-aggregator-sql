# scripts/run_fetch_and_store.py

import sys
import os
from datetime import date, timedelta
import time

# Add src directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.config import DEFAULT_TICKERS
from src.database import create_db_tables, insert_ohlcv_data
from src.fetchers import fetch_yfinance_data
from src.data_cleaner import clean_ohlcv_data

# --- Configuration ---
# Use tickers from config or define specific ones here
TICKERS = DEFAULT_TICKERS
# Fetch data for the last N days (adjust as needed for initial load vs daily update)
# For daily Cron job, fetching last 5-10 days is usually enough to catch adjustments/misses
DAYS_TO_FETCH = 10
# For initial bulk load, set a much larger number or specific dates
# DAYS_TO_FETCH = 365 * 5 # Example: 5 years

# Determine date range
END_DATE = date.today()
START_DATE = END_DATE - timedelta(days=DAYS_TO_FETCH)

# --- Main Script ---
if __name__ == "__main__":
    print("--- Market Data Fetch and Store Script ---")
    script_start_time = time.time()

    # 1. Setup Database Tables (Idempotent)
    if not create_db_tables():
        print("Halting script due to database table setup failure.")
        sys.exit(1) # Exit with error code

    # 2. Loop Through Tickers and Process Data
    print(f"\nFetching data for tickers: {TICKERS}")
    print(f"Date range: {START_DATE} to {END_DATE}")

    total_success = 0
    total_fail = 0

    for ticker in TICKERS:
        print(f"\n--- Processing: {ticker} ---")
        ticker_start_time = time.time()
        success = False
        try:
            # Fetch Raw Data (using yfinance for now)
            raw_df = fetch_yfinance_data(ticker, start_date=START_DATE, end_date=END_DATE)

            if not raw_df.empty:
                # Clean Data
                cleaned_df = clean_ohlcv_data(raw_df, ticker=ticker)

                if cleaned_df is not None and not cleaned_df.empty:
                    # Store Data in Database
                    insert_ohlcv_data(cleaned_df)
                    success = True
                else:
                    print(f"Data cleaning failed or resulted in empty data for {ticker}.")
            else:
                 print(f"Failed to fetch data for {ticker}.")

        except Exception as e:
            print(f"An unexpected error occurred processing {ticker}: {e}")
            # Log the error trace here in a real application
            # import traceback; traceback.print_exc();

        ticker_end_time = time.time()
        status = "SUCCESS" if success else "FAILED"
        print(f"Finished processing {ticker} in {ticker_end_time - ticker_start_time:.2f}s [{status}]")

        if success:
            total_success += 1
        else:
            total_fail += 1

    # 3. Final Summary
    script_end_time = time.time()
    print("\n--- Script Summary ---")
    print(f"Processed {len(TICKERS)} tickers.")
    print(f"Successful: {total_success}")
    print(f"Failed:     {total_fail}")
    print(f"Total execution time: {script_end_time - script_start_time:.2f} seconds.")
    print("----------------------")