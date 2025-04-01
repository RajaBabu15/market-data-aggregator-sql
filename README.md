
# Market Data Aggregation & Relational Storage System

This project provides an automated system to fetch daily OHLCV (Open, High, Low, Close, Volume) market data, clean it, store it in a PostgreSQL database, and visualize the data along with technical indicators like the Simple Moving Average (SMA).

## Features

*   **Data Fetching:** Uses `yfinance` to retrieve daily OHLCV data for specified stock/crypto tickers. (Easily extensible for other APIs like Alpha Vantage).
*   **Data Cleaning:** Basic routines to handle missing values and ensure data types using Pandas. Includes optional validation checks.
*   **Relational Storage:** Stores cleaned data in a PostgreSQL database using SQLAlchemy. The schema is optimized for time-series data with a composite primary key on `(ticker, date)` and relevant indexes. Uses "upsert" (ON CONFLICT DO UPDATE) logic for efficient data loading.
*   **Automation Ready:** Includes a script (`scripts/run_fetch_and_store.py`) designed to be run automatically (e.g., via Cron) for daily data updates.
*   **Data Visualization:** Includes a script (`scripts/run_visualize.py`) to fetch stored data for a specific ticker and date range, calculate a Simple Moving Average (SMA), and generate/save an OHLC/Candlestick plot using `mplfinance`.
*   **Configuration:** Database connection URI is managed via a `.env` file for security.

## Formula Used

**Simple Moving Average (SMA):**
The SMA is calculated by summing the closing prices over a specific period (window `n`) and dividing by the number of periods `n`.

$$
SMA_n = \frac{C_1 + C_2 + \dots + C_n}{n} 
$$

Where \( C_i \) is the closing price at period \( i \). In this project, the SMA is calculated on the `close` price column using `pandas.DataFrame.rolling(window=n).mean()`. The default window (`DEFAULT_SMA_WINDOW`) is set in `src/config.py`.

## Project Structure

```
market-data-aggregator-sql/
|-- src/                      # Source code module
|   |-- __init__.py
|   |-- config.py             # Loads configuration (DB URI, default tickers, SMA window)
|   |-- database.py           # SQLAlchemy setup, table definition, insert/fetch functions
|   |-- fetchers.py           # Data fetching logic (using yfinance)
|   |-- data_cleaner.py       # Data cleaning and validation functions
|   |-- indicators.py         # Technical indicator calculations (SMA)
|   `-- plotting.py           # Data visualization functions (using mplfinance)
|
|-- scripts/                  # Executable scripts
|   |-- run_fetch_and_store.py # Main script for fetching and storing data (for Cron)
|   `-- run_visualize.py       # Script to generate plots from stored data
|
|-- sql/                      # Reference SQL schema
|   `-- create_tables.sql     # SQL reference for table schema (managed by SQLAlchemy)
|
|-- output_plots/             # Default directory where generated plots are saved
|
|-- .env.example              # Example environment file template (RENAME to .env)
|-- .gitignore
|-- requirements.txt
`-- README.md                 # This documentation
```

## Setup

1.  **Prerequisites:**
    *   Python 3.7+
    *   PostgreSQL Server (installed and running)
    *   Git (Optional, for cloning)

2.  **Clone Repository:**
    ```bash
    git clone https://github.com/RajaBabu15/market-data-aggregator-sql.git
    cd market-data-aggregator-sql
    ```

3.  **Create PostgreSQL Database:**
    *   Connect to your PostgreSQL instance (e.g., using `psql` or pgAdmin).
    *   Create a database (e.g., `market_data_db`).
    *   Ensure you have a user/role with permissions to connect, create tables, and insert/select data.
    ```sql
    -- Example using psql
    CREATE DATABASE market_data_db;
    -- CREATE USER your_user WITH PASSWORD 'your_password'; -- If needed
    -- GRANT ALL PRIVILEGES ON DATABASE market_data_db TO your_user; -- Adjust permissions as necessary
    ```

4.  **Configure Environment:**
    *   Rename `.env.example` to `.env`.
    *   **Edit `.env`** and replace the placeholder `DATABASE_URI` with your actual PostgreSQL connection string.
        *   Format: `postgresql+psycopg2://your_user:your_password@your_host:your_port/market_data_db`

5.  **Create Virtual Environment & Install Dependencies:**
    ```bash
    python -m venv venv
    # Activate:
    # Windows: venv\Scripts\activate
    # Linux/macOS: source venv/bin/activate
    pip install -r requirements.txt
    ```

6.  **Initialize Database Table:**
    *   The first time you run `scripts/run_fetch_and_store.py`, it will attempt to create the `ohlcv_data` table using SQLAlchemy based on the definition in `src/database.py`. Ensure your database user has the necessary privileges.

## Usage

**1. Fetching and Storing Data:**

*   This script fetches recent data for tickers defined in `src/config.py` (or modify the script) and stores it in the database.
*   Run it manually from the project root:
    ```bash
    python scripts/run_fetch_and_store.py
    ```
*   **Automation with Cron (Linux/macOS):**
    *   Edit your crontab: `crontab -e`
    *   Add a line to run the script daily (e.g., at 7:00 AM server time). **Use absolute paths!**
    ```cron
    # Example: Run daily at 7:00 AM
    # Make sure venv/bin/python points to the correct python executable inside your virtualenv
    0 7 * * * /path/to/project/market-data-aggregator-sql/venv/bin/python /path/to/project/market-data-aggregator-sql/scripts/run_fetch_and_store.py >> /path/to/project/market-data-aggregator-sql/cron.log 2>&1
    ```
    *   Replace `/path/to/project/...` with the actual absolute paths on your system.
    *   `>> /path/to/project/market-data-aggregator-sql/cron.log 2>&1` redirects standard output and error to a log file.

**2. Visualizing Data:**

*   This script fetches data *from the database* for a specified ticker and generates a plot.
*   Run it from the project root, providing the ticker symbol as an argument:
    ```bash
    # Plot last 180 days for AAPL with default SMA(20)
    python scripts/run_visualize.py AAPL

    # Plot last 365 days for SPY with SMA(50)
    python scripts/run_visualize.py SPY -d 365 -w 50

    # Plot data for MSFT between specific dates
    python scripts/run_visualize.py MSFT -s 2023-01-01 -e 2023-12-31
    ```
*   Plots are saved by default in the `output_plots/` directory.

## Technologies Used

*   **Python 3:** Core programming language.
*   **Pandas:** Data manipulation and analysis.
*   **yfinance:** Fetching market data from Yahoo Finance.
*   **SQLAlchemy:** Python SQL toolkit and Object Relational Mapper (used here for Core expressions and connection management).
*   **psycopg2:** PostgreSQL adapter for Python (used by SQLAlchemy).
*   **Matplotlib:** Core plotting library.
*   **mplfinance:** Specialized library for financial plotting (OHLC, Candlestick).
*   **python-dotenv:** Loading environment variables from `.env` files.
*   **PostgreSQL:** Relational database for storing time-series data.
*   **Cron (Linux/macOS):** Standard Unix job scheduler for automation.

## Limitations

*   **Data Source Reliability:** Depends on the availability and accuracy of the chosen API (yfinance). APIs can change, have rate limits, or provide incomplete/incorrect data.
*   **Error Handling:** Basic error handling is implemented, but robust production systems would require more sophisticated logging, monitoring, and retry mechanisms.
*   **Data Cleaning:** Cleaning is basic (NaN removal). More advanced validation (outlier detection, volume spike analysis) could be added.
*   **Scalability:** For very high frequency data or a huge number of tickers, the current PostgreSQL schema and insertion method might need further optimization (e.g., partitioning, bulk loading with `COPY`).
*   **Cron Environment:** Running Python scripts via Cron requires careful management of paths and environments (using absolute paths and the correct Python interpreter from the virtual environment is crucial).
