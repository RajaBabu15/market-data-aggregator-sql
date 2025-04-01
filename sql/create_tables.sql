-- -- sql/create_tables.sql
-- -- This file is for reference; table creation is handled by SQLAlchemy in database.py

-- CREATE TABLE IF NOT EXISTS ohlcv_data (
--     ticker VARCHAR(15) NOT NULL,
--     date DATE NOT NULL,
--     open NUMERIC(19, 8),
--     high NUMERIC(19, 8),
--     low NUMERIC(19, 8),
--     close NUMERIC(19, 8),
--     volume NUMERIC(25, 4),
--     PRIMARY KEY (ticker, date) -- Composite primary key
-- );

-- -- Optional: Indexes for performance
-- CREATE INDEX IF NOT EXISTS idx_ohlcv_ticker_date ON ohlcv_data (ticker, date);
-- CREATE INDEX IF NOT EXISTS idx_ohlcv_date ON ohlcv_data (date);

-- -- Grant permissions if needed (replace 'your_user' with the actual user from .env)
-- -- GRANT ALL PRIVILEGES ON TABLE ohlcv_data TO your_user;