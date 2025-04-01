# src/config.py

import os
from dotenv import load_dotenv

# Load environment variables from .env file in the project root
dotenv_path = os.path.join(os.path.dirname(__file__), '..', '.env') # Path to .env in root
load_dotenv(dotenv_path=dotenv_path)

# Database Connection String
# Format: postgresql+psycopg2://user:password@host:port/database
DATABASE_URI = os.getenv("DATABASE_URI")

if not DATABASE_URI:
    raise ValueError("DATABASE_URI not found in .env file. Please create .env and set it.")

# --- Other Configurations ---
DEFAULT_TICKERS = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'SPY', 'BTC-USD']
DEFAULT_SMA_WINDOW = 20 # Default window for Simple Moving Average

# Output directory for plots (relative to project root)
PLOT_OUTPUT_DIR = "output_plots"

# Ensure the plot output directory exists
project_root = os.path.dirname(dotenv_path)
abs_plot_output_dir = os.path.join(project_root, PLOT_OUTPUT_DIR)
if not os.path.exists(abs_plot_output_dir):
    try:
        os.makedirs(abs_plot_output_dir)
        print(f"Created plot output directory: {abs_plot_output_dir}")
    except OSError as e:
        print(f"Error creating directory {abs_plot_output_dir}: {e}")