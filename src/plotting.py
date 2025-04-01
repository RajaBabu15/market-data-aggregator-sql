# src/plotting.py

import pandas as pd
import matplotlib.pyplot as plt
import mplfinance as mpf # For better financial plots
import os

from .config import PLOT_OUTPUT_DIR # Import output dir from config

def plot_ohlc_with_indicator(df, ticker, indicator_name, indicator_series, filename_suffix="plot"):
    """
    Generates and saves an OHLC/Candlestick plot with an overlaid indicator.

    Args:
        df (pd.DataFrame): DataFrame with OHLCV data and a DatetimeIndex named 'date'.
                           Requires columns 'open', 'high', 'low', 'close', 'volume'.
        ticker (str): Ticker symbol for title and filename.
        indicator_name (str): Name of the indicator (e.g., 'SMA_20').
        indicator_series (pd.Series): Series containing the indicator values, aligned with df's index.
        filename_suffix (str): Suffix for the output plot filename.
    """
    if df is None or df.empty:
        print(f"Plotting Error: No OHLCV data provided for {ticker}.")
        return
    if indicator_series is None or indicator_series.empty:
        print(f"Plotting Error: No indicator data provided for {ticker}.")
        return

    required_cols = {'open', 'high', 'low', 'close', 'volume'}
    if not required_cols.issubset(df.columns):
        missing = required_cols - set(df.columns)
        print(f"Plotting Error: DataFrame for {ticker} is missing columns: {missing}")
        return

    if not isinstance(df.index, pd.DatetimeIndex):
        print("Plotting Error: DataFrame index must be a DatetimeIndex.")
        return

    print(f"Plotting: Generating plot for {ticker} with {indicator_name}...")

    # Ensure indicator series is aligned and part of the dataframe for mplfinance
    plot_df = df.copy()
    plot_df[indicator_name] = indicator_series

    # Create the plot using mplfinance
    # Additional plot arguments (apdict) to plot the indicator on the main panel
    ap = [mpf.make_addplot(plot_df[indicator_name], panel=0, color='blue', alpha=0.7)] # panel 0 is the main price panel

    # Define plot style and save path
    style = 'yahoo' # Common financial plot style
    save_path = os.path.join(PLOT_OUTPUT_DIR, f"{ticker}_{indicator_name}_{filename_suffix}.png")

    try:
        mpf.plot(
            plot_df,
            type='candle', # 'ohlc' or 'candle'
            style=style,
            title=f"{ticker} OHLCV with {indicator_name}",
            ylabel='Price',
            ylabel_lower='Volume',
            volume=True, # Show volume subplot
            addplot=ap,
            figsize=(15, 8), # Set figure size
            tight_layout=True,
            savefig=dict(fname=save_path, dpi=150) # Save the figure
        )
        print(f"Plotting: Plot saved successfully to {save_path}")

    except Exception as e:
        print(f"Plotting Error: Failed to generate or save plot for {ticker}: {e}")

def print_summary(df, ticker, indicator_name, indicator_series):
     """Prints a simple summary of the latest data."""
     if df is None or df.empty or indicator_series is None or indicator_series.empty:
         print(f"Summary: No data to summarize for {ticker}.")
         return

     try:
        last_row = df.iloc[-1]
        last_indicator = indicator_series.iloc[-1]
        last_date = df.index[-1].strftime('%Y-%m-%d')

        print(f"\n--- Summary for {ticker} (as of {last_date}) ---")
        print(f"  Last Close:      {last_row['close']:.2f}")
        print(f"  Last Volume:     {last_row['volume']:,.0f}")
        print(f"  Last {indicator_name}: {last_indicator:.2f}" if pd.notna(last_indicator) else f"  Last {indicator_name}: N/A")
        print("------------------------------------")

     except IndexError:
         print(f"Summary Error: Could not get last row/indicator for {ticker}.")
     except Exception as e:
          print(f"Summary Error: An unexpected error occurred: {e}")