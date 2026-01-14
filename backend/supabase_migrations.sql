-- Supabase Database Migrations
-- Run these SQL commands in your Supabase SQL Editor

-- Table: bond_valuations
-- Stores bond valuation calculation results
CREATE TABLE IF NOT EXISTS bond_valuations (
    id BIGSERIAL PRIMARY KEY,
    secid VARCHAR(50) NOT NULL,
    valuation_date DATE NOT NULL,
    discount_yield1 DECIMAL(10, 4) NOT NULL,
    discount_yield2 DECIMAL(10, 4) NOT NULL,
    dirty_price DECIMAL(15, 2) NOT NULL,
    clean_price DECIMAL(15, 2) NOT NULL,
    ytm DECIMAL(10, 4) NOT NULL,
    duration DECIMAL(10, 4) NOT NULL,
    modified_duration DECIMAL(10, 4),
    convexity DECIMAL(15, 6),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes for faster queries
CREATE INDEX IF NOT EXISTS idx_bond_valuations_secid ON bond_valuations(secid);
CREATE INDEX IF NOT EXISTS idx_bond_valuations_date ON bond_valuations(valuation_date);
CREATE INDEX IF NOT EXISTS idx_bond_valuations_created ON bond_valuations(created_at DESC);

-- Table: portfolios
-- Stores portfolio configurations and data
CREATE TABLE IF NOT EXISTS portfolios (
    id BIGSERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    positions JSONB NOT NULL DEFAULT '{}',
    total_value DECIMAL(15, 2) NOT NULL DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_portfolios_name ON portfolios(name);
CREATE INDEX IF NOT EXISTS idx_portfolios_created ON portfolios(created_at DESC);

-- Table: calculation_history
-- Stores history of all calculations for audit and analytics
CREATE TABLE IF NOT EXISTS calculation_history (
    id BIGSERIAL PRIMARY KEY,
    calculation_type VARCHAR(50) NOT NULL,
    input_data JSONB NOT NULL,
    result_data JSONB NOT NULL,
    execution_time_ms DECIMAL(10, 2),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_calc_history_type ON calculation_history(calculation_type);
CREATE INDEX IF NOT EXISTS idx_calc_history_created ON calculation_history(created_at DESC);

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

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Triggers to auto-update updated_at
DROP TRIGGER IF EXISTS update_bond_valuations_updated_at ON bond_valuations;
CREATE TRIGGER update_bond_valuations_updated_at 
    BEFORE UPDATE ON bond_valuations
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_portfolios_updated_at ON portfolios;
CREATE TRIGGER update_portfolios_updated_at 
    BEFORE UPDATE ON portfolios
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_files_updated_at ON files;
CREATE TRIGGER update_files_updated_at 
    BEFORE UPDATE ON files
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Row Level Security (RLS) - Enable if needed
-- ALTER TABLE bond_valuations ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE portfolios ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE calculation_history ENABLE ROW LEVEL SECURITY;

-- Example policies (adjust based on your needs)
-- CREATE POLICY "Allow public read access" ON bond_valuations
--     FOR SELECT USING (true);
-- 
-- CREATE POLICY "Allow authenticated insert" ON bond_valuations
--     FOR INSERT WITH CHECK (auth.role() = 'authenticated');
