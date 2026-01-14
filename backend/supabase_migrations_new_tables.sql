-- Supabase Database Migrations - New Tables Only
-- Run these SQL commands in your Supabase SQL Editor

-- Table: market_data_daily
-- Stores daily market data snapshots
CREATE TABLE IF NOT EXISTS market_data_daily (
    id BIGSERIAL PRIMARY KEY,
    ticker VARCHAR(50) NOT NULL,
    data_type VARCHAR(50) NOT NULL, -- 'stock', 'bond', 'currency', 'index', 'crypto'
    date DATE NOT NULL,
    price DECIMAL(15, 4),
    volume BIGINT,
    change_percent DECIMAL(10, 4),
    metadata JSONB DEFAULT '{}', -- Дополнительные данные (marketCap, peRatio, etc.)
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(ticker, data_type, date)
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_market_data_ticker ON market_data_daily(ticker);
CREATE INDEX IF NOT EXISTS idx_market_data_type ON market_data_daily(data_type);
CREATE INDEX IF NOT EXISTS idx_market_data_date ON market_data_daily(date DESC);
CREATE INDEX IF NOT EXISTS idx_market_data_ticker_date ON market_data_daily(ticker, date DESC);

-- Table: files
-- Stores metadata about uploaded files (реестры, отчеты)
CREATE TABLE IF NOT EXISTS files (
    id BIGSERIAL PRIMARY KEY,
    file_name VARCHAR(255) NOT NULL,
    file_path VARCHAR(500) NOT NULL, -- Path in Supabase Storage
    file_type VARCHAR(100) NOT NULL, -- 'register', 'report', 'export', etc.
    file_size BIGINT NOT NULL,
    mime_type VARCHAR(100),
    description TEXT,
    metadata JSONB DEFAULT '{}', -- Дополнительные метаданные
    created_by VARCHAR(255),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_files_type ON files(file_type);
CREATE INDEX IF NOT EXISTS idx_files_created ON files(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_files_path ON files(file_path);

-- Function to update updated_at timestamp (only if not exists)
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Trigger for files table
DROP TRIGGER IF EXISTS update_files_updated_at ON files;
CREATE TRIGGER update_files_updated_at 
    BEFORE UPDATE ON files
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();
