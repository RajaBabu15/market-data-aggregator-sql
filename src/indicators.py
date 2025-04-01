# src/indicators.py

import pandas as pd

def calculate_sma(data_series, window):
    """
    Calculates the Simple Moving Average (SMA).

    Args:
        data_series (pd.Series): Series of data (e.g., closing prices).
        window (int): The rolling window size.

    Returns:
        pd.Series: Series containing the SMA values, with NaNs at the start.
                   Returns empty Series if input is invalid.
    """
    if data_series is None or data_series.empty or not isinstance(window, int) or window <= 0:
        print("Indicator Error: Invalid input for SMA calculation.")
        return pd.Series(dtype=float)
    if len(data_series) < window:
         print(f"Indicator Warning: Data length ({len(data_series)}) is less than SMA window ({window}). Result will be all NaNs.")
         # Return series of NaNs with the same index
         return pd.Series(index=data_series.index, dtype=float)

    try:
        sma = data_series.rolling(window=window, min_periods=window).mean()
        print(f"Indicator: Calculated SMA with window {window}.")
        return sma
    except Exception as e:
        print(f"Indicator Error: Failed to calculate SMA(window={window}): {e}")
        return pd.Series(dtype=float)
