# src/database.py

from sqlalchemy import create_engine, MetaData, Table, Column, String, Date, Numeric, PrimaryKeyConstraint, Index
from sqlalchemy.dialects.postgresql import insert as pg_insert # For ON CONFLICT DO UPDATE
from sqlalchemy.exc import SQLAlchemyError
import pandas as pd

from .config import DATABASE_URI

# --- SQLAlchemy Setup ---
try:
    engine = create_engine(DATABASE_URI, echo=False) # Set echo=True for SQL logging
    metadata = MetaData()
    print("Database engine created successfully.")
except Exception as e:
    print(f"Error creating database engine: {e}")
    engine = None
    metadata = None

# Define the OHLCV table structure using SQLAlchemy Core
ohlcv_table = Table(
    'ohlcv_data', metadata,
    Column('ticker', String(15), nullable=False),
    Column('date', Date, nullable=False),
    Column('open', Numeric(19, 8), nullable=True), # Allow NULLs if data source is missing points
    Column('high', Numeric(19, 8), nullable=True),
    Column('low', Numeric(19, 8), nullable=True),
    Column('close', Numeric(19, 8), nullable=True),
    Column('volume', Numeric(25, 4), nullable=True), # Using Numeric for potentially large volumes
    PrimaryKeyConstraint('ticker', 'date', name='ohlcv_data_pkey'),
    Index('idx_ohlcv_ticker_date', 'ticker', 'date') # Index for efficient lookups
)

# --- Database Functions ---

def create_db_tables():
    """Creates the database tables defined in the metadata if they don't exist."""
    if engine is None or metadata is None:
        print("Database engine not initialized. Cannot create tables.")
        return False
    try:
        print("Attempting to create database tables if they don't exist...")
        metadata.create_all(engine)
        print("Tables checked/created successfully.")
        return True
    except SQLAlchemyError as e:
        print(f"Error creating database tables: {e}")
        return False
    except Exception as e:
        print(f"An unexpected error occurred during table creation: {e}")
        return False


def insert_ohlcv_data(df):
    """
    Inserts or updates OHLCV data from a Pandas DataFrame into the PostgreSQL database.

    Args:
        df (pd.DataFrame): DataFrame with columns matching the ohlcv_table structure
                           (ticker, date, open, high, low, close, volume).
                           'date' column should contain date objects or be parsable.
    """
    if engine is None:
        print("Database engine not initialized. Cannot insert data.")
        return
    if df is None or df.empty:
        print("No data provided for insertion.")
        return

    required_cols = {'ticker', 'date', 'open', 'high', 'low', 'close', 'volume'}
    if not required_cols.issubset(df.columns):
        missing = required_cols - set(df.columns)
        print(f"Error: DataFrame is missing required columns: {missing}")
        return

    # Prepare data for insertion (list of dictionaries)
    # Ensure date is date object, handle potential NaNs -> None for SQL
    df_copy = df.copy()
    df_copy['date'] = pd.to_datetime(df_copy['date']).dt.date
    # Replace Pandas NA/NaN with None for database compatibility
    data_to_insert = df_copy[list(required_cols)].replace({pd.NA: None, np.nan: None}).to_dict(orient='records')


    if not data_to_insert:
        print("Data became empty after processing NAs, nothing to insert.")
        return

    # Use PostgreSQL's ON CONFLICT DO UPDATE (Upsert)
    stmt = pg_insert(ohlcv_table).values(data_to_insert)
    update_dict = {col.name: stmt.excluded[col.name] for col in ohlcv_table.columns if col.name not in ['ticker', 'date']}
    upsert_stmt = stmt.on_conflict_do_update(
        index_elements=['ticker', 'date'], # Constraint name or columns
        set_=update_dict
    )

    try:
        with engine.connect() as connection:
            with connection.begin(): # Start transaction
                connection.execute(upsert_stmt)
        print(f"Successfully inserted/updated {len(data_to_insert)} rows for tickers: {df['ticker'].unique().tolist()}")
    except SQLAlchemyError as e:
        print(f"Database error during data insertion: {e}")
    except Exception as e:
        print(f"An unexpected error occurred during data insertion: {e}")


def fetch_ohlcv_data(ticker, start_date=None, end_date=None):
    """
    Fetches OHLCV data for a specific ticker from the database.

    Args:
        ticker (str): The ticker symbol to fetch.
        start_date (str or date, optional): Start date (inclusive). Defaults to None (no start limit).
        end_date (str or date, optional): End date (inclusive). Defaults to None (no end limit).

    Returns:
        pd.DataFrame: DataFrame containing the OHLCV data, sorted by date.
                      Returns empty DataFrame if no data or error.
    """
    if engine is None:
        print("Database engine not initialized. Cannot fetch data.")
        return pd.DataFrame()

    stmt = ohlcv_table.select().where(ohlcv_table.c.ticker == ticker)

    if start_date:
        stmt = stmt.where(ohlcv_table.c.date >= pd.to_datetime(start_date).date())
    if end_date:
        stmt = stmt.where(ohlcv_table.c.date <= pd.to_datetime(end_date).date())

    stmt = stmt.order_by(ohlcv_table.c.date)

    try:
        with engine.connect() as connection:
            df = pd.read_sql(stmt, connection, index_col='date', parse_dates=['date'])
        # Convert numeric columns back from potentially Decimal types
        for col in ['open', 'high', 'low', 'close', 'volume']:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
        print(f"Fetched {len(df)} rows for ticker {ticker} from database.")
        return df
    except SQLAlchemyError as e:
        print(f"Database error fetching data for {ticker}: {e}")
        return pd.DataFrame()
    except Exception as e:
        print(f"An unexpected error occurred fetching data for {ticker}: {e}")
        return pd.DataFrame()