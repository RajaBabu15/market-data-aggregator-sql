# src/data_cleaner.py

import pandas as pd
import numpy as np

def clean_ohlcv_data(df, ticker="Unknown"):
    """
    Cleans and validates OHLCV data in a DataFrame.

    Args:
        df (pd.DataFrame): Input DataFrame with expected columns
                           ('open', 'high', 'low', 'close', 'volume') and potentially a date index/column.
        ticker (str): Ticker symbol for logging purposes.

    Returns:
        pd.DataFrame: Cleaned DataFrame with columns ('ticker', 'date', 'open', 'high', 'low', 'close', 'volume'),
                      or None if input is invalid or cleaning results in empty data.
    """
    if df is None or df.empty:
        print(f"Cleaner: No data provided for {ticker}.")
        return None

    print(f"Cleaner: Cleaning data for {ticker} ({len(df)} rows)...")
    df_cleaned = df.copy()

    required_cols = {'open', 'high', 'low', 'close', 'volume'}
    if not required_cols.issubset(df_cleaned.columns):
        missing = required_cols - set(df_cleaned.columns)
        print(f"Cleaner Error: DataFrame for {ticker} is missing columns: {missing}")
        return None

    # 1. Ensure Correct Index (needs to be DatetimeIndex for processing, then reset)
    original_index_name = df_cleaned.index.name
    if isinstance(df_cleaned.index, pd.DatetimeIndex):
        df_cleaned['date'] = df_cleaned.index # Ensure date column exists if it was the index
    elif 'date' in df_cleaned.columns:
        df_cleaned['date'] = pd.to_datetime(df_cleaned['date'])
        df_cleaned = df_cleaned.set_index('date', drop=False) # Keep date column, set index temporarily
    else: # Try to use original index if it looks like dates
        try:
            df_cleaned.index = pd.to_datetime(df_cleaned.index)
            df_cleaned['date'] = df_cleaned.index
            print(f"Cleaner Info: Used original index as date for {ticker}.")
        except (TypeError, ValueError):
             print(f"Cleaner Error: DataFrame for {ticker} needs a 'date' index or column.")
             return None

    # Ensure index IS datetime index after potential setting
    if not isinstance(df_cleaned.index, pd.DatetimeIndex):
         # If setting index failed previously or wasn't datetime-like
         print(f"Cleaner Error: Could not establish a valid DatetimeIndex for {ticker}.")
         return None


    # 2. Convert columns to numeric, coercing errors
    for col in ['open', 'high', 'low', 'close', 'volume']:
        df_cleaned[col] = pd.to_numeric(df_cleaned[col], errors='coerce')

    # 3. Handle Missing Values (Drop rows with any NaN in OHLCV)
    initial_rows = len(df_cleaned)
    cols_to_check_na = ['open', 'high', 'low', 'close', 'volume']
    df_cleaned.dropna(subset=cols_to_check_na, inplace=True)
    rows_dropped = initial_rows - len(df_cleaned)
    if rows_dropped > 0:
        print(f"Cleaner: Dropped {rows_dropped} rows with NaN values in OHLCV for {ticker}.")

    if df_cleaned.empty:
        print(f"Cleaner: DataFrame for {ticker} became empty after dropping NaNs.")
        return None

    # 4. Basic Data Validation (Optional but recommended)
    # Check if High >= Low
    invalid_hl = df_cleaned[df_cleaned['high'] < df_cleaned['low']]
    if not invalid_hl.empty:
        print(f"Cleaner Warning: Found {len(invalid_hl)} rows where High < Low for {ticker}. Keeping rows but check data source.")
        # Consider dropping these rows: df_cleaned = df_cleaned[df_cleaned['high'] >= df_cleaned['low']]

    # Check if Close/Open are within High/Low bounds
    invalid_c = df_cleaned[(df_cleaned['close'] > df_cleaned['high']) | (df_cleaned['close'] < df_cleaned['low'])]
    invalid_o = df_cleaned[(df_cleaned['open'] > df_cleaned['high']) | (df_cleaned['open'] < df_cleaned['low'])]
    if not invalid_c.empty or not invalid_o.empty:
        print(f"Cleaner Warning: Found {len(invalid_c)} rows where Close outside H/L and {len(invalid_o)} where Open outside H/L for {ticker}. Check data source.")

    # Check for zero volume (might be valid, e.g., holidays, but good to note)
    zero_vol = df_cleaned[df_cleaned['volume'] == 0]
    if not zero_vol.empty:
         print(f"Cleaner Info: Found {len(zero_vol)} rows with zero volume for {ticker}.")

    # Check for negative prices/volume (should not happen with adjusted data usually)
    if (df_cleaned[['open', 'high', 'low', 'close', 'volume']] < 0).any().any():
        print(f"Cleaner Warning: Found negative values in OHLCV data for {ticker}. Check data source.")
        # Consider dropping: df_cleaned = df_cleaned[(df_cleaned[['open','high','low','close','volume']] >= 0).all(axis=1)]

    print(f"Cleaner: Finished cleaning for {ticker}. Resulting rows: {len(df_cleaned)}")

    # Prepare for DB insertion - ensure 'date' column has only date part, and 'ticker' exists
    # Reset index to move date back to column if needed
    if isinstance(df_cleaned.index, pd.DatetimeIndex):
         df_cleaned.reset_index(inplace=True) # Moves 'date' from index to column

    # Ensure 'date' column exists after reset and contains only date objects
    if 'date' not in df_cleaned.columns:
         print(f"Cleaner Error: 'date' column lost during processing for {ticker}.")
         return None
    df_cleaned['date'] = pd.to_datetime(df_cleaned['date']).dt.date # Ensure only date part

    # Ensure 'ticker' column exists
    df_cleaned['ticker'] = ticker

    # Return dataframe with specific columns required for DB insertion
    final_cols = ['ticker', 'date', 'open', 'high', 'low', 'close', 'volume']
    return df_cleaned[final_cols]